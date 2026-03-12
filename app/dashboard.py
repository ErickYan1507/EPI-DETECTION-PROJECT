# app/dashboard.py - Logique métier du dashboard
from flask import Blueprint, render_template, jsonify, current_app, request
from .database_unified import db, Detection, Alert, AttendanceRecord, TIMEZONE_OFFSET
from datetime import datetime, timedelta
import json
from app.logger import logger
from sqlalchemy import text

dashboard_bp = Blueprint('dashboard', __name__)

def get_db():
    """Get database instance"""
    return db

@dashboard_bp.route('/api/dashboard/stats')
def get_dashboard_stats():
    """Obtenir les statistiques pour le dashboard"""
    try:
        now_local = datetime.utcnow() + TIMEZONE_OFFSET
        last_24h_utc = datetime.utcnow() - timedelta(hours=24)
        recent_rows = AttendanceRecord.query.filter(
            AttendanceRecord.first_seen_at >= last_24h_utc
        ).all()
        
        # Calcul des statistiques
        stats = {
            'total_detections': len(recent_rows),
            'avg_compliance': 0,
            'total_persons': 0,
            'alerts_today': 0,
            'compliance_trend': [],
            'error': None
        }
        
        if recent_rows:
            # Conformité moyenne
            rates = [float(r.compliance_rate) for r in recent_rows if r.compliance_rate is not None]
            total_compliance = sum(rates)
            stats['avg_compliance'] = round(total_compliance / len(rates), 2) if rates else 0
            
            # Total personnes
            stats['total_persons'] = len(recent_rows)
            
            # Alertes aujourd'hui
            local_day_start = datetime.combine(now_local.date(), datetime.min.time())
            utc_day_start = local_day_start - TIMEZONE_OFFSET
            utc_day_end = utc_day_start + timedelta(days=1)
            stats['alerts_today'] = Alert.query.filter(
                Alert.timestamp >= utc_day_start,
                Alert.timestamp < utc_day_end
            ).count()
            
            # Tendance (6 dernières heures)
            for i in range(6):
                hour_start = datetime.utcnow() - timedelta(hours=i+1)
                hour_end = datetime.utcnow() - timedelta(hours=i)
                
                hour_rows = AttendanceRecord.query.filter(
                    AttendanceRecord.first_seen_at >= hour_start,
                    AttendanceRecord.first_seen_at < hour_end
                ).all()
                
                if hour_rows:
                    vals = [float(r.compliance_rate) for r in hour_rows if r.compliance_rate is not None]
                    hour_compliance = (sum(vals) / len(vals)) if vals else 0
                    stats['compliance_trend'].append(round(hour_compliance, 2))
                else:
                    stats['compliance_trend'].append(0)
            
            stats['compliance_trend'].reverse()
        
        logger.info(f"Dashboard stats retrieved: {stats['total_detections']} detections")
        return jsonify(stats)
    
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        return jsonify({
            'error': str(e),
            'total_detections': 0,
            'avg_compliance': 0,
            'total_persons': 0,
            'alerts_today': 0,
            'compliance_trend': []
        }), 500

@dashboard_bp.route('/api/dashboard/alerts')
def get_recent_alerts():
    """Obtenir les alertes récentes"""
    try:
        alerts = Alert.query.filter_by(resolved=False).order_by(
            Alert.timestamp.desc()
        ).limit(10).all()
        
        alerts_data = [{
            'id': alert.id,
            'timestamp': (alert.timestamp + TIMEZONE_OFFSET).strftime('%H:%M:%S') if alert.timestamp else None,
            'message': alert.message,
            'severity': alert.severity,
            'type': alert.type,
            'resolved': alert.resolved
        } for alert in alerts]
        
        logger.info(f"Retrieved {len(alerts_data)} recent alerts")
        return jsonify(alerts_data)
    
    except Exception as e:
        logger.error(f"Error getting alerts: {str(e)}")
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/api/dashboard/detections/hourly')
def get_hourly_detections():
    """Obtenir les détections par heure"""
    try:
        hourly_data = {}
        now_local = datetime.utcnow() + TIMEZONE_OFFSET
        today = now_local.date()
        
        for hour in range(24):
            local_hour_start = datetime.combine(today, datetime.min.time()).replace(hour=hour)
            local_hour_end = local_hour_start + timedelta(hours=1)
            hour_start = local_hour_start - TIMEZONE_OFFSET
            hour_end = local_hour_end - TIMEZONE_OFFSET
            
            count = AttendanceRecord.query.filter(
                AttendanceRecord.first_seen_at >= hour_start,
                AttendanceRecord.first_seen_at < hour_end
            ).count()
            
            hourly_data[f'{hour:02d}:00'] = count
        
        logger.info(f"Retrieved hourly detections data")
        return jsonify(hourly_data)
    
    except Exception as e:
        logger.error(f"Error getting hourly detections: {str(e)}")
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/api/dashboard/compliance/trend')
def get_compliance_trend():
    """Obtenir la tendance de conformité par jour"""
    try:
        days_back = 7
        trend_data = {}
        
        for i in range(days_back):
            day = datetime.utcnow().date() - timedelta(days=i)
            day_start = datetime.combine(day, datetime.min.time())
            day_end = day_start + timedelta(days=1)
            
            day_detections = Detection.query.filter(
                Detection.timestamp >= day_start,
                Detection.timestamp < day_end
            ).all()
            
            if day_detections:
                avg_compliance = sum(d.compliance_rate for d in day_detections if d.compliance_rate) / len(day_detections)
                trend_data[day.strftime('%Y-%m-%d')] = round(avg_compliance, 2)
            else:
                trend_data[day.strftime('%Y-%m-%d')] = 0
        
        logger.info(f"Retrieved compliance trend for {days_back} days")
        return jsonify(trend_data)
    
    except Exception as e:
        logger.error(f"Error getting compliance trend: {str(e)}")
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/api/dashboard/health')
def dashboard_health():
    """Vérifier la santé de la connexion à la base de données"""
    try:
        db.session.execute(text('SELECT 1'))
        logger.info("Database connection health check passed")
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


# -------------------- Arduino API Routes --------------------
class ArduinoRoutes:
    """
    Routes Flask pour contrôler Arduino (intégration basique)
    """

    @staticmethod
    def get_blueprint():
        from flask import Blueprint

        bp = Blueprint('arduino_api', __name__, url_prefix='/api/arduino')

        @bp.route('/status')
        def get_status():
            try:
                arduino = current_app.arduino if hasattr(current_app, 'arduino') else None

                if arduino and getattr(arduino, 'connected', False):
                    return jsonify({
                        'status': 'success',
                        'connected': True,
                        'port': getattr(arduino, 'port', None),
                        'baudrate': getattr(arduino, 'baudrate', None),
                        'timestamp': datetime.utcnow().isoformat()
                    })

                # If app.arduino is not set, check physical_routes Arduino sessions
                try:
                    from app.routes_physical_devices import arduino_sessions
                    # Find any connected session
                    for p, session in arduino_sessions.items():
                        metrics = session.get_current_metrics()
                        # session.connect sets controller.connected inside ArduinoSessionManager
                        controller_connected = getattr(session.controller, 'connected', False) if hasattr(session, 'controller') else False
                        if controller_connected:
                            return jsonify({
                                'status': 'success',
                                'connected': True,
                                'port': p,
                                'baudrate': getattr(session.controller, 'baudrate', None) if controller_connected else None,
                                'timestamp': datetime.utcnow().isoformat()
                            })
                except Exception:
                    # ignore if physical module not available
                    pass

                return jsonify({
                    'status': 'error',
                    'message': 'Arduino non initialisé',
                    'connected': False
                }), 503

            except Exception as e:
                logger.error(f"Erreur status Arduino: {e}")
                return jsonify({'status': 'error', 'message': str(e)}), 500

        @bp.route('/alert/<int:level>', methods=['POST'])
        def send_alert(level):
            try:
                level = max(0, min(100, level))
                arduino = current_app.arduino if hasattr(current_app, 'arduino') else None

                if not arduino or not getattr(arduino, 'connected', False):
                    return jsonify({'status': 'error', 'message': 'Arduino non connecté'}), 503

                success = arduino.send_compliance_level(level)

                if success:
                    if level >= 80:
                        led_color = 'VERT'
                        alert_type = 'SAFE'
                    elif level >= 60:
                        led_color = 'JAUNE'
                        alert_type = 'WARNING'
                    else:
                        led_color = 'ROUGE'
                        alert_type = 'DANGER'

                    logger.info(f"Alerte Arduino envoyée: {level}% -> {led_color}")
                    return jsonify({'status': 'success', 'compliance': level, 'led': led_color, 'alert_type': alert_type})
                else:
                    return jsonify({'status': 'error', 'message': 'Erreur envoi à Arduino'}), 500

            except Exception as e:
                logger.error(f"Erreur alerte Arduino: {e}")
                return jsonify({'status': 'error', 'message': str(e)}), 500

        @bp.route('/detection', methods=['POST'])
        def send_detection():
            try:
                data = request.json or {}
                helmet = bool(data.get('helmet', False))
                vest = bool(data.get('vest', False))
                glasses = bool(data.get('glasses', False))
                confidence = int(data.get('confidence', 0))

                arduino = current_app.arduino if hasattr(current_app, 'arduino') else None
                if not arduino or not getattr(arduino, 'connected', False):
                    return jsonify({'status': 'error', 'message': 'Arduino non connecté'}), 503

                success = arduino.send_detection_data(helmet, vest, glasses, confidence)

                if success:
                    compliance = calculate_compliance(helmet, vest, glasses, confidence)
                    logger.info(f"EPI détection envoyée à Arduino (compliance={compliance}%)")
                    return jsonify({'status': 'success', 'detection': {'helmet': helmet, 'vest': vest, 'glasses': glasses, 'confidence': confidence, 'compliance': compliance}})
                else:
                    return jsonify({'status': 'error', 'message': 'Erreur envoi détection'}), 500

            except Exception as e:
                logger.error(f"Erreur envoi détection Arduino: {e}")
                return jsonify({'status': 'error', 'message': str(e)}), 500

        # Compatibility endpoints expected by existing frontend JS
        @bp.route('/send-compliance', methods=['POST'])
        def send_compliance_post():
            try:
                data = request.json or {}
                level = data.get('level') if 'level' in data else data.get('compliance')
                if level is None:
                    return jsonify({'success': False, 'message': 'level missing'}), 400

                level = int(level)
                arduino = current_app.arduino if hasattr(current_app, 'arduino') else None
                if not arduino or not getattr(arduino, 'connected', False):
                    return jsonify({'success': False, 'message': 'Arduino non connecté'}), 503

                ok = arduino.send_compliance_level(level)
                return jsonify({'success': ok, 'compliance': level})
            except Exception as e:
                logger.error(f"Erreur send-compliance: {e}")
                return jsonify({'success': False, 'message': str(e)}), 500

        @bp.route('/send-detection', methods=['POST'])
        def send_detection_post():
            try:
                data = request.json or {}
                helmet = bool(data.get('helmet', False))
                vest = bool(data.get('vest', False))
                glasses = bool(data.get('glasses', False))
                confidence = int(data.get('confidence', 0))

                arduino = current_app.arduino if hasattr(current_app, 'arduino') else None
                if not arduino or not getattr(arduino, 'connected', False):
                    return jsonify({'success': False, 'message': 'Arduino non connecté'}), 503

                ok = arduino.send_detection_data(helmet, vest, glasses, confidence)
                return jsonify({'success': ok, 'detection': {'helmet': helmet, 'vest': vest, 'glasses': glasses, 'confidence': confidence}})
            except Exception as e:
                logger.error(f"Erreur send-detection: {e}")
                return jsonify({'success': False, 'message': str(e)}), 500

        return bp


def calculate_compliance(helmet, vest, glasses, confidence):
    """Calculer score conformité 0-100"""
    score = 0
    if helmet:
        score += 33
    if vest:
        score += 33
    if glasses:
        score += 34

    score = (score * max(0, min(100, int(confidence)))) // 100
    return max(0, min(100, score))

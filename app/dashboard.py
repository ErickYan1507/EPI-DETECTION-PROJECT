# app/dashboard.py - Logique métier du dashboard
from flask import Blueprint, render_template, jsonify, current_app
from .database_unified import db, Detection, Alert
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
        # Détections des dernières 24h
        last_24h = datetime.utcnow() - timedelta(hours=24)
        recent_detections = Detection.query.filter(
            Detection.timestamp >= last_24h
        ).all()
        
        # Calcul des statistiques
        stats = {
            'total_detections': len(recent_detections),
            'avg_compliance': 0,
            'total_persons': 0,
            'alerts_today': 0,
            'compliance_trend': [],
            'error': None
        }
        
        if recent_detections:
            # Conformité moyenne
            total_compliance = sum(d.compliance_rate for d in recent_detections if d.compliance_rate)
            stats['avg_compliance'] = round(total_compliance / len(recent_detections), 2) if total_compliance > 0 else 0
            
            # Total personnes
            stats['total_persons'] = sum(d.total_persons for d in recent_detections if d.total_persons)
            
            # Alertes aujourd'hui
            today = datetime.utcnow().date()
            stats['alerts_today'] = Alert.query.filter(
                db.func.date(Alert.timestamp) == today
            ).count()
            
            # Tendance (6 dernières heures)
            for i in range(6):
                hour_start = datetime.utcnow() - timedelta(hours=i+1)
                hour_end = datetime.utcnow() - timedelta(hours=i)
                
                hour_detections = Detection.query.filter(
                    Detection.timestamp >= hour_start,
                    Detection.timestamp < hour_end
                ).all()
                
                if hour_detections:
                    hour_compliance = sum(d.compliance_rate for d in hour_detections if d.compliance_rate) / len(hour_detections)
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
            'timestamp': alert.timestamp.strftime('%H:%M:%S'),
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
        today = datetime.utcnow().date()
        
        for hour in range(24):
            hour_start = datetime.combine(today, datetime.min.time()).replace(hour=hour)
            hour_end = hour_start + timedelta(hours=1)
            
            count = Detection.query.filter(
                Detection.timestamp >= hour_start,
                Detection.timestamp < hour_end
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
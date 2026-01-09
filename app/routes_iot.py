"""Routes API pour l'intégration IoT et TinkerCad"""

from flask import Blueprint, request, jsonify, render_template
from datetime import datetime, timedelta
from app.database_unified import db, IoTSensor, IoTDataLog
from app.logger import logger
import json

iot_routes = Blueprint('iot', __name__, url_prefix='/api/iot')

@iot_routes.route('/sensors', methods=['GET'])
def get_sensors():
    """Récupérer tous les capteurs IoT"""
    try:
        sensors = IoTSensor.query.all()
        
        return jsonify({
            'success': True,
            'count': len(sensors),
            'sensors': [s.to_dict() for s in sensors]
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur récupération capteurs: {e}")
        return jsonify({'error': str(e)}), 500

@iot_routes.route('/sensors/<int:sensor_id>', methods=['GET'])
def get_sensor(sensor_id):
    """Récupérer un capteur spécifique"""
    try:
        sensor = IoTSensor.query.get(sensor_id)
        if not sensor:
            return jsonify({'error': 'Capteur non trouvé'}), 404
        
        return jsonify({
            'success': True,
            'sensor': sensor.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur récupération capteur: {e}")
        return jsonify({'error': str(e)}), 500

@iot_routes.route('/sensors/<sensor_id>/data', methods=['GET'])
def get_sensor_data(sensor_id):
    """Récupérer les données d'un capteur"""
    try:
        limit = request.args.get('limit', 100, type=int)
        minutes = request.args.get('minutes', 60, type=int)
        
        sensor = IoTSensor.query.filter_by(sensor_id=sensor_id).first()
        if not sensor:
            return jsonify({'error': 'Capteur non trouvé'}), 404
        
        # Récupérer les données
        time_filter = datetime.utcnow() - timedelta(minutes=minutes)
        data_logs = IoTDataLog.query.filter(
            IoTDataLog.sensor_id == sensor.id,
            IoTDataLog.timestamp >= time_filter
        ).order_by(IoTDataLog.timestamp.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'sensor_id': sensor_id,
            'sensor_name': sensor.sensor_name,
            'count': len(data_logs),
            'data': [d.to_dict() for d in data_logs]
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur récupération données: {e}")
        return jsonify({'error': str(e)}), 500

@iot_routes.route('/sensors/<sensor_id>/stats', methods=['GET'])
def get_sensor_stats(sensor_id):
    """Obtenir les statistiques d'un capteur"""
    try:
        minutes = request.args.get('minutes', 60, type=int)
        
        sensor = IoTSensor.query.filter_by(sensor_id=sensor_id).first()
        if not sensor:
            return jsonify({'error': 'Capteur non trouvé'}), 404
        
        # Récupérer les données
        time_filter = datetime.utcnow() - timedelta(minutes=minutes)
        data_logs = IoTDataLog.query.filter(
            IoTDataLog.sensor_id == sensor.id,
            IoTDataLog.timestamp >= time_filter
        ).all()
        
        if not data_logs:
            return jsonify({
                'success': True,
                'sensor_id': sensor_id,
                'stats': None
            }), 200
        
        # Calculer les statistiques
        compliance_levels = [d.compliance_level for d in data_logs if d.compliance_level is not None]
        worker_present_count = len([d for d in data_logs if d.worker_present])
        motion_detected_count = len([d for d in data_logs if d.motion_detected])
        led_red_count = len([d for d in data_logs if d.led_red])
        buzzer_count = len([d for d in data_logs if d.buzzer_active])
        
        stats = {
            'total_readings': len(data_logs),
            'time_range_minutes': minutes,
            'compliance': {
                'min': min(compliance_levels) if compliance_levels else 0,
                'max': max(compliance_levels) if compliance_levels else 0,
                'avg': sum(compliance_levels) / len(compliance_levels) if compliance_levels else 0
            },
            'worker_present_count': worker_present_count,
            'motion_detected_count': motion_detected_count,
            'alerts': {
                'led_red_triggered': led_red_count,
                'buzzer_triggered': buzzer_count
            }
        }
        
        return jsonify({
            'success': True,
            'sensor_id': sensor_id,
            'stats': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur calcul stats: {e}")
        return jsonify({'error': str(e)}), 500

@iot_routes.route('/simulation/start', methods=['POST'])
def start_simulation():
    """Démarrer la simulation TinkerCad"""
    try:
        from app.main import tinkercad_sim
        
        # Enregistrer le capteur s'il n'existe pas
        if not tinkercad_sim.sensor_db_id:
            tinkercad_sim.register_sensor(
                sensor_name="TinkerCad EPI Simulation",
                location="Virtual Lab"
            )
        
        tinkercad_sim.start_simulation()
        
        return jsonify({
            'success': True,
            'message': 'Simulation démarrée',
            'sensor_id': tinkercad_sim.sensor_id
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur démarrage simulation: {e}")
        return jsonify({'error': str(e)}), 500

@iot_routes.route('/simulation/stop', methods=['POST'])
def stop_simulation():
    """Arrêter la simulation TinkerCad"""
    try:
        from app.main import tinkercad_sim
        
        tinkercad_sim.stop_simulation()
        
        return jsonify({
            'success': True,
            'message': 'Simulation arrêtée'
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur arrêt simulation: {e}")
        return jsonify({'error': str(e)}), 500

@iot_routes.route('/simulation/state', methods=['GET'])
def get_simulation_state():
    """Obtenir l'état actuel de la simulation"""
    try:
        from app.main import tinkercad_sim
        
        return jsonify({
            'success': True,
            'running': tinkercad_sim.is_running,
            'state': tinkercad_sim.get_state(),
            'sensor_id': tinkercad_sim.sensor_id
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur récupération état: {e}")
        return jsonify({'error': str(e)}), 500

@iot_routes.route('/simulation/force-compliance', methods=['POST'])
def force_compliance():
    """Forcer le niveau de conformité pour les tests"""
    try:
        from app.main import tinkercad_sim
        
        data = request.json
        level = data.get('level', 50)
        
        new_state = tinkercad_sim.force_compliance_level(level)
        
        return jsonify({
            'success': True,
            'message': f'Conformité forcée à {level}%',
            'state': new_state
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur forçage conformité: {e}")
        return jsonify({'error': str(e)}), 500

@iot_routes.route('/data-logs', methods=['GET'])
def get_data_logs():
    """Récupérer tous les logs de données IoT"""
    try:
        limit = request.args.get('limit', 100, type=int)
        sensor_id = request.args.get('sensor_id', type=int)
        
        query = IoTDataLog.query.order_by(IoTDataLog.timestamp.desc())
        
        if sensor_id:
            query = query.filter_by(sensor_id=sensor_id)
        
        logs = query.limit(limit).all()
        
        return jsonify({
            'success': True,
            'count': len(logs),
            'logs': [l.to_dict() for l in logs]
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur récupération logs: {e}")
        return jsonify({'error': str(e)}), 500

@iot_routes.route('/summary', methods=['GET'])
def get_iot_summary():
    """Obtenir un résumé des données IoT"""
    try:
        # Comptage
        total_sensors = IoTSensor.query.count()
        active_sensors = IoTSensor.query.filter_by(status='active').count()
        
        # Dernières données
        latest_logs = IoTDataLog.query.order_by(
            IoTDataLog.timestamp.desc()
        ).limit(100).all()
        
        # Statistiques
        avg_compliance = None
        if latest_logs:
            compliance_values = [l.compliance_level for l in latest_logs if l.compliance_level is not None]
            if compliance_values:
                avg_compliance = sum(compliance_values) / len(compliance_values)
        
        alerts_count = len([l for l in latest_logs if l.buzzer_active or l.led_red])
        
        return jsonify({
            'success': True,
            'summary': {
                'total_sensors': total_sensors,
                'active_sensors': active_sensors,
                'avg_compliance': round(avg_compliance, 2) if avg_compliance else 0,
                'recent_alerts': alerts_count,
                'total_readings': IoTDataLog.query.count()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur résumé: {e}")
        return jsonify({'error': str(e)}), 500

@iot_routes.route('/tinkercad/update', methods=['POST'])
def update_tinkercad():
    """Recevoir les mises à jour de la simulation TinkerCad"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        sensor_id = data.get('sensor_id')
        timestamp = data.get('timestamp', datetime.utcnow().isoformat())
        state_data = data.get('data', {})
        
        # Optionnel: Enregistrer dans la BD
        try:
            if sensor_id:
                sensor = IoTSensor.query.filter_by(sensor_id=sensor_id).first()
                if sensor:
                    # Créer un log
                    log = IoTDataLog(
                        sensor_id=sensor.id,
                        timestamp=datetime.fromisoformat(timestamp) if isinstance(timestamp, str) else timestamp,
                        motion_detected=state_data.get('motion_detected', False),
                        worker_present=state_data.get('worker_present', False),
                        compliance_level=state_data.get('compliance_level', 100),
                        led_green=state_data.get('led_green', True),
                        led_red=state_data.get('led_red', False),
                        buzzer_active=state_data.get('buzzer_active', False),
                        raw_data=json.dumps(state_data)
                    )
                    db.session.add(log)
                    db.session.commit()
                    
                    logger.debug(f"TinkerCad update reçu et sauvegardé: {sensor_id}")
        except Exception as e:
            logger.warning(f"Erreur sauvegarde log TinkerCad: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Update received',
            'sensor_id': sensor_id
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur traitement update TinkerCad: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

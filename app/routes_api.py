"""
Routes API pour la détection
"""
from flask import Blueprint, request, jsonify
import cv2
import os
from datetime import datetime, timedelta, timezone
import base64
import re
import numpy as np
from app.database_unified import db, Detection, Alert, TrainingResult
from app.detection import EPIDetector
from app.multi_model_detector import MultiModelDetector
from app.logger import logger
from app.utils import save_uploaded_file, validate_image_file
from app.constants import calculate_compliance_score
from config import config

api_routes = Blueprint('api', __name__, url_prefix='/api')

# ============== UTILITAIRES POUR FUSEAU HORAIRE ==============
# Décalage horaire pour Madagascar (UTC+3 toute l'année)
TIMEZONE_OFFSET = timedelta(hours=3)  # À ajuster selon votre fuseau horaire

def utc_to_local(utc_datetime):
    """Convertir un datetime UTC en heure locale"""
    if utc_datetime is None:
        return None
    if isinstance(utc_datetime, datetime):
        return utc_datetime + TIMEZONE_OFFSET
    return utc_datetime

def format_detection_timestamp(detection):
    """Formater le timestamp d'une détection en heure locale"""
    if detection.timestamp:
        local_time = utc_to_local(detection.timestamp)
        return local_time.strftime('%H:%M:%S')
    return '--:--:--'
# ============================================================

# Détecteurs initialisés à la demande
_detector = None
_multi_detector = None

def get_detector():
    """Obtenir ou initialiser le détecteur (lazy loading)"""
    global _detector
    if _detector is None:
        logger.info("Initialisation du détecteur EPIDetector...")
        _detector = EPIDetector()
    return _detector

def get_multi_detector():
    """Obtenir ou initialiser le multi-détecteur (lazy loading)"""
    global _multi_detector
    if _multi_detector is None:
        logger.info("Initialisation du MultiModelDetector...")
        _multi_detector = MultiModelDetector(use_ensemble=config.DEFAULT_USE_ENSEMBLE)
        logger.info(f"MultiModelDetector initialisé: {len(_multi_detector.models)} modèles")
    return _multi_detector

@api_routes.route('/detect', methods=['POST'])
def detect():
    """Détecter les EPI sur une image uploadée"""
    try:
        image = None
        filepath = None

        # Accept either multipart/form-data file upload ('image') or JSON with base64 image
        if request.files and 'image' in request.files:
            file = request.files['image']
            valid, msg = validate_image_file(file)
            if not valid:
                return jsonify({'error': msg}), 400

            filepath = save_uploaded_file(file, 'image')
            logger.info(f"Image uploadée (fichier): {filepath}")
            image = cv2.imread(filepath)

        elif request.is_json and request.json.get('image'):
            data = request.json.get('image')
            # data may be 'data:image/jpeg;base64,/9j/...' or raw base64
            m = re.match(r'data:(image/\w+);base64,(.+)', data)
            if m:
                img_b64 = m.group(2)
            else:
                # If the client sent plain base64 or data URL without prefix
                img_b64 = data.split(',', 1)[1] if ',' in data else data

            try:
                img_bytes = base64.b64decode(img_b64)
                nparr = np.frombuffer(img_bytes, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                filepath = f"camera_base64_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.jpg"
                # Optionally save the image for records
                try:
                    save_path = os.path.join(config.UPLOAD_FOLDER, 'images')
                    os.makedirs(save_path, exist_ok=True)
                    cv2.imwrite(os.path.join(save_path, filepath), image)
                    filepath = os.path.join(save_path, filepath)
                except Exception:
                    # If saving fails, keep filepath as None
                    filepath = None
                logger.info(f"Image reçue en base64 (decoded), saved: {filepath}")
            except Exception as e:
                logger.error(f"Erreur décodage base64 image: {e}")
                return jsonify({'error': 'Impossible de décoder l\'image base64'}), 400

        else:
            return jsonify({'error': 'Pas de fichier image fourni'}), 400

        if image is None:
            return jsonify({'error': 'Impossible de lire l\'image'}), 400

        if image.size == 0:
            return jsonify({'error': 'Image vide'}), 400

        # Détecter avec multi-détecteur ou détecteur simple
        # Vérifier si l'utilisateur demande le mode ensemble
        use_ensemble = request.args.get('use_ensemble', 'true').lower() == 'true'
        
        try:
            multi_detector = get_multi_detector()
            detections, stats = multi_detector.detect(image, use_ensemble=use_ensemble)
            logger.info(f"Détection avec MultiModelDetector (ensemble={use_ensemble})")
        except Exception as e:
            logger.warning(f"Erreur multi-détecteur, fallback sur détecteur simple: {e}")
            detector = get_detector()
            detections, stats = detector.detect(image)
        
        # Sauvegarder en base avec métadonnées multi-modèles
        import json as json_lib
        model_votes_json = None
        if 'model_votes' in stats:
            model_votes_json = json_lib.dumps(stats['model_votes'])
        
        detection_record = Detection(
            image_path=filepath,
            total_persons=stats['total_persons'],
            with_helmet=stats['with_helmet'],
            with_vest=stats['with_vest'],
            with_glasses=stats['with_glasses'],
            with_boots=stats.get('with_boots', 0),
            compliance_rate=stats['compliance_rate'],
            compliance_level=stats.get('compliance_level'),
            alert_type=stats.get('alert_type'),
            source='image',
            model_used=stats.get('model_used', 'best.pt'),
            ensemble_mode=stats.get('ensemble_mode', False),
            model_votes=model_votes_json,
            aggregation_method=stats.get('aggregation_method')
        )
        db.session.add(detection_record)
        
        # Créer une alerte si nécessaire
        if stats['compliance_rate'] < 80:
            alert = Alert(
                detection_id=None,
                type='compliance',
                message=f"Conformité faible: {stats['compliance_rate']}%",
                severity='warning'
            )
            db.session.add(alert)
            logger.warning(f"Alerte conformité: {stats['compliance_rate']}%")
        
        db.session.commit()
        
        # Formater les détections pour le frontend (compatibilité avec le format x1, y1, x2, y2)
        normalized = []
        for d in detections:
            try:
                cls_name = d.get('class', 'unknown') if isinstance(d, dict) else 'unknown'
                confidence = float(d.get('confidence', 0)) if isinstance(d, dict) else 0.0
                bbox = d.get('bbox', [0, 0, 0, 0]) if isinstance(d, dict) else [0, 0, 0, 0]
                
                # Extraire x1, y1, x2, y2 de bbox
                if isinstance(bbox, (list, tuple)) and len(bbox) >= 4:
                    x1, y1, x2, y2 = bbox[0], bbox[1], bbox[2], bbox[3]
                else:
                    x1, y1, x2, y2 = 0, 0, 0, 0
                
                normalized.append({
                    'class_name': cls_name,
                    'confidence': round(confidence, 3),
                    'x1': int(x1),
                    'y1': int(y1),
                    'x2': int(x2),
                    'y2': int(y2)
                })
            except Exception as fmt_err:
                logger.error(f"Erreur formatage détection: {fmt_err}, d={d}")
                normalized.append({
                    'class_name': 'unknown',
                    'confidence': 0.0,
                    'x1': 0,
                    'y1': 0,
                    'x2': 0,
                    'y2': 0
                })

        return jsonify({
            'success': True,
            'detection_id': detection_record.id,
            'detections': normalized,
            'statistics': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur détection: {e}")
        return jsonify({'error': str(e)}), 500

@api_routes.route('/detections', methods=['GET'])
def get_detections():
    """Récupérer les détections récentes"""
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        detections = Detection.query.order_by(
            Detection.timestamp.desc()
        ).limit(limit).offset(offset).all()
        
        return jsonify({
            'success': True,
            'count': len(detections),
            'detections': [d.to_dict() for d in detections]
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur récupération détections: {e}")
        return jsonify({'error': str(e)}), 500

@api_routes.route('/detection/<int:detection_id>', methods=['GET'])
def get_detection(detection_id):
    """Récupérer une détection spécifique"""
    try:
        detection = Detection.query.get(detection_id)
        if not detection:
            return jsonify({'error': 'Détection non trouvée'}), 404
        
        return jsonify({
            'success': True,
            'detection': detection.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur récupération détection: {e}")
        return jsonify({'error': str(e)}), 500

@api_routes.route('/alerts', methods=['GET'])
def get_alerts():
    """Récupérer les alertes"""
    try:
        resolved = request.args.get('resolved', 'false').lower() == 'true'
        limit = request.args.get('limit', 50, type=int)
        
        query = Alert.query
        if not resolved:
            query = query.filter_by(resolved=False)
        
        alerts = query.order_by(Alert.timestamp.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'count': len(alerts),
            'alerts': [a.to_dict() for a in alerts]
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur récupération alertes: {e}")
        return jsonify({'error': str(e)}), 500

@api_routes.route('/stats', methods=['GET'])
def get_stats():
    """Obtenir les statistiques globales pour le dashboard"""
    try:
        from datetime import timedelta, time, timezone
        
        # Utiliser l'heure locale au lieu d'UTC
        now = datetime.now()
        
        # 1. Taux de conformité (dernière détection ou moyenne dernières 24h)
        recent_detections = Detection.query.order_by(Detection.timestamp.desc()).limit(10).all()
        if recent_detections:
            avg_compliance = sum(d.compliance_rate for d in recent_detections) / len(recent_detections)
        else:
            avg_compliance = 0
        
        # 2. Total de personnes détectées (dernières 24h)
        last_24h = now - timedelta(hours=24)
        detections_24h = Detection.query.filter(
            Detection.timestamp >= last_24h
        ).all()
        total_persons = sum(d.total_persons for d in detections_24h) if detections_24h else 0
        
        # 3. Alertes actives (non résolues)
        from app.database_unified import Alert
        active_alerts = Alert.query.filter(
            Alert.resolved == False
        ).count()
        
        # 4. Détections aujourd'hui (depuis 00:00:00 d'aujourd'hui)
        today_start = datetime.combine(now.date(), time(0, 0, 0))
        detections_today = Detection.query.filter(
            Detection.timestamp >= today_start
        ).count()
        
        # 5. Compter les EPI par type détectés dans les 24 dernières heures
        with_helmet = 0
        with_vest = 0
        with_glasses = 0
        with_boots = 0
        
        for detection in detections_24h:
            with_helmet += detection.with_helmet or 0
            with_vest += detection.with_vest or 0
            with_glasses += detection.with_glasses or 0
            with_boots += detection.with_boots or 0
        
        return jsonify({
            'status': 'success',
            'success': True,
            'compliance_rate': round(avg_compliance, 1),
            'total_persons': total_persons,
            'alerts': active_alerts,
            'detections_today': detections_today,
            'with_helmet': with_helmet,
            'with_vest': with_vest,
            'with_glasses': with_glasses,
            'with_boots': with_boots,
            'stats': {
                'total_detections': detections_today,
                'avg_compliance': round(avg_compliance, 2),
                'active_alerts': active_alerts
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur statistiques: {e}")
        return jsonify({
            'status': 'success',
            'success': True,
            'compliance_rate': 0,
            'total_persons': 0,
            'alerts': 0,
            'detections_today': 0,
            'with_helmet': 0,
            'with_vest': 0,
            'with_glasses': 0,
            'with_boots': 0,
            'error': str(e)
        }), 200

@api_routes.route('/training-results', methods=['GET'])
def get_training_results():
    """Récupérer tous les résultats d'entraînement"""
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        results = TrainingResult.query.order_by(
            TrainingResult.timestamp.desc()
        ).limit(limit).offset(offset).all()
        
        return jsonify({
            'success': True,
            'count': len(results),
            'training_results': [r.to_dict() for r in results]
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur récupération résultats: {e}")
        return jsonify({'error': str(e)}), 500

@api_routes.route('/training-results/<int:result_id>', methods=['GET'])
def get_training_result(result_id):
    """Récupérer un résultat d'entraînement spécifique"""
    try:
        result = TrainingResult.query.get(result_id)
        if not result:
            return jsonify({'error': 'Résultat non trouvé'}), 404
        
        return jsonify({
            'success': True,
            'training_result': result.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur récupération résultat: {e}")
        return jsonify({'error': str(e)}), 500

@api_routes.route('/training-results/latest', methods=['GET'])
def get_latest_training():
    """Récupérer le résultat d'entraînement le plus récent"""
    try:
        result = TrainingResult.query.order_by(
            TrainingResult.timestamp.desc()
        ).first()
        
        if not result:
            return jsonify({
                'success': True,
                'training_result': None,
                'message': 'Aucun résultat d\'entraînement'
            }), 200
        
        return jsonify({
            'success': True,
            'training_result': result.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur récupération dernier résultat: {e}")
        return jsonify({'error': str(e)}), 500

@api_routes.route('/training-results/by-model/<model_name>', methods=['GET'])
def get_training_by_model(model_name):
    """Récupérer les résultats pour un modèle spécifique"""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        results = TrainingResult.query.filter_by(
            model_name=model_name
        ).order_by(
            TrainingResult.timestamp.desc()
        ).limit(limit).all()
        
        return jsonify({
            'success': True,
            'count': len(results),
            'model_name': model_name,
            'training_results': [r.to_dict() for r in results]
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur recherche par modèle: {e}")
        return jsonify({'error': str(e)}), 500

@api_routes.route('/training-summary', methods=['GET'])
def get_training_summary():
    """Obtenir un résumé des entraînements"""
    try:
        from sqlalchemy import func
        
        total_trainings = TrainingResult.query.count()
        
        latest = TrainingResult.query.order_by(
            TrainingResult.timestamp.desc()
        ).first()
        
        avg_train_accuracy = db.session.query(
            func.avg(TrainingResult.train_accuracy)
        ).scalar() or 0
        
        avg_val_accuracy = db.session.query(
            func.avg(TrainingResult.val_accuracy)
        ).scalar() or 0
        
        return jsonify({
            'success': True,
            'summary': {
                'total_trainings': total_trainings,
                'avg_train_accuracy': round(float(avg_train_accuracy), 4) if avg_train_accuracy else 0,
                'avg_val_accuracy': round(float(avg_val_accuracy), 4) if avg_val_accuracy else 0,
                'latest_training': latest.to_dict() if latest else None
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur résumé: {e}")
        return jsonify({'error': str(e)}), 500

@api_routes.route('/chart/alerts', methods=['GET'])
def chart_alerts():
    """Obtenir les données des alertes pour un graphique"""
    try:
        days = request.args.get('days', 7, type=int)
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        alerts = Alert.query.filter(
            Alert.timestamp >= cutoff_date
        ).order_by(Alert.timestamp.asc()).all()
        
        # Grouper par jour et par sévérité
        data_by_day = {}
        for alert in alerts:
            day = alert.timestamp.strftime('%Y-%m-%d')
            if day not in data_by_day:
                data_by_day[day] = {
                    'low': 0,
                    'medium': 0,
                    'high': 0,
                    'critical': 0,
                    'total': 0
                }
            
            severity = alert.severity or 'low'
            if severity in data_by_day[day]:
                data_by_day[day][severity] += 1
            data_by_day[day]['total'] += 1
        
        # Convertir en liste triée
        chart_data = []
        for day in sorted(data_by_day.keys()):
            chart_data.append({
                'date': day,
                **data_by_day[day]
            })
        
        return jsonify({
            'success': True,
            'period_days': days,
            'total_alerts': len(alerts),
            'data': chart_data
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur graphique alertes: {e}")
        return jsonify({'error': str(e)}), 500


@api_routes.route('/chart/cumulative', methods=['GET'])
def chart_cumulative():
    """Obtenir les données cumulatives (conformité, détections)"""
    try:
        days = request.args.get('days', 7, type=int)
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        detections = Detection.query.filter(
            Detection.timestamp >= cutoff_date
        ).order_by(Detection.timestamp.asc()).all()
        
        # Grouper par jour
        data_by_day = {}
        cumulative_compliance = 0
        cumulative_detections = 0
        
        for detection in detections:
            day = detection.timestamp.strftime('%Y-%m-%d')
            if day not in data_by_day:
                data_by_day[day] = {
                    'total_persons': 0,
                    'with_helmet': 0,
                    'with_vest': 0,
                    'with_glasses': 0,
                    'with_boots': 0,
                    'count': 0
                }
            
            data_by_day[day]['total_persons'] += detection.total_persons or 0
            data_by_day[day]['with_helmet'] += detection.with_helmet or 0
            data_by_day[day]['with_vest'] += detection.with_vest or 0
            data_by_day[day]['with_glasses'] += detection.with_glasses or 0
            data_by_day[day]['with_boots'] += detection.with_boots or 0
            data_by_day[day]['count'] += 1
        
        # Calculer conformité par jour en utilisant le nouvel algorithme
        chart_data = []
        for day in sorted(data_by_day.keys()):
            day_data = data_by_day[day]
            
            # Utiliser le nouvel algorithme de conformité
            avg_compliance = calculate_compliance_score(
                total_persons=day_data['total_persons'],
                with_helmet=day_data['with_helmet'],
                with_vest=day_data['with_vest'],
                with_glasses=day_data['with_glasses'],
                with_boots=day_data['with_boots']
            )
            
            chart_data.append({
                'date': day,
                'total_persons': day_data['total_persons'],
                'with_helmet': day_data['with_helmet'],
                'with_vest': day_data['with_vest'],
                'with_glasses': day_data['with_glasses'],
                'with_boots': day_data['with_boots'],
                'avg_compliance_rate': round(avg_compliance, 2),
                'detection_count': day_data['count']
            })
        
        return jsonify({
            'success': True,
            'period_days': days,
            'total_detections': len(detections),
            'data': chart_data
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur graphique cumulatif: {e}")
        return jsonify({'error': str(e)}), 500


@api_routes.route('/models/list', methods=['GET'])
def list_models():
    """Obtenir la liste des modèles disponibles"""
    try:
        multi_detector = get_multi_detector()
        model_list = multi_detector.get_model_list()
        
        return jsonify({
            'success': True,
            'count': len(model_list),
            'models': model_list,
            'current_mode': 'ensemble' if multi_detector.use_ensemble else 'single'
        }), 200
    except Exception as e:
        logger.error(f"Erreur liste modèles: {e}")
        return jsonify({'error': str(e)}), 500

@api_routes.route('/models/mode', methods=['POST'])
def set_model_mode():
    """Changer le mode de détection (single/ensemble)"""
    try:
        data = request.json
        use_ensemble = data.get('use_ensemble', True)
        
        multi_detector = get_multi_detector()
        multi_detector.set_ensemble_mode(use_ensemble)
        
        return jsonify({
            'success': True,
            'mode': 'ensemble' if multi_detector.use_ensemble else 'single',
            'message': f"Mode {'ensemble' if use_ensemble else 'single'} activé"
        }), 200
    except Exception as e:
        logger.error(f"Erreur changement mode: {e}")
        return jsonify({'error': str(e)}), 500

@api_routes.route('/models/compare', methods=['POST'])
def compare_models():
    """Comparer les performances de tous les modèles sur une image"""
    try:
        # Récupérer l'image
        if not request.files or 'image' not in request.files:
            return jsonify({'error': 'Pas de fichier image fourni'}), 400
        
        file = request.files['image']
        valid, msg = validate_image_file(file)
        if not valid:
            return jsonify({'error': msg}), 400
        
        filepath = save_uploaded_file(file, 'image')
        image = cv2.imread(filepath)
        
        if image is None or image.size == 0:
            return jsonify({'error': 'Image invalide'}), 400
        
        # Comparer tous les modèles
        multi_detector = get_multi_detector()
        comparison_results = []
        
        for model_name, model_info in multi_detector.models.items():
            detector = model_info['detector']
            start_time = time.perf_counter()
            
            try:
                detections, stats = detector.detect(image)
                detection_time = (time.perf_counter() - start_time) * 1000
                
                comparison_results.append({
                    'model_name': model_name,
                    'weight': model_info['weight'],
                    'detections_count': len(detections),
                    'total_persons': stats.get('total_persons', 0),
                    'with_helmet': stats.get('with_helmet', 0),
                    'with_vest': stats.get('with_vest', 0),
                    'with_glasses': stats.get('with_glasses', 0),
                    'compliance_rate': stats.get('compliance_rate', 0),
                    'inference_ms': stats.get('inference_ms', 0),
                    'total_ms': round(detection_time, 1)
                })
            except Exception as e:
                logger.error(f"Erreur modèle {model_name}: {e}")
                comparison_results.append({
                    'model_name': model_name,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'comparisons': comparison_results,
            'image_path': filepath
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur comparaison modèles: {e}")
        return jsonify({'error': str(e)}), 500
@api_routes.route('/alerts-recent', methods=['GET'])
def get_recent_alerts():
    """Obtenir les alertes récentes depuis la base de données"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        alerts = Alert.query.filter_by(resolved=False).order_by(
            Alert.timestamp.desc()
        ).limit(limit).all()
        
        alerts_data = []
        for alert in alerts:
            # Calculer le temps écoulé
            time_diff = datetime.now() - alert.timestamp
            if time_diff.total_seconds() < 60:
                time_str = f"Il y a {int(time_diff.total_seconds())} sec"
            elif time_diff.total_seconds() < 3600:
                time_str = f"Il y a {int(time_diff.total_seconds() / 60)} min"
            else:
                time_str = f"Il y a {int(time_diff.total_seconds() / 3600)} h"
            
            alerts_data.append({
                'id': alert.id,
                'type': alert.type,
                'message': alert.message,
                'severity': alert.severity,
                'timestamp': alert.timestamp.isoformat(),
                'time_ago': time_str
            })
        
        return jsonify({
            'success': True,
            'count': len(alerts_data),
            'alerts': alerts_data
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur alertes récentes: {e}")
        return jsonify({'error': str(e)}), 500

@api_routes.route('/realtime', methods=['GET'])
def get_realtime():
    """Obtenir les dernières détections en temps réel"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        detections = Detection.query.order_by(
            Detection.timestamp.desc()
        ).limit(limit).all()
        
        data = {
            'count': len(detections),
            'timestamps': [],
            'persons': [],
            'helmets': [],
            'vests': [],
            'glasses': [],
            'boots': [],
            'compliance_rates': [],
            'alert_types': [],
            'full_data': []  # Ajouter les données complètes
        }
        
        for det in detections:
            # Timestamps ISO pour conversion côté client
            data['timestamps'].append(det.timestamp.isoformat())
            data['persons'].append(det.total_persons or 0)
            data['helmets'].append(det.with_helmet or 0)
            data['vests'].append(det.with_vest or 0)
            data['glasses'].append(det.with_glasses or 0)
            data['boots'].append(det.with_boots or 0)
            data['compliance_rates'].append(int(det.compliance_rate or 0))
            data['alert_types'].append(det.alert_type or 'none')
            
            # Données complètes
            data['full_data'].append({
                'id': det.id,
                'timestamp': det.timestamp.isoformat(),
                'total_persons': det.total_persons or 0,
                'with_helmet': det.with_helmet or 0,
                'with_vest': det.with_vest or 0,
                'with_glasses': det.with_glasses or 0,
                'with_boots': det.with_boots or 0,
                'compliance_rate': det.compliance_rate or 0,
                'alert_type': det.alert_type or 'none'
            })
        
        return jsonify({
            'success': True,
            **data
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur realtime: {e}")
        return jsonify({'error': str(e)}), 500
@api_routes.route('/health', methods=['GET'])
def health_check():
    """Vérifier l'état de l'application"""
    try:
        multi_detector = get_multi_detector()
        return jsonify({
            'status': 'healthy',
            'version': '2.0.0',
            'multi_model_enabled': config.MULTI_MODEL_ENABLED,
            'models_loaded': len(multi_detector.models),
            'ensemble_mode': multi_detector.use_ensemble
        }), 200
    except Exception:
        return jsonify({
            'status': 'healthy',
            'version': '2.0.0',
            'multi_model_enabled': False
        }), 200

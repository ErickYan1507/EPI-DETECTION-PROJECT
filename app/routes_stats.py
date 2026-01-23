"""
Routes pour les statistiques en temps réel
- /api/stats: Statistiques globales (taux conformité, personnes, alertes, détections)
- /api/chart/hourly: Données pour graphique détections par heure
- /api/chart/epi: Données pour graphique répartition EPI (casques, gilets, lunettes)
- /api/chart/alerts: Données pour graphique alertes par sévérité
- /api/chart/cumulative: Données cumulatives détections
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from app.database_unified import db, Detection, Alert, TrainingResult, Worker
from sqlalchemy import func, and_
import json

stats_bp = Blueprint('stats', __name__, url_prefix='/api')

# ============================================================================
# ENDPOINT: /api/stats - Statistiques globales en temps réel
# ============================================================================

@stats_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Récupère les statistiques globales en temps réel
    Retourne: compliance_rate, total_persons, with_helmet, with_vest, with_glasses, alerts, detections_today
    """
    try:
        # Récupérer les détections d'aujourd'hui
        today_start = datetime.combine(datetime.today(), datetime.min.time())
        today_detections = Detection.query.filter(
            Detection.timestamp >= today_start
        ).all()
        
        if not today_detections:
            return jsonify({
                'compliance_rate': 0,
                'total_persons': 0,
                'with_helmet': 0,
                'with_vest': 0,
                'with_glasses': 0,
                'with_boots': 0,
                'alerts': 0,
                'detections_today': 0,
                'status': 'no_data'
            }), 200
        
        # Calculer les statistiques
        total_detections = len(today_detections)
        total_persons = sum(d.total_persons or 0 for d in today_detections)
        with_helmet = sum(d.with_helmet or 0 for d in today_detections)
        with_vest = sum(d.with_vest or 0 for d in today_detections)
        with_glasses = sum(d.with_glasses or 0 for d in today_detections)
        with_boots = sum(d.with_boots or 0 for d in today_detections)
        
        # Taux de conformité
        if total_persons > 0:
            # Personne en conformité = avec tous les EPI
            compliant_persons = sum(
                min(d.with_helmet or 0, d.with_vest or 0, d.with_glasses or 0, d.with_boots or 0)
                for d in today_detections
            )
            compliance_rate = (compliant_persons / total_persons * 100) if total_persons > 0 else 0
        else:
            compliance_rate = 0
        
        # Compter les alertes actives
        active_alerts = Alert.query.filter(
            Alert.resolved == False,
            Alert.timestamp >= today_start
        ).count()
        
        return jsonify({
            'compliance_rate': round(compliance_rate, 2),
            'total_persons': total_persons,
            'with_helmet': with_helmet,
            'with_vest': with_vest,
            'with_glasses': with_glasses,
            'with_boots': with_boots,
            'alerts': active_alerts,
            'detections_today': total_detections,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        }), 200
        
    except Exception as e:
        print(f"❌ Erreur /api/stats: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


# ============================================================================
# ENDPOINT: /api/chart/hourly - Détections par heure
# ============================================================================

@stats_bp.route('/chart/hourly', methods=['GET'])
def get_hourly_data():
    """
    Récupère les détections et conformité par heure pour les 24 dernières heures
    Retourne: hours (labels), detections (valeurs), compliance (taux de conformité par heure)
    """
    try:
        # Récupérer les détections des 24 dernières heures
        now = datetime.now()
        hours_data = {}
        compliance_data = {}
        
        for i in range(24):
            hour = (now - timedelta(hours=i)).hour
            hour_label = f"{hour:02d}h"
            hours_data[hour_label] = {'count': 0, 'persons': 0, 'compliant': 0}
            compliance_data[hour_label] = 0
        
        # Récupérer les détections
        start_time = now - timedelta(hours=24)
        detections = Detection.query.filter(
            Detection.timestamp >= start_time
        ).all()
        
        # Compter par heure et calculer la conformité
        for detection in detections:
            hour = detection.timestamp.hour
            hour_label = f"{hour:02d}h"
            if hour_label in hours_data:
                hours_data[hour_label]['count'] += 1
                total_persons = detection.total_persons or 0
                hours_data[hour_label]['persons'] += total_persons
                
                # Personne conforme = avec tous les EPI
                if total_persons > 0:
                    compliant = min(
                        detection.with_helmet or 0,
                        detection.with_vest or 0,
                        detection.with_glasses or 0,
                        detection.with_boots or 0
                    )
                    hours_data[hour_label]['compliant'] += compliant
        
        # Calculer le taux de conformité par heure
        for hour_label, data in hours_data.items():
            if data['persons'] > 0:
                compliance_data[hour_label] = round((data['compliant'] / data['persons'] * 100), 1)
            else:
                compliance_data[hour_label] = 0
        
        # Retourner les données triées par heure
        hours = sorted(hours_data.keys(), key=lambda x: int(x.split('h')[0]))
        detections_count = [hours_data[h]['count'] for h in hours]
        compliance_values = [compliance_data[h] for h in hours]
        
        return jsonify({
            'hours': hours,
            'detections': detections_count,
            'compliance': compliance_values,
            'status': 'success'
        }), 200
        
    except Exception as e:
        print(f"❌ Erreur /api/chart/hourly: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


# ============================================================================
# ENDPOINT: /api/chart/epi - Répartition EPI (casques, gilets, lunettes)
# ============================================================================

@stats_bp.route('/chart/epi', methods=['GET'])
def get_epi_data():
    """
    Répartition des EPI détectés
    Retourne: helmets, vests, glasses
    """
    try:
        today_start = datetime.combine(datetime.today(), datetime.min.time())
        
        # Récupérer les détections d'aujourd'hui
        detections = Detection.query.filter(
            Detection.timestamp >= today_start
        ).all()
        
        # Somme des EPI
        helmets = sum(d.with_helmet or 0 for d in detections)
        vests = sum(d.with_vest or 0 for d in detections)
        glasses = sum(d.with_glasses or 0 for d in detections)
        boots = sum(d.with_boots or 0 for d in detections)
        
        return jsonify({
            'helmets': helmets,
            'vests': vests,
            'glasses': glasses,
            'boots': boots,
            'status': 'success'
        }), 200
        
    except Exception as e:
        print(f"❌ Erreur /api/chart/epi: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


# ============================================================================
# ENDPOINT: /api/chart/alerts - Alertes par sévérité
# ============================================================================

@stats_bp.route('/chart/alerts', methods=['GET'])
def get_alerts_data():
    """
    Alertes groupées par sévérité
    Retourne: high, medium, low
    """
    try:
        today_start = datetime.combine(datetime.today(), datetime.min.time())
        
        # Compter les alertes par sévérité
        high_alerts = Alert.query.filter(
            Alert.severity == 'high',
            Alert.timestamp >= today_start
        ).count()
        
        medium_alerts = Alert.query.filter(
            Alert.severity == 'medium',
            Alert.timestamp >= today_start
        ).count()
        
        low_alerts = Alert.query.filter(
            Alert.severity == 'low',
            Alert.timestamp >= today_start
        ).count()
        
        return jsonify({
            'high': high_alerts,
            'medium': medium_alerts,
            'low': low_alerts,
            'status': 'success'
        }), 200
        
    except Exception as e:
        print(f"❌ Erreur /api/chart/alerts: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


# ============================================================================
# ENDPOINT: /api/chart/cumulative - Données cumulatives
# ============================================================================

@stats_bp.route('/chart/cumulative', methods=['GET'])
def get_cumulative_data():
    """
    Données cumulatives pour graphique cumulé
    """
    try:
        # Récupérer les détections des 30 derniers jours
        start_date = datetime.now() - timedelta(days=30)
        
        # Grouper par jour
        daily_data = {}
        cumulative = 0
        
        for i in range(30):
            date = (datetime.now() - timedelta(days=i)).date()
            day_label = date.strftime('%d/%m')
            
            day_start = datetime.combine(date, datetime.min.time())
            day_end = datetime.combine(date, datetime.max.time())
            
            count = Detection.query.filter(
                and_(
                    Detection.timestamp >= day_start,
                    Detection.timestamp <= day_end
                )
            ).count()
            
            cumulative += count
            daily_data[day_label] = cumulative
        
        # Retourner les données triées
        labels = sorted(daily_data.keys(), key=lambda x: datetime.strptime(x, '%d/%m'))
        values = [daily_data[label] for label in labels]
        
        return jsonify({
            'labels': labels,
            'data': values,
            'status': 'success'
        }), 200
        
    except Exception as e:
        print(f"❌ Erreur /api/chart/cumulative: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


# ============================================================================
# ENDPOINT: /api/stats/training - Statistiques d'entraînement
# ============================================================================

@stats_bp.route('/stats/training', methods=['GET'])
def get_training_stats():
    """
    Récupère les statistiques du dernier entraînement
    """
    try:
        # Récupérer le dernier résultat d'entraînement
        latest = TrainingResult.query.order_by(
            TrainingResult.timestamp.desc()
        ).first()
        
        if not latest:
            return jsonify({
                'status': 'no_data',
                'message': 'Aucun entraînement trouvé'
            }), 200
        
        return jsonify({
            'model_name': latest.model_name,
            'model_version': latest.model_version,
            'epochs': latest.epochs,
            'batch_size': latest.batch_size,
            'image_size': latest.image_size,
            'precision': latest.val_precision or 0,
            'recall': latest.val_recall or 0,
            'f1_score': latest.val_f1_score or 0,
            'accuracy': latest.val_accuracy or 0,
            'training_time': latest.training_time_seconds or 0,
            'fps': latest.fps or 0,
            'timestamp': latest.timestamp.isoformat(),
            'status': 'success'
        }), 200
        
    except Exception as e:
        print(f"❌ Erreur /api/stats/training: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


# ============================================================================
# ENDPOINT: /api/stats/uploads - Statistiques des uploads
# ============================================================================

@stats_bp.route('/stats/uploads', methods=['GET'])
def get_uploads_stats():
    """
    Récupère les statistiques des fichiers uploadés
    """
    try:
        from pathlib import Path
        import os
        
        upload_dir = Path('uploads')
        if not upload_dir.exists():
            return jsonify({
                'total_files': 0,
                'total_size_mb': 0,
                'image_count': 0,
                'video_count': 0,
                'status': 'success'
            }), 200
        
        total_files = 0
        total_size = 0
        image_count = 0
        video_count = 0
        
        for file in upload_dir.rglob('*'):
            if file.is_file():
                total_files += 1
                total_size += file.stat().st_size
                
                if file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
                    image_count += 1
                elif file.suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv']:
                    video_count += 1
        
        return jsonify({
            'total_files': total_files,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'image_count': image_count,
            'video_count': video_count,
            'status': 'success'
        }), 200
        
    except Exception as e:
        print(f"❌ Erreur /api/stats/uploads: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


# ============================================================================
# ENDPOINT: /api/stats/live - Statistiques en direct (WebSocket-like polling)
# ============================================================================

@stats_bp.route('/stats/live', methods=['GET'])
def get_live_stats():
    """
    Récupère les statistiques en direct (mise à jour à chaque appel)
    """
    try:
        # Récupérer les données actuelles
        now = datetime.now()
        
        # Dernière détection
        latest_detection = Detection.query.order_by(
            Detection.timestamp.desc()
        ).first()
        
        # Détections de la dernière heure
        one_hour_ago = now - timedelta(hours=1)
        hourly_detections = Detection.query.filter(
            Detection.timestamp >= one_hour_ago
        ).count()
        
        # Alertes non résolues
        unresolved_alerts = Alert.query.filter(
            Alert.resolved == False
        ).count()
        
        return jsonify({
            'latest_detection_time': latest_detection.timestamp.isoformat() if latest_detection else None,
            'detections_last_hour': hourly_detections,
            'unresolved_alerts': unresolved_alerts,
            'current_time': now.isoformat(),
            'status': 'success'
        }), 200
        
    except Exception as e:
        print(f"❌ Erreur /api/stats/live: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


# ============================================================================
# ENDPOINT: /api/realtime - Données temps réel pour table des détections
# ============================================================================

@stats_bp.route('/realtime', methods=['GET'])
def get_realtime():
    """
    Récupère les dernières détections en temps réel pour affichage tableau
    Limite: 10 dernières détections
    """
    try:
        # Récupérer les 10 dernières détections
        recent = Detection.query.order_by(
            Detection.timestamp.desc()
        ).limit(10).all()
        
        if not recent:
            return jsonify({
                'timestamps': [],
                'persons': [],
                'helmets': [],
                'vests': [],
                'glasses': [],
                'boots': [],
                'compliance_rates': [],
                'status': 'no_data'
            }), 200
        
        # Construire les listes
        timestamps = []
        persons = []
        helmets = []
        vests = []
        glasses = []
        boots = []
        compliance_rates = []
        
        for det in recent:
            # Format temps
            time_str = det.timestamp.strftime('%H:%M:%S')
            timestamps.append(time_str)
            
            # Comptages
            persons.append(det.total_persons or 0)
            helmets.append(det.with_helmet or 0)
            vests.append(det.with_vest or 0)
            glasses.append(det.with_glasses or 0)
            boots.append(det.with_boots or 0)
            
            # Taux de conformité pour cette détection
            if det.total_persons and det.total_persons > 0:
                compliant = min(
                    det.with_helmet or 0,
                    det.with_vest or 0,
                    det.with_glasses or 0,
                    det.with_boots or 0
                )
                rate = (compliant / det.total_persons * 100)
                compliance_rates.append(round(rate, 2))
            else:
                compliance_rates.append(0)
        
        return jsonify({
            'timestamps': timestamps,
            'persons': persons,
            'helmets': helmets,
            'vests': vests,
            'glasses': glasses,
            'boots': boots,
            'compliance_rates': compliance_rates,
            'status': 'success'
        }), 200
        
    except Exception as e:
        print(f"❌ Erreur /api/realtime: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


# ============================================================================
# ENDPOINTS EXPORT PDF
# ============================================================================

@stats_bp.route('/export/detection-pdf', methods=['GET'])
def export_detection_pdf():
    """Exporter un rapport PDF des détections"""
    try:
        from app.pdf_export import PDFExporter
        from flask import current_app, send_file
        from datetime import date, timedelta

        # Paramètres de date
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        start_date = None
        end_date = None

        if start_date_str:
            try:
                start_date = date.fromisoformat(start_date_str)
            except ValueError:
                return jsonify({'error': 'Format de date de début invalide (utilisez YYYY-MM-DD)'}), 400

        if end_date_str:
            try:
                end_date = date.fromisoformat(end_date_str)
            except ValueError:
                return jsonify({'error': 'Format de date de fin invalide (utilisez YYYY-MM-DD)'}), 400

        # Créer l'exporteur PDF
        pdf_exporter = PDFExporter()

        # Générer le rapport
        pdf_path = pdf_exporter.generate_detection_report(
            start_date=start_date,
            end_date=end_date,
            title="Rapport de Détection EPI"
        )

        # Retourner le fichier PDF
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"epi_detection_report_{date.today().strftime('%Y%m%d')}.pdf",
            mimetype='application/pdf'
        )

    except Exception as e:
        print(f"❌ Erreur export PDF détections: {e}")
        return jsonify({'error': str(e)}), 500


@stats_bp.route('/export/training-pdf', methods=['GET'])
def export_training_pdf():
    """Exporter un rapport PDF des résultats d'entraînement"""
    try:
        from app.pdf_export import PDFExporter
        from flask import send_file

        # Paramètre optionnel pour un résultat spécifique
        training_id = request.args.get('training_id', type=int)

        # Créer l'exporteur PDF
        pdf_exporter = PDFExporter()

        # Générer le rapport
        pdf_path = pdf_exporter.generate_training_report(
            training_result_id=training_id,
            title="Rapport de Résultats d'Entraînement"
        )

        # Retourner le fichier PDF
        filename = f"training_report_{'id_' + str(training_id) + '_' if training_id else ''}{date.today().strftime('%Y%m%d')}.pdf"
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )

    except Exception as e:
        print(f"❌ Erreur export PDF entraînement: {e}")
        return jsonify({'error': str(e)}), 500


@stats_bp.route('/export/presence-pdf', methods=['GET'])
def export_presence_pdf():
    """Exporter un rapport PDF des présences quotidiennes"""
    try:
        from app.pdf_export import PDFExporter
        from flask import send_file
        from datetime import date, timedelta

        # Paramètres de date
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        start_date = None
        end_date = None

        if start_date_str:
            try:
                start_date = date.fromisoformat(start_date_str)
            except ValueError:
                return jsonify({'error': 'Format de date de début invalide (utilisez YYYY-MM-DD)'}), 400

        if end_date_str:
            try:
                end_date = date.fromisoformat(end_date_str)
            except ValueError:
                return jsonify({'error': 'Format de date de fin invalide (utilisez YYYY-MM-DD)'}), 400

        # Créer l'exporteur PDF
        pdf_exporter = PDFExporter()

        # Générer le rapport
        pdf_path = pdf_exporter.generate_presence_report(
            start_date=start_date,
            end_date=end_date,
            title="Rapport de Présence Quotidienne"
        )

        # Retourner le fichier PDF
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"presence_report_{date.today().strftime('%Y%m%d')}.pdf",
            mimetype='application/pdf'
        )

    except Exception as e:
        print(f"❌ Erreur export PDF présence: {e}")
        return jsonify({'error': str(e)}), 500

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
from app.database_unified import db, Detection, Alert, TrainingResult, Worker, AttendanceRecord, TIMEZONE_OFFSET
from app.constants import calculate_compliance_score
from sqlalchemy import func, and_
import json
import os

stats_bp = Blueprint('stats', __name__, url_prefix='/api')


def _local_now():
    return datetime.utcnow() + TIMEZONE_OFFSET


def _utc_bounds_for_local_day(ref_local=None):
    ref_local = ref_local or _local_now()
    local_start = datetime.combine(ref_local.date(), datetime.min.time())
    local_end = local_start + timedelta(days=1)
    return local_start - TIMEZONE_OFFSET, local_end - TIMEZONE_OFFSET


@stats_bp.route('/ping', methods=['GET'])
def ping():
    """Endpoint de test pour vérifier que l'API répond"""
    try:
        return jsonify({'status': 'ok', 'message': 'pong', 'time': datetime.utcnow().isoformat() + 'Z'}), 200
    except Exception:
        return jsonify({'status': 'error'}), 500

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
        # Base métier: présence journalière unique (1 personne/jour)
        day_start_utc, day_end_utc = _utc_bounds_for_local_day()
        today_rows = AttendanceRecord.query.filter(
            AttendanceRecord.first_seen_at >= day_start_utc,
            AttendanceRecord.first_seen_at < day_end_utc,
        ).all()

        # Garder "detections_today" compatible avec l'UI, mais basé sur personnes uniques du jour.
        total_detections = len(today_rows)

        if not today_rows:
            active_alerts = Alert.query.filter(
                Alert.resolved == False,
                Alert.timestamp >= day_start_utc,
                Alert.timestamp < day_end_utc,
            ).count()
            return jsonify({
                'compliance_rate': 0,
                'total_persons': 0,
                'with_helmet': 0,
                'with_vest': 0,
                'with_glasses': 0,
                'with_boots': 0,
                'alerts': active_alerts,
                'detections_today': 0,
                'status': 'no_data'
            }), 200

        total_persons = len(today_rows)
        with_helmet = sum(1 for r in today_rows if bool(r.helmet_detected))
        with_vest = sum(1 for r in today_rows if bool(r.vest_detected))
        with_glasses = sum(1 for r in today_rows if bool(r.glasses_detected))
        with_boots = sum(1 for r in today_rows if bool(r.boots_detected))

        # RÈGLE: si personne=0 => conformité=0, sinon score agrégé.
        if total_persons == 0:
            compliance_rate = 0.0
        else:
            compliance_rate = calculate_compliance_score(
                total_persons=total_persons,
                with_helmet=with_helmet,
                with_vest=with_vest,
                with_glasses=with_glasses,
                with_boots=with_boots
            )

        # Alertes actives sur la fenêtre locale du jour (UTC bornes locales).
        active_alerts = Alert.query.filter(
            Alert.resolved == False,
            Alert.timestamp >= day_start_utc,
            Alert.timestamp < day_end_utc
        ).all()
        
        return jsonify({
            'compliance_rate': round(compliance_rate, 2),
            'total_persons': total_persons,
            'with_helmet': with_helmet,
            'with_vest': with_vest,
            'with_glasses': with_glasses,
            'with_boots': with_boots,
            'alerts': len(active_alerts),
            'detections_today': total_detections,
            'timestamp': _local_now().isoformat(),
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
    Récupère les détections et conformité par heure pour aujourd'hui
    Retourne: hours (labels), detections (valeurs), compliance (taux de conformité par heure)
    """
    try:
        # Récupérer les détections d'aujourd'hui (évite d'afficher des heures anciennes)
        now_local = _local_now()
        day_start_utc, day_end_utc = _utc_bounds_for_local_day(now_local)
        hours_data = {}
        compliance_data = {}
        
        for hour in range(24):
            hour_label = f"{hour:02d}h"
            hours_data[hour_label] = {'count': 0, 'persons': 0, 'compliant': 0}
            compliance_data[hour_label] = 0
        
        # Récupérer les détections
        rows = AttendanceRecord.query.filter(
            and_(
                AttendanceRecord.first_seen_at >= day_start_utc,
                AttendanceRecord.first_seen_at < day_end_utc
            )
        ).all()

        # Compter par heure en local, par personne unique/jour
        for row in rows:
            local_dt = (row.first_seen_at + TIMEZONE_OFFSET) if row.first_seen_at else None
            if not local_dt:
                continue
            hour = local_dt.hour
            hour_label = f"{hour:02d}h"
            if hour_label in hours_data:
                hours_data[hour_label]['count'] += 1
                hours_data[hour_label]['persons'] += 1
        
        # Calculer le taux de conformité par heure en utilisant le nouvel algorithme
        for hour_label, data in hours_data.items():
            if data['persons'] > 0:
                # Recalculer la conformité avec le nouvel algorithme
                # Récupérer les détections pour cette heure (filtrage en mémoire pour compatibilité SQLite)
                hour_int = int(hour_label.split('h')[0])
                rows_hour = []
                for r in rows:
                    if not r.first_seen_at:
                        continue
                    local_dt = r.first_seen_at + TIMEZONE_OFFSET
                    if local_dt.hour == hour_int:
                        rows_hour.append(r)
                
                # Compter les EPI totaux pour cette heure
                total_helmet = sum(1 for r in rows_hour if bool(r.helmet_detected))
                total_vest = sum(1 for r in rows_hour if bool(r.vest_detected))
                total_glasses = sum(1 for r in rows_hour if bool(r.glasses_detected))
                total_boots = sum(1 for r in rows_hour if bool(r.boots_detected))
                
                # Appliquer le nouvel algorithme
                compliance_data[hour_label] = calculate_compliance_score(
                    total_persons=data['persons'],
                    with_helmet=total_helmet,
                    with_vest=total_vest,
                    with_glasses=total_glasses,
                    with_boots=total_boots
                )
            else:
                compliance_data[hour_label] = 0
        
        # Retourner les données triées par heure (00h -> 23h)
        hours = [f"{h:02d}h" for h in range(24)]
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
        day_start_utc, day_end_utc = _utc_bounds_for_local_day()
        rows = AttendanceRecord.query.filter(
            AttendanceRecord.first_seen_at >= day_start_utc,
            AttendanceRecord.first_seen_at < day_end_utc
        ).all()

        helmets = sum(1 for r in rows if bool(r.helmet_detected))
        vests = sum(1 for r in rows if bool(r.vest_detected))
        glasses = sum(1 for r in rows if bool(r.glasses_detected))
        boots = sum(1 for r in rows if bool(r.boots_detected))
        
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

@stats_bp.route('/chart/alerts-stats', methods=['GET'])
def get_alerts_data():
    """
    Endpoint legacy stats for alerts by severity.
    Kept for compatibility without conflicting with /api/chart/alerts.
    """
    try:
        period = request.args.get('period', 'today')
        days = request.args.get('days', type=int)
        show_resolved = request.args.get('resolved', 'all')

        if days is not None:
            days = max(1, min(days, 365))
            start_date = datetime.now() - timedelta(days=days)
        elif period == 'today':
            start_date = datetime.combine(datetime.today(), datetime.min.time())
        elif period == 'week':
            start_date = datetime.now() - timedelta(days=7)
        elif period == 'month':
            start_date = datetime.now() - timedelta(days=30)
        else:
            start_date = datetime(2000, 1, 1)

        base_query = Alert.query.filter(Alert.timestamp >= start_date)
        if show_resolved == 'true':
            base_query = base_query.filter(Alert.resolved == True)
        elif show_resolved == 'false':
            base_query = base_query.filter(Alert.resolved == False)

        def normalize_severity(value):
            sev = (value or 'low').strip().lower()
            if sev in ('critical', 'critique', 'high'):
                return 'high'
            if sev in ('warning', 'warn', 'medium', 'moyen'):
                return 'medium'
            return 'low'

        totals = {'high': 0, 'medium': 0, 'low': 0}
        for alert in base_query.all():
            totals[normalize_severity(alert.severity)] += 1

        total_alerts = totals['high'] + totals['medium'] + totals['low']
        print(
            f"OK /api/chart/alerts-stats: period={period}, days={days}, "
            f"resolved={show_resolved}, total={total_alerts} "
            f"(high={totals['high']}, medium={totals['medium']}, low={totals['low']})"
        )

        return jsonify({
            'high': totals['high'],
            'medium': totals['medium'],
            'low': totals['low'],
            'total': total_alerts,
            'period': period,
            'days': days,
            'status': 'success'
        }), 200

    except Exception as e:
        print(f"Error /api/chart/alerts-stats: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'status': 'error'}), 500


# ============================================================================
# ENDPOINT: /api/chart/cumulative - Données cumulatives
# ============================================================================

@stats_bp.route('/chart/cumulative', methods=['GET'])
def get_cumulative_data():
    """
    Données cumulatives pour graphique cumulé - retourne le cumul réel des détections
    """
    try:
        # Récupérer le nombre de jours depuis le paramètre (par défaut 7 jours)
        days = int(request.args.get('days', 7))
        
        # Limiter entre 1 et 90 jours
        days = max(1, min(days, 90))
        
        # Date de début et de fin
        end_date = _local_now().date()
        start_date = end_date - timedelta(days=days - 1)
        
        # Dictionnaire pour stocker les données quotidiennes avec dates complètes
        daily_data = []
        
        # Parcourir du plus ancien au plus récent
        for i in range(days):
            date = start_date + timedelta(days=i)
            local_day_start = datetime.combine(date, datetime.min.time())
            utc_day_start = local_day_start - TIMEZONE_OFFSET
            utc_day_end = utc_day_start + timedelta(days=1)
            count = AttendanceRecord.query.filter(
                and_(
                    AttendanceRecord.first_seen_at >= utc_day_start,
                    AttendanceRecord.first_seen_at < utc_day_end
                )
            ).count()
            
            daily_data.append({
                'date': date,
                'label': date.strftime('%d/%m'),
                'count': count
            })
        
        # Calculer le cumul (somme progressive)
        cumulative = 0
        labels = []
        cumulative_values = []
        
        for day in daily_data:
            cumulative += day['count']
            labels.append(day['label'])
            cumulative_values.append(cumulative)
        
        print(f"✅ /api/chart/cumulative: {days} jours, {len(labels)} points, cumul final: {cumulative}")
        
        return jsonify({
            'labels': labels,
            'data': cumulative_values,
            'cumulative': cumulative_values,  # Alias pour compatibilité
            'days': labels,  # Alias pour compatibilité
            'total_detections': cumulative,
            'period_days': days,
            'status': 'success'
        }), 200
        
    except Exception as e:
        print(f"❌ Erreur /api/chart/cumulative: {e}")
        import traceback
        traceback.print_exc()
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
        now = _local_now()
        
        # Dernière détection
        latest_detection = Detection.query.order_by(
            Detection.timestamp.desc()
        ).first()
        
        # Détections de la dernière heure
        one_hour_ago_utc = datetime.utcnow() - timedelta(hours=1)
        hourly_detections = Detection.query.filter(
            Detection.timestamp >= one_hour_ago_utc
        ).count()
        
        # Alertes non résolues
        unresolved_alerts = Alert.query.filter(
            Alert.resolved == False
        ).count()
        
        return jsonify({
            'latest_detection_time': (latest_detection.timestamp + TIMEZONE_OFFSET).isoformat() if latest_detection and latest_detection.timestamp else None,
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
            time_str = (det.timestamp + TIMEZONE_OFFSET).strftime('%H:%M:%S')
            timestamps.append(time_str)
            
            # Comptages
            persons.append(det.total_persons or 0)
            helmets.append(det.with_helmet or 0)
            vests.append(det.with_vest or 0)
            glasses.append(det.with_glasses or 0)
            boots.append(det.with_boots or 0)
            
            # Taux de conformité pour cette détection - Utiliser le nouvel algorithme
            if det.total_persons and det.total_persons > 0:
                rate = calculate_compliance_score(
                    total_persons=det.total_persons,
                    with_helmet=det.with_helmet or 0,
                    with_vest=det.with_vest or 0,
                    with_glasses=det.with_glasses or 0,
                    with_boots=det.with_boots or 0
                )
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

        # Vérifier que le fichier existe
        if not os.path.exists(pdf_path):
            print(f"❌ PDF file not found: {pdf_path}")
            return jsonify({'error': 'Erreur: le fichier PDF n\'a pas pu être créé'}), 500

        # Retourner le fichier PDF
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"epi_detection_report_{date.today().strftime('%Y%m%d')}.pdf",
            mimetype='application/pdf'
        )

    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback_str = traceback.format_exc()
        print(f"❌ Erreur export PDF détections: {error_msg}")
        print(f"Traceback: {traceback_str}")
        return jsonify({'error': f'Erreur lors de la génération du PDF: {error_msg}'}), 500


@stats_bp.route('/export/training-pdf', methods=['GET'])
def export_training_pdf():
    """Exporter un rapport PDF des résultats d'entraînement"""
    try:
        from app.pdf_export import PDFExporter
        from flask import send_file
        from datetime import date

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
        id_part = f"id_{training_id}_" if training_id else ""
        filename = f"training_report_{id_part}{date.today().strftime('%Y%m%d')}.pdf"
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

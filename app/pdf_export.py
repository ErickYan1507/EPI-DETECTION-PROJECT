from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from datetime import datetime, timedelta, date
import os
import logging

logger = logging.getLogger(__name__)

class PDFExporter:
    def __init__(self, export_dir='exports/pdf'):
        # Normalize export_dir to an absolute path under the app package directory
        base_dir = os.path.dirname(__file__)  # path to app/
        # If provided path is relative, make it relative to the app directory
        if not os.path.isabs(export_dir):
            self.export_dir = os.path.abspath(os.path.join(base_dir, export_dir))
        else:
            self.export_dir = export_dir
        # Ensure directory exists
        os.makedirs(self.export_dir, exist_ok=True)

    def generate_detection_report(self, start_date=None, end_date=None, title="Rapport de Détection EPI"):
        """Générer un rapport PDF des détections"""
        try:
            from app.database_unified import Detection, Alert
            
            if not start_date:
                start_date = date.today() - timedelta(days=7)
            if not end_date:
                end_date = date.today()

            logger.info(f"🔍 Generating detection report from {start_date} to {end_date}")

            # Récupérer les données
            try:
                detections = Detection.query.filter(
                    Detection.timestamp >= start_date,
                    Detection.timestamp <= end_date + timedelta(days=1)
                ).order_by(Detection.timestamp.desc()).all()
                logger.info(f"✅ Found {len(detections)} detections")
            except Exception as e:
                logger.error(f"❌ Error querying detections: {e}")
                detections = []

            try:
                alerts = Alert.query.filter(
                    Alert.timestamp >= start_date,
                    Alert.timestamp <= end_date + timedelta(days=1)
                ).order_by(Alert.timestamp.desc()).all()
                logger.info(f"✅ Found {len(alerts)} alerts")
            except Exception as e:
                logger.error(f"❌ Error querying alerts: {e}")
                alerts = []

            filename = f"detection_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf"
            filepath = os.path.join(self.export_dir, filename)

            # Ensure parent directory exists (defensive)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            doc = SimpleDocTemplate(filepath, pagesize=landscape(letter))
            story = []

            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.HexColor('#2c3e50')
            )

            # Titre
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 0.2*inch))

            # Informations du rapport
            info_text = f"""
            <b>Date de génération:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}<br/>
            <b>Période:</b> {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}<br/>
            <b>Nombre de détections:</b> {len(detections)}<br/>
            <b>Nombre d'alertes:</b> {len(alerts)}
            """
            story.append(Paragraph(info_text, styles["Normal"]))
            story.append(Spacer(1, 0.3*inch))

            # Statistiques générales
            if detections:
                total_persons = sum(d.total_persons or 0 for d in detections)
                compliant_detections = [d for d in detections if d.compliance_rate is not None and d.compliance_rate > 0]
                
                if compliant_detections:
                    avg_compliance = sum(d.compliance_rate for d in compliant_detections) / len(compliant_detections)
                else:
                    avg_compliance = 0
                
                def _normalize_alert_bucket(det):
                    raw = (str(det.alert_type or '').strip().lower())
                    # Legacy/new values coexist in DB (safe/warning/danger vs Aucune/Avertissement/Critique).
                    if raw in {'safe', 'aucune', 'none', 'info', 'low'}:
                        return 'safe'
                    if raw in {'warning', 'avertissement', 'medium'}:
                        return 'warning'
                    if raw in {'danger', 'critique', 'critical', 'high'}:
                        return 'danger'

                    # Fallback on compliance if alert_type is missing or unknown.
                    compliance = det.compliance_rate or 0
                    if compliance >= 80:
                        return 'safe'
                    if compliance >= 50:
                        return 'warning'
                    return 'danger'

                safe_count = sum(1 for d in detections if _normalize_alert_bucket(d) == 'safe')
                warning_count = sum(1 for d in detections if _normalize_alert_bucket(d) == 'warning')
                danger_count = sum(1 for d in detections if _normalize_alert_bucket(d) == 'danger')
                
                helmet_count = sum(d.with_helmet or 0 for d in detections)
                vest_count = sum(d.with_vest or 0 for d in detections)
                glasses_count = sum(d.with_glasses or 0 for d in detections)
                boots_count = sum(d.with_boots or 0 for d in detections)

                stats_text = f"""
                <b>📊 Statistiques Générales</b><br/>
                <b>Total personnes détectées:</b> {total_persons}<br/>
                <b>Conformité moyenne:</b> {avg_compliance:.2f}%<br/>
                <b>Détections sûres:</b> {safe_count} ({safe_count/len(detections)*100:.1f}%) | 
                <b>Avertissements:</b> {warning_count} ({warning_count/len(detections)*100:.1f}%) | 
                <b>Dangers:</b> {danger_count} ({danger_count/len(detections)*100:.1f}%)<br/>
                <b>EPI Détectés:</b> Casques: {helmet_count} | Gilets: {vest_count} | Lunettes: {glasses_count} | Bottes: {boots_count}
                """
                story.append(Paragraph(stats_text, styles["Normal"]))
                story.append(Spacer(1, 0.2*inch))

            # Tableau des détections (limité à 50 lignes par page)
            if detections:
                story.append(Paragraph("<b>📋 Détail des Détections</b>", styles["Heading2"]))
                story.append(Spacer(1, 0.1*inch))

                # Première batch
                for batch_idx in range(0, len(detections), 50):
                    batch = detections[batch_idx:batch_idx+50]
                    data = [['Date/Heure', 'Personnes', 'Casques', 'Gilets', 'Lunettes', 'Bottes', 'Conformité', 'Statut']]

                    for det in batch:
                        try:
                            timestamp_str = det.timestamp.strftime('%d/%m %H:%M') if det.timestamp else 'N/A'
                            total = det.total_persons or 0
                            helmet = det.with_helmet or 0
                            vest = det.with_vest or 0
                            glasses = det.with_glasses or 0
                            boots = det.with_boots or 0
                            compliance = det.compliance_rate or 0
                            status = (det.alert_type or 'unknown').upper()

                            data.append([
                                timestamp_str,
                                str(total),
                                str(helmet),
                                str(vest),
                                str(glasses),
                                str(boots),
                                f"{compliance:.1f}%",
                                status
                            ])
                        except Exception as e:
                            logger.error(f"Error adding detection row: {e}")
                            continue

                    if data and len(data) > 1:  # Si on a au moins une ligne de données
                        table = Table(data, colWidths=[1.2*inch, 0.9*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.9*inch, 0.9*inch])
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 10),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),
                            ('FONTSIZE', (0, 1), (-1, -1), 8),
                            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
                        ]))
                        story.append(table)
                        if batch_idx + 50 < len(detections):
                            story.append(PageBreak())
            else:
                story.append(Paragraph("<i>Aucune détection enregistrée pour cette période.</i>", styles["Normal"]))

            # Résumé des alertes
            if alerts:
                story.append(PageBreak())
                story.append(Paragraph("<b>🚨 Alertes Récentes</b>", styles["Heading2"]))
                story.append(Spacer(1, 0.1*inch))
                
                alert_data = [['Date/Heure', 'Sévérité', 'Description']]
                for alert in alerts[:50]:
                    try:
                        timestamp_str = alert.timestamp.strftime('%d/%m %H:%M') if alert.timestamp else 'N/A'
                        severity = (alert.severity or 'unknown').upper()
                        description = alert.message or alert.description or 'N/A'
                        alert_data.append([timestamp_str, severity, description[:80]])
                    except Exception as e:
                        logger.error(f"Error adding alert row: {e}")
                        continue
                
                if alert_data and len(alert_data) > 1:
                    alert_table = Table(alert_data, colWidths=[2*inch, 1.5*inch, 4*inch])
                    alert_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(alert_table)
            
            # Construire le document
            doc.build(story)
            logger.info(f"✅ PDF generated successfully: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"❌ Error generating PDF: {e}", exc_info=True)
            raise

    def generate_training_report(self, training_result_id=None, title="Rapport de Résultats d'Entraînement"):
        """Générer un rapport PDF des résultats d'entraînement"""
        try:
            from app.database_unified import TrainingResult
            
            if training_result_id:
                training_results = [TrainingResult.query.get_or_404(training_result_id)]
            else:
                training_results = TrainingResult.query.order_by(TrainingResult.timestamp.desc()).limit(10).all()

            filename = f"training_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(self.export_dir, filename)

            # Ensure parent directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            doc = SimpleDocTemplate(filepath, pagesize=letter)
            story = []

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=20,
                spaceAfter=30,
                textColor=colors.HexColor('#2c3e50')
            )

            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 0.2*inch))

            for result in training_results:
                # En-tête du modèle
                model_title = f"<b>🤖 Modèle: {result.model_name or 'N/A'}</b>"
                if result.model_version:
                    model_title += f" (v{result.model_version})"
                story.append(Paragraph(model_title, styles["Heading2"]))
                story.append(Spacer(1, 0.1*inch))

                # Informations générales
                info_text = f"""
                <b>Date d'entraînement:</b> {result.timestamp.strftime('%d/%m/%Y %H:%M') if result.timestamp else 'N/A'}<br/>
                <b>Dataset:</b> {result.dataset_name or 'N/A'} ({result.dataset_size or 0} images)<br/>
                <b>Classes:</b> {result.num_classes or 4}<br/>
                <b>Epochs:</b> {result.epochs or 'N/A'}<br/>
                <b>Batch size:</b> {result.batch_size or 'N/A'}<br/>
                <b>Temps d'entraînement:</b> {result.training_time_seconds or 0:.1f} secondes
                """
                story.append(Paragraph(info_text, styles["Normal"]))
                story.append(Spacer(1, 0.15*inch))

                # Métriques
                metrics_data = [
                    ['Métrique', 'Entraînement', 'Validation', 'Test'],
                    ['Précision', f"{result.train_precision:.3f}" if result.train_precision else "N/A",
                     f"{result.val_precision:.3f}" if result.val_precision else "N/A",
                     f"{result.test_precision:.3f}" if result.test_precision else "N/A"],
                    ['Rappel', f"{result.train_recall:.3f}" if result.train_recall else "N/A",
                     f"{result.val_recall:.3f}" if result.val_recall else "N/A",
                     f"{result.test_recall:.3f}" if result.test_recall else "N/A"],
                    ['F1-Score', f"{result.train_f1_score:.3f}" if result.train_f1_score else "N/A",
                     f"{result.val_f1_score:.3f}" if result.val_f1_score else "N/A",
                     f"{result.test_f1_score:.3f}" if result.test_f1_score else "N/A"],
                    ['Perte', f"{result.train_loss:.4f}" if result.train_loss else "N/A",
                     f"{result.val_loss:.4f}" if result.val_loss else "N/A",
                     f"{result.test_loss:.4f}" if result.test_loss else "N/A"]
                ]

                metrics_table = Table(metrics_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 1.2*inch])
                metrics_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
                ]))

                story.append(metrics_table)
                story.append(Spacer(1, 0.2*inch))

            # Générer le PDF
            doc.build(story)
            logger.info(f"✅ Training report generated: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"❌ Error generating training report: {e}", exc_info=True)
            raise

    def generate_presence_report(self, start_date=None, end_date=None, title="Rapport de Présence Quotidienne"):
        """Générer un rapport PDF des présences quotidiennes"""
        try:
            from app.database_unified import DailyPresence
            import json
            
            if not start_date:
                start_date = date.today() - timedelta(days=7)
            if not end_date:
                end_date = date.today()

            # Récupérer les données
            presences = DailyPresence.query.filter(
                DailyPresence.date >= start_date,
                DailyPresence.date <= end_date
            ).order_by(DailyPresence.date.desc()).all()

            filename = f"presence_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf"
            filepath = os.path.join(self.export_dir, filename)

            # Ensure parent directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            doc = SimpleDocTemplate(filepath, pagesize=landscape(letter))
            story = []

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.HexColor('#2c3e50')
            )

            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 0.2*inch))

            # Statistiques générales
            total_days = (end_date - start_date).days + 1
            total_presences = len(presences)
            total_detections = sum(p.detection_count or 0 for p in presences)
            
            compliant_presences = [p for p in presences if p.compliance_score is not None and p.compliance_score > 0]
            avg_compliance = sum(p.compliance_score for p in compliant_presences) / len(compliant_presences) if compliant_presences else 0

            stats_text = f"""
            <b>📅 Période:</b> {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}<br/>
            <b>Jours couverts:</b> {total_days}<br/>
            <b>Total présences:</b> {total_presences}<br/>
            <b>Total détections:</b> {total_detections}<br/>
            <b>Conformité moyenne:</b> {avg_compliance:.2f}%
            """
            story.append(Paragraph(stats_text, styles["Normal"]))
            story.append(Spacer(1, 0.3*inch))

            # Tableau des présences
            if presences:
                data = [['Date', 'ID Badge', 'Première Détection', 'Dernière Détection', 'Nombre Détections', 'Conformité', 'Équipement']]

                for presence in presences[:100]:  # Limiter à 100 lignes
                    try:
                        equipment = presence.equipment_status
                        if equipment:
                            try:
                                eq_data = json.loads(equipment)
                                eq_text = []
                                if eq_data.get('helmet'): eq_text.append('Casque')
                                if eq_data.get('vest'): eq_text.append('Gilet')
                                if eq_data.get('glasses'): eq_text.append('Lunettes')
                                if eq_data.get('boots'): eq_text.append('Bottes')
                                equipment_str = ', '.join(eq_text) if eq_text else 'Aucun'
                            except:
                                equipment_str = 'N/A'
                        else:
                            equipment_str = 'N/A'

                        data.append([
                            presence.date.strftime('%d/%m/%Y') if presence.date else 'N/A',
                            presence.badge_id or 'N/A',
                            presence.first_detection.strftime('%H:%M') if presence.first_detection else 'N/A',
                            presence.last_detection.strftime('%H:%M') if presence.last_detection else 'N/A',
                            str(presence.detection_count or 0),
                            f"{presence.compliance_score:.1f}%" if presence.compliance_score else "N/A",
                            equipment_str
                        ])
                    except Exception as e:
                        logger.error(f"Error processing presence: {e}")
                        continue

                if data and len(data) > 1:
                    table = Table(data, colWidths=[1*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1*inch, 1*inch, 1.5*inch])
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
                        ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ]))
                    story.append(table)

            # Générer le PDF
            doc.build(story)
            logger.info(f"✅ Presence report generated: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"❌ Error generating presence report: {e}", exc_info=True)
            raise

    def generate_attendance_list_report(self, start_date=None, end_date=None, report_type="daily"):
        """Generer une liste de presence PDF (impression liste) pour les rapports email."""
        try:
            from app.database_unified import AttendanceRecord, utc_to_local

            if not start_date:
                start_date = date.today() - timedelta(days=1)
            if not end_date:
                end_date = date.today()

            rows = AttendanceRecord.query.filter(
                AttendanceRecord.attendance_date >= start_date,
                AttendanceRecord.attendance_date <= end_date
            ).order_by(
                AttendanceRecord.attendance_date.desc(),
                AttendanceRecord.last_seen_at.desc()
            ).limit(2000).all()

            now_dt = datetime.now()
            list_sheet_no = f"LST-{report_type.upper()}-{now_dt.strftime('%Y%m%d%H%M%S')}"
            filename = (
                f"attendance_list_{report_type}_"
                f"{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf"
            )
            filepath = os.path.join(self.export_dir, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            doc = SimpleDocTemplate(filepath, pagesize=landscape(letter))
            story = []
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                "AttendanceTitle",
                parent=styles["Heading1"],
                fontSize=20,
                spaceAfter=18,
                textColor=colors.HexColor("#111827"),
            )

            story.append(Paragraph("LISTE DE PRESENCE", title_style))
            story.append(
                Paragraph(
                    (
                        f"<b>Periode:</b> {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}<br/>"
                        f"<b>Date du jour:</b> {now_dt.strftime('%d/%m/%Y')}<br/>"
                        f"<b>Numero de fiche:</b> {list_sheet_no}<br/>"
                        f"<b>Total lignes:</b> {len(rows)}"
                    ),
                    styles["Normal"],
                )
            )
            story.append(Spacer(1, 0.15 * inch))

            headers = [
                "Nom complet",
                "ID (6)",
                "Fonction",
                "Adresse",
                "Date",
                "Heure d'entree",
                "Presence",
                "% equipement",
                "Photo",
            ]

            table_data = [headers]
            for row in rows:
                person = row.person
                rid6 = f"{((person.id if person else row.person_id) or 0):06d}"
                is_present = bool(person and (person.manual_presence_today is None or person.manual_presence_today))
                presence_label = "Present" if is_present else "Absent"
                epi_count = (
                    (1 if bool(row.helmet_detected) else 0)
                    + (1 if bool(row.vest_detected) else 0)
                    + (1 if bool(row.glasses_detected) else 0)
                    + (1 if bool(row.boots_detected) else 0)
                )
                epi_percent = int(round((epi_count * 100.0) / 4.0))

                photo_cell = "-"
                photo_path = (person.identity_photo_path or "").strip() if person else ""
                if photo_path:
                    resolved = photo_path
                    if not os.path.isabs(resolved):
                        base_dir = os.path.dirname(__file__)
                        resolved = os.path.abspath(os.path.join(base_dir, "..", photo_path))
                    if os.path.exists(resolved):
                        try:
                            photo_cell = RLImage(resolved, width=0.38 * inch, height=0.5 * inch)
                        except Exception:
                            photo_cell = "-"

                first_seen = utc_to_local(row.first_seen_at).strftime("%H:%M:%S") if row.first_seen_at else "-"
                adate = row.attendance_date.strftime("%d/%m/%Y") if row.attendance_date else "-"

                table_data.append(
                    [
                        person.full_name if person and person.full_name else "-",
                        rid6,
                        person.job_title if person and person.job_title else "-",
                        person.address if person and person.address else "-",
                        adate,
                        first_seen,
                        presence_label,
                        f"{epi_percent}%",
                        photo_cell,
                    ]
                )

            if len(table_data) > 141:
                table_data = table_data[:141]

            table = Table(
                table_data,
                colWidths=[
                    1.5 * inch,
                    0.7 * inch,
                    1.0 * inch,
                    1.3 * inch,
                    0.8 * inch,
                    0.85 * inch,
                    0.75 * inch,
                    0.75 * inch,
                    0.55 * inch,
                ],
                repeatRows=1,
            )
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 8),
                        ("ALIGN", (1, 1), (1, -1), "CENTER"),
                        ("ALIGN", (6, 1), (7, -1), "CENTER"),
                        ("ALIGN", (8, 1), (8, -1), "CENTER"),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("FONTSIZE", (0, 1), (-1, -1), 7),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                        ("LEFTPADDING", (0, 0), (-1, -1), 4),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                        ("TOPPADDING", (0, 0), (-1, -1), 3),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ]
                )
            )
            story.append(table)
            story.append(Spacer(1, 0.2 * inch))

            qr_payload = f"Date du jour: {now_dt.strftime('%d/%m/%Y')}\nNumero fiche: {list_sheet_no}"
            qr_widget = qr.QrCodeWidget(qr_payload)
            bounds = qr_widget.getBounds()
            qr_size = 1.1 * inch
            width = bounds[2] - bounds[0]
            height = bounds[3] - bounds[1]
            qr_drawing = Drawing(qr_size, qr_size, transform=[qr_size / width, 0, 0, qr_size / height, 0, 0])
            qr_drawing.add(qr_widget)
            story.append(Paragraph("<b>QR unique de la liste</b>", styles["Normal"]))
            story.append(qr_drawing)
            story.append(Spacer(1, 0.12 * inch))
            story.append(
                Paragraph(
                    f"Date du jour: {now_dt.strftime('%d/%m/%Y')}<br/>Numero de fiche (reference liste): {list_sheet_no}",
                    styles["Normal"],
                )
            )
            story.append(Spacer(1, 0.22 * inch))

            signature_table = Table(
                [["Signature responsable", "Signature et cachet"]],
                colWidths=[3.8 * inch, 3.8 * inch],
            )
            signature_table.setStyle(
                TableStyle(
                    [
                        ("LINEABOVE", (0, 0), (0, 0), 1, colors.black),
                        ("LINEABOVE", (1, 0), (1, 0), 1, colors.black),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("TOPPADDING", (0, 0), (-1, -1), 5),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ]
                )
            )
            story.append(signature_table)

            doc.build(story)
            logger.info(f"✅ Attendance list report generated: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"❌ Error generating attendance list report: {e}", exc_info=True)
            raise

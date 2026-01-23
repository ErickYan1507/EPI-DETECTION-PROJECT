from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime, timedelta, date
import os
from app.database_unified import Detection, Alert, TrainingResult, DailyPresence

class PDFExporter:
    def __init__(self, export_dir='exports/pdf'):
        self.export_dir = export_dir
        os.makedirs(export_dir, exist_ok=True)

    def generate_detection_report(self, start_date=None, end_date=None, title="Rapport de Détection EPI"):
        """Générer un rapport PDF des détections"""
        if not start_date:
            start_date = date.today() - timedelta(days=7)
        if not end_date:
            end_date = date.today()

        # Récupérer les données
        detections = Detection.query.filter(
            Detection.timestamp >= start_date,
            Detection.timestamp <= end_date + timedelta(days=1)
        ).order_by(Detection.timestamp.desc()).all()

        alerts = Alert.query.filter(
            Alert.timestamp >= start_date,
            Alert.timestamp <= end_date + timedelta(days=1)
        ).order_by(Alert.timestamp.desc()).all()

        filename = f"detection_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf"
        filepath = os.path.join(self.export_dir, filename)

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
        story.append(Spacer(1, 20))

        # Informations du rapport
        info_text = f"""
        <b>Date de génération:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}<br/>
        <b>Période:</b> {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}<br/>
        <b>Nombre de détections:</b> {len(detections)}<br/>
        <b>Nombre d'alertes:</b> {len(alerts)}
        """
        story.append(Paragraph(info_text, styles["Normal"]))
        story.append(Spacer(1, 30))

        # Statistiques générales
        if detections:
            total_persons = sum(d.total_persons for d in detections)
            avg_compliance = sum(d.compliance_rate for d in detections if d.compliance_rate) / len([d for d in detections if d.compliance_rate])
            safe_count = sum(1 for d in detections if d.alert_type == 'safe')
            warning_count = sum(1 for d in detections if d.alert_type == 'warning')
            danger_count = sum(1 for d in detections if d.alert_type == 'danger')

            stats_text = f"""
            <b>📊 Statistiques Générales</b><br/>
            <b>Total personnes détectées:</b> {total_persons}<br/>
            <b>Conformité moyenne:</b> {avg_compliance:.2f}%<br/>
            <b>Détections sûres:</b> {safe_count} ({safe_count/len(detections)*100:.1f}%)<br/>
            <b>Avertissements:</b> {warning_count} ({warning_count/len(detections)*100:.1f}%)<br/>
            <b>Dangers:</b> {danger_count} ({danger_count/len(detections)*100:.1f}%)
            """
            story.append(Paragraph(stats_text, styles["Normal"]))
            story.append(Spacer(1, 20))

        # Tableau des détections
        if detections:
            story.append(Paragraph("<b>📋 Détail des Détections</b>", styles["Heading2"]))
            story.append(Spacer(1, 10))

            data = [['Date/Heure', 'Personnes', 'Casques', 'Gilets', 'Lunettes', 'Conformité', 'Statut']]

            for det in detections[:100]:  # Limiter à 100 lignes
                status_color = {
                    'safe': '#2ecc71',
                    'warning': '#f39c12',
                    'danger': '#e74c3c'
                }.get(det.alert_type, '#95a5a6')

                status_html = f'<font color="{status_color}">{det.alert_type.upper()}</font>'

                data.append([
                    det.timestamp.strftime('%d/%m %H:%M'),
                    str(det.total_persons),
                    str(det.with_helmet),
                    str(det.with_vest),
                    str(det.with_glasses),
                    f"{det.compliance_rate:.1f}%" if det.compliance_rate else "N/A",
                    Paragraph(status_html, styles["Normal"])
                ])

            table = Table(data, colWidths=[1.2*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
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

        # Section Alertes
        if alerts:
            story.append(Spacer(1, 30))
            story.append(Paragraph("<b>🚨 Alertes et Incidents</b>", styles["Heading2"]))
            story.append(Spacer(1, 10))

            alert_data = [['Date/Heure', 'Type', 'Message', 'Sévérité', 'Résolu']]

            for alert in alerts[:50]:  # Limiter à 50 alertes
                severity_color = {
                    'low': '#2ecc71',
                    'medium': '#f39c12',
                    'high': '#e74c3c',
                    'critical': '#8e44ad'
                }.get(alert.severity, '#95a5a6')

                severity_html = f'<font color="{severity_color}">{alert.severity.upper()}</font>'
                resolved_text = "Oui" if alert.resolved else "Non"

                alert_data.append([
                    alert.timestamp.strftime('%d/%m %H:%M'),
                    alert.type.title(),
                    alert.message[:50] + "..." if len(alert.message) > 50 else alert.message,
                    Paragraph(severity_html, styles["Normal"]),
                    resolved_text
                ])

            alert_table = Table(alert_data, colWidths=[1.2*inch, 1*inch, 2.5*inch, 1*inch, 0.8*inch])
            alert_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
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

            story.append(alert_table)

        # Générer le PDF
        doc.build(story)
        print(f"Rapport de détection généré: {filepath}")

        return filepath

    def generate_training_report(self, training_result_id=None, title="Rapport de Résultats d'Entraînement"):
        """Générer un rapport PDF des résultats d'entraînement"""
        if training_result_id:
            training_results = [TrainingResult.query.get_or_404(training_result_id)]
        else:
            training_results = TrainingResult.query.order_by(TrainingResult.timestamp.desc()).limit(10).all()

        filename = f"training_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.export_dir, filename)

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
        story.append(Spacer(1, 20))

        for result in training_results:
            # En-tête du modèle
            model_title = f"<b>🤖 Modèle: {result.model_name}</b>"
            if result.model_version:
                model_title += f" (v{result.model_version})"
            story.append(Paragraph(model_title, styles["Heading2"]))
            story.append(Spacer(1, 10))

            # Informations générales
            info_text = f"""
            <b>Date d'entraînement:</b> {result.timestamp.strftime('%d/%m/%Y %H:%M')}<br/>
            <b>Dataset:</b> {result.dataset_name or 'N/A'} ({result.dataset_size or 0} images)<br/>
            <b>Classes:</b> {result.num_classes or 4}<br/>
            <b>Époques:</b> {result.epochs or 'N/A'}<br/>
            <b>Batch size:</b> {result.batch_size or 'N/A'}<br/>
            <b>Temps d'entraînement:</b> {result.training_time_seconds or 0:.1f} secondes
            """
            story.append(Paragraph(info_text, styles["Normal"]))
            story.append(Spacer(1, 15))

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
            story.append(Spacer(1, 20))

            # Métriques de performance
            perf_text = f"""
            <b>⚡ Performance:</b><br/>
            <b>Temps d'inférence moyen:</b> {result.inference_time_ms:.2f} ms<br/>
            <b>FPS estimé:</b> {result.fps:.1f} images/seconde<br/>
            <b>Mémoire GPU:</b> {result.gpu_memory_mb or 0:.1f} MB
            """
            story.append(Paragraph(perf_text, styles["Normal"]))
            story.append(Spacer(1, 30))

        # Générer le PDF
        doc.build(story)
        print(f"Rapport d'entraînement généré: {filepath}")

        return filepath

    def generate_presence_report(self, start_date=None, end_date=None, title="Rapport de Présence Quotidienne"):
        """Générer un rapport PDF des présences quotidiennes"""
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
        story.append(Spacer(1, 20))

        # Statistiques générales
        total_days = (end_date - start_date).days + 1
        total_presences = len(presences)
        total_detections = sum(p.detection_count for p in presences)
        avg_compliance = sum(p.compliance_score for p in presences if p.compliance_score) / len([p for p in presences if p.compliance_score]) if presences else 0

        stats_text = f"""
        <b>📅 Période:</b> {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}<br/>
        <b>Jours couverts:</b> {total_days}<br/>
        <b>Total présences:</b> {total_presences}<br/>
        <b>Total détections:</b> {total_detections}<br/>
        <b>Conformité moyenne:</b> {avg_compliance:.2f}%
        """
        story.append(Paragraph(stats_text, styles["Normal"]))
        story.append(Spacer(1, 30))

        # Tableau des présences
        if presences:
            data = [['Date', 'ID Badge', 'Première Détection', 'Dernière Détection', 'Nombre Détections', 'Conformité', 'Équipement']]

            for presence in presences[:100]:  # Limiter à 100 lignes
                equipment = presence.equipment_status
                if equipment:
                    try:
                        import json
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
                    presence.date.strftime('%d/%m/%Y'),
                    presence.badge_id or 'N/A',
                    presence.first_detection.strftime('%H:%M') if presence.first_detection else 'N/A',
                    presence.last_detection.strftime('%H:%M') if presence.last_detection else 'N/A',
                    str(presence.detection_count),
                    f"{presence.compliance_score:.1f}%" if presence.compliance_score else "N/A",
                    equipment_str
                ])

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
        print(f"Rapport de présence généré: {filepath}")

        return filepath

    # Méthode de compatibilité pour l'ancien code
    def generate_report(self, detections, title="Rapport de Détection EPI"):
        """Méthode de compatibilité - utilise generate_detection_report"""
        return self.generate_detection_report(title=title)
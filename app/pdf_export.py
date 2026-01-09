from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import os

class PDFExporter:
    def __init__(self, export_dir='exports/pdf'):
        self.export_dir = export_dir
        os.makedirs(export_dir, exist_ok=True)
    
    def generate_report(self, detections, title="Rapport de Détection EPI"):
        """Générer un rapport PDF complet"""
        filename = f"epi_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
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
        <b>Nombre de détections:</b> {len(detections)}<br/>
        <b>Période couverte:</b> {detections[-1].timestamp.strftime('%d/%m/%Y') if detections else 'N/A'}
        """
        story.append(Paragraph(info_text, styles["Normal"]))
        story.append(Spacer(1, 30))
        
        # Tableau des détections
        if detections:
            data = [['Heure', 'Personnes', 'Casques', 'Gilets', 'Lunettes', 'Conformité', 'Statut']]
            
            for det in detections[:50]:  # Limiter à 50 lignes
                status_color = {
                    'safe': '#2ecc71',
                    'warning': '#f39c12',
                    'danger': '#e74c3c'
                }.get(det.alert_type, '#95a5a6')
                
                status_html = f'<font color="{status_color}">{det.alert_type.upper()}</font>'
                
                data.append([
                    det.timestamp.strftime('%H:%M:%S'),
                    str(det.total_persons),
                    str(det.with_helmet),
                    str(det.with_vest),
                    str(det.with_glasses),
                    f"{det.compliance_rate}%",
                    Paragraph(status_html, styles["Normal"])
                ])
            
            table = Table(data, colWidths=[1*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
            ]))
            
            story.append(table)
        
        # Statistiques résumées
        story.append(Spacer(1, 40))
        story.append(Paragraph("<b>Statistiques Résumées</b>", styles["Heading2"]))
        
        if detections:
            avg_compliance = sum(d.compliance_rate for d in detections) / len(detections)
            total_persons = sum(d.total_persons for d in detections)
            
            stats_text = f"""
            <b>Conformité moyenne:</b> {avg_compliance:.2f}%<br/>
            <b>Total personnes détectées:</b> {total_persons}<br/>
            <b>Nombre d'alertes:</b> {sum(1 for d in detections if d.alert_type != 'safe')}<br/>
            <b>Taux de sécurité:</b> {(sum(1 for d in detections if d.alert_type == 'safe') / len(detections) * 100):.1f}%
            """
            story.append(Paragraph(stats_text, styles["Normal"]))
        
        # Générer le PDF
        doc.build(story)
        print(f"Rapport généré: {filepath}")
        
        return filepath
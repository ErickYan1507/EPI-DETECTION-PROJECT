"""
Interface en ligne de commande (CLI) pour les tâches administratives
"""
import click
import logging
from pathlib import Path
from app.main_new import get_app
from app.database import Detection, Alert, Worker, SystemLog
from app.logger import logger

@click.group()
def cli():
    """CLI de gestion EPI Detection"""
    pass

@cli.command()
def init_db():
    """Initialiser la base de données"""
    app, db, _ = get_app()
    with app.app_context():
        logger.info("Création des tables...")
        db.create_all()
        logger.info("Base de données initialisée ✓")

@cli.command()
def drop_db():
    """Supprimer toutes les tables (⚠️ ATTENTION)"""
    if click.confirm('Êtes-vous sûr? Cela supprimera TOUTES les données.'):
        app, db, _ = get_app()
        with app.app_context():
            logger.warning("Suppression de toutes les tables...")
            db.drop_all()
            logger.info("Tables supprimées ✓")

@cli.command()
@click.option('--days', default=30, help='Nombre de jours avant suppression')
def cleanup(days):
    """Nettoyer les fichiers et données anciennes"""
    from app.utils import cleanup_old_files
    from datetime import timedelta, datetime
    
    app, db, _ = get_app()
    with app.app_context():
        logger.info(f"Nettoyage des fichiers plus vieux que {days} jours...")
        cleanup_old_files(days)
        
        # Supprimer les détections anciennes
        cutoff_date = datetime.now() - timedelta(days=days)
        old_detections = Detection.query.filter(
            Detection.timestamp < cutoff_date
        ).all()
        
        for detection in old_detections:
            db.session.delete(detection)
        
        db.session.commit()
        logger.info(f"Nettoyage terminé: {len(old_detections)} détections supprimées ✓")

@cli.command()
def show_stats():
    """Afficher les statistiques globales"""
    app, db, _ = get_app()
    with app.app_context():
        total_detections = Detection.query.count()
        total_alerts = Alert.query.count()
        active_workers = Worker.query.filter_by(is_active=True).count()
        unresolved_alerts = Alert.query.filter_by(resolved=False).count()
        
        click.echo("\n" + "="*50)
        click.echo("📊 STATISTIQUES GLOBALES")
        click.echo("="*50)
        click.echo(f"Détections totales:     {total_detections}")
        click.echo(f"Alertes totales:        {total_alerts}")
        click.echo(f"Alertes non résolues:   {unresolved_alerts}")
        click.echo(f"Travailleurs actifs:    {active_workers}")
        click.echo("="*50 + "\n")

@cli.command()
@click.option('--name', prompt='Nom du travailleur', help='Nom du travailleur')
@click.option('--badge', prompt='ID badge', help='ID du badge')
@click.option('--dept', prompt='Département', help='Département')
def add_worker(name, badge, dept):
    """Ajouter un travailleur"""
    app, db, _ = get_app()
    with app.app_context():
        worker = Worker(
            name=name,
            badge_id=badge,
            department=dept
        )
        db.session.add(worker)
        db.session.commit()
        logger.info(f"Travailleur ajouté: {name} ({badge}) ✓")

@cli.command()
def list_workers():
    """Lister tous les travailleurs"""
    app, db, _ = get_app()
    with app.app_context():
        workers = Worker.query.all()
        
        click.echo("\n" + "="*70)
        click.echo("👷 LISTE DES TRAVAILLEURS")
        click.echo("="*70)
        click.echo(f"{'ID':<5} {'Nom':<20} {'Badge':<15} {'Département':<20} {'Score':<8}")
        click.echo("-"*70)
        
        for worker in workers:
            click.echo(f"{worker.id:<5} {worker.name:<20} {worker.badge_id:<15} "
                      f"{worker.department:<20} {worker.compliance_score:<8.1f}%")
        
        click.echo("="*70 + "\n")

@cli.command()
def show_recent_alerts():
    """Afficher les alertes récentes"""
    app, db, _ = get_app()
    with app.app_context():
        alerts = Alert.query.order_by(
            Alert.timestamp.desc()
        ).limit(10).all()
        
        click.echo("\n" + "="*80)
        click.echo("🔔 ALERTES RÉCENTES")
        click.echo("="*80)
        click.echo(f"{'ID':<5} {'Timestamp':<20} {'Severity':<12} {'Message':<40}")
        click.echo("-"*80)
        
        for alert in alerts:
            timestamp = alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            message = alert.message[:40]
            click.echo(f"{alert.id:<5} {timestamp:<20} {alert.severity:<12} {message:<40}")
        
        click.echo("="*80 + "\n")

@cli.command()
def export_stats():
    """Exporter les statistiques en CSV"""
    import csv
    
    app, db, _ = get_app()
    with app.app_context():
        detections = Detection.query.all()
        
        csv_path = Path('exports') / 'statistics.csv'
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'id', 'timestamp', 'total_persons', 'with_helmet',
                'with_vest', 'with_glasses', 'compliance_rate', 'alert_type'
            ])
            writer.writeheader()
            
            for det in detections:
                writer.writerow({
                    'id': det.id,
                    'timestamp': det.timestamp.isoformat(),
                    'total_persons': det.total_persons,
                    'with_helmet': det.with_helmet,
                    'with_vest': det.with_vest,
                    'with_glasses': det.with_glasses,
                    'compliance_rate': det.compliance_rate,
                    'alert_type': det.alert_type
                })
        
        logger.info(f"Statistiques exportées vers {csv_path} ✓")

if __name__ == '__main__':
    cli()

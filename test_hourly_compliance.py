#!/usr/bin/env python3
"""Test conformité par heure"""
from app.database_unified import db, Detection
from app.main import app
from datetime import datetime, timedelta
from app.constants import calculate_compliance_score

with app.app_context():
    print('=== DONNÉES PAR HEURE (dernières 24h) ===\n')
    
    start_time = datetime.now() - timedelta(hours=24)
    detections = Detection.query.filter(Detection.timestamp >= start_time).all()
    
    hourly_data = {}
    for det in detections:
        hour = det.timestamp.hour
        if hour not in hourly_data:
            hourly_data[hour] = {'count': 0, 'total_persons': 0, 'with_helmet': 0, 'with_vest': 0, 'with_glasses': 0, 'with_boots': 0}
        hourly_data[hour]['count'] += 1
        hourly_data[hour]['total_persons'] += det.total_persons or 0
        hourly_data[hour]['with_helmet'] += det.with_helmet or 0
        hourly_data[hour]['with_vest'] += det.with_vest or 0
        hourly_data[hour]['with_glasses'] += det.with_glasses or 0
        hourly_data[hour]['with_boots'] += det.with_boots or 0
    
    for hour in sorted(hourly_data.keys()):
        data = hourly_data[hour]
        compliance = calculate_compliance_score(
            total_persons=data['total_persons'], 
            with_helmet=data['with_helmet'], 
            with_vest=data['with_vest'], 
            with_glasses=data['with_glasses'], 
            with_boots=data['with_boots']
        )
        print(f'{hour:02d}h: {data["count"]:3d} dets, Personnes: {data["total_persons"]:3d}, Conformité: {compliance:.1f}%')

    print('\n=== DONNÉES PAR JOUR (7 derniers jours) ===\n')
    
    start_date = datetime.now() - timedelta(days=7)
    detections = Detection.query.filter(Detection.timestamp >= start_date).all()
    
    daily_data = {}
    for det in detections:
        day = det.timestamp.strftime('%Y-%m-%d')
        if day not in daily_data:
            daily_data[day] = {'count': 0, 'total_persons': 0, 'with_helmet': 0, 'with_vest': 0, 'with_glasses': 0, 'with_boots': 0}
        daily_data[day]['count'] += 1
        daily_data[day]['total_persons'] += det.total_persons or 0
        daily_data[day]['with_helmet'] += det.with_helmet or 0
        daily_data[day]['with_vest'] += det.with_vest or 0
        daily_data[day]['with_glasses'] += det.with_glasses or 0
        daily_data[day]['with_boots'] += det.with_boots or 0
    
    for day in sorted(daily_data.keys()):
        data = daily_data[day]
        compliance = calculate_compliance_score(
            total_persons=data['total_persons'], 
            with_helmet=data['with_helmet'], 
            with_vest=data['with_vest'], 
            with_glasses=data['with_glasses'], 
            with_boots=data['with_boots']
        )
        print(f'{day}: {data["count"]:4d} dets, Personnes: {data["total_persons"]:4d}, Conformité: {compliance:.1f}%')

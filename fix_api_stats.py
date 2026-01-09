from datetime import date, datetime

old_code = '''@app.route('/api/stats', methods=['GET'])
def get_stats():
    total_detections = Detection.query.count()
    avg_compliance = db.session.query(db.func.avg(Detection.compliance_rate)).scalar() or 0
    total_persons = db.session.query(db.func.sum(Detection.total_persons)).scalar() or 0
    active_alerts = Alert.query.filter_by(resolved=False).count()
    
    return jsonify({
        'total_detections': total_detections,
        'avg_compliance': round(avg_compliance, 2),
        'total_persons': total_persons,
        'active_alerts': active_alerts,
        'last_update': datetime.now().isoformat()
    })'''

new_code = '''@app.route('/api/stats', methods=['GET'])
def get_stats():
    from datetime import date
    
    total_detections = Detection.query.count()
    avg_compliance = db.session.query(db.func.avg(Detection.compliance_rate)).scalar() or 0
    total_persons = db.session.query(db.func.sum(Detection.total_persons)).scalar() or 0
    active_alerts = Alert.query.filter_by(resolved=False).count()
    
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_detections = Detection.query.filter(Detection.timestamp >= today_start).count()
    
    return jsonify({
        'compliance_rate': round(avg_compliance, 2),
        'total_persons': total_persons or 0,
        'alerts': active_alerts,
        'detections_today': today_detections,
        'total_detections': total_detections,
        'last_update': datetime.now().isoformat()
    })'''

with open('app/main.py', 'r') as f:
    content = f.read()

content = content.replace(old_code, new_code)

with open('app/main.py', 'w') as f:
    f.write(content)

print("Fixed!")

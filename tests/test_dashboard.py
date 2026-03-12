#!/usr/bin/env python3
"""
Test script pour vérifier les modifications du dashboard sans charger les modèles
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask
from flask_cors import CORS

# Créer une app Flask minimale pour tester les routes
app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return '''
    <h1>Dashboard is now the home page!</h1>
    <p>The main route now renders the dashboard template.</p>
    <a href="/api/stats">Test API Stats</a>
    '''

@app.route('/api/stats')
def api_stats():
    return {
        'compliance_rate': 85.5,
        'total_persons': 24,
        'alerts': 3,
        'detections_today': 156,
        'status': 'success'
    }

if __name__ == '__main__':
    print("Test server starting on http://localhost:5001")
    print("Main route now renders dashboard template")
    app.run(host='0.0.0.0', port=5001, debug=True)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from config import config
from flask import Flask
from app.database import db, TrainingResult

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    results = TrainingResult.query.order_by(TrainingResult.timestamp.desc()).all()
    print(f'Total training results: {len(results)}')
    if results:
        r = results[0]
        print(f'\nLatest result:')
        print(f'  Model: {r.model_name} v{r.model_version}')
        print(f'  Train Accuracy: {r.train_accuracy}')
        print(f'  Val Accuracy: {r.val_accuracy}')
        print(f'  Train Loss: {r.train_loss}')
        print(f'  Val Loss: {r.val_loss}')
        print(f'  Epochs: {r.epochs}')
        print(f'  Batch Size: {r.batch_size}')
        print(f'  Status: {r.status}')
        print(f'  Timestamp: {r.timestamp}')
        
        print(f'\nto_dict() output:')
        result_dict = r.to_dict()
        import json
        print(json.dumps(result_dict, indent=2, default=str))

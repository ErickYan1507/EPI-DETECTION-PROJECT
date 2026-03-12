#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check and add missing columns in MySQL for models defined in app/database_unified.py
Currently ensures `detections.training_result_id` exists.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config import config
from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

mysql_uri = config.DATABASE_URI
if 'mysql' not in mysql_uri.lower():
    logging.error('DATABASE_URI is not MySQL. Aborting.')
    sys.exit(1)

engine = create_engine(mysql_uri, future=True)

with engine.connect() as conn:
    logging.info(f'Connected to MySQL: {mysql_uri}')
    # Check column exists
    res = conn.execute(text("SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'detections' AND COLUMN_NAME = 'training_result_id'"))
    row = res.fetchone()
    if row:
        logging.info('Column detections.training_result_id already exists. Nothing to do.')
    else:
        logging.info('Column detections.training_result_id missing — adding column...')
        try:
            # Add column as integer NULL and then optionally add FK (wrapped in try)
            conn.execute(text('ALTER TABLE detections ADD COLUMN training_result_id INT NULL'))
            logging.info('✓ Column added')
            # try to add foreign key if training_results table exists and key not exists
            fk_check = conn.execute(text("SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'detections' AND CONSTRAINT_TYPE = 'FOREIGN KEY'"))
            fk_count = fk_check.scalar()
            try:
                conn.execute(text('ALTER TABLE detections ADD CONSTRAINT fk_detections_training FOREIGN KEY (training_result_id) REFERENCES training_results(id)'))
                logging.info('✓ Foreign key fk_detections_training added')
            except Exception as e:
                logging.warning(f'Could not add foreign key (ignored): {e}')
        except Exception as e:
            logging.error(f'Failed to add column: {e}')
            sys.exit(1)

logging.info('Done.')

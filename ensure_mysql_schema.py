#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compare SQLAlchemy model columns with MySQL information_schema and add any missing columns.
Safe: adds columns with nullable allowed; attempts to add FK constraints but ignores failures.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config import config
from sqlalchemy import create_engine, text
from sqlalchemy.sql.sqltypes import Integer, String, DateTime, Float, Boolean, Text, Date
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Models to check
from app.database_unified import Detection, Alert, TrainingResult, Worker, IoTSensor, SystemLog, NotificationRecipient, NotificationHistory, NotificationConfig, ReportSchedule
models = [Detection, Alert, TrainingResult, Worker, IoTSensor, SystemLog, NotificationRecipient, NotificationHistory, NotificationConfig, ReportSchedule]

mysql_uri = config.DATABASE_URI
if 'mysql' not in mysql_uri.lower():
    logging.error('DATABASE_URI is not a MySQL URI; aborting.')
    sys.exit(1)

engine = create_engine(mysql_uri, future=True)

def col_type_to_mysql(col):
    t = col.type
    if isinstance(t, Integer):
        return 'INT'
    if isinstance(t, Float):
        return 'FLOAT'
    if isinstance(t, Boolean):
        return 'TINYINT(1)'
    if isinstance(t, DateTime):
        return 'DATETIME'
    if isinstance(t, Date):
        return 'DATE'
    if isinstance(t, Text):
        return 'TEXT'
    if isinstance(t, String):
        length = getattr(t, 'length', None)
        if length:
            return f'VARCHAR({length})'
        return 'TEXT'
    # fallback
    return 'TEXT'

with engine.connect() as conn:
    logging.info(f'Connected to MySQL: {mysql_uri}')
    for model in models:
        table = model.__tablename__
        logging.info(f'Checking table `{table}`')
        # fetch existing columns
        res = conn.execute(text("SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :table"), {'table': table})
        existing = {row[0] for row in res.fetchall()}
        to_add = []
        for col in model.__table__.columns:
            name = col.name
            if name not in existing:
                to_add.append(col)
        if not to_add:
            logging.info(f'  All columns present for `{table}`')
            continue
        logging.info(f'  Missing columns for `{table}`: {", ".join([c.name for c in to_add])}')
        for col in to_add:
            name = col.name
            col_sql_type = col_type_to_mysql(col)
            nullable = 'NULL' if col.nullable else 'NOT NULL'
            default_clause = ''
            # add the column
            sql = f'ALTER TABLE `{table}` ADD COLUMN `{name}` {col_sql_type} {nullable} {default_clause}'
            try:
                conn.execute(text(sql))
                logging.info(f'    ✓ Added column `{name}` ({col_sql_type})')
                # attempt to add FK if column has foreign keys
                if col.foreign_keys:
                    for fk in col.foreign_keys:
                        ref = fk.target_fullname  # like training_results.id
                        # build FK name
                        fk_name = f'fk_{table}_{name}'
                        try:
                            fk_sql = f'ALTER TABLE `{table}` ADD CONSTRAINT `{fk_name}` FOREIGN KEY (`{name}`) REFERENCES {ref}'
                            conn.execute(text(fk_sql))
                            logging.info(f'      ✓ Added FK {fk_name} -> {ref}')
                        except Exception as e:
                            logging.warning(f'      Could not add FK for {name}: {e}')
            except Exception as e:
                logging.error(f'    ❌ Failed to add column `{name}`: {e}')

logging.info('Schema ensure complete.')

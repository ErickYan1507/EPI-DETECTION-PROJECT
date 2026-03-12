#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ensure foreign key constraints are present and correctly formed in MySQL.
- Scans SQLAlchemy models for ForeignKey definitions
- Verifies parent/child table engines (prefers InnoDB)
- Verifies charset/collation compatibility (warns if mismatch)
- Ensures an index exists on referenced column (creates if missing)
- Adds FK constraint with safe options
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config import config
from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Import models
from app import database_unified as dbm
models = [
    dbm.Detection,
    dbm.Alert,
    dbm.TrainingResult,
    dbm.Worker,
    dbm.IoTSensor,
    dbm.SystemLog,
    dbm.NotificationRecipient,
    dbm.NotificationHistory,
    dbm.NotificationConfig,
    dbm.ReportSchedule
]

mysql_uri = config.DATABASE_URI
if 'mysql' not in mysql_uri.lower():
    logging.error('DATABASE_URI is not MySQL; aborting.')
    sys.exit(1)

engine = create_engine(mysql_uri, future=True)

summary = {'added_fks': [], 'skipped': [], 'warnings': []}

with engine.connect() as conn:
    logging.info(f'Connected to MySQL: {mysql_uri}')

    for model in models:
        table = model.__tablename__
        for col in model.__table__.columns:
            if not col.foreign_keys:
                continue
            child_col = col.name
            for fk in col.foreign_keys:
                target = fk.target_fullname  # e.g. training_results.id
                if '.' in target:
                    parent_table, parent_col = target.split('.')
                else:
                    logging.warning(f'Unexpected FK target format: {target}')
                    summary['skipped'].append((table, child_col, target))
                    continue

                logging.info(f'Processing FK: {table}.{child_col} -> {parent_table}.{parent_col}')

                # 1) ensure both tables exist
                r = conn.execute(text("SELECT TABLE_NAME, ENGINE, TABLE_COLLATION FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :t"), {'t': table})
                child_info = r.fetchone()
                r = conn.execute(text("SELECT TABLE_NAME, ENGINE, TABLE_COLLATION FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :t"), {'t': parent_table})
                parent_info = r.fetchone()

                if not child_info or not parent_info:
                    logging.warning(f'  One of tables missing: child={child_info}, parent={parent_info}. Skipping FK.')
                    summary['skipped'].append((table, child_col, target))
                    continue

                child_engine = child_info[1]
                parent_engine = parent_info[1]
                child_coll = child_info[2]
                parent_coll = parent_info[2]

                # 2) ensure engines are InnoDB
                if child_engine and child_engine.upper() != 'INNODB':
                    try:
                        logging.info(f'  Converting engine {table} -> InnoDB (was {child_engine})')
                        conn.execute(text(f"ALTER TABLE `{table}` ENGINE=InnoDB"))
                    except Exception as e:
                        logging.warning(f'  Could not convert engine for {table}: {e}')
                        summary['warnings'].append(str(e))
                if parent_engine and parent_engine.upper() != 'INNODB':
                    try:
                        logging.info(f'  Converting engine {parent_table} -> InnoDB (was {parent_engine})')
                        conn.execute(text(f"ALTER TABLE `{parent_table}` ENGINE=InnoDB"))
                    except Exception as e:
                        logging.warning(f'  Could not convert engine for {parent_table}: {e}')
                        summary['warnings'].append(str(e))

                # 3) check charset/collation compatibility (warn only)
                if child_coll and parent_coll and child_coll != parent_coll:
                    logging.warning(f'  Collation mismatch: {table}={child_coll} vs {parent_table}={parent_coll}. FK may fail. Consider converting.')
                    summary['warnings'].append(f'Collation mismatch {table} vs {parent_table}')

                # 4) ensure referenced column has an index on parent
                r = conn.execute(text("SELECT COUNT(*) FROM information_schema.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :t AND COLUMN_NAME = :c"), {'t': parent_table, 'c': parent_col})
                idx_count = r.scalar()
                if idx_count == 0:
                    idx_name = f'idx_{parent_table}_{parent_col}'
                    try:
                        logging.info(f'  Creating index `{idx_name}` on {parent_table}({parent_col})')
                        conn.execute(text(f"ALTER TABLE `{parent_table}` ADD INDEX `{idx_name}` (`{parent_col}`)"))
                    except Exception as e:
                        logging.warning(f'  Could not create index on {parent_table}.{parent_col}: {e}')
                        summary['warnings'].append(str(e))

                # 5) ensure index exists on child side for FK column (MySQL doesn't require but good)
                r = conn.execute(text("SELECT COUNT(*) FROM information_schema.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :t AND COLUMN_NAME = :c"), {'t': table, 'c': child_col})
                child_idx = r.scalar()
                if child_idx == 0:
                    cidx_name = f'idx_{table}_{child_col}'
                    try:
                        logging.info(f'  Creating index `{cidx_name}` on {table}({child_col})')
                        conn.execute(text(f"ALTER TABLE `{table}` ADD INDEX `{cidx_name}` (`{child_col}`)"))
                    except Exception as e:
                        logging.warning(f'  Could not create index on {table}.{child_col}: {e}')
                        summary['warnings'].append(str(e))

                # 6) check if FK already exists
                r = conn.execute(text("SELECT CONSTRAINT_NAME FROM information_schema.REFERENTIAL_CONSTRAINTS WHERE CONSTRAINT_SCHEMA = DATABASE() AND TABLE_NAME = :t"), {'t': table})
                existing_fks = {row[0] for row in r.fetchall()} if r is not None else set()
                fk_name = f'fk_{table}_{child_col}'
                if fk_name in existing_fks:
                    logging.info(f'  FK {fk_name} already exists, skipping')
                    continue

                # 7) add FK
                try:
                    sql = f"ALTER TABLE `{table}` ADD CONSTRAINT `{fk_name}` FOREIGN KEY (`{child_col}`) REFERENCES `{parent_table}`(`{parent_col}`) ON DELETE SET NULL ON UPDATE CASCADE"
                    logging.info(f'  Adding FK {fk_name}...')
                    conn.execute(text(sql))
                    logging.info(f'    ✓ FK {fk_name} added')
                    summary['added_fks'].append((table, child_col, parent_table, parent_col, fk_name))
                except Exception as e:
                    logging.warning(f'    Could not add FK {fk_name}: {e}')
                    summary['warnings'].append(str(e))

    logging.info('Foreign key ensure complete.')

# Print summary
logging.info('Summary:')
logging.info(f"  Added FKs: {len(summary['added_fks'])}")
for f in summary['added_fks']:
    logging.info(f'    - {f[4]}: {f[0]}.{f[1]} -> {f[2]}.{f[3]}')
if summary['warnings']:
    logging.info('  Warnings:')
    for w in summary['warnings']:
        logging.info(f'    - {w}')

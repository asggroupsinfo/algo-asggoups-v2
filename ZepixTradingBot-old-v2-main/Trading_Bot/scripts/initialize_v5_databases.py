#!/usr/bin/env python3
"""
V5 Database Initialization Script

Creates and initializes the 3-database V5 architecture:
1. zepix_combined_v3.db - V3 Combined Logic database
2. zepix_price_action.db - V6 Price Action database (shared by all timeframes)
3. zepix_bot.db - Central System database

Usage:
    python scripts/initialize_v5_databases.py

Version: 1.0.0
Date: 2026-01-18
"""

import os
import sys
import sqlite3
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_CONFIG = {
    'v3_combined': {
        'db_file': 'data/zepix_combined_v3.db',
        'schema_file': 'data/schemas/combined_v3_schema.sql',
        'description': 'V3 Combined Logic Database'
    },
    'v6_price_action': {
        'db_file': 'data/zepix_price_action.db',
        'schema_file': 'data/schemas/price_action_v6_schema.sql',
        'description': 'V6 Price Action Database'
    },
    'central_system': {
        'db_file': 'data/zepix_bot.db',
        'schema_file': 'data/schemas/central_system_schema.sql',
        'description': 'Central System Database'
    }
}


def get_base_path() -> Path:
    """Get the base path for the Trading_Bot directory"""
    script_path = Path(__file__).resolve()
    # scripts/initialize_v5_databases.py -> Trading_Bot/
    return script_path.parent.parent


def ensure_directories(base_path: Path) -> bool:
    """Ensure required directories exist"""
    try:
        data_dir = base_path / 'data'
        schemas_dir = base_path / 'data' / 'schemas'
        
        data_dir.mkdir(parents=True, exist_ok=True)
        schemas_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Directories verified: {data_dir}")
        return True
    except Exception as e:
        logger.error(f"Failed to create directories: {e}")
        return False


def verify_schema_files(base_path: Path) -> bool:
    """Verify all schema files exist"""
    all_exist = True
    
    for db_name, config in DATABASE_CONFIG.items():
        schema_path = base_path / config['schema_file']
        if not schema_path.exists():
            logger.error(f"Schema file missing: {schema_path}")
            all_exist = False
        else:
            logger.info(f"Schema file found: {schema_path}")
    
    return all_exist


def create_database(base_path: Path, db_name: str, config: dict) -> dict:
    """
    Create a single database and apply its schema.
    
    Returns:
        dict with status, tables created, and any errors
    """
    result = {
        'db_name': db_name,
        'description': config['description'],
        'db_file': config['db_file'],
        'success': False,
        'tables': [],
        'error': None
    }
    
    db_path = base_path / config['db_file']
    schema_path = base_path / config['schema_file']
    
    try:
        # Read schema file
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Create database and apply schema
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Execute schema
        cursor.executescript(schema_sql)
        conn.commit()
        
        # Get list of tables created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        result['success'] = True
        result['tables'] = tables
        result['size_bytes'] = db_path.stat().st_size
        
        logger.info(f"Created {db_name}: {len(tables)} tables")
        
    except Exception as e:
        result['error'] = str(e)
        logger.error(f"Failed to create {db_name}: {e}")
    
    return result


def verify_database(base_path: Path, db_name: str, config: dict) -> dict:
    """
    Verify a database exists and has the expected tables.
    
    Returns:
        dict with verification status
    """
    result = {
        'db_name': db_name,
        'exists': False,
        'tables': [],
        'queryable': False,
        'error': None
    }
    
    db_path = base_path / config['db_file']
    
    try:
        if not db_path.exists():
            result['error'] = 'Database file does not exist'
            return result
        
        result['exists'] = True
        result['size_bytes'] = db_path.stat().st_size
        
        # Try to connect and query
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        result['tables'] = tables
        result['queryable'] = True
        
    except Exception as e:
        result['error'] = str(e)
    
    return result


def initialize_all_databases() -> dict:
    """
    Initialize all V5 databases.
    
    Returns:
        dict with overall status and per-database results
    """
    base_path = get_base_path()
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'base_path': str(base_path),
        'success': True,
        'databases': {}
    }
    
    logger.info("=" * 60)
    logger.info("V5 DATABASE INITIALIZATION")
    logger.info("=" * 60)
    logger.info(f"Base path: {base_path}")
    
    # Step 1: Ensure directories exist
    if not ensure_directories(base_path):
        results['success'] = False
        results['error'] = 'Failed to create directories'
        return results
    
    # Step 2: Verify schema files exist
    if not verify_schema_files(base_path):
        results['success'] = False
        results['error'] = 'Missing schema files'
        return results
    
    # Step 3: Create each database
    logger.info("-" * 60)
    logger.info("Creating databases...")
    logger.info("-" * 60)
    
    for db_name, config in DATABASE_CONFIG.items():
        db_result = create_database(base_path, db_name, config)
        results['databases'][db_name] = db_result
        
        if not db_result['success']:
            results['success'] = False
    
    # Step 4: Verify all databases
    logger.info("-" * 60)
    logger.info("Verifying databases...")
    logger.info("-" * 60)
    
    for db_name, config in DATABASE_CONFIG.items():
        verify_result = verify_database(base_path, db_name, config)
        results['databases'][db_name]['verification'] = verify_result
        
        if not verify_result['queryable']:
            results['success'] = False
            logger.error(f"Verification failed for {db_name}")
        else:
            logger.info(f"Verified {db_name}: {len(verify_result['tables'])} tables")
    
    return results


def print_summary(results: dict):
    """Print a summary of the initialization results"""
    print("\n" + "=" * 60)
    print("V5 DATABASE INITIALIZATION SUMMARY")
    print("=" * 60)
    print(f"Timestamp: {results['timestamp']}")
    print(f"Base Path: {results['base_path']}")
    print(f"Overall Status: {'SUCCESS' if results['success'] else 'FAILED'}")
    print("-" * 60)
    
    for db_name, db_result in results['databases'].items():
        status = 'OK' if db_result['success'] else 'FAILED'
        tables = len(db_result.get('tables', []))
        size = db_result.get('size_bytes', 0)
        
        print(f"\n{db_result['description']}:")
        print(f"  File: {db_result['db_file']}")
        print(f"  Status: {status}")
        print(f"  Tables: {tables}")
        print(f"  Size: {size} bytes")
        
        if db_result.get('tables'):
            print(f"  Table List: {', '.join(db_result['tables'])}")
        
        if db_result.get('error'):
            print(f"  Error: {db_result['error']}")
    
    print("\n" + "=" * 60)
    
    if results['success']:
        print("ALL DATABASES INITIALIZED SUCCESSFULLY")
    else:
        print("INITIALIZATION FAILED - Check errors above")
    
    print("=" * 60)


def main():
    """Main entry point"""
    try:
        results = initialize_all_databases()
        print_summary(results)
        
        # Exit with appropriate code
        sys.exit(0 if results['success'] else 1)
        
    except Exception as e:
        logger.error(f"Initialization failed with exception: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

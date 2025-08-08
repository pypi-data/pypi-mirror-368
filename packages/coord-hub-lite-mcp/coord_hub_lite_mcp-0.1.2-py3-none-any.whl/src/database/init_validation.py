"""
Database initialization validation tools.
Provides functions to validate database schema, migration state, and diagnose issues.
"""
import os
import sqlite3
from typing import Dict, List, Any, Tuple
from pathlib import Path

from sqlalchemy import text, inspect
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import engine, get_async_session


# Expected tables that should exist after migration
EXPECTED_TABLES = [
    'agents', 'tasks', 'task_dependencies', 'task_events',
    'plans', 'agent_sessions', 'audit_log', 'system_metrics',
    'alembic_version'
]


async def validate_database_schema() -> Dict[str, Any]:
    """
    Validate the database schema against expected structure.
    
    Returns:
        Dict containing validation results with:
        - valid: bool indicating if schema is valid
        - tables: list of existing tables
        - migration_state: dict with migration info
        - issues: list of issues found
    """
    result = {
        'valid': True,
        'tables': [],
        'migration_state': {},
        'issues': []
    }
    
    try:
        # Use synchronous SQLite connection for validation
        db_path = _get_database_path()
        if not os.path.exists(db_path):
            result['valid'] = False
            result['issues'].append("Database file does not exist")
            return result
            
        # Connect with sqlite3 directly to avoid async issues
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Get list of existing tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            existing_tables = [row[0] for row in cursor.fetchall()]
            result['tables'] = existing_tables
            
            # Check migration state
            migration_state = await check_migration_state()
            result['migration_state'] = migration_state
            
            # Validate all expected tables exist
            missing_tables = set(EXPECTED_TABLES) - set(existing_tables)
            if missing_tables:
                result['valid'] = False
                result['issues'].append(f"Missing tables: {list(missing_tables)}")
            
            # Check if migration is current
            if not migration_state.get('is_current', False):
                result['valid'] = False
                result['issues'].append("Database migration is not current")
                
    except Exception as e:
        result['valid'] = False
        result['issues'].append(f"Database connection error: {str(e)}")
    
    return result


async def check_migration_state() -> Dict[str, Any]:
    """
    Check the current migration state using Alembic version table.
    
    Returns:
        Dict with migration state information:
        - current_version: current migration version
        - target_version: target migration version 
        - is_current: boolean indicating if migration is current
    """
    result = {
        'current_version': None,
        'target_version': '001',  # Our current migration
        'is_current': False
    }
    
    try:
        db_path = _get_database_path()
        if not os.path.exists(db_path):
            return result
            
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Check if alembic_version table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version';")
            if not cursor.fetchone():
                result['current_version'] = None
                result['is_current'] = False
                return result
            
            # Get current version from alembic_version table
            cursor.execute("SELECT version_num FROM alembic_version")
            row = cursor.fetchone()
            
            if row:
                result['current_version'] = row[0]
                result['is_current'] = (row[0] == result['target_version'])
            else:
                result['current_version'] = None
                result['is_current'] = False
                
    except Exception as e:
        result['error'] = str(e)
    
    return result


async def verify_table_creation() -> Dict[str, Any]:
    """
    Verify that all required tables have been created.
    
    Returns:
        Dict containing:
        - existing_tables: list of tables that exist
        - missing_tables: list of tables that are missing
        - extra_tables: list of unexpected tables
    """
    result = {
        'existing_tables': [],
        'missing_tables': [],
        'extra_tables': []
    }
    
    try:
        db_path = _get_database_path()
        if not os.path.exists(db_path):
            result['missing_tables'] = EXPECTED_TABLES
            return result
            
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            existing_tables = set([row[0] for row in cursor.fetchall()])
            expected_tables = set(EXPECTED_TABLES)
            
            result['existing_tables'] = list(existing_tables)
            result['missing_tables'] = list(expected_tables - existing_tables)
            result['extra_tables'] = list(existing_tables - expected_tables)
            
    except Exception as e:
        result['error'] = str(e)
    
    return result


async def diagnose_database_issues() -> Dict[str, Any]:
    """
    Comprehensive diagnosis of database setup issues.
    
    Returns:
        Dict with diagnostic information and recommendations
    """
    diagnosis = {
        'database_file_exists': False,
        'connection_successful': False,
        'schema_issues': [],
        'migration_issues': [],
        'recommendations': []
    }
    
    # Check if database file exists
    db_path = _get_database_path()
    diagnosis['database_file_exists'] = os.path.exists(db_path)
    
    if not diagnosis['database_file_exists']:
        diagnosis['recommendations'].append(
            "Database file does not exist. Run 'alembic upgrade head' to create it."
        )
        return diagnosis
    
    try:
        # Test database connection
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
            diagnosis['connection_successful'] = True
            
        # Check schema
        schema_validation = await validate_database_schema()
        if not schema_validation['valid']:
            diagnosis['schema_issues'] = schema_validation['issues']
            
        # Check migrations
        migration_state = await check_migration_state()
        if not migration_state['is_current']:
            diagnosis['migration_issues'].append(
                f"Migration not current: {migration_state['current_version']} -> {migration_state['target_version']}"
            )
            
        # Generate recommendations based on issues found
        if diagnosis['schema_issues']:
            diagnosis['recommendations'].append(
                "Schema issues detected. Check table creation and run migrations."
            )
            
        if diagnosis['migration_issues']:
            diagnosis['recommendations'].append(
                "Run 'alembic upgrade head' to apply pending migrations."
            )
            
        if not diagnosis['schema_issues'] and not diagnosis['migration_issues']:
            diagnosis['recommendations'].append("Database appears to be properly configured.")
            
    except Exception as e:
        diagnosis['connection_successful'] = False
        diagnosis['schema_issues'].append(f"Connection error: {str(e)}")
        diagnosis['recommendations'].append(
            "Cannot connect to database. Check database configuration and permissions."
        )
    
    return diagnosis


def get_schema_status() -> Dict[str, Any]:
    """
    Get a comprehensive status of the database schema.
    This is a synchronous convenience function.
    
    Returns:
        Dict with schema status information
    """
    import asyncio
    
    # For synchronous usage, wrap async functions
    async def _get_status():
        validation = await validate_database_schema()
        table_check = await verify_table_creation()
        migration_check = await check_migration_state()
        
        return {
            'tables_exist': len(table_check['missing_tables']) == 0,
            'migration_current': migration_check['is_current'],
            'schema_valid': validation['valid'],
            'missing_tables': table_check['missing_tables'],
            'extra_tables': table_check['extra_tables'],
            'migration_version': migration_check['current_version'],
            'issues': validation['issues'],
            'recommendations': []
        }
    
    try:
        return asyncio.run(_get_status())
    except Exception as e:
        return {
            'tables_exist': False,
            'migration_current': False,
            'schema_valid': False,
            'missing_tables': EXPECTED_TABLES,
            'extra_tables': [],
            'migration_version': None,
            'issues': [f"Error getting schema status: {str(e)}"],
            'recommendations': ["Check database configuration and connectivity"]
        }


def _get_database_path() -> str:
    """Get the database file path from configuration."""
    database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///coord_hub_lite.db")
    
    if database_url.startswith("sqlite"):
        # Extract path from SQLite URL
        path_part = database_url.split("///")[-1]
        # Handle relative paths
        if not path_part.startswith("/"):
            path_part = os.path.join(os.getcwd(), path_part)
        return path_part
    
    # For non-SQLite databases, return empty (file check not applicable)
    return ""


# CLI-style main function for testing
async def main():
    """Main function for testing the validation tools."""
    print("🔍 Database Validation Tool")
    print("=" * 40)
    
    print("\n1. Checking schema validation...")
    schema_result = await validate_database_schema()
    print(f"   Valid: {schema_result['valid']}")
    print(f"   Tables: {len(schema_result['tables'])}")
    if schema_result['issues']:
        print(f"   Issues: {schema_result['issues']}")
    
    print("\n2. Checking migration state...")
    migration_result = await check_migration_state()
    print(f"   Current: {migration_result['current_version']}")
    print(f"   Target: {migration_result['target_version']}")
    print(f"   Is Current: {migration_result['is_current']}")
    
    print("\n3. Verifying table creation...")
    table_result = await verify_table_creation()
    print(f"   Existing: {len(table_result['existing_tables'])}")
    print(f"   Missing: {table_result['missing_tables']}")
    
    print("\n4. Running comprehensive diagnosis...")
    diagnosis = await diagnose_database_issues()
    print(f"   DB File Exists: {diagnosis['database_file_exists']}")
    print(f"   Connection OK: {diagnosis['connection_successful']}")
    if diagnosis['recommendations']:
        print("   Recommendations:")
        for rec in diagnosis['recommendations']:
            print(f"     - {rec}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
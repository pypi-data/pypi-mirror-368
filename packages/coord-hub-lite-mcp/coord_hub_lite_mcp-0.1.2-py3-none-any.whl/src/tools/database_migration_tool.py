#!/usr/bin/env python3
"""
Universal Database Migration Tool for Coord-Hub-Lite
This tool can be used by agents to migrate any coord-hub-lite database to the latest schema.
Handles schema detection, versioning, and incremental migrations.
"""

import sqlite3
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DatabaseMigrator:
    """Handles database schema migrations for coord-hub-lite"""
    
    def __init__(self, db_path: str = None):
        """Initialize migrator with database path"""
        if db_path is None:
            # Try to find database in standard locations
            possible_paths = [
                "coord_hub_lite.db",
                "data/coord_hub_lite.db",
                "../coord_hub_lite.db",
                "src/database/coord_hub_lite.db",
                os.path.expanduser("~/.coord-hub-lite/coord_hub_lite.db")
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    db_path = path
                    break
            else:
                db_path = "coord_hub_lite.db"
        
        self.db_path = db_path
        logger.info(f"Using database: {self.db_path}")
        
    def get_current_schema(self) -> Dict[str, List[str]]:
        """Get current database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        schema = {}
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            schema[table_name] = [col[1] for col in columns]
        
        conn.close()
        return schema
    
    def detect_schema_version(self) -> str:
        """Detect current schema version based on structure"""
        schema = self.get_current_schema()
        
        # Check for schema_version table
        if 'schema_version' in schema:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT version FROM schema_version ORDER BY id DESC LIMIT 1")
            result = cursor.fetchone()
            conn.close()
            if result:
                return result[0]
        
        # Detect version based on schema structure
        if 'tasks' not in schema:
            return "0.0.0"  # No schema
        
        tasks_columns = schema.get('tasks', [])
        
        # Check for various versions based on columns
        if 'created_by_agent_type' in tasks_columns and 'task_artifacts' in schema:
            return "2.0.0"  # Latest with artifacts and agent type
        elif 'requires_documentation' in tasks_columns:
            return "1.5.0"  # Has documentation support
        elif 'meta_data' in tasks_columns:
            return "1.2.0"  # Has metadata
        elif 'title' in tasks_columns:
            return "1.0.0"  # Basic schema with title
        else:
            return "0.5.0"  # Old schema with name instead of title
            
    def backup_database(self) -> str:
        """Create backup before migration"""
        backup_path = f"{self.db_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Copy database file
        with open(self.db_path, 'rb') as source:
            with open(backup_path, 'wb') as backup:
                backup.write(source.read())
        
        logger.info(f"Database backed up to: {backup_path}")
        return backup_path
    
    def apply_migration_v1_0_0(self, conn: sqlite3.Connection):
        """Migrate to v1.0.0 - Basic schema with title field"""
        cursor = conn.cursor()
        
        # Check if tasks table exists with old schema
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
        if cursor.fetchone():
            # Check if it has 'name' column instead of 'title'
            cursor.execute("PRAGMA table_info(tasks)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'name' in columns and 'title' not in columns:
                # Rename name to title
                cursor.execute("ALTER TABLE tasks RENAME COLUMN name TO title")
                logger.info("Renamed 'name' column to 'title' in tasks table")
    
    def apply_migration_v1_2_0(self, conn: sqlite3.Connection):
        """Migrate to v1.2.0 - Add metadata support"""
        cursor = conn.cursor()
        
        # Add meta_data column if missing
        cursor.execute("PRAGMA table_info(tasks)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'meta_data' not in columns:
            cursor.execute("ALTER TABLE tasks ADD COLUMN meta_data TEXT DEFAULT '{}'")
            logger.info("Added meta_data column to tasks table")
    
    def apply_migration_v1_5_0(self, conn: sqlite3.Connection):
        """Migrate to v1.5.0 - Add documentation support"""
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(tasks)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'requires_documentation' not in columns:
            cursor.execute("ALTER TABLE tasks ADD COLUMN requires_documentation INTEGER DEFAULT 0")
            logger.info("Added requires_documentation column")
        
        if 'documentation_paths' not in columns:
            cursor.execute("ALTER TABLE tasks ADD COLUMN documentation_paths TEXT DEFAULT '[]'")
            logger.info("Added documentation_paths column")
        
        if 'documentation_context' not in columns:
            cursor.execute("ALTER TABLE tasks ADD COLUMN documentation_context TEXT")
            logger.info("Added documentation_context column")
    
    def apply_migration_v2_0_0(self, conn: sqlite3.Connection):
        """Migrate to v2.0.0 - Add artifacts and agent type tracking"""
        cursor = conn.cursor()
        
        # Add created_by_agent_type to tasks
        cursor.execute("PRAGMA table_info(tasks)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'created_by_agent_type' not in columns:
            cursor.execute("ALTER TABLE tasks ADD COLUMN created_by_agent_type TEXT")
            logger.info("Added created_by_agent_type column to tasks")
        
        # Create task_artifacts table if it doesn't exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='task_artifacts'")
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE task_artifacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    artifact_type VARCHAR(50) NOT NULL,
                    content TEXT NOT NULL,
                    created_by VARCHAR(100),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                    CHECK (artifact_type IN ('tdd_red', 'tdd_green', 'review_feedback', 
                           'test_results', 'console_logs', 'completion_report', 'integration_test'))
                )
            """)
            cursor.execute("CREATE INDEX idx_artifact_task_type ON task_artifacts(task_id, artifact_type)")
            cursor.execute("CREATE INDEX idx_artifact_created_at ON task_artifacts(created_at)")
            logger.info("Created task_artifacts table")
        
        # Update tasks status constraints
        cursor.execute("""
            SELECT sql FROM sqlite_master 
            WHERE type='table' AND name='tasks' AND sql LIKE '%CHECK%status%'
        """)
        current_sql = cursor.fetchone()
        
        if current_sql and 'needs_review' not in str(current_sql):
            # Need to recreate table with new constraints
            logger.info("Recreating tasks table with updated status constraints...")
            
            # Create new table with updated schema
            cursor.execute("""
                CREATE TABLE tasks_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL,
                    status VARCHAR(50) DEFAULT 'pending',
                    priority VARCHAR(20) DEFAULT 'medium',
                    created_by_agent_type VARCHAR(50),
                    agent_id VARCHAR(100),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    started_at DATETIME,
                    completed_at DATETIME,
                    requires_documentation INTEGER DEFAULT 0,
                    documentation_paths TEXT DEFAULT '[]',
                    documentation_context TEXT,
                    meta_data TEXT DEFAULT '{}',
                    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE SET NULL,
                    CHECK (status IN ('pending', 'assigned', 'in_progress', 'needs_review', 
                           'approved', 'needs_fixes', 'completed', 'failed', 'cancelled', 
                           'merged', 'audited', 'ready_for_release')),
                    CHECK (priority IN ('critical', 'high', 'medium', 'low'))
                )
            """)
            
            # Copy data
            cursor.execute("""
                INSERT INTO tasks_new 
                SELECT * FROM tasks
            """)
            
            # Drop old table and rename new
            cursor.execute("DROP TABLE tasks")
            cursor.execute("ALTER TABLE tasks_new RENAME TO tasks")
            
            # Recreate indexes
            cursor.execute("CREATE INDEX idx_task_status ON tasks(status)")
            cursor.execute("CREATE INDEX idx_task_created_at ON tasks(created_at)")
            cursor.execute("CREATE INDEX idx_task_priority_status ON tasks(priority, status)")
            cursor.execute("CREATE INDEX idx_tasks_agent_id ON tasks(agent_id)")
            
            logger.info("Tasks table recreated with new constraints")
    
    def create_missing_tables(self, conn: sqlite3.Connection):
        """Create any missing tables with latest schema"""
        cursor = conn.cursor()
        
        # Create schema_version table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version VARCHAR(20) NOT NULL,
                applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                description TEXT
            )
        """)
        
        # Create agents table if missing
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id VARCHAR(100) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                type VARCHAR(50) NOT NULL,
                status VARCHAR(50) DEFAULT 'inactive',
                capabilities TEXT DEFAULT '{}',
                meta_data TEXT DEFAULT '{}',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_heartbeat DATETIME,
                CHECK (type IN ('executor', 'reviewer', 'tester', 'architect', 'data_reviewer')),
                CHECK (status IN ('active', 'inactive', 'busy', 'error'))
            )
        """)
        
        # Create other missing tables...
        tables_sql = {
            'task_events': """
                CREATE TABLE IF NOT EXISTS task_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    event_type VARCHAR(50) NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    actor VARCHAR(100) NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    meta_data TEXT DEFAULT '{}',
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
                )
            """,
            'plans': """
                CREATE TABLE IF NOT EXISTS plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(255) NOT NULL,
                    version INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    status VARCHAR(50) DEFAULT 'draft',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    meta_data TEXT DEFAULT '{}',
                    UNIQUE(name, version),
                    CHECK (status IN ('draft', 'active', 'archived'))
                )
            """,
            'agent_sessions': """
                CREATE TABLE IF NOT EXISTS agent_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id VARCHAR(100) NOT NULL,
                    started_at DATETIME NOT NULL,
                    ended_at DATETIME,
                    last_heartbeat DATETIME NOT NULL,
                    status VARCHAR(50) DEFAULT 'active',
                    meta_data TEXT DEFAULT '{}',
                    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE,
                    CHECK (status IN ('active', 'completed', 'failed', 'timeout'))
                )
            """,
            'audit_log': """
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity_type VARCHAR(50) NOT NULL,
                    entity_id VARCHAR(100) NOT NULL,
                    action VARCHAR(50) NOT NULL,
                    actor VARCHAR(100) NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    changes TEXT DEFAULT '{}',
                    meta_data TEXT DEFAULT '{}'
                )
            """,
            'system_metrics': """
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name VARCHAR(100) NOT NULL,
                    metric_value REAL NOT NULL,
                    metric_type VARCHAR(50) NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    tags TEXT DEFAULT '{}',
                    meta_data TEXT DEFAULT '{}',
                    CHECK (metric_type IN ('gauge', 'counter', 'histogram', 'timer'))
                )
            """
        }
        
        for table_name, sql in tables_sql.items():
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if not cursor.fetchone():
                cursor.execute(sql)
                logger.info(f"Created {table_name} table")
        
        # Create task_dependencies if missing
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='task_dependencies'")
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE task_dependencies (
                    dependent_task_id INTEGER NOT NULL,
                    dependency_task_id INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (dependent_task_id, dependency_task_id),
                    FOREIGN KEY (dependent_task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                    FOREIGN KEY (dependency_task_id) REFERENCES tasks(id) ON DELETE CASCADE
                )
            """)
            cursor.execute("CREATE INDEX idx_task_deps_dependent ON task_dependencies(dependent_task_id)")
            cursor.execute("CREATE INDEX idx_task_deps_dependency ON task_dependencies(dependency_task_id)")
            logger.info("Created task_dependencies table")
    
    def migrate(self, target_version: str = "2.0.0") -> bool:
        """Run migration to target version"""
        try:
            # Backup first
            backup_path = self.backup_database()
            
            # Get current version
            current_version = self.detect_schema_version()
            logger.info(f"Current schema version: {current_version}")
            
            if current_version >= target_version:
                logger.info(f"Database already at version {current_version}, no migration needed")
                return True
            
            # Connect to database
            conn = sqlite3.connect(self.db_path)
            
            try:
                # Apply migrations in order
                migrations = [
                    ("1.0.0", self.apply_migration_v1_0_0),
                    ("1.2.0", self.apply_migration_v1_2_0),
                    ("1.5.0", self.apply_migration_v1_5_0),
                    ("2.0.0", self.apply_migration_v2_0_0),
                ]
                
                for version, migration_func in migrations:
                    if current_version < version <= target_version:
                        logger.info(f"Applying migration to v{version}...")
                        migration_func(conn)
                        
                        # Record migration
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO schema_version (version, description)
                            VALUES (?, ?)
                        """, (version, f"Migration to v{version}"))
                        conn.commit()
                
                # Create any missing tables
                self.create_missing_tables(conn)
                conn.commit()
                
                logger.info(f"Successfully migrated to v{target_version}")
                return True
                
            except Exception as e:
                logger.error(f"Migration failed: {e}")
                conn.rollback()
                
                # Restore from backup
                logger.info(f"Restoring from backup: {backup_path}")
                with open(backup_path, 'rb') as backup:
                    with open(self.db_path, 'wb') as db:
                        db.write(backup.read())
                return False
                
            finally:
                conn.close()
                
        except Exception as e:
            logger.error(f"Migration error: {e}")
            return False
    
    def validate_schema(self) -> Tuple[bool, List[str]]:
        """Validate current schema against expected"""
        issues = []
        schema = self.get_current_schema()
        
        # Expected tables
        expected_tables = [
            'tasks', 'agents', 'task_events', 'plans', 'agent_sessions',
            'audit_log', 'system_metrics', 'task_artifacts', 'task_dependencies'
        ]
        
        for table in expected_tables:
            if table not in schema:
                issues.append(f"Missing table: {table}")
        
        # Check critical columns in tasks table
        if 'tasks' in schema:
            required_columns = [
                'id', 'title', 'description', 'status', 'priority',
                'created_by_agent_type', 'agent_id', 'meta_data'
            ]
            tasks_columns = schema['tasks']
            for col in required_columns:
                if col not in tasks_columns:
                    issues.append(f"Missing column in tasks: {col}")
        
        return len(issues) == 0, issues


def main():
    """Main function for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Coord-Hub-Lite Database Migration Tool')
    parser.add_argument('--db-path', help='Path to database file')
    parser.add_argument('--check', action='store_true', help='Check current schema version')
    parser.add_argument('--validate', action='store_true', help='Validate schema')
    parser.add_argument('--migrate', action='store_true', help='Run migration to latest version')
    parser.add_argument('--target-version', default='2.0.0', help='Target version for migration')
    
    args = parser.parse_args()
    
    migrator = DatabaseMigrator(args.db_path)
    
    if args.check:
        version = migrator.detect_schema_version()
        print(f"Current schema version: {version}")
        schema = migrator.get_current_schema()
        print(f"Tables: {list(schema.keys())}")
        
    elif args.validate:
        valid, issues = migrator.validate_schema()
        if valid:
            print("✅ Schema validation passed")
        else:
            print("❌ Schema validation failed:")
            for issue in issues:
                print(f"  - {issue}")
    
    elif args.migrate:
        success = migrator.migrate(args.target_version)
        if success:
            print(f"✅ Migration to v{args.target_version} completed successfully")
        else:
            print("❌ Migration failed, database restored from backup")
            sys.exit(1)
    
    else:
        # Default action: check and migrate if needed
        version = migrator.detect_schema_version()
        print(f"Current version: {version}")
        
        if version < "2.0.0":
            print("Migration needed. Starting migration...")
            success = migrator.migrate()
            if success:
                print("✅ Migration completed successfully")
            else:
                print("❌ Migration failed")
                sys.exit(1)
        else:
            print("✅ Database is up to date")


if __name__ == "__main__":
    main()
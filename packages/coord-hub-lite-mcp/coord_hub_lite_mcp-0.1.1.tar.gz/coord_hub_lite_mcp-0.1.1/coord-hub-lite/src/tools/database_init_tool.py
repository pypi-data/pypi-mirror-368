#!/usr/bin/env python3
"""
Database Initialization Tool for Coord-Hub-Lite
Creates a fresh database with the latest schema for new installations.
This tool solves the common issue of database setup in new repositories.
"""

import sqlite3
import os
import sys
from pathlib import Path
from datetime import datetime
import logging
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DatabaseInitializer:
    """Creates and initializes a fresh coord-hub-lite database with latest schema."""
    
    LATEST_VERSION = "2.0.0"
    
    def __init__(self, db_path: str = None, force: bool = False):
        """
        Initialize the database creator.
        
        Args:
            db_path: Path where database should be created (defaults to ./coord_hub_lite.db)
            force: If True, overwrite existing database
        """
        if db_path is None:
            # Default to current directory
            db_path = "coord_hub_lite.db"
        
        self.db_path = Path(db_path).resolve()
        self.force = force
        logger.info(f"Database path: {self.db_path}")
    
    def check_existing(self) -> bool:
        """Check if database already exists."""
        return self.db_path.exists()
    
    def backup_existing(self) -> str:
        """Backup existing database if present."""
        if self.db_path.exists():
            backup_path = f"{self.db_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            logger.info(f"Backing up existing database to: {backup_path}")
            
            with open(self.db_path, 'rb') as source:
                with open(backup_path, 'wb') as backup:
                    backup.write(source.read())
            
            return backup_path
        return None
    
    def create_database(self) -> bool:
        """
        Create a fresh database with the latest schema.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check for existing database
            if self.check_existing() and not self.force:
                logger.warning(f"Database already exists at {self.db_path}")
                logger.warning("Use --force to overwrite or --backup to create backup first")
                return False
            
            # Backup if forcing overwrite
            if self.check_existing() and self.force:
                self.backup_existing()
                os.remove(self.db_path)
                logger.info("Removed existing database")
            
            # Create new database with proper permissions
            logger.info("Creating new database with latest schema...")
            conn = sqlite3.connect(str(self.db_path))
            
            try:
                cursor = conn.cursor()
                
                # Enable foreign keys
                cursor.execute("PRAGMA foreign_keys = ON")
                
                # Create schema_version table
                cursor.execute("""
                    CREATE TABLE schema_version (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        version VARCHAR(20) NOT NULL,
                        applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        description TEXT
                    )
                """)
                
                # Create agents table
                cursor.execute("""
                    CREATE TABLE agents (
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
                cursor.execute("CREATE INDEX idx_agent_type ON agents(type)")
                cursor.execute("CREATE INDEX idx_agent_status ON agents(status)")
                
                # Create tasks table with all quality gate statuses
                cursor.execute("""
                    CREATE TABLE tasks (
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
                cursor.execute("CREATE INDEX idx_task_status ON tasks(status)")
                cursor.execute("CREATE INDEX idx_task_created_at ON tasks(created_at)")
                cursor.execute("CREATE INDEX idx_task_priority_status ON tasks(priority, status)")
                cursor.execute("CREATE INDEX idx_tasks_agent_id ON tasks(agent_id)")
                
                # Create task_artifacts table for TDD artifacts
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
                
                # Create task_dependencies table
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
                
                # Create task_events table
                cursor.execute("""
                    CREATE TABLE task_events (
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
                """)
                cursor.execute("CREATE INDEX idx_task_event_type ON task_events(event_type)")
                cursor.execute("CREATE INDEX idx_task_event_timestamp_task ON task_events(task_id, timestamp)")
                
                # Create plans table
                cursor.execute("""
                    CREATE TABLE plans (
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
                """)
                cursor.execute("CREATE INDEX idx_plan_name ON plans(name)")
                cursor.execute("CREATE INDEX idx_plan_status ON plans(status)")
                
                # Create agent_sessions table
                cursor.execute("""
                    CREATE TABLE agent_sessions (
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
                """)
                cursor.execute("CREATE INDEX idx_session_status ON agent_sessions(status)")
                cursor.execute("CREATE INDEX idx_session_heartbeat ON agent_sessions(last_heartbeat)")
                
                # Create audit_log table
                cursor.execute("""
                    CREATE TABLE audit_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        entity_type VARCHAR(50) NOT NULL,
                        entity_id VARCHAR(100) NOT NULL,
                        action VARCHAR(50) NOT NULL,
                        actor VARCHAR(100) NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        changes TEXT DEFAULT '{}',
                        meta_data TEXT DEFAULT '{}'
                    )
                """)
                cursor.execute("CREATE INDEX idx_audit_entity ON audit_log(entity_type, entity_id)")
                cursor.execute("CREATE INDEX idx_audit_actor ON audit_log(actor)")
                cursor.execute("CREATE INDEX idx_audit_action ON audit_log(action)")
                cursor.execute("CREATE INDEX idx_audit_timestamp ON audit_log(timestamp)")
                
                # Create system_metrics table
                cursor.execute("""
                    CREATE TABLE system_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        metric_name VARCHAR(100) NOT NULL,
                        metric_value REAL NOT NULL,
                        metric_type VARCHAR(50) NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        tags TEXT DEFAULT '{}',
                        meta_data TEXT DEFAULT '{}',
                        CHECK (metric_type IN ('gauge', 'counter', 'histogram', 'timer'))
                    )
                """)
                cursor.execute("CREATE INDEX idx_metric_name_timestamp ON system_metrics(metric_name, timestamp)")
                cursor.execute("CREATE INDEX idx_metric_type ON system_metrics(metric_type)")
                
                # Insert schema version
                cursor.execute("""
                    INSERT INTO schema_version (version, description)
                    VALUES (?, ?)
                """, (self.LATEST_VERSION, f"Initial database creation with schema v{self.LATEST_VERSION}"))
                
                # Commit all changes
                conn.commit()
                
                # Set proper permissions (read/write for user and group)
                os.chmod(str(self.db_path), 0o664)
                
                logger.info(f"✅ Successfully created database at: {self.db_path}")
                logger.info(f"✅ Schema version: {self.LATEST_VERSION}")
                logger.info("✅ All tables created with quality gate enforcement")
                logger.info("✅ Database permissions set to 664 (rw-rw-r--)")
                
                return True
                
            except Exception as e:
                logger.error(f"Failed to create schema: {e}")
                conn.rollback()
                return False
                
            finally:
                conn.close()
                
        except Exception as e:
            logger.error(f"Failed to create database: {e}")
            return False
    
    def verify_database(self) -> dict:
        """
        Verify the created database is valid and complete.
        
        Returns:
            Dictionary with verification results
        """
        if not self.db_path.exists():
            return {"valid": False, "error": "Database does not exist"}
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Check all required tables exist
            required_tables = [
                'schema_version', 'agents', 'tasks', 'task_artifacts',
                'task_dependencies', 'task_events', 'plans', 
                'agent_sessions', 'audit_log', 'system_metrics'
            ]
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            missing_tables = set(required_tables) - set(existing_tables)
            
            if missing_tables:
                return {
                    "valid": False,
                    "error": f"Missing tables: {', '.join(missing_tables)}"
                }
            
            # Check schema version
            cursor.execute("SELECT version FROM schema_version ORDER BY id DESC LIMIT 1")
            version = cursor.fetchone()
            
            if not version:
                return {"valid": False, "error": "No schema version found"}
            
            # Check permissions
            stat = os.stat(str(self.db_path))
            permissions = oct(stat.st_mode)[-3:]
            
            conn.close()
            
            return {
                "valid": True,
                "path": str(self.db_path),
                "version": version[0],
                "tables": existing_tables,
                "permissions": permissions,
                "size": os.path.getsize(str(self.db_path))
            }
            
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def print_connection_info(self):
        """Print information needed to connect to the database."""
        print("\n" + "="*60)
        print("COORD-HUB-LITE DATABASE CREATED SUCCESSFULLY")
        print("="*60)
        print(f"Database Path: {self.db_path}")
        print(f"Schema Version: {self.LATEST_VERSION}")
        print("\nTo use this database with coord-hub-lite MCP server:")
        print("1. Update your MCP settings to point to this database")
        print("2. Or set environment variable:")
        print(f"   export COORD_HUB_DB_PATH={self.db_path}")
        print("\nFor Python scripts:")
        print(f"   db_path = '{self.db_path}'")
        print("\nThe database is ready for use with full quality gate enforcement!")
        print("="*60 + "\n")


def main():
    """Main function for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Initialize a fresh Coord-Hub-Lite database with latest schema',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create database in current directory
  python database_init_tool.py
  
  # Create database at specific path
  python database_init_tool.py --path /path/to/project/coord_hub.db
  
  # Force overwrite existing database
  python database_init_tool.py --force
  
  # Verify existing database
  python database_init_tool.py --verify --path existing.db
        """
    )
    
    parser.add_argument(
        '--path', '--db-path',
        help='Path where database should be created (default: ./coord_hub_lite.db)',
        default='coord_hub_lite.db'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force overwrite if database exists (creates backup first)'
    )
    
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verify database structure after creation'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Minimal output'
    )
    
    args = parser.parse_args()
    
    if args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    
    # Initialize the database creator
    initializer = DatabaseInitializer(
        db_path=args.path,
        force=args.force
    )
    
    # Check if just verifying
    if args.verify and initializer.check_existing():
        result = initializer.verify_database()
        if result['valid']:
            print(f"✅ Database is valid")
            print(f"   Version: {result['version']}")
            print(f"   Tables: {len(result['tables'])}")
            print(f"   Size: {result['size']} bytes")
            print(f"   Permissions: {result['permissions']}")
        else:
            print(f"❌ Database validation failed: {result['error']}")
            sys.exit(1)
    else:
        # Create the database
        success = initializer.create_database()
        
        if success:
            # Verify it was created correctly
            result = initializer.verify_database()
            if result['valid']:
                if not args.quiet:
                    initializer.print_connection_info()
                sys.exit(0)
            else:
                print(f"❌ Database creation succeeded but verification failed: {result['error']}")
                sys.exit(1)
        else:
            print("❌ Failed to create database")
            sys.exit(1)


if __name__ == "__main__":
    main()
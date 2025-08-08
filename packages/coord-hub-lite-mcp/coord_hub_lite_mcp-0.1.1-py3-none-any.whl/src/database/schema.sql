-- Coord-Hub-Lite Database Schema
-- SQLite-compatible DDL with support for PostgreSQL migration
-- 
-- This schema defines all tables, constraints, and indexes for the system.
-- Tables: tasks, agents, task_dependencies, task_events, plans, agent_sessions, audit_log, system_metrics

-- Enable foreign key support in SQLite
PRAGMA foreign_keys = ON;

-- ============================================================================
-- AGENTS TABLE
-- ============================================================================
-- Registry of all agents in the system (executors, reviewers, testers, etc.)
CREATE TABLE IF NOT EXISTS agents (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('executor', 'reviewer', 'tester', 'architect', 'data_reviewer')),
    status VARCHAR(50) NOT NULL DEFAULT 'inactive' CHECK (status IN ('active', 'inactive', 'busy', 'error')),
    capabilities JSON NOT NULL DEFAULT '{}',
    meta_data JSON NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_heartbeat TIMESTAMP
);

-- Indexes for agents
CREATE INDEX idx_agent_type ON agents(type);
CREATE INDEX idx_agent_status ON agents(status);
CREATE INDEX idx_agent_last_heartbeat ON agents(last_heartbeat);

-- ============================================================================
-- TASKS TABLE
-- ============================================================================
-- Core work items in the system
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending' 
        CHECK (status IN ('pending', 'assigned', 'in_progress', 'completed', 'failed', 'cancelled')),
    priority VARCHAR(20) NOT NULL DEFAULT 'medium' 
        CHECK (priority IN ('critical', 'high', 'medium', 'low')),
    agent_id VARCHAR(100) REFERENCES agents(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    meta_data JSON NOT NULL DEFAULT '{}'
);

-- Indexes for tasks
CREATE INDEX idx_task_status ON tasks(status);
CREATE INDEX idx_task_agent_id ON tasks(agent_id);
CREATE INDEX idx_task_created_at ON tasks(created_at);
CREATE INDEX idx_task_priority_status ON tasks(priority, status);

-- Trigger to update updated_at on row update (SQLite version)
CREATE TRIGGER update_tasks_updated_at 
AFTER UPDATE ON tasks
BEGIN
    UPDATE tasks SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ============================================================================
-- TASK_DEPENDENCIES TABLE
-- ============================================================================
-- Many-to-many relationship for task dependencies
CREATE TABLE IF NOT EXISTS task_dependencies (
    dependent_task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    dependency_task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (dependent_task_id, dependency_task_id)
);

-- Indexes for task dependencies
CREATE INDEX idx_task_deps_dependent ON task_dependencies(dependent_task_id);
CREATE INDEX idx_task_deps_dependency ON task_dependencies(dependency_task_id);

-- ============================================================================
-- TASK_EVENTS TABLE
-- ============================================================================
-- Audit trail for all task state changes
CREATE TABLE IF NOT EXISTS task_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    actor VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    meta_data JSON NOT NULL DEFAULT '{}'
);

-- Indexes for task events
CREATE INDEX idx_task_event_task_id ON task_events(task_id);
CREATE INDEX idx_task_event_type ON task_events(event_type);
CREATE INDEX idx_task_event_timestamp ON task_events(timestamp);
CREATE INDEX idx_task_event_timestamp_task ON task_events(task_id, timestamp);

-- ============================================================================
-- PLANS TABLE
-- ============================================================================
-- Versioned plan documents (PLAN.md, TASKLIST.md, etc.)
CREATE TABLE IF NOT EXISTS plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    version INTEGER NOT NULL,
    content TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'draft' 
        CHECK (status IN ('draft', 'active', 'archived')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    meta_data JSON NOT NULL DEFAULT '{}',
    UNIQUE(name, version)
);

-- Indexes for plans
CREATE INDEX idx_plan_name ON plans(name);
CREATE INDEX idx_plan_status ON plans(status);

-- Trigger to update updated_at on row update
CREATE TRIGGER update_plans_updated_at 
AFTER UPDATE ON plans
BEGIN
    UPDATE plans SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ============================================================================
-- AGENT_SESSIONS TABLE
-- ============================================================================
-- Track agent session lifecycles and heartbeats
CREATE TABLE IF NOT EXISTS agent_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id VARCHAR(100) NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP,
    last_heartbeat TIMESTAMP NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active' 
        CHECK (status IN ('active', 'completed', 'failed', 'timeout')),
    meta_data JSON NOT NULL DEFAULT '{}'
);

-- Indexes for agent sessions
CREATE INDEX idx_session_agent_id ON agent_sessions(agent_id);
CREATE INDEX idx_session_status ON agent_sessions(status);
CREATE INDEX idx_session_heartbeat ON agent_sessions(last_heartbeat);

-- ============================================================================
-- AUDIT_LOG TABLE
-- ============================================================================
-- Comprehensive audit logging for all entities
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    actor VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    changes JSON NOT NULL DEFAULT '{}',
    meta_data JSON NOT NULL DEFAULT '{}'
);

-- Indexes for audit log
CREATE INDEX idx_audit_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_actor ON audit_log(actor);
CREATE INDEX idx_audit_action ON audit_log(action);
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp);

-- ============================================================================
-- SYSTEM_METRICS TABLE
-- ============================================================================
-- Performance and system metrics tracking
CREATE TABLE IF NOT EXISTS system_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name VARCHAR(100) NOT NULL,
    metric_value REAL NOT NULL,
    metric_type VARCHAR(50) NOT NULL 
        CHECK (metric_type IN ('gauge', 'counter', 'histogram', 'timer')),
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tags JSON NOT NULL DEFAULT '{}',
    meta_data JSON NOT NULL DEFAULT '{}'
);

-- Indexes for system metrics
CREATE INDEX idx_metric_name ON system_metrics(metric_name);
CREATE INDEX idx_metric_name_timestamp ON system_metrics(metric_name, timestamp);
CREATE INDEX idx_metric_type ON system_metrics(metric_type);
CREATE INDEX idx_metric_timestamp ON system_metrics(timestamp);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View for active tasks with agent information
CREATE VIEW active_tasks_view AS
SELECT 
    t.id,
    t.title,
    t.description,
    t.status,
    t.priority,
    t.agent_id,
    a.name as agent_name,
    a.type as agent_type,
    t.created_at,
    t.updated_at,
    t.started_at
FROM tasks t
LEFT JOIN agents a ON t.agent_id = a.id
WHERE t.status NOT IN ('completed', 'cancelled');

-- View for agent workload
CREATE VIEW agent_workload_view AS
SELECT 
    a.id,
    a.name,
    a.type,
    a.status,
    COUNT(t.id) as active_tasks,
    MAX(t.priority = 'critical') as has_critical_tasks
FROM agents a
LEFT JOIN tasks t ON a.id = t.agent_id AND t.status IN ('assigned', 'in_progress')
GROUP BY a.id, a.name, a.type, a.status;

-- View for task completion metrics
CREATE VIEW task_completion_metrics_view AS
SELECT 
    DATE(completed_at) as completion_date,
    COUNT(*) as tasks_completed,
    AVG(CAST((julianday(completed_at) - julianday(created_at)) * 24 * 60 AS REAL)) as avg_completion_time_minutes,
    COUNT(DISTINCT agent_id) as unique_agents
FROM tasks
WHERE status = 'completed' AND completed_at IS NOT NULL
GROUP BY DATE(completed_at);

-- ============================================================================
-- INITIAL DATA (Optional)
-- ============================================================================

-- Insert system agent if needed
INSERT OR IGNORE INTO agents (id, name, type, status, capabilities) 
VALUES ('system', 'System Agent', 'architect', 'active', '{"system": true}');

-- ============================================================================
-- POSTGRESQL COMPATIBILITY NOTES
-- ============================================================================
-- When migrating to PostgreSQL, the following changes will be needed:
-- 1. Change AUTOINCREMENT to SERIAL for primary keys
-- 2. Change TIMESTAMP to TIMESTAMP WITH TIME ZONE
-- 3. Change JSON to JSONB for better performance
-- 4. Update trigger syntax to PostgreSQL format
-- 5. Change REAL to DOUBLE PRECISION
-- 6. Update datetime functions (julianday -> PostgreSQL equivalents)
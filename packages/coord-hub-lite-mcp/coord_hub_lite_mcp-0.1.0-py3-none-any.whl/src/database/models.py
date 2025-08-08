"""
SQLAlchemy models for Coord-Hub-Lite database.
Async-compatible models with proper relationships and constraints.
"""
from datetime import datetime
from typing import Optional, Dict, List, Any
from sqlalchemy import (
    Column, String, Integer, DateTime, JSON, ForeignKey, 
    CheckConstraint, Index, Table, Text, Float, UniqueConstraint
)
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from sqlalchemy.sql import func

class Base(DeclarativeBase):
    pass

# Association table for task dependencies (many-to-many)
task_dependencies = Table(
    'task_dependencies',
    Base.metadata,
    Column('dependent_task_id', Integer, ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True),
    Column('dependency_task_id', Integer, ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime, server_default=func.now(), nullable=False),
    Index('idx_task_deps_dependent', 'dependent_task_id'),
    Index('idx_task_deps_dependency', 'dependency_task_id')
)


class Task(Base):
    """Task model representing work items in the system."""
    __tablename__ = 'tasks'
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Core fields
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
        default='pending'
    )
    priority: Mapped[str] = mapped_column(
        String(20), 
        nullable=False,
        default='medium'
    )
    
    # Track which agent type created this task
    created_by_agent_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    
    # Agent assignment
    agent_id: Mapped[Optional[str]] = mapped_column(
        String(100), 
        ForeignKey('agents.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Documentation support
    requires_documentation: Mapped[bool] = mapped_column(
        nullable=False,
        default=False
    )
    documentation_paths: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=lambda: []
    )
    documentation_context: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Metadata
    meta_data: Mapped[Dict[str, Any]] = mapped_column(
        JSON, 
        nullable=False,
        default=dict
    )
    
    # Relationships
    agent = relationship("Agent", back_populates="tasks")
    events = relationship("TaskEvent", back_populates="task", cascade="all, delete-orphan")
    artifacts = relationship("TaskArtifact", back_populates="task", cascade="all, delete-orphan")
    
    # Self-referential many-to-many for dependencies
    dependencies = relationship(
        "Task",
        secondary=task_dependencies,
        primaryjoin=id == task_dependencies.c.dependent_task_id,
        secondaryjoin=id == task_dependencies.c.dependency_task_id,
        backref="dependents"
    )
    
    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'assigned', 'in_progress', 'needs_review', 'approved', 'needs_fixes', 'completed', 'failed', 'cancelled', 'merged', 'audited', 'ready_for_release')",
            name='ck_task_status'
        ),
        CheckConstraint(
            "priority IN ('critical', 'high', 'medium', 'low')",
            name='ck_task_priority'
        ),
        Index('idx_task_status', 'status'),
        Index('idx_task_created_at', 'created_at'),
        Index('idx_task_priority_status', 'priority', 'status'),
    )


class Agent(Base):
    """Agent model representing workers in the system."""
    __tablename__ = 'agents'
    
    # Primary key - using string ID for agent names
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    
    # Core fields
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
        default='inactive'
    )
    
    # Capabilities and metadata
    capabilities: Mapped[Dict[str, Any]] = mapped_column(
        JSON, 
        nullable=False,
        default=dict
    )
    meta_data: Mapped[Dict[str, Any]] = mapped_column(
        JSON, 
        nullable=False,
        default=dict
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(),
        nullable=False
    )
    last_heartbeat: Mapped[Optional[datetime]] = mapped_column(
        DateTime, 
        nullable=True,
        index=True
    )
    
    # Relationships
    tasks = relationship("Task", back_populates="agent")
    sessions = relationship("AgentSession", back_populates="agent", cascade="all, delete-orphan")
    
    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "type IN ('executor', 'reviewer', 'tester', 'architect', 'data_reviewer')",
            name='ck_agent_type'
        ),
        CheckConstraint(
            "status IN ('active', 'inactive', 'busy', 'error')",
            name='ck_agent_status'
        ),
        Index('idx_agent_type', 'type'),
        Index('idx_agent_status', 'status'),
    )


class TaskEvent(Base):
    """Audit trail for task state changes."""
    __tablename__ = 'task_events'
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Task reference
    task_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey('tasks.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Event details
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    old_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    new_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    actor: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Timestamp
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(),
        nullable=False,
        index=True
    )
    
    # Additional context
    meta_data: Mapped[Dict[str, Any]] = mapped_column(
        JSON, 
        nullable=False,
        default=dict
    )
    
    # Relationships
    task = relationship("Task", back_populates="events")
    
    # Table constraints
    __table_args__ = (
        Index('idx_task_event_type', 'event_type'),
        Index('idx_task_event_timestamp_task', 'task_id', 'timestamp'),
    )


class Plan(Base):
    """Versioned plan documents."""
    __tablename__ = 'plans'
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Plan details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
        default='draft'
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Metadata
    meta_data: Mapped[Dict[str, Any]] = mapped_column(
        JSON, 
        nullable=False,
        default=dict
    )
    
    # Table constraints
    __table_args__ = (
        UniqueConstraint('name', 'version', name='uq_plan_name_version'),
        CheckConstraint(
            "status IN ('draft', 'active', 'archived')",
            name='ck_plan_status'
        ),
        Index('idx_plan_name', 'name'),
        Index('idx_plan_status', 'status'),
    )


class AgentSession(Base):
    """Track agent session lifecycles."""
    __tablename__ = 'agent_sessions'
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Agent reference
    agent_id: Mapped[str] = mapped_column(
        String(100), 
        ForeignKey('agents.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Session details
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_heartbeat: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False,
        index=True
    )
    status: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
        default='active'
    )
    
    # Metadata
    meta_data: Mapped[Dict[str, Any]] = mapped_column(
        JSON, 
        nullable=False,
        default=dict
    )
    
    # Relationships
    agent = relationship("Agent", back_populates="sessions")
    
    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'completed', 'failed', 'timeout')",
            name='ck_session_status'
        ),
        Index('idx_session_status', 'status'),
        Index('idx_session_heartbeat', 'last_heartbeat'),
    )


class AuditLog(Base):
    """Comprehensive audit logging for all entities."""
    __tablename__ = 'audit_log'
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Entity reference
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Action details
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    actor: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Timestamp
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(),
        nullable=False,
        index=True
    )
    
    # Changes and metadata
    changes: Mapped[Dict[str, Any]] = mapped_column(
        JSON, 
        nullable=False,
        default=dict
    )
    meta_data: Mapped[Dict[str, Any]] = mapped_column(
        JSON, 
        nullable=False,
        default=dict
    )
    
    # Table constraints
    __table_args__ = (
        Index('idx_audit_entity', 'entity_type', 'entity_id'),
        Index('idx_audit_actor', 'actor'),
        Index('idx_audit_action', 'action'),
        Index('idx_audit_timestamp', 'timestamp'),
    )


class SystemMetric(Base):
    """Performance and system metrics tracking."""
    __tablename__ = 'system_metrics'
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Metric details
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Timestamp
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(),
        nullable=False,
        index=True
    )
    
    # Tags and metadata
    tags: Mapped[Dict[str, str]] = mapped_column(
        JSON, 
        nullable=False,
        default=dict
    )
    meta_data: Mapped[Dict[str, Any]] = mapped_column(
        JSON, 
        nullable=False,
        default=dict
    )
    
    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "metric_type IN ('gauge', 'counter', 'histogram', 'timer')",
            name='ck_metric_type'
        ),
        Index('idx_metric_name_timestamp', 'metric_name', 'timestamp'),
        Index('idx_metric_type', 'metric_type'),
    )


class TaskArtifact(Base):
    """Artifacts for tasks - TDD artifacts, review feedback, test results, etc."""
    __tablename__ = 'task_artifacts'
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Task reference
    task_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('tasks.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Artifact details
    artifact_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
    
    # Relationship
    task = relationship("Task", back_populates="artifacts")
    
    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "artifact_type IN ('tdd_red', 'tdd_green', 'review_feedback', 'test_results', 'console_logs', 'completion_report', 'integration_test')",
            name='ck_artifact_type'
        ),
        Index('idx_artifact_task_type', 'task_id', 'artifact_type'),
        Index('idx_artifact_created_at', 'created_at'),
    )
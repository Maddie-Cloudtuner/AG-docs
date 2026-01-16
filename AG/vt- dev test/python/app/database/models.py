from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class Resource(Base):
    """Cloud resource model"""
    __tablename__ = "resources"
    
    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False, index=True)
    cloud = Column(String(50), nullable=False, index=True)
    account_id = Column(String(255), nullable=False)
    resource_type = Column(String(100), nullable=False, index=True)
    native_tags = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class VirtualTag(Base):
    """Virtual tag model"""
    __tablename__ = "virtual_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(String(255), ForeignKey("resources.resource_id"), nullable=False, index=True)
    tag_key = Column(String(255), nullable=False, index=True)
    tag_value = Column(Text, nullable=False)
    source = Column(String(50), default="MANUAL", index=True)
    confidence = Column(Float, default=1.0)
    auto_applied = Column(Boolean, default=False, index=True)
    approval_status = Column(String(20), default="PENDING", index=True)  # PENDING, APPROVED, DENIED
    rule_id = Column(Integer, ForeignKey("rules.id"), nullable=True)
    created_by = Column(String(255), default="manual")
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Rule(Base):
    """Tagging rule model"""
    __tablename__ = "rules"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String(255), nullable=False, unique=True)
    condition = Column(Text, nullable=False)
    tag_key = Column(String(255), nullable=False)
    tag_value = Column(Text, nullable=False)
    scope = Column(String(50), default="All")
    priority = Column(Integer, default=1)
    created_by = Column(String(255), default="system")
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())


class MLInference(Base):
    """ML inference results model"""
    __tablename__ = "ml_inferences"
    
    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(String(255), ForeignKey("resources.resource_id"), nullable=False, index=True)
    model_version = Column(String(50), nullable=False)
    predictions = Column(JSON, nullable=False)
    predicted_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())


class TagAudit(Base):
    """Tag audit trail model"""
    __tablename__ = "tag_audit"
    
    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(String(255), ForeignKey("resources.resource_id"), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)
    tag_key = Column(String(255), nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    source = Column(String(50), nullable=False)
    performed_by = Column(String(255), nullable=False)
    tag_metadata = Column(JSON, default={})  # Renamed from 'metadata' to avoid SQLAlchemy reserved keyword
    timestamp = Column(DateTime, default=datetime.utcnow, server_default=func.now(), index=True)


class SchedulerJob(Base):
    """Scheduler job execution tracking"""
    __tablename__ = "scheduler_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_name = Column(String(255), nullable=False, index=True)
    status = Column(String(50), nullable=False, index=True)
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    resources_processed = Column(Integer, default=0)
    tags_applied = Column(Integer, default=0)
    errors = Column(Text, nullable=True)

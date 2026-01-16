"""
Database Models for Virtual Tagging System
===========================================
SQLAlchemy models for production deployment.
"""

from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import uuid

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


class TagSchema(Base):
    """Schema definition table - loaded from cloud_resource_tags_complete.xlsx"""
    __tablename__ = 'tag_schema'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cloud_provider = Column(String(50), default='All')  # All, AWS, GCP, Azure
    resource_scope = Column(String(100), default='Global')
    tag_category = Column(String(50), nullable=False)  # Critical, Non-Critical, Optional
    tag_key = Column(String(255), nullable=False, index=True)
    tag_value = Column(String(255), nullable=False)
    is_case_sensitive = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class NativeTagMapping(Base):
    """Maps native tag keys to schema tag keys (1:1 mapping)"""
    __tablename__ = 'native_tag_mappings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    native_key = Column(String(255), nullable=False, unique=True, index=True)
    schema_key = Column(String(255), nullable=False, index=True)
    confidence = Column(Float, default=0.95)
    created_at = Column(DateTime, default=datetime.utcnow)


class ValueNormalization(Base):
    """Maps native tag values to normalized schema values"""
    __tablename__ = 'value_normalizations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tag_key = Column(String(255), nullable=False, index=True)
    native_value = Column(String(255), nullable=False)
    normalized_value = Column(String(255), nullable=False)
    confidence = Column(Float, default=0.90)


class ResourceTypeRule(Base):
    """Default tags for resource types"""
    __tablename__ = 'resource_type_rules'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    resource_type = Column(String(255), nullable=False, unique=True, index=True)
    default_tags = Column(JSON)  # {"Department": "DevOps", "Application": "monitoring"}
    confidence = Column(Float, default=0.75)
    created_at = Column(DateTime, default=datetime.utcnow)


class ServiceRule(Base):
    """Default tags for service names"""
    __tablename__ = 'service_rules'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    service_name = Column(String(255), nullable=False, unique=True, index=True)
    default_tags = Column(JSON)
    confidence = Column(Float, default=0.75)


class CloudResource(Base):
    """Cloud resources table"""
    __tablename__ = 'cloud_resources'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    cloud_resource_id = Column(String(500), nullable=False, unique=True, index=True)
    name = Column(String(500))
    resource_type = Column(String(255), index=True)
    service_name = Column(String(255), index=True)
    region = Column(String(100))
    pool_id = Column(String(100))
    native_tags = Column(JSON)  # Original tags from cloud
    last_seen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    virtual_tags = relationship("VirtualTag", back_populates="resource")


class VirtualTag(Base):
    """Virtual tags applied to resources"""
    __tablename__ = 'virtual_tags'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    resource_id = Column(String(36), ForeignKey('cloud_resources.id'), nullable=False, index=True)
    tag_key = Column(String(255), nullable=False, index=True)
    tag_value = Column(String(255), nullable=False)
    source = Column(String(50))  # NATIVE, INFERRED, RULE_BASED, MANUAL
    confidence = Column(Float, default=0.0)
    reasoning = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    resource = relationship("CloudResource", back_populates="virtual_tags")


class TagAudit(Base):
    """Audit trail for tag changes"""
    __tablename__ = 'tag_audit'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    resource_id = Column(String(36), index=True)
    action = Column(String(50))  # CREATE, UPDATE, DELETE
    tag_key = Column(String(255))
    old_value = Column(String(255))
    new_value = Column(String(255))
    performed_by = Column(String(255))
    timestamp = Column(DateTime, default=datetime.utcnow)


# Database setup helper
def init_database(db_url: str = 'sqlite:///virtual_tags.db'):
    """Initialize database and create tables"""
    engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return engine, Session()


if __name__ == '__main__':
    engine, session = init_database()
    print(f"Database initialized: {engine.url}")
    print("Tables created:")
    for table in Base.metadata.tables:
        print(f"  - {table}")

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from .database import Base

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    device_name = Column(String(100), nullable=False)
    ip_address = Column(String(45), nullable=False, index=True)
    mac_address = Column(String(17), nullable=False, unique=True, index=True)
    os_info = Column(String(100), default="Unknown")
    status = Column(String(20), default="ONLINE")
    risk_score = Column(Float, default=0.0)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)

    events = relationship("SecurityEvent", back_populates="device", cascade="all, delete-orphan")
    ports = relationship("OpenPort", back_populates="device", cascade="all, delete-orphan")

class OpenPort(Base):
    __tablename__ = "open_ports"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    port = Column(Integer, nullable=False)
    protocol = Column(String(10), default="TCP")
    service_name = Column(String(50), default="Unknown")
    banner = Column(String(255), nullable=True)
    discovered_at = Column(DateTime, default=datetime.utcnow)

    device = relationship("Device", back_populates="ports")

class SecurityEvent(Base):
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    severity = Column(String(20), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)
    source_ip = Column(String(45), nullable=True)
    target_ip = Column(String(45), nullable=True)
    port = Column(Integer, nullable=True)
    description = Column(Text, nullable=False)
    resolved = Column(Boolean, default=False)

    device = relationship("Device", back_populates="events")

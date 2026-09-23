from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class OpenPortBase(BaseModel):
    port: int
    protocol: str = "TCP"
    service_name: Optional[str] = "Unknown"
    banner: Optional[str] = None

class OpenPortCreate(OpenPortBase):
    pass

class OpenPortResponse(OpenPortBase):
    id: int
    discovered_at: datetime
    class Config:
        from_attributes = True

class DeviceTelemetryPayload(BaseModel):
    device_name: str
    ip_address: str
    mac_address: str
    os_info: str
    open_ports: List[OpenPortCreate]
    active_connections_count: int

class DeviceResponse(BaseModel):
    id: int
    device_name: str
    ip_address: str
    mac_address: str
    os_info: str
    status: str
    risk_score: float
    first_seen: datetime
    last_seen: datetime
    ports: List[OpenPortResponse] = []
    class Config:
        from_attributes = True

class SecurityEventResponse(BaseModel):
    id: int
    device_id: Optional[int]
    timestamp: datetime
    severity: str
    event_type: str
    source_ip: Optional[str]
    target_ip: Optional[str]
    port: Optional[int]
    description: str
    resolved: bool
    class Config:
        from_attributes = True

class ScanRequest(BaseModel):
    target_cidr: str
    start_port: int = 1
    end_port: int = 1024

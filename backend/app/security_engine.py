from sqlalchemy.orm import Session
from .models import Device, SecurityEvent, OpenPort
from datetime import datetime

CRITICAL_RISK_PORTS = {
    21: ("FTP", "HIGH"),
    22: ("SSH", "MEDIUM"),
    23: ("TELNET", "CRITICAL"),
    80: ("HTTP", "LOW"),
    445: ("SMB", "CRITICAL"),
    3389: ("RDP", "HIGH"),
    5900: ("VNC", "HIGH"),
    1433: ("MSSQL", "HIGH"),
    3306: ("MYSQL", "MEDIUM"),
}

class SecurityEngine:
    def __init__(self, db: Session):
        self.db = db

    def process_telemetry(self, payload) -> Device:
        device = self.db.query(Device).filter(Device.mac_address == payload.mac_address).first()
        
        if not device:
            device = Device(
                device_name=payload.device_name,
                ip_address=payload.ip_address,
                mac_address=payload.mac_address,
                os_info=payload.os_info,
                status="ONLINE",
                risk_score=0.0
            )
            self.db.add(device)
            self.db.commit()
            self.db.refresh(device)
            
            self._raise_event(
                device_id=device.id,
                severity="INFO",
                event_type="NEW_ASSET_DETECTED",
                source_ip=payload.ip_address,
                description=f"New network asset discovered: {payload.device_name} ({payload.ip_address})"
            )
        else:
            if device.ip_address != payload.ip_address:
                self._raise_event(
                    device_id=device.id,
                    severity="MEDIUM",
                    event_type="IP_ADDRESS_CHANGED",
                    source_ip=payload.ip_address,
                    description=f"Asset {device.device_name} changed IP from {device.ip_address} to {payload.ip_address}"
                )
                device.ip_address = payload.ip_address

            device.last_seen = datetime.utcnow()
            device.status = "ONLINE"
            device.os_info = payload.os_info

        current_ports = {p.port for p in device.ports}
        calculated_risk = 0.0
        
        self.db.query(OpenPort).filter(OpenPort.device_id == device.id).delete()
        
        for port_data in payload.open_ports:
            op = OpenPort(
                device_id=device.id,
                port=port_data.port,
                protocol=port_data.protocol,
                service_name=port_data.service_name,
                banner=port_data.banner
            )
            self.db.add(op)

            if port_data.port in CRITICAL_RISK_PORTS:
                srv_name, sev = CRITICAL_RISK_PORTS[port_data.port]
                weight = {"LOW": 10, "MEDIUM": 20, "HIGH": 35, "CRITICAL": 50}[sev]
                calculated_risk += weight

                if port_data.port not in current_ports:
                    self._raise_event(
                        device_id=device.id,
                        severity=sev,
                        event_type="EXPOSED_CRITICAL_PORT",
                        source_ip=payload.ip_address,
                        port=port_data.port,
                        description=f"Exposed dangerous network service detected: {srv_name} on port {port_data.port}"
                    )

        if payload.active_connections_count > 100:
            calculated_risk += 25
            self._raise_event(
                device_id=device.id,
                severity="HIGH",
                event_type="HIGH_CONNECTION_DENSITY",
                source_ip=payload.ip_address,
                description=f"Unusually high active socket connection count: {payload.active_connections_count} sockets"
            )

        device.risk_score = min(calculated_risk, 100.0)
        self.db.commit()
        self.db.refresh(device)
        return device

    def _raise_event(self, device_id, severity, event_type, source_ip, description, port=None, target_ip=None):
        event = SecurityEvent(
            device_id=device_id,
            severity=severity,
            event_type=event_type,
            source_ip=source_ip,
            target_ip=target_ip,
            port=port,
            description=description
        )
        self.db.add(event)
        self.db.commit()

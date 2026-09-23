import json
from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from .database import engine, Base, get_db
from .models import Device, SecurityEvent
from .schemas import DeviceTelemetryPayload, DeviceResponse, SecurityEventResponse, ScanRequest
from .security_engine import SecurityEngine
from .scanner import run_scoped_scan

Base.metadata.create_all(bind=engine)

app = FastAPI(title="NetGuard SOC Security API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                pass

manager = ConnectionManager()

@app.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/v1/telemetry", response_model=DeviceResponse)
async def receive_telemetry(payload: DeviceTelemetryPayload, db: Session = Depends(get_db)):
    engine_inst = SecurityEngine(db)
    device = engine_inst.process_telemetry(payload)
    
    await manager.broadcast({
        "type": "TELEMETRY_UPDATE",
        "device_id": device.id,
        "device_name": device.device_name,
        "risk_score": device.risk_score
    })
    return device

@app.get("/api/v1/devices", response_model=List[DeviceResponse])
def list_devices(db: Session = Depends(get_db)):
    return db.query(Device).all()

@app.get("/api/v1/events", response_model=List[SecurityEventResponse])
def list_events(db: Session = Depends(get_db)):
    return db.query(SecurityEvent).order_by(SecurityEvent.timestamp.desc()).limit(100).all()

@app.post("/api/v1/scan")
async def execute_scan(req: ScanRequest, db: Session = Depends(get_db)):
    try:
        ports_to_scan = list(range(req.start_port, min(req.end_port + 1, 65535)))
        results = run_scoped_scan(req.target_cidr, ports_to_scan)
        
        event = SecurityEvent(
            severity="INFO",
            event_type="AUTHORIZED_SCAN_COMPLETED",
            source_ip="LOCAL_SOC",
            target_ip=req.target_cidr,
            description=f"Scoped port scan completed on {req.target_cidr}. Discovered {len(results)} open ports."
        )
        db.add(event)
        db.commit()

        await manager.broadcast({
            "type": "SCAN_COMPLETED",
            "target": req.target_cidr,
            "open_ports_count": len(results)
        })

        return {"target": req.target_cidr, "open_ports": results}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

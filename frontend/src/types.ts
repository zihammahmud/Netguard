export interface OpenPort {
  id: number;
  port: number;
  protocol: string;
  service_name: string;
  banner?: string;
  discovered_at: string;
}

export interface Device {
  id: number;
  device_name: string;
  ip_address: string;
  mac_address: string;
  os_info: string;
  status: 'ONLINE' | 'OFFLINE' | 'DEGRADED';
  risk_score: number;
  first_seen: string;
  last_seen: string;
  ports: OpenPort[];
}

export interface SecurityEvent {
  id: number;
  device_id?: number;
  timestamp: string;
  severity: 'INFO' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  event_type: string;
  source_ip?: string;
  target_ip?: string;
  port?: number;
  description: string;
  resolved: boolean;
}

import socket
import platform
import psutil
import requests
import time
import uuid

# Replace with your deployed Render URL later (e.g. https://your-backend.onrender.com/api/v1/telemetry)
BACKEND_URL = "http://127.0.0.1:8000/api/v1/telemetry"
REPORT_INTERVAL = 10

def get_mac_address() -> str:
    mac_num = uuid.getnode()
    return ':'.join(("%012X" % mac_num)[i:i+2] for i in range(0, 12, 2))

def get_local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def scan_open_listening_ports():
    open_ports = []
    for conn in psutil.net_connections(kind='inet'):
        if conn.status == 'LISTEN':
            port = conn.laddr.port
            open_ports.append({
                "port": port,
                "protocol": "TCP",
                "service_name": socket.getservbyport(port, "tcp") if port < 1024 else "Unknown",
                "banner": f"PID: {conn.pid}"
            })
    return open_ports

def run_agent():
    print("[+] NetGuard Telemetry Agent Running...")
    mac = get_mac_address()
    hostname = socket.gethostname()
    os_sys = f"{platform.system()} {platform.release()}"

    while True:
        try:
            local_ip = get_local_ip()
            listening_ports = scan_open_listening_ports()
            active_connections = len(psutil.net_connections())

            payload = {
                "device_name": hostname,
                "ip_address": local_ip,
                "mac_address": mac,
                "os_info": os_sys,
                "open_ports": listening_ports,
                "active_connections_count": active_connections
            }

            res = requests.post(BACKEND_URL, json=payload, timeout=5)
            if res.status_code == 200:
                print(f"[{time.strftime('%H:%M:%S')}] Telemetry synced -> Risk Score: {res.json().get('risk_score')}")
            else:
                print(f"[!] Server Error: {res.status_code}")

        except Exception as e:
            print(f"[!] Telemetry send failed: {e}")

        time.sleep(REPORT_INTERVAL)

if __name__ == "__main__":
    run_agent()

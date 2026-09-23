import socket
import ipaddress
import concurrent.futures
from typing import List, Dict, Any

RFC1918_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8")
]

def is_authorized_target(target_ip: str) -> bool:
    try:
        ip = ipaddress.ip_address(target_ip)
        return any(ip in net for net in RFC1918_NETWORKS)
    except ValueError:
        return False

def scan_single_port(ip: str, port: int, timeout: float = 0.8) -> Dict[str, Any]:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((ip, port))
            if result == 0:
                banner = ""
                try:
                    s.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
                    banner = s.recv(128).decode("utf-8", errors="ignore").strip().split("\n")[0]
                except Exception:
                    banner = "No Banner"
                return {"port": port, "status": "OPEN", "banner": banner}
    except Exception:
        pass
    return {"port": port, "status": "CLOSED", "banner": ""}

def run_scoped_scan(target_ip: str, ports: List[int]) -> List[Dict[str, Any]]:
    if not is_authorized_target(target_ip):
        raise ValueError(f"Scan aborted: Target {target_ip} is outside RFC1918 private IPv4 scope.")

    open_ports = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(scan_single_port, target_ip, port): port for port in ports}
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res["status"] == "OPEN":
                open_ports.append(res)
    return open_ports

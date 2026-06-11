import socket

def scan_ports(ip_address: str):
    common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 465, 993, 995, 3306, 3389, 8080, 8443]
    open_ports = []
    
    for port in common_ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        try:
            result = sock.connect_ex((ip_address, port))
            if result == 0:
                open_ports.append(port)
        except Exception:
            pass
        finally:
            sock.close()
            
    return {"open_ports": open_ports}

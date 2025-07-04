import subprocess
import re
import platform
import os
from datetime import datetime
from typing import Dict, List
import socket

# Expresiones regulares para parsear ping
PING_RE_LINUX = re.compile(r"min/avg/max.*= ([\d.]+)/([\d.]+)/([\d.]+)")
PING_RE_WINDOWS = re.compile(r"Minimum = (\d+)ms, Maximum = (\d+)ms, Average = (\d+)ms")
LOSS_RE = re.compile(r"(\d+)% packet loss|(\d+)% perdidos")

def is_valid_host(host: str) -> bool:
    """Valida que el host sea una IP válida o un dominio válido"""
    try:
        socket.inet_aton(host)
        return True
    except socket.error:
        # Si no es IP, verificar si es un dominio válido
        if re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', host):
            return True
        return False

def ping(host: str, count: int = 4, timeout: int = 2) -> Dict:
    """
    Ejecuta ping a un host específico
    """
    system = platform.system().lower()
    
    if system == "windows":
        cmd = ["ping", "-n", str(count), "-w", str(timeout * 1000), host]
    else:
        cmd = ["ping", "-c", str(count), "-W", str(timeout), host]
    
    try:
        proc = subprocess.run(cmd, text=True, capture_output=True, timeout=30)
        output = proc.stdout
        
        if proc.returncode != 0:
            return {
                "host": host,
                "packets_transmitted": count,
                "packets_received": 0,
                "packet_loss": 100.0,
                "min_ms": 0.0,
                "avg_ms": 0.0,
                "max_ms": 0.0,
                "timestamp": datetime.now().isoformat()
            }
        
        # Parsear resultados según el SO
        if system == "windows":
            return _parse_ping_windows(output, host, count)
        else:
            return _parse_ping_linux(output, host, count)
            
    except subprocess.TimeoutExpired:
        return {
            "host": host,
            "packets_transmitted": count,
            "packets_received": 0,
            "packet_loss": 100.0,
            "min_ms": 0.0,
            "avg_ms": 0.0,
            "max_ms": 0.0,
            "timestamp": datetime.now().isoformat()
        }

def _parse_ping_linux(output: str, host: str, count: int) -> Dict:
    """Parsea la salida de ping en sistemas Linux/macOS"""
    try:
        # Buscar estadísticas de tiempo
        time_match = PING_RE_LINUX.search(output)
        if time_match:
            min_ms, avg_ms, max_ms = map(float, time_match.groups())
        else:
            min_ms = avg_ms = max_ms = 0.0
        
        # Buscar pérdida de paquetes
        loss_match = LOSS_RE.search(output)
        if loss_match:
            loss = float(loss_match.group(1))
        else:
            loss = 0.0
        
        packets_received = count - int(count * loss / 100)
        
        return {
            "host": host,
            "packets_transmitted": count,
            "packets_received": packets_received,
            "packet_loss": loss,
            "min_ms": min_ms,
            "avg_ms": avg_ms,
            "max_ms": max_ms,
            "timestamp": datetime.now().isoformat()
        }
    except Exception:
        return {
            "host": host,
            "packets_transmitted": count,
            "packets_received": 0,
            "packet_loss": 100.0,
            "min_ms": 0.0,
            "avg_ms": 0.0,
            "max_ms": 0.0,
            "timestamp": datetime.now().isoformat()
        }

def _parse_ping_windows(output: str, host: str, count: int) -> Dict:
    """Parsea la salida de ping en sistemas Windows"""
    try:
        # Buscar estadísticas de tiempo
        time_match = PING_RE_WINDOWS.search(output)
        if time_match:
            min_ms, max_ms, avg_ms = map(float, time_match.groups())
        else:
            min_ms = avg_ms = max_ms = 0.0
        
        # Buscar pérdida de paquetes
        loss_match = LOSS_RE.search(output)
        if loss_match:
            loss = float(loss_match.group(1) or loss_match.group(2))
        else:
            loss = 0.0
        
        packets_received = count - int(count * loss / 100)
        
        return {
            "host": host,
            "packets_transmitted": count,
            "packets_received": packets_received,
            "packet_loss": loss,
            "min_ms": min_ms,
            "avg_ms": avg_ms,
            "max_ms": max_ms,
            "timestamp": datetime.now().isoformat()
        }
    except Exception:
        return {
            "host": host,
            "packets_transmitted": count,
            "packets_received": 0,
            "packet_loss": 100.0,
            "min_ms": 0.0,
            "avg_ms": 0.0,
            "max_ms": 0.0,
            "timestamp": datetime.now().isoformat()
        }

def traceroute(host: str, max_hops: int = 30) -> List[Dict]:
    """
    Ejecuta traceroute a un host específico
    """
    system = platform.system().lower()
    
    if system == "windows":
        # En Windows el comando es tracert y suele estar en el PATH
        cmd = ["tracert", "-h", str(max_hops), host]
    else:
        # En Linux/Unix buscar traceroute en ubicaciones comunes
        traceroute_paths = [
            "traceroute",           # Si está en el PATH
            "/usr/bin/traceroute",  # Ubicación común
            "/usr/sbin/traceroute", # Ubicación en algunas distros
            "/bin/traceroute"       # Otra ubicación posible
        ]
        
        # Encontrar el primer path que exista
        traceroute_path = None
        for path in traceroute_paths:
            try:
                # Verificar si el comando existe y es ejecutable
                if path == "traceroute":
                    # Comprobar si está en el PATH
                    result = subprocess.run(["which", "traceroute"], 
                                           capture_output=True, text=True, check=False)
                    if result.returncode == 0:
                        traceroute_path = "traceroute"
                        break
                elif os.path.isfile(path) and os.access(path, os.X_OK):
                    traceroute_path = path
                    break
            except:
                continue
        
        # Si no se encuentra, usar el valor por defecto
        if not traceroute_path:
            traceroute_path = "traceroute"  # Intentar con el comando básico
            
        cmd = [traceroute_path, "-n", "-m", str(max_hops), host]
    
    try:
        proc = subprocess.run(cmd, text=True, capture_output=True, timeout=60)
        output = proc.stdout
        
        if system == "windows":
            return _parse_traceroute_windows(output)
        else:
            return _parse_traceroute_linux(output)
            
    except subprocess.TimeoutExpired:
        return []

def _parse_traceroute_linux(output: str) -> List[Dict]:
    """Parsea la salida de traceroute en sistemas Linux/macOS"""
    hops = []
    lines = output.splitlines()
    
    for line in lines[1:]:  # Saltar la primera línea
        if not line.strip():
            continue
            
        parts = line.split()
        if len(parts) < 2:
            continue
            
        try:
            hop_no = int(parts[0])
            
            if parts[1] == "*":
                hops.append({
                    "hop": hop_no,
                    "host": "timeout",
                    "rtt_ms": None
                })
            else:
                host_ip = parts[1]
                rtt_ms = float(parts[2]) if len(parts) > 2 else None
                hops.append({
                    "hop": hop_no,
                    "host": host_ip,
                    "rtt_ms": rtt_ms
                })
        except (ValueError, IndexError):
            continue
    
    return hops

def _parse_traceroute_windows(output: str) -> List[Dict]:
    """Parsea la salida de tracert en sistemas Windows"""
    hops = []
    lines = output.splitlines()
    
    for i, line in enumerate(lines):
        if line.strip().startswith(str(i + 1)):
            try:
                parts = line.split()
                hop_no = int(parts[0])
                
                # Buscar IP en la línea
                ip_pattern = r'\d+\.\d+\.\d+\.\d+'
                ip_match = re.search(ip_pattern, line)
                
                if ip_match:
                    host_ip = ip_match.group()
                    # Buscar tiempo de respuesta
                    time_pattern = r'(\d+)\s*ms'
                    time_matches = re.findall(time_pattern, line)
                    rtt_ms = float(time_matches[0]) if time_matches else None
                    
                    hops.append({
                        "hop": hop_no,
                        "host": host_ip,
                        "rtt_ms": rtt_ms
                    })
                else:
                    hops.append({
                        "hop": hop_no,
                        "host": "timeout",
                        "rtt_ms": None
                    })
            except (ValueError, IndexError):
                continue
    
    return hops
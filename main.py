from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List
import asyncio
import uvicorn

from utils import ping, traceroute, is_valid_host
from models import PingResult, TracerouteResult, TraceHop, HealthCheck, ErrorResponse

app = FastAPI(
    title="Connectivity API",
    description="API para verificar conectividad de red mediante ping y traceroute",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lista de hosts permitidos por seguridad
ALLOWED_HOSTS = {
    "1.1.1.1",
    "8.8.8.8", 
    "8.8.4.4",
    "1.0.0.1",
    "google.com",
    "cloudflare.com",
    "github.com",
    "stackoverflow.com",
    "python.org",
    "fastapi.tiangolo.com"
}

def validate_host(host: str):
    """Valida que el host esté permitido y sea válido"""
    if host not in ALLOWED_HOSTS:
        raise HTTPException(
            status_code=400,
            detail=f"Host '{host}' no está permitido. Hosts permitidos: {sorted(ALLOWED_HOSTS)}"
        )
    
    if not is_valid_host(host):
        raise HTTPException(
            status_code=400,
            detail=f"Host '{host}' no es válido"
        )

@app.get("/", response_model=HealthCheck)
async def root():
    """Endpoint de salud del servicio"""
    return HealthCheck(
        status="OK",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Endpoint de verificación de salud"""
    return HealthCheck(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )

@app.get("/ping", response_model=PingResult)
async def do_ping(
    host: str = Query(..., description="IP o nombre de dominio a verificar"),
    count: int = Query(4, ge=1, le=10, description="Número de paquetes a enviar (1-10)")
):
    """
    Ejecuta ping a un host específico
    
    - **host**: IP o nombre de dominio a verificar
    - **count**: Número de paquetes ICMP a enviar (1-10)
    """
    validate_host(host)
    
    try:
        # Ejecutar ping en un hilo separado para no bloquear
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, ping, host, count)
        
        return PingResult(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error ejecutando ping: {str(e)}"
        )

@app.get("/traceroute", response_model=TracerouteResult)
async def do_traceroute(
    host: str = Query(..., description="IP o nombre de dominio a trazar"),
    max_hops: int = Query(30, ge=1, le=50, description="Número máximo de saltos (1-50)")
):
    """
    Ejecuta traceroute a un host específico
    
    - **host**: IP o nombre de dominio a trazar
    - **max_hops**: Número máximo de saltos permitidos (1-50)
    """
    validate_host(host)
    
    try:
        # Ejecutar traceroute en un hilo separado para no bloquear
        loop = asyncio.get_event_loop()
        hops_data = await loop.run_in_executor(None, traceroute, host, max_hops)
        
        hops = [TraceHop(**hop) for hop in hops_data]
        
        return TracerouteResult(
            host=host,
            hops=hops,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error ejecutando traceroute: {str(e)}"
        )

@app.get("/allowed-hosts")
async def get_allowed_hosts():
    """Obtiene la lista de hosts permitidos"""
    return {
        "allowed_hosts": sorted(ALLOWED_HOSTS),
        "count": len(ALLOWED_HOSTS),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/ping/bulk")
async def bulk_ping(
    hosts: List[str] = Query(..., description="Lista de hosts a verificar"),
    count: int = Query(4, ge=1, le=10, description="Número de paquetes por host")
):
    """
    Ejecuta ping a múltiples hosts simultáneamente
    
    - **hosts**: Lista de IPs o dominios a verificar
    - **count**: Número de paquetes ICMP a enviar por host
    """
    if len(hosts) > 5:
        raise HTTPException(
            status_code=400,
            detail="Máximo 5 hosts permitidos por solicitud"
        )
    
    # Validar todos los hosts
    for host in hosts:
        validate_host(host)
    
    try:
        # Ejecutar ping a todos los hosts en paralelo
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, ping, host, count) for host in hosts]
        results = await asyncio.gather(*tasks)
        
        return {
            "results": [PingResult(**result) for result in results],
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error ejecutando ping masivo: {str(e)}"
        )

# Manejador de errores personalizado
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            detail=exc.detail,
            error_code=f"HTTP_{exc.status_code}",
            timestamp=datetime.now().isoformat()
        ).dict()
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
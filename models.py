from pydantic import BaseModel, Field
from typing import List, Optional

class PingResult(BaseModel):
    host: str
    packets_transmitted: int
    packets_received: int
    packet_loss: float = Field(..., description="Porcentaje 0-100")
    min_ms: float
    avg_ms: float
    max_ms: float
    timestamp: str

class TraceHop(BaseModel):
    hop: int
    host: str
    rtt_ms: Optional[float] = None

class TracerouteResult(BaseModel):
    host: str
    hops: List[TraceHop]
    timestamp: str

class HealthCheck(BaseModel):
    status: str
    timestamp: str
    version: str

class ErrorResponse(BaseModel):
    detail: str
    error_code: str
    timestamp: str
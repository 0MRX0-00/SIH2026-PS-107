from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class RootHealthResponse(BaseModel):
    status: str = Field(default="healthy", description="Overall health status")
    service: str = Field(default="e-bis-sahayak-backend")
    version: str = Field(default="0.1.0")
    phase: str = Field(default="Phase 1: Foundation")


class SubsystemStatus(BaseModel):
    database: bool = Field(..., description="PostgreSQL database connectivity")
    vector_store_configured: bool = Field(..., description="Qdrant vector store connection status")
    embedding_provider: str = Field(..., description="Configured embedding engine")
    details: Optional[Dict[str, Any]] = None


class DetailedHealthResponse(BaseModel):
    status: str
    environment: str
    version: str
    phase: str
    subsystems: SubsystemStatus

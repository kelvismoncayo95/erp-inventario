"""Schemas de Proveedor."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone


class ProveedorBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200)
    ruc: Optional[str] = Field(None, max_length=20)
    telefono: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    direccion: Optional[str] = Field(None, max_length=255)
    contacto: Optional[str] = Field(None, max_length=100)


class ProveedorCrear(ProveedorBase):
    pass


class ProveedorActualizar(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    ruc: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None
    contacto: Optional[str] = None


class ProveedorRespuesta(ProveedorBase):
    id: int
    creado_en: datetime

    class Config:
        from_attributes = True

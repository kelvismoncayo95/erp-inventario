"""
Schemas para Categoría.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone


class CategoriaBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=255)


class CategoriaCrear(CategoriaBase):
    pass


class CategoriaActualizar(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=255)


class CategoriaRespuesta(CategoriaBase):
    id: int
    creado_en: datetime

    class Config:
        from_attributes = True

"""Schemas de Orden de Compra."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
from decimal import Decimal


class ItemCompraCrear(BaseModel):
    producto_id: int
    cantidad: int = Field(..., gt=0, description="Cantidad mayor a 0")
    precio_unitario: Decimal = Field(..., ge=0, description="Precio costo unitario")


class ItemCompraRespuesta(BaseModel):
    id: int
    producto_id: int
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal
    producto_nombre: Optional[str] = None

    class Config:
        from_attributes = True


class OrdenCompraCrear(BaseModel):
    proveedor_id: int
    fecha_entrega_esperada: Optional[datetime] = None
    items: List[ItemCompraCrear] = Field(..., min_length=1)


class OrdenCompraRespuesta(BaseModel):
    id: int
    numero_orden: str
    fecha: datetime
    fecha_entrega_esperada: Optional[datetime] = None
    total: Decimal
    estado: str
    proveedor_id: int
    proveedor_nombre: Optional[str] = None
    creado_por: int
    creado_por_nombre: Optional[str] = None
    creado_en: datetime

    class Config:
        from_attributes = True


class OrdenCompraDetalle(OrdenCompraRespuesta):
    items: List[ItemCompraRespuesta] = []


class OrdenCompraRecibir(BaseModel):
    mensaje: str
    orden_id: int
    estado: str
    items_actualizados: List[dict]

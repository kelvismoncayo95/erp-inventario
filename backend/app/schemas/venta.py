from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
from decimal import Decimal


class ItemVentaCrear(BaseModel):
    producto_id: int = Field(..., gt=0)
    cantidad: int = Field(..., gt=0)


class ItemVentaRespuesta(BaseModel):
    id: int
    producto_id: int
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal
    producto_nombre: Optional[str] = None

    class Config:
        from_attributes = True


class VentaCrear(BaseModel):
    cliente_nombre: Optional[str] = Field(None, max_length=200)
    cliente_telefono: Optional[str] = Field(None, max_length=20)
    items: List[ItemVentaCrear] = Field(..., min_length=1)


class VentaRespuesta(BaseModel):
    id: int
    numero_factura: Optional[str] = None
    fecha: datetime
    subtotal: Decimal
    iva: Decimal
    total: Decimal
    estado: str
    cliente_nombre: Optional[str] = None
    cliente_telefono: Optional[str] = None
    creado_por: Optional[int] = None
    vendedor_nombre: Optional[str] = None
    items: List[ItemVentaRespuesta] = []

    class Config:
        from_attributes = True


class VentaAnular(BaseModel):
    mensaje: str
    venta_id: int
    nuevo_estado: str
    stock_devuelto: list = []

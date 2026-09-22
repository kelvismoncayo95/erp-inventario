from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200)
    sku: str = Field(..., min_length=1, max_length=50)
    descripcion: Optional[str] = Field(None, max_length=500)
    precio_costo: Decimal = Field(..., gt=0)
    precio_venta: Decimal = Field(..., gt=0)
    stock_actual: int = Field(0, ge=0)
    stock_minimo: int = Field(5, ge=0)
    stock_maximo: int = Field(100, ge=0)
    categoria_id: Optional[int] = None
    proveedor_id: Optional[int] = None


class ProductoCrear(ProductoBase):
    pass


class ProductoActualizar(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    descripcion: Optional[str] = Field(None, max_length=500)
    precio_costo: Optional[Decimal] = Field(None, gt=0)
    precio_venta: Optional[Decimal] = Field(None, gt=0)
    stock_actual: Optional[int] = Field(None, ge=0)
    stock_minimo: Optional[int] = Field(None, ge=0)
    stock_maximo: Optional[int] = Field(None, ge=0)
    categoria_id: Optional[int] = None
    proveedor_id: Optional[int] = None
    activo: Optional[int] = Field(None, ge=0, le=1)


class ProductoRespuesta(BaseModel):
    id: int
    nombre: str
    sku: str
    descripcion: Optional[str] = None
    precio_costo: Decimal
    precio_venta: Decimal
    stock_actual: int
    stock_minimo: int
    stock_maximo: int
    categoria_id: Optional[int] = None
    proveedor_id: Optional[int] = None
    activo: int
    creado_en: datetime
    actualizado_en: Optional[datetime] = None
    categoria_nombre: Optional[str] = None
    proveedor_nombre: Optional[str] = None
    eliminado_por_nombre: Optional[str] = None
    fecha_eliminacion: Optional[datetime] = None
    reactivado_por_nombre: Optional[str] = None
    fecha_reactivacion: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductoRespuestaVendedor(BaseModel):
    id: int
    nombre: str
    sku: str
    descripcion: Optional[str] = None
    precio_venta: Decimal
    categoria_nombre: Optional[str] = None
    proveedor_nombre: Optional[str] = None
    disponible: bool = True


class ReactivarProducto(BaseModel):
    stock_inicial: int = Field(..., gt=0, description="Stock con el que se reactiva (mayor a 0)")

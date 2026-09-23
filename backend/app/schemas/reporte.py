"""
Schemas de Reportes.
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone


class ResumenGeneral(BaseModel):
    """Resumen del dashboard."""
    total_productos: int
    valor_inventario: float
    total_ventas: int
    ingresos_totales: float
    ganancia_total: float


class ProductoMasVendido(BaseModel):
    """Producto con estadísticas de venta."""
    producto_id: int
    nombre: str
    sku: str
    total_vendido: int
    ingresos: float
    num_ventas: int


class GananciaPorPeriodo(BaseModel):
    """Ganancia agrupada por período."""
    periodo: datetime
    num_ventas: int
    ingresos: float
    costo: float
    ganancia: float


class ProductoStockBajo(BaseModel):
    """Producto con stock bajo mínimo."""
    id: int
    nombre: str
    sku: str
    stock_actual: int
    stock_minimo: int
    diferencia: int

    class Config:
        from_attributes = True

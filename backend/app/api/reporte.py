"""
Endpoints de Reportes.
Solo accesibles para administradores.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.reporte import (
    ResumenGeneral,
    ProductoMasVendido,
    GananciaPorPeriodo,
    ProductoStockBajo,
)
from app.services.reporte_service import ReporteService
from app.core.dependencies import requerir_admin


router = APIRouter(
    prefix="/reportes",
    tags=["Reportes"],
)


@router.get("/resumen", response_model=ResumenGeneral)
def resumen(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_admin),
):
    """Resumen general del sistema. Solo admin."""
    return ReporteService.resumen_general(db)


@router.get("/productos-mas-vendidos", response_model=List[ProductoMasVendido])
def productos_mas_vendidos(
    limite: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_admin),
):
    """Top N productos más vendidos. Solo admin."""
    return ReporteService.productos_mas_vendidos(db, limite)


@router.get("/ganancias", response_model=List[GananciaPorPeriodo])
def ganancias(
    periodo: str = Query("mes", pattern="^(dia|mes|año|year)$"),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_admin),
):
    """Ganancias agrupadas por día, mes o año. Solo admin."""
    return ReporteService.ganancias_por_periodo(db, periodo)


@router.get("/stock-bajo", response_model=List[ProductoStockBajo])
def stock_bajo(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_admin),
):
    """Productos con stock bajo mínimo. Solo admin."""
    return ReporteService.stock_bajo(db)

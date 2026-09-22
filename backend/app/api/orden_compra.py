from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.database import get_db
from app.models.orden_compra import OrdenCompra
from app.models.item_compra import ItemCompra
from app.models.usuario import Usuario
from app.schemas.orden_compra import (
    OrdenCompraCrear,
    OrdenCompraRespuesta,
    OrdenCompraDetalle,
    OrdenCompraRecibir,
    ItemCompraRespuesta,
)
from app.services.orden_compra_service import (
    OrdenCompraService,
    OrdenInvalidaError,
)
from app.core.dependencies import (
    get_current_user,
    requerir_admin_o_encargado,
)


router = APIRouter(prefix="/ordenes-compra", tags=["Órdenes de Compra"])


def _get_usuario_nombre(db: Session, usuario_id):
    """Busca el nombre del usuario sin depender de relationship."""
    if not usuario_id:
        return None
    u = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    return u.nombre if u else None


def _serializar(orden: OrdenCompra, db: Session, con_items: bool = False) -> dict:
    d = OrdenCompraRespuesta.model_validate(orden).model_dump()
    d["proveedor_nombre"] = orden.proveedor.nombre if orden.proveedor else None
    d["creado_por_nombre"] = _get_usuario_nombre(db, orden.creado_por)
    if con_items:
        d["items"] = []
        for it in orden.items:
            item_d = ItemCompraRespuesta.model_validate(it).model_dump()
            item_d["producto_nombre"] = it.producto.nombre if it.producto else None
            d["items"].append(item_d)
    return d


@router.get("/", response_model=List[OrdenCompraRespuesta])
def listar_ordenes(
    skip: int = 0,
    limit: int = 100,
    estado: str = None,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    query = db.query(OrdenCompra).options(joinedload(OrdenCompra.proveedor))
    if estado:
        query = query.filter(OrdenCompra.estado == estado)
    ordenes = query.order_by(OrdenCompra.id.desc()).offset(skip).limit(limit).all()
    return [_serializar(o, db, con_items=False) for o in ordenes]


@router.get("/{orden_id}", response_model=OrdenCompraDetalle)
def obtener_orden(
    orden_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    orden = db.query(OrdenCompra).options(
        joinedload(OrdenCompra.proveedor),
        joinedload(OrdenCompra.items).joinedload(ItemCompra.producto),
    ).filter(OrdenCompra.id == orden_id).first()
    if not orden:
        raise HTTPException(404, f"Orden {orden_id} no encontrada")
    return _serializar(orden, db, con_items=True)


@router.post("/", response_model=OrdenCompraDetalle, status_code=status.HTTP_201_CREATED)
def crear_orden(
    datos: OrdenCompraCrear,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_admin_o_encargado),
):
    items = [i.model_dump() for i in datos.items]
    try:
        orden = OrdenCompraService.crear_orden(
            db=db,
            proveedor_id=datos.proveedor_id,
            items=items,
            usuario_id=usuario.id,
            fecha_entrega_esperada=datos.fecha_entrega_esperada,
        )
        orden_completa = db.query(OrdenCompra).options(
            joinedload(OrdenCompra.proveedor),
            joinedload(OrdenCompra.items).joinedload(ItemCompra.producto),
        ).filter(OrdenCompra.id == orden.id).first()
        return _serializar(orden_completa, db, con_items=True)
    except OrdenInvalidaError as e:
        raise HTTPException(400, str(e))


@router.post("/{orden_id}/recibir", response_model=OrdenCompraRecibir)
def recibir_orden(
    orden_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_admin_o_encargado),
):
    try:
        return OrdenCompraService.recibir_orden(db=db, orden_id=orden_id, usuario_id=usuario.id)
    except OrdenInvalidaError as e:
        raise HTTPException(400, str(e))


@router.post("/{orden_id}/cancelar", response_model=dict)
def cancelar_orden(
    orden_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_admin_o_encargado),
):
    try:
        return OrdenCompraService.cancelar_orden(db=db, orden_id=orden_id, usuario_id=usuario.id)
    except OrdenInvalidaError as e:
        raise HTTPException(400, str(e))

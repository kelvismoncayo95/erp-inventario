from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.proveedor import Proveedor
from app.models.usuario import Usuario
from app.schemas.proveedor import (
    ProveedorCrear,
    ProveedorActualizar,
    ProveedorRespuesta,
)
from app.core.dependencies import (
    get_current_user,
    requerir_admin_o_encargado,
)


router = APIRouter(prefix="/proveedores", tags=["Proveedores"])


@router.get("/", response_model=List[ProveedorRespuesta])
def listar_proveedores(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return db.query(Proveedor).order_by(Proveedor.nombre).all()


@router.get("/{proveedor_id}", response_model=ProveedorRespuesta)
def obtener_proveedor(
    proveedor_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    prov = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
    if not prov:
        raise HTTPException(404, f"Proveedor {proveedor_id} no encontrado")
    return prov


@router.post("/", response_model=ProveedorRespuesta, status_code=status.HTTP_201_CREATED)
def crear_proveedor(
    datos: ProveedorCrear,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_admin_o_encargado),
):
    if datos.ruc:
        existente = db.query(Proveedor).filter(Proveedor.ruc == datos.ruc).first()
        if existente:
            raise HTTPException(400, f"Ya existe un proveedor con RUC '{datos.ruc}'")
    nuevo = Proveedor(**datos.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.put("/{proveedor_id}", response_model=ProveedorRespuesta)
def actualizar_proveedor(
    proveedor_id: int,
    datos: ProveedorActualizar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_admin_o_encargado),
):
    prov = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
    if not prov:
        raise HTTPException(404, f"Proveedor {proveedor_id} no encontrado")
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(prov, campo, valor)
    db.commit()
    db.refresh(prov)
    return prov


@router.delete("/{proveedor_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_proveedor(
    proveedor_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_admin_o_encargado),
):
    prov = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
    if not prov:
        raise HTTPException(404, f"Proveedor {proveedor_id} no encontrado")
    # Verificar si tiene órdenes de compra asociadas
    from app.models.orden_compra import OrdenCompra
    tiene_ordenes = db.query(OrdenCompra).filter(OrdenCompra.proveedor_id == proveedor_id).count()
    if tiene_ordenes > 0:
        raise HTTPException(400, f"No se puede eliminar: tiene {tiene_ordenes} órdenes de compra asociadas")
    db.delete(prov)
    db.commit()
    return None

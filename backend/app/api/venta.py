from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.database import get_db
from app.models.venta import Venta
from app.models.usuario import Usuario
from app.schemas.venta import VentaCrear, VentaRespuesta, VentaAnular
from app.services.venta_service import (
    VentaService,
    StockInsuficienteError,
    VentaInvalidaError,
    PermisoDenegadoError,
)
from app.core.dependencies import (
    get_current_user,
    requerir_vendedor_o_encargado,
)


router = APIRouter(prefix="/ventas", tags=["Ventas"])


@router.post("/", response_model=VentaRespuesta, status_code=status.HTTP_201_CREATED)
def crear_venta(
    venta: VentaCrear,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_vendedor_o_encargado),
):
    items = [{"producto_id": i.producto_id, "cantidad": i.cantidad} for i in venta.items]
    try:
        return VentaService.crear_venta(
            db=db, items=items, usuario_id=usuario.id,
            cliente_nombre=venta.cliente_nombre,
            cliente_telefono=venta.cliente_telefono,
        )
    except StockInsuficienteError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Error: {str(e)}")


@router.get("/", response_model=List[VentaRespuesta])
def listar_ventas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    query = db.query(Venta).options(joinedload(Venta.usuario))
    # El vendedor solo ve sus propias ventas
    if usuario.rol == "vendedor":
        query = query.filter(Venta.creado_por == usuario.id)
    ventas = query.order_by(Venta.id.desc()).offset(skip).limit(limit).all()
    resultado = []
    for v in ventas:
        d = VentaRespuesta.model_validate(v).model_dump()
        d["vendedor_nombre"] = v.usuario.nombre if v.usuario else None
        resultado.append(d)
    return resultado


@router.get("/{venta_id}", response_model=VentaRespuesta)
def obtener_venta(
    venta_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    venta = db.query(Venta).options(joinedload(Venta.usuario)).filter(Venta.id == venta_id).first()
    if not venta:
        raise HTTPException(404, f"Venta {venta_id} no encontrada")
    if usuario.rol == "vendedor" and venta.creado_por != usuario.id:
        raise HTTPException(403, "Solo puedes ver tus propias ventas")
    d = VentaRespuesta.model_validate(venta).model_dump()
    d["vendedor_nombre"] = venta.usuario.nombre if venta.usuario else None
    return d


# CAMBIO: admin también puede anular ventas.
# Se cambia la dependencia para aceptar cualquier usuario logueado y que
# el servicio aplique las reglas por rol (admin/encargado sin límite,
# vendedor solo propias <5min).
@router.post("/{venta_id}/anular", response_model=VentaAnular)
def anular_venta(
    venta_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    if usuario.rol not in ("admin", "encargado", "vendedor"):
        raise HTTPException(403, "Tu rol no permite anular ventas")
    try:
        return VentaService.anular_venta(
            db=db, venta_id=venta_id,
            usuario_id=usuario.id, rol_usuario=usuario.rol,
        )
    except PermisoDenegadoError as e:
        raise HTTPException(403, str(e))
    except VentaInvalidaError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Error: {str(e)}")

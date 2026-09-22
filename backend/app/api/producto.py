from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Union
from datetime import datetime

from app.database import get_db
from app.models.producto import Producto
from app.models.usuario import Usuario
from app.schemas.producto import (
    ProductoCrear,
    ProductoActualizar,
    ProductoRespuesta,
    ProductoRespuestaVendedor,
    ReactivarProducto,
)
from app.core.dependencies import (
    get_current_user,
    requerir_admin,
    requerir_admin_o_encargado,
)


router = APIRouter(prefix="/productos", tags=["Productos"])


def _serializar(producto: Producto, rol: str) -> dict:
    if rol == "vendedor":
        return ProductoRespuestaVendedor(
            id=producto.id,
            nombre=producto.nombre,
            sku=producto.sku,
            descripcion=producto.descripcion,
            precio_venta=producto.precio_venta,
            categoria_nombre=producto.categoria.nombre if producto.categoria else None,
            proveedor_nombre=producto.proveedor.nombre if producto.proveedor else None,
            disponible=(producto.stock_actual > 0 and producto.activo == 1),
        )
    return ProductoRespuesta.model_validate(producto)


# GET /productos/
@router.get("/", response_model=List[Union[ProductoRespuesta, ProductoRespuestaVendedor]])
def listar_productos(
    skip: int = 0,
    limit: int = 500,
    solo_activos: bool = True,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    query = db.query(Producto).options(
        joinedload(Producto.categoria),
        joinedload(Producto.proveedor),
    )
    if solo_activos:
        query = query.filter(Producto.activo == 1)
    productos = query.offset(skip).limit(limit).all()
    return [_serializar(p, usuario.rol) for p in productos]


# GET /productos/buscar/{codigo}
@router.get("/buscar/{codigo}", response_model=Union[ProductoRespuesta, ProductoRespuestaVendedor])
def buscar_por_codigo(
    codigo: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    producto = db.query(Producto).options(
        joinedload(Producto.categoria),
        joinedload(Producto.proveedor),
    ).filter(Producto.sku == codigo).first()
    if not producto:
        raise HTTPException(404, f"No se encontró producto con el código '{codigo}'")
    return _serializar(producto, usuario.rol)


# GET /productos/{id}
@router.get("/{producto_id}", response_model=Union[ProductoRespuesta, ProductoRespuestaVendedor])
def obtener_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    producto = db.query(Producto).options(
        joinedload(Producto.categoria),
        joinedload(Producto.proveedor),
    ).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(404, f"Producto {producto_id} no encontrado")
    return _serializar(producto, usuario.rol)


# POST /productos/  (admin y encargado)
@router.post("/", response_model=ProductoRespuesta, status_code=status.HTTP_201_CREATED)
def crear_producto(
    producto: ProductoCrear,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_admin_o_encargado),
):
    if db.query(Producto).filter(Producto.sku == producto.sku).first():
        raise HTTPException(400, f"Ya existe un producto con el SKU '{producto.sku}'")
    nuevo = Producto(**producto.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


# PUT /productos/{id}
@router.put("/{producto_id}", response_model=ProductoRespuesta)
def actualizar_producto(
    producto_id: int,
    datos: ProductoActualizar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_admin_o_encargado),
):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(404, f"Producto {producto_id} no encontrado")
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(producto, campo, valor)
    db.commit()
    db.refresh(producto)
    return producto


# DELETE /productos/{id}
# CAMBIO: admin y encargado pueden eliminar sin importar el stock.
# El producto NO se borra de la BD, solo se marca activo=0 con auditoría.
@router.delete("/{producto_id}", response_model=dict)
def eliminar_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_admin_o_encargado),
):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(404, f"Producto {producto_id} no encontrado")
    if producto.activo == 0:
        raise HTTPException(400, f"El producto '{producto.nombre}' ya estaba eliminado")
    producto.activo = 0
    producto.eliminado_por = usuario.id
    producto.fecha_eliminacion = datetime.utcnow()
    db.commit()
    return {
        "mensaje": f"Producto '{producto.nombre}' eliminado correctamente",
        "producto_id": producto.id,
        "eliminado_por": usuario.nombre,
    }


# POST /productos/{id}/reactivar  (requiere stock_inicial > 0)
@router.post("/{producto_id}/reactivar", response_model=ProductoRespuesta)
def reactivar_producto(
    producto_id: int,
    datos: ReactivarProducto,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_admin_o_encargado),
):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(404, f"Producto {producto_id} no encontrado")
    if producto.activo == 1:
        raise HTTPException(400, f"El producto '{producto.nombre}' ya está activo")
    producto.activo = 1
    producto.stock_actual = datos.stock_inicial
    producto.reactivado_por = usuario.id
    producto.fecha_reactivacion = datetime.utcnow()
    db.commit()
    db.refresh(producto)
    return producto

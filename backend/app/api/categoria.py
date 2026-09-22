"""
Endpoints para Categorías.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.categoria import Categoria
from app.schemas.categoria import (
    CategoriaCrear,
    CategoriaActualizar,
    CategoriaRespuesta,
)

router = APIRouter(prefix="/categorias", tags=["Categorías"])


@router.get("/", response_model=List[CategoriaRespuesta])
def listar_categorias(db: Session = Depends(get_db)):
    return db.query(Categoria).all()


@router.get("/{categoria_id}", response_model=CategoriaRespuesta)
def obtener_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(404, f"Categoría {categoria_id} no encontrada")
    return categoria


@router.post("/", response_model=CategoriaRespuesta, status_code=status.HTTP_201_CREATED)
def crear_categoria(categoria: CategoriaCrear, db: Session = Depends(get_db)):
    existente = db.query(Categoria).filter(Categoria.nombre == categoria.nombre).first()
    if existente:
        raise HTTPException(400, f"Ya existe una categoría con el nombre '{categoria.nombre}'")
    
    nueva = Categoria(**categoria.model_dump())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


@router.put("/{categoria_id}", response_model=CategoriaRespuesta)
def actualizar_categoria(
    categoria_id: int,
    datos: CategoriaActualizar,
    db: Session = Depends(get_db)
):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(404, f"Categoría {categoria_id} no encontrada")
    
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(categoria, campo, valor)
    
    db.commit()
    db.refresh(categoria)
    return categoria


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(404, f"Categoría {categoria_id} no encontrada")
    
    # Verificar que no tenga productos asociados
    from app.models.producto import Producto
    productos_asociados = db.query(Producto).filter(Producto.categoria_id == categoria_id).count()
    if productos_asociados > 0:
        raise HTTPException(
            400, 
            f"No se puede eliminar: hay {productos_asociados} producto(s) en esta categoría"
        )
    
    db.delete(categoria)
    db.commit()

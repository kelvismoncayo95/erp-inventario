"""
Endpoints de autenticación y gestión de usuarios.

- POST /auth/register         → Registro inicial (solo funciona si no hay usuarios)
- POST /auth/login            → Iniciar sesión
- GET  /auth/me               → Ver datos del usuario logueado
- GET  /auth/usuarios         → Listar usuarios (solo admin)
- POST /auth/usuarios         → Crear usuario (solo admin)
- GET  /auth/usuarios/{id}    → Ver usuario (solo admin)
- PUT  /auth/usuarios/{id}    → Actualizar usuario (solo admin)
- DELETE /auth/usuarios/{id}  → Desactivar usuario (solo admin)
- POST /auth/usuarios/{id}/activar → Reactivar usuario (solo admin)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import (
    UsuarioRegistrar,
    UsuarioCrear,
    UsuarioActualizar,
    UsuarioRespuesta,
    Token,
)
from app.core.security import hashear_password, verificar_password, crear_token_acceso
from app.core.dependencies import get_current_user, requerir_admin


router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"],
)


# ============================================
# POST /auth/register - Registro inicial
# ============================================
@router.post("/register", response_model=UsuarioRespuesta, status_code=status.HTTP_201_CREATED)
def registrar_usuario(usuario: UsuarioRegistrar, db: Session = Depends(get_db)):
    """
    Registro inicial del sistema.
    
    **Solo funciona si NO hay ningún usuario en la base de datos.**
    El primer usuario se crea como admin automáticamente.
    
    Después del primer admin, los usuarios se crean desde
    `POST /auth/usuarios` (que requiere ser admin).
    """
    # Verificar que NO existan usuarios (solo bootstrap)
    total_usuarios = db.query(Usuario).count()
    if total_usuarios > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El sistema ya tiene usuarios. Contacte al administrador."
        )
    
    # Crear el primer usuario como admin
    nuevo_usuario = Usuario(
        nombre=usuario.nombre,
        email=usuario.email,
        password_hash=hashear_password(usuario.password),
        rol="admin",
    )
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    return nuevo_usuario


# ============================================
# POST /auth/login - Iniciar sesión
# ============================================
@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Inicia sesión con email y contraseña.
    
    Devuelve un token JWT que debe enviarse en las siguientes peticiones
    en el header: `Authorization: Bearer <token>`
    """
    usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verificar_password(form_data.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo. Contacte al administrador."
        )
    
    token = crear_token_acceso(data={"sub": usuario.email, "rol": usuario.rol})
    
    return Token(
        access_token=token,
        token_type="bearer",
        usuario=usuario,
    )


# ============================================
# GET /auth/me - Ver usuario actual
# ============================================
@router.get("/me", response_model=UsuarioRespuesta)
def ver_usuario_actual(usuario: Usuario = Depends(get_current_user)):
    """Devuelve los datos del usuario logueado."""
    return usuario


# ============================================
# GET /auth/usuarios - Listar usuarios (solo admin)
# ============================================
@router.get("/usuarios", response_model=List[UsuarioRespuesta])
def listar_usuarios(
    db: Session = Depends(get_db),
    admin: Usuario = Depends(requerir_admin)
):
    """Lista todos los usuarios del sistema. Solo admin."""
    return db.query(Usuario).order_by(Usuario.id).all()


# ============================================
# POST /auth/usuarios - Crear usuario (solo admin)
# ============================================
@router.post("/usuarios", response_model=UsuarioRespuesta, status_code=status.HTTP_201_CREATED)
def crear_usuario(
    datos: UsuarioCrear,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(requerir_admin)
):
    """
    Crea un usuario nuevo (encargado o vendedor).
    Solo admin.
    """
    existente = db.query(Usuario).filter(Usuario.email == datos.email).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un usuario con el email '{datos.email}'"
        )
    
    nuevo = Usuario(
        nombre=datos.nombre,
        email=datos.email,
        password_hash=hashear_password(datos.password),
        rol=datos.rol,
    )
    
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    
    return nuevo


# ============================================
# GET /auth/usuarios/{id} - Ver usuario (solo admin)
# ============================================
@router.get("/usuarios/{usuario_id}", response_model=UsuarioRespuesta)
def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(requerir_admin)
):
    """Ver un usuario por ID. Solo admin."""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(404, f"Usuario {usuario_id} no encontrado")
    return usuario


# ============================================
# PUT /auth/usuarios/{id} - Actualizar (solo admin)
# ============================================
@router.put("/usuarios/{usuario_id}", response_model=UsuarioRespuesta)
def actualizar_usuario(
    usuario_id: int,
    datos: UsuarioActualizar,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(requerir_admin)
):
    """Actualiza datos de un usuario. Solo admin."""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(404, f"Usuario {usuario_id} no encontrado")
    
    # No permitir que el admin se desactive a sí mismo
    if usuario.id == admin.id and datos.activo == 0:
        raise HTTPException(400, "No puedes desactivarte a ti mismo")
    
    # Si cambia el email, verificar que no exista otro con ese email
    if datos.email and datos.email != usuario.email:
        existente = db.query(Usuario).filter(Usuario.email == datos.email).first()
        if existente:
            raise HTTPException(400, f"Ya existe un usuario con el email '{datos.email}'")
    
    # Actualizar campos (si vienen)
    if datos.nombre is not None:
        usuario.nombre = datos.nombre
    if datos.email is not None:
        usuario.email = datos.email
    if datos.password is not None:
        usuario.password_hash = hashear_password(datos.password)
    if datos.rol is not None:
        usuario.rol = datos.rol
    if datos.activo is not None:
        usuario.activo = datos.activo
    
    db.commit()
    db.refresh(usuario)
    return usuario


# ============================================
# DELETE /auth/usuarios/{id} - Desactivar (solo admin)
# ============================================
@router.delete("/usuarios/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def desactivar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(requerir_admin)
):
    """
    Desactiva un usuario (borrado lógico).
    Solo admin. No puede desactivarse a sí mismo.
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(404, f"Usuario {usuario_id} no encontrado")
    
    if usuario.id == admin.id:
        raise HTTPException(400, "No puedes desactivarte a ti mismo")
    
    usuario.activo = 0
    db.commit()
    return None


# ============================================
# POST /auth/usuarios/{id}/activar - Reactivar (solo admin)
# ============================================
@router.post("/usuarios/{usuario_id}/activar", response_model=UsuarioRespuesta)
def reactivar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(requerir_admin)
):
    """Reactiva un usuario inactivo. Solo admin."""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(404, f"Usuario {usuario_id} no encontrado")
    
    usuario.activo = 1
    db.commit()
    db.refresh(usuario)
    return usuario

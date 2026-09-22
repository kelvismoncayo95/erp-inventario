"""
Dependencias de seguridad para FastAPI.
Aquí se valida el usuario actual y los roles.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.core.security import decodificar_token
from app.models.usuario import Usuario


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# ============================================
# USUARIO ACTUAL (cualquier rol)
# ============================================
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Usuario:
    """Obtiene el usuario actual a partir del token JWT."""
    credenciales_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decodificar_token(token)
    if payload is None:
        raise credenciales_invalidas
    
    email: Optional[str] = payload.get("sub")
    if email is None:
        raise credenciales_invalidas
    
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if usuario is None:
        raise credenciales_invalidas
    
    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    return usuario


# ============================================
# SOLO ADMIN
# ============================================
def requerir_admin(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    """Solo admin. Se usa para gestionar usuarios y ver reportes completos."""
    if usuario.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de administrador"
        )
    return usuario


# ============================================
# ADMIN O ENCARGADO
# ============================================
def requerir_admin_o_encargado(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    """Admin o encargado. Se usa para recibir mercadería, ver stock, etc."""
    if usuario.rol not in ("admin", "encargado"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de administrador o encargado"
        )
    return usuario


# ============================================
# CUALQUIERA QUE PUEDA VENDER (admin no vende)
# ============================================
def requerir_vendedor_o_encargado(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    """Vendedor o encargado. Se usa para crear ventas (admin NO vende)."""
    if usuario.rol not in ("vendedor", "encargado"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de vendedor o encargado"
        )
    return usuario

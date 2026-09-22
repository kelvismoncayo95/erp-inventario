"""
Schemas de Usuario para autenticación y gestión.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


# ============================================
# ROLES VÁLIDOS DEL SISTEMA
# ============================================
ROLES_VALIDOS = ["admin", "encargado", "vendedor"]


# ============================================
# REGISTRO PÚBLICO (solo para el primer admin)
# ============================================
class UsuarioRegistrar(BaseModel):
    """Schema para el registro inicial (bootstrap del primer admin)."""
    nombre: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(..., description="Email válido")
    password: str = Field(..., min_length=4, max_length=100)
    rol: str = Field("admin", pattern="^(admin|encargado|vendedor)$")


# ============================================
# CREAR USUARIO (lo hace el admin)
# ============================================
class UsuarioCrear(BaseModel):
    """Schema para que el admin cree un usuario."""
    nombre: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(..., description="Email válido")
    password: str = Field(..., min_length=4, max_length=100)
    rol: str = Field(..., pattern="^(encargado|vendedor)$", description="Solo encargado o vendedor")


# ============================================
# ACTUALIZAR USUARIO
# ============================================
class UsuarioActualizar(BaseModel):
    """Schema para actualizar datos de un usuario (opcional)."""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=4, max_length=100)
    rol: Optional[str] = Field(None, pattern="^(admin|encargado|vendedor)$")
    activo: Optional[int] = Field(None, ge=0, le=1)


# ============================================
# LOGIN
# ============================================
class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str


# ============================================
# RESPUESTA
# ============================================
class UsuarioRespuesta(BaseModel):
    id: int
    nombre: str
    email: str
    rol: str
    activo: int
    creado_en: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioRespuesta

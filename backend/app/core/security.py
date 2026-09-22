"""
Seguridad: JWT, hashing de contraseñas, tokens.
Los valores sensibles vienen del .env (nunca hardcodeados).
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

# ============================================
# CONFIGURACIÓN (desde .env)
# ============================================
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "❌ SECRET_KEY no configurada. Copia .env.example a .env y define la tuya."
    )

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================
# CONTRASEÑAS
# ============================================
def hashear_password(password: str) -> str:
    """Convierte una contraseña plana en hash bcrypt."""
    return pwd_context.hash(password)


def verificar_password(plain_password: str, hashed_password: str) -> bool:
    """Compara contraseña plana contra hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ============================================
# TOKENS JWT
# ============================================
def crear_token_acceso(data: dict) -> str:
    """Genera un JWT firmado con expiración."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decodificar_token(token: str) -> Optional[dict]:
    """Decodifica un JWT. Devuelve None si es inválido o expirado."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

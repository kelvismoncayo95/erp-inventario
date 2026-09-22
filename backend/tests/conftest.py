"""
Fixtures compartidas por todos los tests.
Una fixture es un dato o setup que pytest inyecta automáticamente.
"""
import pytest
from app.core.security import hashear_password


@pytest.fixture
def password_valida():
    """Contraseña de prueba en texto plano."""
    return "MiPassword123"


@pytest.fixture
def hash_ejemplo(password_valida):
    """Hash bcrypt de la contraseña de prueba (se genera una vez por test)."""
    return hashear_password(password_valida)


@pytest.fixture
def usuario_datos():
    """Datos típicos de usuario para tests."""
    return {
        "nombre": "Juan Test",
        "email": "test@erp.com",
        "password": "TestPassword123",
        "rol": "vendedor",
    }

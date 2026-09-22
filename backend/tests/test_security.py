"""
Tests unitarios del módulo de seguridad.
NO tocan la base de datos: prueban funciones puras.
"""
from app.core.security import (
    hashear_password,
    verificar_password,
    crear_token_acceso,
    decodificar_token,
)


class TestPasswords:
    """Tests de hashing de contraseñas."""

    def test_hash_genera_string_distinto(self, password_valida):
        """El hash nunca debe ser igual a la contraseña original."""
        hashed = hashear_password(password_valida)
        assert hashed != password_valida
        assert len(hashed) > 20
        assert hashed.startswith("$2b$")

    def test_verificar_password_correcta(self, password_valida, hash_ejemplo):
        """Con la contraseña correcta, la verificación debe pasar."""
        assert verificar_password(password_valida, hash_ejemplo) is True

    def test_verificar_password_incorrecta(self, hash_ejemplo):
        """Con una contraseña incorrecta, la verificación debe fallar."""
        assert verificar_password("otra_cosa", hash_ejemplo) is False

    def test_dos_hashes_de_la_misma_password_son_distintos(self, password_valida):
        """bcrypt usa salt aleatorio: dos hashes del mismo texto son distintos."""
        h1 = hashear_password(password_valida)
        h2 = hashear_password(password_valida)
        assert h1 != h2


class TestTokens:
    """Tests de creación y decodificación de tokens JWT."""

    def test_crear_y_decodificar_token(self):
        """Un token creado debe decodificarse correctamente."""
        data = {"sub": "test@erp.com", "rol": "admin"}
        token = crear_token_acceso(data)
        assert isinstance(token, str)
        assert len(token) > 50

        payload = decodificar_token(token)
        assert payload is not None
        assert payload["sub"] == "test@erp.com"
        assert payload["rol"] == "admin"
        assert "exp" in payload

    def test_token_invalido_devuelve_none(self):
        """Un string que no es JWT debe devolver None."""
        assert decodificar_token("esto.no.es.un.jwt") is None

    def test_token_falsificado_devuelve_none(self):
        """
        Un token modificado debe fallar la verificación de firma.

        Modificamos un carácter en el MEDIO del token (no el último),
        porque base64url puede tener bits sin usar al final y cambiar
        ese carácter no alteraría los bytes decodificados.
        """
        token = crear_token_acceso({"sub": "user@test.com"})
        medio = len(token) // 2
        caracter_original = token[medio]
        caracter_nuevo = "X" if caracter_original != "X" else "Y"
        token_roto = token[:medio] + caracter_nuevo + token[medio + 1:]
        assert token_roto != token
        assert decodificar_token(token_roto) is None


class TestSchemas:
    """Tests de validación de schemas Pydantic."""

    def test_usuario_crear_con_datos_validos(self, usuario_datos):
        from app.schemas.usuario import UsuarioCrear
        u = UsuarioCrear(**usuario_datos)
        assert u.email == "test@erp.com"
        assert u.rol == "vendedor"

    def test_usuario_crear_con_email_invalido_falla(self, usuario_datos):
        from app.schemas.usuario import UsuarioCrear
        from pydantic import ValidationError
        import pytest

        datos = usuario_datos.copy()
        datos["email"] = "no-es-un-email"
        with pytest.raises(ValidationError):
            UsuarioCrear(**datos)

    def test_producto_crear_con_precio_negativo_falla(self):
        from app.schemas.producto import ProductoCrear
        from pydantic import ValidationError
        import pytest

        with pytest.raises(ValidationError):
            ProductoCrear(
                nombre="Test",
                sku="TEST-001",
                precio_costo=-5,
                precio_venta=10,
            )

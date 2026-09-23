from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Usuario(Base):
    """Modelo de Usuario del sistema."""
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    rol = Column(String(20), default="vendedor")  # admin, encargado, vendedor
    activo = Column(Integer, default=1)
    creado_en = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    ventas = relationship("Venta", back_populates="usuario")

    def __repr__(self):
        return f"<Usuario {self.email} ({self.rol})>"

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Proveedor(Base):
    """Modelo de Proveedor."""
    __tablename__ = "proveedores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    ruc = Column(String(20), unique=True)
    telefono = Column(String(20))
    email = Column(String(100))
    direccion = Column(String(255))
    contacto = Column(String(100))
    creado_en = Column(DateTime, default=datetime.now(timezone.utc))

    # Relaciones
    productos = relationship("Producto", back_populates="proveedor")
    ordenes_compra = relationship("OrdenCompra", back_populates="proveedor")

    def __repr__(self):
        return f"<Proveedor {self.nombre}>"

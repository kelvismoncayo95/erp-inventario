from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class OrdenCompra(Base):
    """Modelo de Orden de Compra a proveedores."""
    __tablename__ = "ordenes_compra"

    id = Column(Integer, primary_key=True, index=True)
    numero_orden = Column(String(20), unique=True)
    fecha = Column(DateTime, default=datetime.now(timezone.utc))
    fecha_entrega_esperada = Column(DateTime)
    total = Column(Numeric(10, 2), nullable=False)
    estado = Column(String(20), default="pendiente")  # pendiente, recibida, cancelada

    proveedor_id = Column(Integer, ForeignKey("proveedores.id"))
    creado_por = Column(Integer, ForeignKey("usuarios.id"))
    creado_en = Column(DateTime, default=datetime.now(timezone.utc))

    # Relaciones
    proveedor = relationship("Proveedor", back_populates="ordenes_compra")
    items = relationship("ItemCompra", back_populates="orden", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<OrdenCompra #{self.id} - {self.estado}>"

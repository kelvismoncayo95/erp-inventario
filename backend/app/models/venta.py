from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Venta(Base):
    """Modelo de Venta."""
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True, index=True)
    numero_factura = Column(String(20), unique=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    subtotal = Column(Numeric(10, 2), nullable=False)
    iva = Column(Numeric(10, 2), default=0)
    total = Column(Numeric(10, 2), nullable=False)
    estado = Column(String(20), default="completada")

    # Datos del cliente (opcionales)
    cliente_nombre = Column(String(200))
    cliente_telefono = Column(String(20))

    # Auditoría
    creado_por = Column(Integer, ForeignKey("usuarios.id"))
    creado_en = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    usuario = relationship("Usuario", back_populates="ventas")
    items = relationship("ItemVenta", back_populates="venta", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Venta #{self.id} - Total: {self.total}>"

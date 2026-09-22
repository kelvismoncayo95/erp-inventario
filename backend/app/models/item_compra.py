from sqlalchemy import Column, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class ItemCompra(Base):
    """Modelo de Item de Compra (producto dentro de una orden de compra)."""
    __tablename__ = "items_compra"

    id = Column(Integer, primary_key=True, index=True)
    orden_id = Column(Integer, ForeignKey("ordenes_compra.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)

    # Relaciones
    orden = relationship("OrdenCompra", back_populates="items")
    producto = relationship("Producto", back_populates="items_compra")

    def __repr__(self):
        return f"<ItemCompra Producto:{self.producto_id} x{self.cantidad}>"

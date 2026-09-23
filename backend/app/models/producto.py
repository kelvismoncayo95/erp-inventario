from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    sku = Column(String(50), unique=True, nullable=False)
    descripcion = Column(String(500))
    precio_costo = Column(Numeric(10, 2), nullable=False)
    precio_venta = Column(Numeric(10, 2), nullable=False)
    stock_actual = Column(Integer, default=0)
    stock_minimo = Column(Integer, default=5)
    stock_maximo = Column(Integer, default=100)
    activo = Column(Integer, default=1)
    creado_en = Column(DateTime, default=datetime.utcnow)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"))
    # Auditoría de eliminación / reactivación
    eliminado_por = Column(Integer, ForeignKey("usuarios.id"))
    fecha_eliminacion = Column(DateTime)
    reactivado_por = Column(Integer, ForeignKey("usuarios.id"))
    fecha_reactivacion = Column(DateTime)

    categoria = relationship("Categoria", back_populates="productos")
    proveedor = relationship("Proveedor", back_populates="productos")
    items_venta = relationship("ItemVenta", back_populates="producto")
    items_compra = relationship("ItemCompra", back_populates="producto")

    def __repr__(self):
        return f"<Producto {self.nombre} (SKU: {self.sku})>"

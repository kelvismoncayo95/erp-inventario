"""
Script para crear todas las tablas en PostgreSQL.
Se ejecuta UNA SOLA VEZ para crear la estructura inicial.
"""
from app.database import engine, Base

# IMPORTANTE: importar los modelos para que SQLAlchemy los "vea"
from app.models import (
    Usuario,
    Categoria,
    Proveedor,
    Producto,
    Venta,
    ItemVenta,
    OrdenCompra,
    ItemCompra,
)

print("🔧 Creando tablas en PostgreSQL...")

# Crear todas las tablas
Base.metadata.create_all(bind=engine)

print("✅ Tablas creadas exitosamente")
print("")
print("📋 Tablas en la base de datos:")
for tabla in Base.metadata.sorted_tables:
    print(f"  - {tabla.name}")

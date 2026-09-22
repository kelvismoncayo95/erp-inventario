"""
Script para insertar datos de prueba en la base de datos.
"""
from app.database import SessionLocal
from app.models import Usuario, Categoria, Proveedor, Producto

# Crear una sesión
db = SessionLocal()

try:
    print("🔧 Insertando datos de prueba...")
    print("")

    # 1. Crear un usuario admin
    admin = Usuario(
        nombre="Administrador",
        email="admin@erp.com",
        password_hash="hash_de_prueba_123",  # En el proyecto real, esto será encriptado
        rol="admin"
    )
    db.add(admin)
    print("✅ Usuario admin creado")

    # 2. Crear un vendedor
    vendedor = Usuario(
        nombre="Juan Vendedor",
        email="vendedor@erp.com",
        password_hash="hash_de_prueba_456",
        rol="vendedor"
    )
    db.add(vendedor)
    print("✅ Usuario vendedor creado")

    # 3. Crear categorías
    categoria_bebidas = Categoria(
        nombre="Bebidas",
        descripcion="Bebidas frías y calientes"
    )
    categoria_snacks = Categoria(
        nombre="Snacks",
        descripcion="Papas, galletas y más"
    )
    db.add(categoria_bebidas)
    db.add(categoria_snacks)
    print("✅ Categorías creadas")

    # 4. Crear proveedores
    proveedor1 = Proveedor(
        nombre="Distribuidora del Sur",
        ruc="123456789",
        telefono="099123456",
        email="ventas@delsur.com",
        direccion="Av. 18 de Julio 1234",
        contacto="María González"
    )
    proveedor2 = Proveedor(
        nombre="Alimentos del Este",
        ruc="987654321",
        telefono="099654321",
        email="info@alimentoseste.com",
        direccion="Bulevar Artigas 5678",
        contacto="Carlos Rodríguez"
    )
    db.add(proveedor1)
    db.add(proveedor2)
    print("✅ Proveedores creados")

    # 5. Hacer commit para obtener los IDs
    db.commit()

    # Refrescar para obtener los IDs generados
    db.refresh(categoria_bebidas)
    db.refresh(categoria_snacks)
    db.refresh(proveedor1)
    db.refresh(proveedor2)

    print(f"   - Categoría Bebidas ID: {categoria_bebidas.id}")
    print(f"   - Categoría Snacks ID: {categoria_snacks.id}")
    print(f"   - Proveedor 1 ID: {proveedor1.id}")
    print(f"   - Proveedor 2 ID: {proveedor2.id}")

    # 6. Crear productos
    producto1 = Producto(
        nombre="Coca-Cola 500ml",
        sku="COCA-500",
        descripcion="Botella de Coca-Cola de 500ml",
        precio_costo=25.00,
        precio_venta=45.00,
        stock_actual=100,
        stock_minimo=10,
        stock_maximo=200,
        categoria_id=categoria_bebidas.id,
        proveedor_id=proveedor1.id
    )
    producto2 = Producto(
        nombre="Papas Fritas Lays",
        sku="LAYS-001",
        descripcion="Paquete de papas fritas 150g",
        precio_costo=30.00,
        precio_venta=60.00,
        stock_actual=50,
        stock_minimo=5,
        stock_maximo=100,
        categoria_id=categoria_snacks.id,
        proveedor_id=proveedor2.id
    )
    producto3 = Producto(
        nombre="Agua Mineral 600ml",
        sku="AGUA-600",
        descripcion="Botella de agua mineral",
        precio_costo=15.00,
        precio_venta=30.00,
        stock_actual=200,
        stock_minimo=20,
        stock_maximo=500,
        categoria_id=categoria_bebidas.id,
        proveedor_id=proveedor1.id
    )
    db.add(producto1)
    db.add(producto2)
    db.add(producto3)

    db.commit()
    print("✅ Productos creados")

    print("")
    print("🎉 ¡Datos de prueba insertados exitosamente!")
    print("")
    print("📊 Resumen:")
    print(f"  - Usuarios: 2")
    print(f"  - Categorías: 2")
    print(f"  - Proveedores: 2")
    print(f"  - Productos: 3")

except Exception as e:
    db.rollback()
    print(f"❌ Error: {e}")
    raise
finally:
    db.close()

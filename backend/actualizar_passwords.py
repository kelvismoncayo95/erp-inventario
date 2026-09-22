"""
Script para actualizar/crear usuarios de prueba.
"""
from app.database import SessionLocal
from app.models.usuario import Usuario
from app.core.security import hashear_password

db = SessionLocal()

try:
    print("🔧 Actualizando usuarios de prueba...")
    print("")

    # Admin
    admin = db.query(Usuario).filter(Usuario.email == "admin@erp.com").first()
    if admin:
        admin.password_hash = hashear_password("admin123")
        admin.rol = "admin"
        print("✅ Admin: admin@erp.com / admin123")
    else:
        admin = Usuario(
            nombre="Administrador",
            email="admin@erp.com",
            password_hash=hashear_password("admin123"),
            rol="admin",
        )
        db.add(admin)
        print("✅ Admin creado: admin@erp.com / admin123")

    # Vendedor
    vendedor = db.query(Usuario).filter(Usuario.email == "vendedor@erp.com").first()
    if vendedor:
        vendedor.password_hash = hashear_password("vendedor123")
        vendedor.rol = "vendedor"
        print("✅ Vendedor: vendedor@erp.com / vendedor123")
    else:
        vendedor = Usuario(
            nombre="Juan Vendedor",
            email="vendedor@erp.com",
            password_hash=hashear_password("vendedor123"),
            rol="vendedor",
        )
        db.add(vendedor)
        print("✅ Vendedor creado: vendedor@erp.com / vendedor123")

    # Proveedor (NUEVO)
    proveedor = db.query(Usuario).filter(Usuario.email == "proveedor@erp.com").first()
    if proveedor:
        proveedor.password_hash = hashear_password("proveedor123")
        proveedor.rol = "proveedor"
        print("✅ Proveedor: proveedor@erp.com / proveedor123")
    else:
        proveedor = Usuario(
            nombre="Distribuidora del Sur",
            email="proveedor@erp.com",
            password_hash=hashear_password("proveedor123"),
            rol="proveedor",
        )
        db.add(proveedor)
        print("✅ Proveedor creado: proveedor@erp.com / proveedor123")

    db.commit()
    print("")
    print("🎉 Usuarios listos")

except Exception as e:
    db.rollback()
    print(f"❌ Error: {e}")
    raise
finally:
    db.close()

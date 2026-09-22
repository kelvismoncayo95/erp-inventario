"""
Archivo principal de FastAPI.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base

# Importar los modelos para que SQLAlchemy los "vea"
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

# Importar los routers (endpoints)
from app.api import auth, producto, venta, reporte, categoria


# ============================================
# Crear las tablas (si no existen)
# ============================================
Base.metadata.create_all(bind=engine)


# ============================================
# Crear la aplicación FastAPI
# ============================================
app = FastAPI(
    title="ERP Inventario API",
    description="Sistema de gestión de inventario y ventas",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# ============================================
# Configurar CORS
# ============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Registrar los routers
# ============================================
app.include_router(auth.router)
app.include_router(producto.router)
app.include_router(venta.router)
app.include_router(reporte.router)
app.include_router(categoria.router)

# ============================================
# Rutas principales
# ============================================
@app.get("/", tags=["Inicio"])
def raiz():
    return {
        "mensaje": "ERP Inventario API",
        "version": "1.0.0",
        "estado": "🟢 Funcionando",
        "documentacion": "/docs"
    }


@app.get("/health", tags=["Inicio"])
def health_check():
    return {
        "status": "ok",
        "database": "conectada"
    }

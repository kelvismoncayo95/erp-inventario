"""
Punto de entrada de la aplicación FastAPI.
Registra routers, CORS, logging y rate limiting.
"""
import time
from sqlalchemy import text
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Logging (debe ir ANTES de cualquier otro import que use logger)
from app.core.logging_config import logger

# Rate limiting
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.rate_limit import limiter

# Routers
from app.api import (
    auth,
    producto,
    venta,
    reporte,
    categoria,
    proveedor,
    orden_compra,
)


# ============================================
# APP
# ============================================
app = FastAPI(
    title="ERP Inventario",
    description="Sistema de gestión de inventario, ventas y compras",
    version="1.0.0",
)

# Estado global para slowapi
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ============================================
# CORS
# ============================================
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://.*:5500|http://localhost:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# MIDDLEWARE DE LOGGING
# ============================================
@app.middleware("http")
async def registrar_requests(request: Request, call_next):
    """Registra cada request: método, ruta, status, duración."""
    inicio = time.time()
    try:
        response = await call_next(request)
        duracion_ms = (time.time() - inicio) * 1000
        logger.info(
            f"{request.method} {request.url.path} → {response.status_code} "
            f"({duracion_ms:.1f}ms)"
        )
        return response
    except Exception as e:
        duracion_ms = (time.time() - inicio) * 1000
        logger.error(
            f"{request.method} {request.url.path} → ERROR "
            f"({duracion_ms:.1f}ms): {type(e).__name__}: {e}"
        )
        raise


# ============================================
# ROUTERS
# ============================================
app.include_router(auth.router)
app.include_router(producto.router)
app.include_router(venta.router)
app.include_router(reporte.router)
app.include_router(categoria.router)
app.include_router(proveedor.router)
app.include_router(orden_compra.router)


# ============================================
# ENDPOINTS BÁSICOS
# ============================================
@app.get("/", tags=["Health"])
def raiz():
    return {"app": "ERP Inventario", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
def health():
    from app.database import SessionLocal
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        estado_db = "conectada"
    except Exception as e:
        logger.error(f"DB health check falló: {e}")
        estado_db = "error"
    return {"status": "ok", "database": estado_db}

"""
Configuración centralizada de logging.
Los logs van a consola Y a archivo (logs/erp.log).
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Crear carpeta de logs si no existe
LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "erp.log"


def configurar_logging():
    """
    Configura el logger raíz.
    - Consola: todo desde INFO
    - Archivo: rota a los 5MB, guarda 3 backups (15MB máx)
    """
    formato = "[%(asctime)s] %(levelname)s %(name)s: %(message)s"
    formatter = logging.Formatter(formato, datefmt="%Y-%m-%d %H:%M:%S")

    # Handler 1: consola
    consola = logging.StreamHandler(sys.stdout)
    consola.setFormatter(formatter)
    consola.setLevel(logging.INFO)

    # Handler 2: archivo con rotación
    archivo = RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    archivo.setFormatter(formatter)
    archivo.setLevel(logging.INFO)

    # Configurar el logger raíz
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    # Limpiar handlers previos (por si se llama 2 veces)
    root.handlers.clear()
    root.addHandler(consola)
    root.addHandler(archivo)

    # Bajar el ruido de librerías externas
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    return logging.getLogger("erp")


logger = configurar_logging()

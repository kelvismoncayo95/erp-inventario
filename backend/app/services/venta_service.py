"""
Servicio de Ventas.
Lógica transaccional de ventas y anulaciones.
"""
import os
from sqlalchemy.orm import Session
from sqlalchemy import select
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

from app.models.producto import Producto
from app.models.venta import Venta
from app.models.item_venta import ItemVenta


# ============================================
# CONFIGURACIÓN (desde .env)
# ============================================
load_dotenv()

MINUTOS_ANULACION_VENDEDOR = int(os.getenv("MINUTOS_ANULACION_VENDEDOR", "5"))
IVA_PORCENTAJE = Decimal(os.getenv("IVA_PORCENTAJE", "22")) / Decimal("100")


# ============================================
# EXCEPCIONES
# ============================================
class StockInsuficienteError(Exception):
    pass


class VentaInvalidaError(Exception):
    pass


class PermisoDenegadoError(Exception):
    pass


class VentaService:

    @staticmethod
    def crear_venta(db, items, usuario_id, cliente_nombre=None, cliente_telefono=None):
        try:
            items_procesados = []
            subtotal_total = Decimal("0.00")

            for item in items:
                producto_id = item["producto_id"]
                cantidad = item["cantidad"]

                producto = db.execute(
                    select(Producto)
                    .where(Producto.id == producto_id)
                    .with_for_update()
                ).scalar_one_or_none()

                if producto is None:
                    raise StockInsuficienteError(f"Producto con ID {producto_id} no existe")
                if not producto.activo:
                    raise StockInsuficienteError(f"El producto '{producto.nombre}' está inactivo")
                if producto.stock_actual < cantidad:
                    raise StockInsuficienteError(
                        f"Stock insuficiente para '{producto.nombre}'. "
                        f"Disponible: {producto.stock_actual}, solicitado: {cantidad}"
                    )

                precio_unitario = producto.precio_venta
                subtotal = precio_unitario * cantidad
                subtotal_total += subtotal

                items_procesados.append({
                    "producto": producto,
                    "cantidad": cantidad,
                    "precio_unitario": precio_unitario,
                    "subtotal": subtotal,
                })

            iva = subtotal_total * IVA_PORCENTAJE
            total = subtotal_total + iva

            venta = Venta(
                numero_factura=f"V-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                subtotal=subtotal_total,
                iva=iva,
                total=total,
                estado="completada",
                cliente_nombre=cliente_nombre,
                cliente_telefono=cliente_telefono,
                creado_por=usuario_id,
            )
            db.add(venta)
            db.flush()

            for item in items_procesados:
                producto = item["producto"]
                item_venta = ItemVenta(
                    venta_id=venta.id,
                    producto_id=producto.id,
                    cantidad=item["cantidad"],
                    precio_unitario=item["precio_unitario"],
                    subtotal=item["subtotal"],
                )
                db.add(item_venta)
                producto.stock_actual -= item["cantidad"]

            db.commit()
            db.refresh(venta)
            return venta

        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def anular_venta(db: Session, venta_id: int, usuario_id: int, rol_usuario: str) -> dict:
        """
        Anula una venta y devuelve el stock.

        Reglas por rol:
        - **admin**: sin límite de tiempo, cualquier venta
        - **encargado**: sin límite de tiempo, cualquier venta
        - **vendedor**: solo las propias, dentro de los primeros 5 minutos
        """
        try:
            venta = db.query(Venta).filter(Venta.id == venta_id).first()
            if not venta:
                raise VentaInvalidaError(f"Venta con ID {venta_id} no encontrada.")

            if venta.estado == "anulada":
                raise VentaInvalidaError(f"La venta {venta.numero_factura} ya está anulada.")

            if rol_usuario == "vendedor":
                # Solo puede anular sus propias ventas
                if venta.creado_por != usuario_id:
                    raise PermisoDenegadoError(
                        "Solo puedes anular ventas que tú mismo hayas realizado."
                    )
                # Solo dentro de los 5 minutos
                ahora = datetime.now(timezone.utc)
                minutos = (ahora - venta.fecha).total_seconds() / 60
                if minutos > MINUTOS_ANULACION_VENDEDOR:
                    raise PermisoDenegadoError(
                        f"Como vendedor, solo puedes anular ventas dentro de los "
                        f"primeros {MINUTOS_ANULACION_VENDEDOR} minutos. "
                        f"Esta venta tiene {minutos:.1f} minutos. "
                        f"Contacta a un encargado o administrador."
                    )

            if rol_usuario not in ("admin", "encargado", "vendedor"):
                raise PermisoDenegadoError("Tu rol no permite anular ventas.")

            stock_devuelto = []
            for item in venta.items:
                producto = db.execute(
                    select(Producto)
                    .where(Producto.id == item.producto_id)
                    .with_for_update()
                ).scalar_one_or_none()
                if producto:
                    producto.stock_actual += item.cantidad
                    stock_devuelto.append({
                        "producto_id": producto.id,
                        "nombre": producto.nombre,
                        "cantidad_devuelta": item.cantidad,
                        "nuevo_stock": producto.stock_actual,
                    })

            venta.estado = "anulada"
            db.commit()
            db.refresh(venta)

            return {
                "mensaje": f"Venta {venta.numero_factura} anulada exitosamente.",
                "venta_id": venta.id,
                "nuevo_estado": venta.estado,
                "stock_devuelto": stock_devuelto,
            }

        except (VentaInvalidaError, PermisoDenegadoError):
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise VentaInvalidaError(f"Error al anular la venta: {str(e)}")

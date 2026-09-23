"""
Servicio de Órdenes de Compra.
Lógica transaccional para compras y entrada de stock.
"""
from sqlalchemy.orm import Session
from sqlalchemy import select
from decimal import Decimal
from datetime import datetime, timezone

from app.models.producto import Producto
from app.models.orden_compra import OrdenCompra
from app.models.item_compra import ItemCompra


class OrdenInvalidaError(Exception):
    """Error cuando una orden no puede procesarse."""
    pass


class OrdenCompraService:

    @staticmethod
    def crear_orden(
        db: Session,
        proveedor_id: int,
        items: list,
        usuario_id: int,
        fecha_entrega_esperada=None,
    ) -> OrdenCompra:
        """
        Crea una orden de compra en estado 'pendiente'.
        NO modifica el stock todavía — eso pasa al recibirla.
        """
        try:
            items_procesados = []
            total = Decimal("0.00")

            for item in items:
                producto = db.query(Producto).filter(Producto.id == item["producto_id"]).first()
                if not producto:
                    raise OrdenInvalidaError(f"Producto {item['producto_id']} no existe")

                precio_unitario = Decimal(str(item["precio_unitario"]))
                cantidad = int(item["cantidad"])
                subtotal = precio_unitario * cantidad
                total += subtotal

                items_procesados.append({
                    "producto_id": producto.id,
                    "cantidad": cantidad,
                    "precio_unitario": precio_unitario,
                    "subtotal": subtotal,
                })

            orden = OrdenCompra(
                numero_orden=f"OC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                total=total,
                estado="pendiente",
                proveedor_id=proveedor_id,
                creado_por=usuario_id,
                fecha_entrega_esperada=fecha_entrega_esperada,
            )
            db.add(orden)
            db.flush()

            for it in items_procesados:
                ic = ItemCompra(
                    orden_id=orden.id,
                    producto_id=it["producto_id"],
                    cantidad=it["cantidad"],
                    precio_unitario=it["precio_unitario"],
                    subtotal=it["subtotal"],
                )
                db.add(ic)

            db.commit()
            db.refresh(orden)
            return orden

        except OrdenInvalidaError:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise OrdenInvalidaError(f"Error al crear orden: {str(e)}")

    @staticmethod
    def recibir_orden(db: Session, orden_id: int, usuario_id: int) -> dict:
        """
        Marca la orden como 'recibida' y SUMA el stock de cada producto.
        También actualiza el precio de costo del producto al último recibido.
        TRANSACCIÓN: todo o nada.
        """
        try:
            orden = db.query(OrdenCompra).filter(OrdenCompra.id == orden_id).first()
            if not orden:
                raise OrdenInvalidaError(f"Orden {orden_id} no encontrada")
            if orden.estado != "pendiente":
                raise OrdenInvalidaError(
                    f"Solo se pueden recibir órdenes 'pendientes'. Esta está '{orden.estado}'."
                )

            items_actualizados = []
            for item in orden.items:
                producto = db.execute(
                    select(Producto)
                    .where(Producto.id == item.producto_id)
                    .with_for_update()
                ).scalar_one_or_none()

                if not producto:
                    raise OrdenInvalidaError(
                        f"Producto {item.producto_id} ya no existe en el catálogo"
                    )

                producto.stock_actual += item.cantidad
                producto.precio_costo = item.precio_unitario

                items_actualizados.append({
                    "producto_id": producto.id,
                    "nombre": producto.nombre,
                    "cantidad_sumada": item.cantidad,
                    "nuevo_stock": producto.stock_actual,
                })

            orden.estado = "recibida"
            db.commit()
            db.refresh(orden)

            return {
                "mensaje": f"Orden {orden.numero_orden} recibida. Stock actualizado.",
                "orden_id": orden.id,
                "estado": orden.estado,
                "items_actualizados": items_actualizados,
            }

        except OrdenInvalidaError:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise OrdenInvalidaError(f"Error al recibir orden: {str(e)}")

    @staticmethod
    def cancelar_orden(db: Session, orden_id: int, usuario_id: int) -> dict:
        """
        Cancela una orden pendiente. NO toca stock (nunca se sumó).
        """
        try:
            orden = db.query(OrdenCompra).filter(OrdenCompra.id == orden_id).first()
            if not orden:
                raise OrdenInvalidaError(f"Orden {orden_id} no encontrada")
            if orden.estado != "pendiente":
                raise OrdenInvalidaError(
                    f"Solo se pueden cancelar órdenes 'pendientes'. Esta está '{orden.estado}'."
                )

            orden.estado = "cancelada"
            db.commit()
            db.refresh(orden)

            return {
                "mensaje": f"Orden {orden.numero_orden} cancelada",
                "orden_id": orden.id,
                "estado": orden.estado,
            }

        except OrdenInvalidaError:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise OrdenInvalidaError(f"Error al cancelar orden: {str(e)}")

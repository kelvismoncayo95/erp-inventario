"""
Servicio de Reportes.
Usa consultas agregadas (SUM, COUNT, GROUP BY) para generar estadísticas.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.producto import Producto
from app.models.venta import Venta
from app.models.item_venta import ItemVenta


class ReporteService:

    @staticmethod
    def resumen_general(db: Session) -> dict:
        """Dashboard: totales generales del sistema."""
        # Total de productos activos
        total_productos = db.query(func.count(Producto.id)).filter(
            Producto.activo == 1
        ).scalar() or 0

        # Valor del inventario (stock * precio_costo)
        valor_inventario = db.query(
            func.coalesce(func.sum(Producto.stock_actual * Producto.precio_costo), 0)
        ).filter(Producto.activo == 1).scalar() or 0

        # Total de ventas completadas
        total_ventas = db.query(func.count(Venta.id)).filter(
            Venta.estado == "completada"
        ).scalar() or 0

        # Ingresos totales
        ingresos_totales = db.query(
            func.coalesce(func.sum(Venta.total), 0)
        ).filter(Venta.estado == "completada").scalar() or 0

        # Ganancia total: suma de (subtotal - costo * cantidad)
        ganancia_total = db.query(
            func.coalesce(
                func.sum(ItemVenta.subtotal - (ItemVenta.cantidad * Producto.precio_costo)),
                0
            )
        ).join(
            Producto, ItemVenta.producto_id == Producto.id
        ).join(
            Venta, ItemVenta.venta_id == Venta.id
        ).filter(Venta.estado == "completada").scalar() or 0

        return {
            "total_productos": int(total_productos),
            "valor_inventario": float(valor_inventario),
            "total_ventas": int(total_ventas),
            "ingresos_totales": float(ingresos_totales),
            "ganancia_total": float(ganancia_total),
        }

    @staticmethod
    def productos_mas_vendidos(db: Session, limite: int = 10) -> list:
        """Top N productos más vendidos (por cantidad)."""
        resultados = (
            db.query(
                Producto.id.label("producto_id"),
                Producto.nombre,
                Producto.sku,
                func.sum(ItemVenta.cantidad).label("total_vendido"),
                func.sum(ItemVenta.subtotal).label("ingresos"),
                func.count(func.distinct(Venta.id)).label("num_ventas"),
            )
            .join(ItemVenta, Producto.id == ItemVenta.producto_id)
            .join(Venta, ItemVenta.venta_id == Venta.id)
            .filter(Venta.estado == "completada")
            .group_by(Producto.id, Producto.nombre, Producto.sku)
            .order_by(func.sum(ItemVenta.cantidad).desc())
            .limit(limite)
            .all()
        )

        return [
            {
                "producto_id": r.producto_id,
                "nombre": r.nombre,
                "sku": r.sku,
                "total_vendido": int(r.total_vendido or 0),
                "ingresos": float(r.ingresos or 0),
                "num_ventas": int(r.num_ventas or 0),
            }
            for r in resultados
        ]

    @staticmethod
    def ganancias_por_periodo(db: Session, periodo: str = "mes") -> list:
        """Ganancias agrupadas por día, mes o año."""
        if periodo == "dia":
            trunc = func.date_trunc("day", Venta.fecha)
        elif periodo == "año" or periodo == "year":
            trunc = func.date_trunc("year", Venta.fecha)
        else:
            trunc = func.date_trunc("month", Venta.fecha)

        resultados = (
            db.query(
                trunc.label("periodo"),
                func.count(func.distinct(Venta.id)).label("num_ventas"),
                func.sum(Venta.total).label("ingresos"),
                func.sum(ItemVenta.cantidad * Producto.precio_costo).label("costo"),
            )
            .join(ItemVenta, Venta.id == ItemVenta.venta_id)
            .join(Producto, ItemVenta.producto_id == Producto.id)
            .filter(Venta.estado == "completada")
            .group_by(trunc)
            .order_by(trunc.desc())
            .all()
        )

        resultado_final = []
        for r in resultados:
            ingresos = float(r.ingresos or 0)
            costo = float(r.costo or 0)
            resultado_final.append({
                "periodo": r.periodo,
                "num_ventas": int(r.num_ventas or 0),
                "ingresos": ingresos,
                "costo": costo,
                "ganancia": ingresos - costo,
            })
        return resultado_final

    @staticmethod
    def stock_bajo(db: Session) -> list:
        """Productos cuyo stock actual está por debajo o igual al mínimo."""
        productos = (
            db.query(Producto)
            .filter(
                Producto.activo == 1,
                Producto.stock_actual <= Producto.stock_minimo
            )
            .order_by(Producto.stock_actual.asc())
            .all()
        )

        return [
            {
                "id": p.id,
                "nombre": p.nombre,
                "sku": p.sku,
                "stock_actual": p.stock_actual,
                "stock_minimo": p.stock_minimo,
                "diferencia": p.stock_actual - p.stock_minimo,
            }
            for p in productos
        ]

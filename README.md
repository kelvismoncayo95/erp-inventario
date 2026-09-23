# 📦 ERP Inventario

Sistema de gestión de inventario y ventas con roles diferenciados (admin, encargado, vendedor). Backend en **FastAPI + PostgreSQL**, frontend en **HTML/CSS/JS vanilla**.

Proyecto de portafolio orientado a pequeños comercios que necesitan controlar stock, compras a proveedores, ventas y reportes.

---

## 🎯 Características

### 📋 Inventario
- CRUD completo de productos con soft-delete (nunca se borran, quedan con historial)
- Categorías y proveedores
- Indicador de stock en 3 estados: OK / Bajo / Sin stock
- Reactivación de productos con stock mínimo configurable

### 🛒 Ventas
- Punto de venta con carrito y búsqueda por nombre o SKU
- Cálculo automático de IVA (22%)
- Anulación con devolución automática de stock
- Regla por rol: vendedor solo anula en los primeros 5 minutos
- Historial completo con quién vendió y cuándo

### 📥 Compras (Órdenes a proveedores)
- Creación de órdenes de compra con múltiples productos
- Al recibir la orden, el stock se suma automáticamente
- Actualización del precio de costo al último valor recibido
- Estados: pendiente / recibida / cancelada

### 📊 Reportes (solo admin)
- Resumen general: productos, valor de inventario, ventas, ingresos
- Top productos más vendidos
- Ganancias por día / mes / año
- Alertas de stock bajo

### 👥 Usuarios y roles

| Rol | Puede |
|---|---|
| Admin | Todo, excepto vender. Ve simulacro de venta. |
| Encargado | Vender, comprar, gestionar productos. No ve reportes ni crea usuarios. |
| Vendedor | Solo vender y consultar precios. Anula sus propias ventas antes de 5 min. |

---

## 🛠️ Stack

- **Backend:** FastAPI, SQLAlchemy 2.x, Pydantic v2
- **Base de datos:** PostgreSQL
- **Auth:** JWT con roles (python-jose + passlib bcrypt)
- **Frontend:** HTML + CSS + JavaScript vanilla (sin frameworks)

---

## 📁 Estructura

Backend en `backend/` con `app/api`, `app/models`, `app/schemas`, `app/services`, `app/core`.
Frontend en `frontend/` con `index.html`, `estilos.css` y módulos en `js/`.

---

## 🚀 Instalación

Requisitos: Python 3.11+ y PostgreSQL 14+.

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Editar .env con DATABASE_URL y SECRET_KEY
python3 crear_tablas.py
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Swagger: http://localhost:8000/docs

### Frontend

```bash
cd frontend
python3 -m http.server 5500
```

Abrir: http://localhost:5500

---

## 🔑 Credenciales demo

| Rol | Email |
|---|---|
| Admin | admin@erp.com |
| Encargado | kelvis@erp.com |
| Vendedor | vendedor@erp.com |

---

## 🔌 API principal

| Método | Endpoint | Descripción |
|---|---|---|
| POST | /auth/login | Login |
| GET | /productos/ | Listar productos |
| POST | /ventas/ | Crear venta transaccional |
| POST | /ventas/{id}/anular | Anular y devolver stock |
| POST | /ordenes-compra/ | Crear orden a proveedor |
| POST | /ordenes-compra/{id}/recibir | Recibir orden y sumar stock |
| GET | /reportes/resumen | KPIs generales (solo admin) |

---

## 🔒 Seguridad

- JWT firmado con SECRET_KEY del .env
- Contraseñas hasheadas con bcrypt
- Roles validados por dependencias FastAPI
- CORS restringido al frontend
- Soft-delete con auditoría (nunca se borran datos)

---

## 📝 Licencia

MIT - libre para usar, modificar y aprender.

---

## 👤 Autor

Kelvis Moncayo - 2026.

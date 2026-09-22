# 📋 ESTADO DEL PROYECTO - ERP Inventario

## 🤝 ACUERDO DE TRABAJO CON LA IA

**Cada vez que el usuario diga "lo dejamos hasta aquí", "por hoy terminamos", "seguimos mañana" o similar, la IA debe responder SIEMPRE con:**

1. **Resumen completo de lo que se hizo en la sesión**
2. **Lista completa de lo que falta (actualizada)**
3. **Contexto:** con qué tecnologías trabajamos, en qué archivos, y por qué
4. **Próximo paso concreto:** qué hacer cuando se retome

**No esperar a que el usuario lo pida. Es automático.**

**Además, la IA debe actualizar este archivo `ESTADO_PROYECTO.md` con los cambios de cada sesión.**

---

## 📌 TAREAS PENDIENTES (en orden de prioridad)

### 🔴 Alta prioridad (para Workana)

- [ ] **Sección de Categorías** en frontend (backend ya tiene endpoints)
- [ ] **Sección de Proveedores** en frontend (backend ya tiene endpoints)
- [ ] **Sección de Órdenes de Compra** en frontend (repone stock)
- [ ] **Sección de Usuarios** en frontend (admin crea vendedores)
- [ ] **Detalle de Venta** en frontend (ver items de cada venta)
- [ ] **Subir Proyecto 1 (ERP) a GitHub**

### 🟡 Media prioridad

- [ ] Tests automatizados
- [ ] Video demo del proyecto funcionando
- [ ] README público para el repositorio

### 🟢 Baja prioridad (después)

- [ ] Completar Proyecto 2 (Mototaxi) — app móvil
- [ ] Despliegue en producción

---

**Última actualización:** 16 de septiembre de 2026




# 📋 ESTADO DEL PROYECTO - ERP Inventario

**Última actualización:** 16 de septiembre de 2026

---

## 🎯 Descripción del proyecto

Sistema de gestión de inventario y ventas (mini-ERP) con:
- Backend en FastAPI + SQLAlchemy
- Base de datos PostgreSQL
- Frontend en HTML/JS vanilla
- Autenticación con JWT y roles

**Objetivo:** Proyecto de portafolio para Workana.

---

## 🏗️ Arquitectura

- **PostgreSQL:** Windows (puerto 5432)
- **Backend (FastAPI):** Ubuntu/WSL (puerto 8000)
- **Frontend (HTML/JS):** Ubuntu/WSL (puerto 5500)
- **Acceso remoto:** Tailscale + SSH (puerto 2222)
- **Portproxy en Windows:** 2222 → SSH, 8000 → API, 5500 → Frontend

---

## ✅ LO QUE ESTÁ HECHO

### 🗄️ Base de datos

- 8 tablas creadas con SQLAlchemy:
  - `usuarios` (con roles: admin, vendedor)
  - `categorias`
  - `proveedores`
  - `productos`
  - `ventas`
  - `items_venta`
  - `ordenes_compra`
  - `items_compra`
- Fechas automáticas (`CURRENT_TIMESTAMP`)
- Campos obligatorios (`NOT NULL`)
- Datos de prueba insertados

### 🔧 Backend (FastAPI)

**Endpoints implementados:**

| Módulo | Endpoints |
|--------|-----------|
| **Auth** | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` |
| **Productos** | `GET /productos/`, `GET /productos/{id}`, `POST /productos/`, `PUT /productos/{id}`, `DELETE /productos/{id}`, `POST /productos/{id}/reactivar` |
| **Ventas** | `POST /ventas/`, `GET /ventas/`, `GET /ventas/{id}`, `POST /ventas/{id}/anular` |
| **Reportes** | `GET /reportes/resumen`, `GET /reportes/productos-mas-vendidos`, `GET /reportes/ganancias`, `GET /reportes/stock-bajo` |
| **Health** | `GET /`, `GET /health` |

**Servicios implementados:**
- `venta_service.py` → Lógica transaccional con `SELECT FOR UPDATE` y `ROLLBACK`
- `reporte_service.py` → Consultas agregadas (SUM, COUNT, GROUP BY)

**Schemas (Pydantic v2):**
- `producto.py`, `venta.py`, `usuario.py`, `reporte.py`

**Seguridad:**
- JWT con `python-jose`
- Hash de contraseñas con `passlib[bcrypt]`
- Roles: admin y vendedor

### 🎨 Frontend (HTML/JS)

**Pestañas funcionales:**

- ✅ **Login** → Formulario de login con JWT
- ✅ **Productos** → Lista con búsqueda, filtros, crear, eliminar
- ✅ **Nuevo Producto** → Formulario completo
- ✅ **Ventas** → Selección de productos, confirmar venta, historial
- ✅ **Reportes** → Resumen, más vendidos, ganancias, stock bajo

### 🔐 Infraestructura

- ✅ Tailscale (PC ↔ iPhone)
- ✅ SSH en Windows (puerto 22) y Ubuntu (puerto 22)
- ✅ Portproxy para 2222, 8000, 5500
- ✅ Firewall abierto para esos puertos
- ✅ PostgreSQL con contraseña `151295`
- ✅ Conexión desde Ubuntu a PostgreSQL vía `172.31.160.1`

---

## ❌ LO QUE FALTA

### Backend

- ❌ Endpoints de **Categorías** (el modelo existe, falta la API)
- ❌ Endpoints de **Proveedores** (el modelo existe, falta la API)
- ❌ Endpoints de **Órdenes de Compra** (el modelo existe, falta la API)
- ❌ Endpoints de **Gestión de Usuarios** (solo hay registro y login)

### Frontend

- ❌ Pestaña de **Categorías** (gestión visual)
- ❌ Pestaña de **Proveedores** (gestión visual)
- ❌ Pestaña de **Órdenes de Compra**
- ❌ Detalle completo de venta (ver items de una venta)
- ❌ Gestión de vendedores (crear, editar, desactivar)
- ❌ Paginación en listas largas

### Extras

- ❌ Tests automatizados
- ❌ Despliegue en producción (HTTPS, dominio)
- ❌ Documentación para el usuario final
- ❌ Video demo para Workana

---

## 🛠️ COMANDOS ESENCIALES

### Levantar PostgreSQL (Windows)

```powershell
net start postgresql-x64-17

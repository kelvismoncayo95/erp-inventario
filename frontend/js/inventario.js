/* =====================================================
   inventario.js — productos + categorías
   ===================================================== */
console.log('📦 inventario.js cargado');

let productosCache = [];
let categoriasCache = [];
let filtroCampo = 'todos';

/* ---------- PRODUCTOS ---------- */
async function cargarProductos() {
  try {
    const res = await apiFetch('/productos/?solo_activos=false');
    if (!res.ok) throw new Error('Error cargando productos');
    productosCache = await res.json();
    filtrarProductos();
    if (puedeTab('ventas')) renderVentaProductos();
    renderStatsProductos();
  } catch (ex) { console.error(ex); }
}

function renderStatsProductos() {
  const st = $('stat-productos');
  if (!st) return;
  const total = productosCache.length;
  const activos = productosCache.filter(p => p.activo == 1).length;
  const stockBajo = productosCache.filter(p =>
    p.activo == 1 && p.stock_actual != null && p.stock_actual <= p.stock_minimo).length;
  st.innerHTML = `
    <div class="stat">Total <strong>${total}</strong></div>
    <div class="stat">Activos <strong>${activos}</strong></div>
    <div class="stat">Stock bajo <strong>${stockBajo}</strong></div>`;
}

function filtrarProductos() {
  if (!$('lista-productos')) return;
  const texto = ($('filtro-texto')?.value || '').toLowerCase().trim();
  const estado = document.querySelector('input[name="filtro-estado"]:checked')?.value || 'activos';
  const rol = getRol();
  const esVendedor = rol === 'vendedor';

  let lista = productosCache.slice();
  if (esVendedor) {
    lista = lista.filter(p => p.disponible !== false && p.activo !== 0);
  } else {
    if (estado === 'activos') lista = lista.filter(p => p.activo == 1);
    else if (estado === 'eliminados') lista = lista.filter(p => p.activo != 1);
  }

  if (texto) {
    lista = lista.filter(p => {
      const campos = {
        todos: [p.nombre, p.sku, p.descripcion, p.categoria_nombre, p.proveedor_nombre, p.categoria?.nombre, p.proveedor?.nombre],
        nombre: [p.nombre], sku: [p.sku], descripcion: [p.descripcion],
        proveedor: [p.proveedor_nombre, p.proveedor?.nombre],
        categoria: [p.categoria_nombre, p.categoria?.nombre]
      };
      const arr = campos[filtroCampo] || campos.todos;
      return arr.some(v => v && String(v).toLowerCase().includes(texto));
    });
  }
  renderProductos(lista);
}

function stockClass(p) {
  if (p.stock_actual == null) return 'stock-ok';
  if (p.stock_actual <= 0) return 'stock-low';
  if (p.stock_actual <= p.stock_minimo) return 'stock-warn';
  return 'stock-ok';
}

function renderProductos(lista) {
  const cont = $('lista-productos');
  if (!cont) return;
  if (!lista.length) { cont.innerHTML = '<p class="vacio">No hay productos que coincidan con la búsqueda</p>'; return; }

  const rol = getRol();
  const esVendedor = rol === 'vendedor';
  const puedeElim = permisos().puedeEliminarProducto;
  const puedeReact = permisos().puedeReactivar;

  cont.innerHTML = lista.map(p => {
    const elim = p.activo === 0;
    const catNombre = p.categoria_nombre || p.categoria?.nombre;
    const provNombre = p.proveedor_nombre || p.proveedor?.nombre;

    if (esVendedor) {
      const disponible = p.disponible !== false;
      return `
      <div class="prod-card">
        <div class="prod-head"><div class="prod-name">${esc(p.nombre)}</div></div>
        <span class="prod-sku">${esc(p.sku)}</span>
        <div class="prod-desc">${esc(p.descripcion || '')}</div>
        <div class="prod-info-row">
          ${catNombre ? `<span class="tag cat">🏷️ ${esc(catNombre)}</span>` : ''}
        </div>
        <div class="prod-footer">
          <div class="prod-price">${money(p.precio_venta)}</div>
          <span class="stock-pill ${disponible ? 'stock-ok' : 'stock-low'}">${disponible ? '✅ Disponible' : '❌ Sin stock'}</span>
        </div>
      </div>`;
    }

    return `
    <div class="prod-card ${elim ? 'eliminado' : ''}">
      <div class="prod-head"><div class="prod-name">${esc(p.nombre)}</div></div>
      <span class="prod-sku">${esc(p.sku)}</span>
      <div class="prod-desc">${esc(p.descripcion || 'Sin descripción')}</div>
      <div class="prod-info-row">
        ${catNombre ? `<span class="tag cat">🏷️ ${esc(catNombre)}</span>` : ''}
        ${provNombre ? `<span class="tag prov">🚚 ${esc(provNombre)}</span>` : ''}
      </div>
      <div class="prod-footer">
        <div class="prod-price">${money(p.precio_venta)}</div>
        <span class="stock-pill ${stockClass(p)}">${p.stock_actual} u.</span>
      </div>
      <div class="prod-actions">
        ${elim && puedeReact
          ? `<button class="btn btn-success" onclick="reactivarProducto(${p.id})">♻️ Reactivar</button>`
          : (!elim && puedeElim
            ? `<button class="btn btn-danger" onclick="eliminarProducto(${p.id})">🗑️ Eliminar</button>`
            : '')}
      </div>
    </div>`;
  }).join('');
}

async function eliminarProducto(id) {
  if (!confirm('¿Eliminar producto? Se guarda historial pero no se borra de la BD.')) return;
  try {
    const res = await apiFetch(`/productos/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error(extraerMensaje(await res.json().catch(() => ({})), 'Error al eliminar'));
    await cargarProductos();
  } catch (ex) { alert(ex.message); }
}

async function reactivarProducto(id) {
  const stock = prompt('¿Con cuánto stock quieres reactivar? (mínimo 10)', '10');
  if (stock === null) return;
  const n = parseInt(stock);
  if (isNaN(n) || n < 10) { alert('El stock debe ser 10 o mayor'); return; }
  try {
    const res = await apiFetch(`/productos/${id}/reactivar`, {
      method: 'POST',
      body: JSON.stringify({ stock_inicial: n })
    });
    if (!res.ok) throw new Error(extraerMensaje(await res.json().catch(() => ({})), 'Error al reactivar'));
    await cargarProductos();
    alert('♻️ Producto reactivado con ' + n + ' unidades');
  } catch (ex) { alert(ex.message); }
}

/* ---------- CREAR PRODUCTO ---------- */
async function crearProducto(e) {
  e.preventDefault();
  const data = {
    nombre: $('np-nombre').value.trim(),
    sku: $('np-sku').value.trim(),
    descripcion: $('np-descripcion').value.trim() || null,
    precio_costo: parseFloat($('np-costo').value || 0),
    precio_venta: parseFloat($('np-venta').value || 0),
    stock_actual: parseInt($('np-stock').value || 0),
    stock_minimo: parseInt($('np-min').value || 5),
    stock_maximo: parseInt($('np-max').value || 100),
    categoria_id: $('np-categoria').value ? parseInt($('np-categoria').value) : null
  };
  const msg = $('np-msg');
  try {
    const res = await apiFetch('/productos/', { method: 'POST', body: JSON.stringify(data) });
    if (!res.ok) throw new Error(extraerMensaje(await res.json().catch(() => ({})), 'Error al crear'));
    msg.textContent = '✅ Producto creado correctamente'; msg.className = 'msg ok';
    e.target.reset();
    await cargarProductos();
    setTimeout(() => { msg.textContent = ''; }, 3000);
  } catch (ex) { msg.textContent = '❌ ' + ex.message; msg.className = 'msg err'; }
}

/* ---------- CATEGORÍAS ---------- */
async function cargarCategorias() {
  try {
    const res = await apiFetch('/categorias/');
    if (!res.ok) return;
    categoriasCache = await res.json();
    const sel = $('np-categoria');
    if (sel) sel.innerHTML = '<option value="">— Sin categoría —</option>' +
      categoriasCache.map(c => `<option value="${c.id}">${esc(c.nombre)}</option>`).join('');
    renderCategorias();
  } catch (ex) { console.error(ex); }
}

function renderCategorias() {
  const cont = $('lista-categorias');
  if (!cont) return;
  if (!categoriasCache.length) { cont.innerHTML = '<p class="vacio">Aún no hay categorías</p>'; return; }
  cont.innerHTML = categoriasCache.map(c => {
    const count = productosCache.filter(p => p.categoria_id === c.id && p.activo == 1).length;
    return `
    <div class="categoria-card">
      <div class="cat-icon">🏷️</div>
      <div class="cat-name">${esc(c.nombre)}</div>
      <div class="cat-desc">${esc(c.descripcion || 'Sin descripción')}</div>
      <div class="cat-actions">
        <span class="cat-count">${count} producto${count !== 1 ? 's' : ''}</span>
        <button class="btn btn-danger btn-sm" onclick="eliminarCategoria(${c.id})">Eliminar</button>
      </div>
    </div>`;
  }).join('');
}

async function crearCategoria(e) {
  e.preventDefault();
  const msg = $('cat-msg');
  try {
    const res = await apiFetch('/categorias/', {
      method: 'POST',
      body: JSON.stringify({
        nombre: $('cat-nombre').value.trim(),
        descripcion: $('cat-descripcion').value.trim() || null
      })
    });
    if (!res.ok) throw new Error(extraerMensaje(await res.json().catch(() => ({})), 'Error'));
    msg.textContent = '✅ Categoría creada'; msg.className = 'msg ok';
    e.target.reset();
    await cargarCategorias();
    setTimeout(() => { msg.textContent = ''; }, 3000);
  } catch (ex) { msg.textContent = '❌ ' + ex.message; msg.className = 'msg err'; }
}

async function eliminarCategoria(id) {
  if (!confirm('¿Eliminar categoría?')) return;
  try {
    const res = await apiFetch(`/categorias/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Error al eliminar');
    await cargarCategorias();
  } catch (ex) { alert(ex.message); }
}

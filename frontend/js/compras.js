/* =====================================================
   compras.js — órdenes de compra
   ===================================================== */
console.log('📦 compras.js cargado');

let ordenesCache = [];
let itemsOrdenActual = [];

/* ---------- Abrir / cerrar formulario ---------- */
function abrirNuevaOrden() {
  $('form-orden-container').style.display = 'block';
  itemsOrdenActual = [];
  renderItemsOrden();
  llenarSelectProveedores('oc-proveedor');
  llenarSelectProductos('oc-producto');
  $('form-orden-container').scrollIntoView({ behavior: 'smooth' });
}

function cerrarNuevaOrden() {
  $('form-orden-container').style.display = 'none';
  itemsOrdenActual = [];
  $('oc-msg').textContent = '';
}

/* ---------- Llenar selects ---------- */
function llenarSelectProveedores(selectId) {
  const sel = $(selectId);
  if (!sel) return;
  sel.innerHTML = '<option value="">— Seleccionar proveedor —</option>' +
    (window.proveedoresCache || []).map(p =>
      `<option value="${p.id}">${esc(p.nombre)}</option>`).join('');
}

function llenarSelectProductos(selectId) {
  const sel = $(selectId);
  if (!sel) return;
  sel.innerHTML = '<option value="">— Producto —</option>' +
    productosCache.filter(p => p.activo == 1).map(p =>
      `<option value="${p.id}" data-costo="${p.precio_costo || 0}">${esc(p.nombre)} (${esc(p.sku)})</option>`
    ).join('');
}

/* Al elegir producto, autocompletar el precio con el costo */
function autocompletarPrecio() {
  const sel = $('oc-producto');
  const opt = sel.options[sel.selectedIndex];
  if (opt && opt.dataset.costo) {
    $('oc-precio').value = Number(opt.dataset.costo).toFixed(2);
  }
}

/* ---------- Items de la orden ---------- */
function agregarItemOrden() {
  const prodId = parseInt($('oc-producto').value);
  const cant = parseInt($('oc-cantidad').value || 1);
  const precio = parseFloat($('oc-precio').value || 0);

  if (!prodId) return alert('Selecciona un producto');
  if (cant <= 0) return alert('Cantidad debe ser mayor a 0');
  if (precio < 0) return alert('Precio inválido');

  const p = productosCache.find(x => x.id === prodId);
  if (!p) return;

  const ex = itemsOrdenActual.find(i => i.producto_id === prodId);
  if (ex) {
    ex.cantidad += cant;
    ex.precio_unitario = precio;
    ex.subtotal = ex.cantidad * precio;
  } else {
    itemsOrdenActual.push({
      producto_id: prodId,
      producto_nombre: p.nombre,
      cantidad: cant,
      precio_unitario: precio,
      subtotal: cant * precio
    });
  }

  $('oc-cantidad').value = 1;
  $('oc-precio').value = '';
  $('oc-producto').value = '';
  renderItemsOrden();
}

function renderItemsOrden() {
  const cont = $('oc-items-lista');
  if (!cont) return;
  if (!itemsOrdenActual.length) {
    cont.innerHTML = '<p class="muted center" style="padding:16px">Aún no agregaste productos</p>';
    $('oc-total').textContent = money(0);
    return;
  }
  cont.innerHTML = itemsOrdenActual.map((i, idx) => `
    <div class="oc-item">
      <div class="oc-item-info">
        <strong>${esc(i.producto_nombre)}</strong>
        <small>${i.cantidad} × ${money(i.precio_unitario)}</small>
      </div>
      <div class="oc-item-total">${money(i.subtotal)}</div>
      <button class="ci-del" onclick="quitarItemOrden(${idx})">✕</button>
    </div>
  `).join('');
  const total = itemsOrdenActual.reduce((a, i) => a + i.subtotal, 0);
  $('oc-total').textContent = money(total);
}

function quitarItemOrden(idx) {
  itemsOrdenActual.splice(idx, 1);
  renderItemsOrden();
}

/* ---------- Guardar orden ---------- */
async function guardarOrden() {
  const proveedorId = parseInt($('oc-proveedor').value);
  const fecha = $('oc-fecha').value || null;
  const msg = $('oc-msg');

  if (!proveedorId) return alert('Selecciona un proveedor');
  if (!itemsOrdenActual.length) return alert('Agrega al menos un producto');

  try {
    const body = {
      proveedor_id: proveedorId,
      fecha_entrega_esperada: fecha ? fecha + 'T00:00:00' : null,
      items: itemsOrdenActual.map(i => ({
        producto_id: i.producto_id,
        cantidad: i.cantidad,
        precio_unitario: i.precio_unitario
      }))
    };
    const res = await apiFetch('/ordenes-compra/', {
      method: 'POST',
      body: JSON.stringify(body)
    });
    if (!res.ok) throw new Error(extraerMensaje(await res.json().catch(() => ({})), 'Error'));
    msg.textContent = '✅ Orden creada'; msg.className = 'msg ok';
    itemsOrdenActual = [];
    renderItemsOrden();
    $('oc-proveedor').value = '';
    $('oc-fecha').value = '';
    await cargarOrdenes();
    setTimeout(() => { cerrarNuevaOrden(); }, 1000);
  } catch (ex) {
    msg.textContent = '❌ ' + ex.message; msg.className = 'msg err';
  }
}

/* ---------- Listar órdenes ---------- */
async function cargarOrdenes() {
  const cont = $('lista-ordenes');
  if (!cont) return;
  const estadoFiltro = document.querySelector('input[name="filtro-orden"]:checked')?.value || 'todas';
  const url = estadoFiltro === 'todas' ? '/ordenes-compra/' : `/ordenes-compra/?estado=${estadoFiltro}`;
  try {
    const res = await apiFetch(url);
    if (!res.ok) throw new Error('Error cargando órdenes');
    ordenesCache = await res.json();
    renderOrdenes();
  } catch (ex) { cont.innerHTML = '<p class="vacio">❌ ' + ex.message + '</p>'; }
}

function renderOrdenes() {
  const cont = $('lista-ordenes');
  if (!cont) return;
  if (!ordenesCache.length) {
    cont.innerHTML = '<p class="vacio">No hay órdenes para mostrar</p>';
    return;
  }
  cont.innerHTML = ordenesCache.map(o => {
    const pendiente = o.estado === 'pendiente';
    const fecha = (o.fecha || '').replace('T', ' ').slice(0, 10);
    const badgeClass = o.estado === 'recibida' ? '' : (o.estado === 'cancelada' ? 'anulada' : 'pendiente');
    return `
    <div class="venta-card">
      <div class="vc-head">
        <span class="vc-num">${esc(o.numero_orden)}</span>
        <span class="vc-status ${badgeClass}">${esc(o.estado)}</span>
      </div>
      <div class="vc-row"><span>Fecha</span><strong>${esc(fecha)}</strong></div>
      <div class="vc-row"><span>Proveedor</span><strong>${esc(o.proveedor_nombre || '—')}</strong></div>
      <div class="vc-row"><span>Creado por</span><strong>${esc(o.creado_por_nombre || '—')}</strong></div>
      <div class="vc-total">${money(o.total)}</div>
      <div class="vc-actions">
        <button class="btn btn-ghost" onclick="verDetalleOrden(${o.id})">👁️ Ver</button>
        ${pendiente ? `<button class="btn btn-success" onclick="recibirOrden(${o.id})">📥 Recibir</button>` : ''}
        ${pendiente ? `<button class="btn btn-danger" onclick="cancelarOrden(${o.id})">✕ Cancelar</button>` : ''}
      </div>
    </div>`;
  }).join('');
}

async function verDetalleOrden(id) {
  try {
    const res = await apiFetch(`/ordenes-compra/${id}`);
    if (!res.ok) throw new Error('No se pudo cargar');
    const o = await res.json();
    const items = (o.items || []).map(i =>
      `• ${i.producto_nombre || 'Producto ' + i.producto_id} — ${i.cantidad} × ${money(i.precio_unitario)} = ${money(i.subtotal)}`
    ).join('\n');
    alert(`Orden: ${o.numero_orden}\nEstado: ${o.estado}\nProveedor: ${o.proveedor_nombre || '—'}\n\n${items}\n\nTotal: ${money(o.total)}`);
  } catch (ex) { alert(ex.message); }
}

async function recibirOrden(id) {
  if (!confirm('¿Marcar la orden como recibida? Se SUMARÁ el stock de todos los productos.')) return;
  try {
    const res = await apiFetch(`/ordenes-compra/${id}/recibir`, { method: 'POST' });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(extraerMensaje(data, 'Error'));
    alert('✅ ' + (data.mensaje || 'Orden recibida'));
    await cargarOrdenes();
    await cargarProductos();
  } catch (ex) { alert('❌ ' + ex.message); }
}

async function cancelarOrden(id) {
  if (!confirm('¿Cancelar esta orden? No se puede deshacer.')) return;
  try {
    const res = await apiFetch(`/ordenes-compra/${id}/cancelar`, { method: 'POST' });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(extraerMensaje(data, 'Error'));
    alert('✅ ' + (data.mensaje || 'Orden cancelada'));
    await cargarOrdenes();
  } catch (ex) { alert('❌ ' + ex.message); }
}

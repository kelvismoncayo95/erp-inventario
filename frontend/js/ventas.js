/* =====================================================
   ventas.js — vender real + simulacro (admin)
   Búsqueda en vivo por nombre / SKU / código de barra.
   ===================================================== */
console.log('📦 ventas.js cargado');

let carritoVenta = [];

/* ---------- LISTA DE PRODUCTOS PARA VENDER ---------- */
function renderVentaProductos() {
  const cont = $('venta-lista-productos');
  if (!cont) return;
  const buscar = ($('venta-buscar')?.value || '').toLowerCase().trim();
  const esAdmin = getRol() === 'admin';

  let lista = productosCache.filter(p => p.activo == 1 && (p.stock_actual == null || p.stock_actual > 0));
  if (buscar) {
    lista = lista.filter(p =>
      (p.nombre || '').toLowerCase().includes(buscar) ||
      (p.sku || '').toLowerCase().includes(buscar) ||
      (p.descripcion || '').toLowerCase().includes(buscar)
    );
  }

  if (!lista.length) {
    cont.innerHTML = buscar
      ? '<p class="vacio">No se encontró ningún producto con ese nombre o código</p>'
      : '<p class="vacio">No hay productos disponibles</p>';
    return;
  }

  /* Máx. 30 resultados para que no se vuelva lento */
  cont.innerHTML = lista.slice(0, 30).map(p => `
    <div class="vp-item">
      <div class="vp-info">
        <div class="vp-name">${esc(p.nombre)}</div>
        <div class="vp-meta">
          <span class="price">${money(p.precio_venta)}</span> ·
          Código: ${esc(p.sku)}${!esAdmin && p.stock_actual != null ? ` · Stock: ${p.stock_actual}` : ''}
        </div>
      </div>
      <div class="vp-qty">
        <input type="number" id="qty-${p.id}" value="1" min="1" ${!esAdmin && p.stock_actual != null ? `max="${p.stock_actual}"` : ''}
               onkeydown="if(event.key==='Enter'){event.preventDefault();agregarAlCarrito(${p.id});}">
        <button class="vp-add" onclick="agregarAlCarrito(${p.id})">+</button>
      </div>
    </div>
  `).join('');
}

/* ---------- CARRITO ---------- */
function agregarAlCarrito(prodId) {
  const qtyEl = $(`qty-${prodId}`);
  const cant = parseInt(qtyEl?.value || 1);
  const p = productosCache.find(x => x.id === prodId);
  if (!p) return;
  const esAdmin = getRol() === 'admin';
  if (!esAdmin && p.stock_actual != null && cant > p.stock_actual) { alert('No hay suficiente stock'); return; }

  const ex = carritoVenta.find(i => i.producto_id === prodId);
  if (ex) ex.cantidad += cant;
  else carritoVenta.push({
    producto_id: prodId, nombre: p.nombre,
    precio_unitario: Number(p.precio_venta), cantidad: cant
  });
  if (qtyEl) qtyEl.value = 1;
  renderCarrito();
}

function renderCarrito() {
  const cont = $('carrito-lista');
  const count = $('cart-count');
  if (!cont || !count) return;
  const totalItems = carritoVenta.reduce((a,b) => a + b.cantidad, 0);
  count.textContent = totalItems + ' item' + (totalItems !== 1 ? 's' : '');

  if (!carritoVenta.length) {
    cont.innerHTML = '<p class="muted center">Carrito vacío</p>';
    if ($('carrito-subtotal')) $('carrito-subtotal').textContent = '0';
    if ($('carrito-iva')) $('carrito-iva').textContent = '0';
    if ($('carrito-total')) $('carrito-total').textContent = '0';
    return;
  }
  let sub = 0;
  cont.innerHTML = carritoVenta.map((i, idx) => {
    const st = i.precio_unitario * i.cantidad; sub += st;
    return `<div class="cart-item">
      <span class="ci-name">${esc(i.nombre)}</span>
      <span class="ci-qty">x${i.cantidad}</span>
      <span class="ci-price">${money(st)}</span>
      <button class="ci-del" onclick="quitarDelCarrito(${idx})">✕</button>
    </div>`;
  }).join('');
  const iva = sub * 0.22;
  $('carrito-subtotal').textContent = money(sub);
  $('carrito-iva').textContent = money(iva);
  $('carrito-total').textContent = money(sub + iva);
}

function quitarDelCarrito(idx) { carritoVenta.splice(idx, 1); renderCarrito(); }

/* ---------- CONFIRMAR VENTA ---------- */
async function confirmarVenta() {
  if (!carritoVenta.length) return alert('El carrito está vacío');
  const esAdmin = getRol() === 'admin';

  if (esAdmin) {
    const total = carritoVenta.reduce((a,i) => a + i.precio_unitario * i.cantidad, 0) * 1.22;
    alert(`🧪 SIMULACRO completado\n\nItems: ${carritoVenta.length}\nTotal ficticio: ${money(total)}\n\nNo se guardó en la base de datos.`);
    carritoVenta = []; renderCarrito();
    if ($('venta-cliente')) $('venta-cliente').value = '';
    if ($('venta-telefono')) $('venta-telefono').value = '';
    return;
  }

  try {
    const res = await apiFetch('/ventas/', {
      method: 'POST',
      body: JSON.stringify({
        items: carritoVenta.map(i => ({ producto_id: i.producto_id, cantidad: i.cantidad })),
        cliente_nombre: $('venta-cliente').value.trim() || null,
        cliente_telefono: $('venta-telefono').value.trim() || null
      })
    });
    if (!res.ok) throw new Error(extraerMensaje(await res.json().catch(() => ({})), 'Error'));
    alert('✅ Venta registrada correctamente');
    carritoVenta = []; renderCarrito();
    $('venta-cliente').value = ''; $('venta-telefono').value = '';
    await cargarProductos(); await cargarVentas();
  } catch (ex) { alert('❌ ' + ex.message); }
}

/* ---------- HISTORIAL ---------- */
async function cargarVentas() {
  const cont = $('lista-ventas');
  if (!cont) return;
  try {
    const res = await apiFetch('/ventas/');
    if (!res.ok) return;
    const ventas = await res.json();
    if (!ventas.length) { cont.innerHTML = '<p class="vacio">Aún no hay ventas registradas</p>'; return; }

    cont.innerHTML = ventas.map(v => {
      const anulada = v.estado !== 'completada';
      const fecha = (v.fecha || '').replace('T', ' ').slice(0, 16);
      const puedeAnular = permisos().puedeAnular;
      return `
      <div class="venta-card">
        <div class="vc-head">
          <span class="vc-num">${esc(v.numero_factura)}</span>
          <span class="vc-status ${anulada ? 'anulada' : ''}">${esc(v.estado)}</span>
        </div>
        <div class="vc-row"><span>Fecha</span><strong>${esc(fecha)}</strong></div>
        <div class="vc-row"><span>Vendió</span><strong>${esc(v.vendedor_nombre || '—')}</strong></div>
        <div class="vc-row"><span>Cliente</span><strong>${esc(v.cliente_nombre || '—')}</strong></div>
        <div class="vc-total">${money(v.total)}</div>
        <div class="vc-actions">
          <button class="btn btn-ghost" onclick="verDetalleVenta(${v.id})">👁️ Ver</button>
          ${!anulada && puedeAnular ? `<button class="btn btn-danger" onclick="anularVenta(${v.id})">✕ Anular</button>` : ''}
        </div>
      </div>`;
    }).join('');
  } catch (ex) { console.error(ex); }
}

async function verDetalleVenta(id) {
  try {
    const res = await apiFetch(`/ventas/${id}`);
    if (!res.ok) throw new Error('No se pudo cargar');
    const v = await res.json();
    const items = v.items || v.items_venta || [];
    const txt = items.map(i =>
      `• ${i.producto?.nombre || 'Producto ' + i.producto_id} x${i.cantidad} = ${money(i.subtotal)}`
    ).join('\n');
    alert(`Factura: ${v.numero_factura}\nCliente: ${v.cliente_nombre || '—'}\nVendió: ${v.vendedor_nombre || '—'}\n\n${txt}\n\nSubtotal: ${money(v.subtotal)}\nIVA: ${money(v.iva)}\nTotal: ${money(v.total)}`);
  } catch (ex) { alert(ex.message); }
}

async function anularVenta(id) {
  if (!confirm('¿Anular venta? Se devolverá el stock.')) return;
  try {
    const res = await apiFetch(`/ventas/${id}/anular`, { method: 'POST' });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(extraerMensaje(data, 'Error al anular'));
    alert('✅ ' + (data.mensaje || 'Venta anulada'));
    await cargarVentas(); await cargarProductos();
  } catch (ex) { alert('❌ ' + ex.message); }
}

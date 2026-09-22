/* =====================================================
   admin.js — reportes (solo admin) + usuarios (solo admin)
   ===================================================== */
console.log('📦 admin.js cargado');

let periodoReporte = 'mes';
let usuariosCache = [];

/* ---------- REPORTES ---------- */
async function cargarReportes() {
  if (!permisos().puedeVerReportes) return;
  try {
    const urls = [
      '/reportes/resumen',
      '/reportes/productos-mas-vendidos',
      `/reportes/ganancias?periodo=${periodoReporte}`,
      '/reportes/stock-bajo'
    ];
    const [r1, r2, r3, r4] = await Promise.all(
      urls.map(u => apiFetch(u).then(r => r.ok ? r.json() : null).catch(() => null))
    );
    renderResumen(r1); renderMasVendidos(r2); renderGanancias(r3); renderStockBajo(r4);
  } catch (ex) { console.error(ex); }
}

function renderResumen(d) {
  const c = $('rep-resumen'); if (!c) return;
  d = d || {};
  c.innerHTML = `
    <div class="kpi k-blue">
      <div class="kpi-icon">📦</div>
      <div class="kpi-label">Productos</div>
      <div class="kpi-value">${fmt(d.productos || d.total_productos || 0)}</div>
    </div>
    <div class="kpi k-pink">
      <div class="kpi-icon">💰</div>
      <div class="kpi-label">Valor inventario</div>
      <div class="kpi-value">${money(d.valor_inventario || 0)}</div>
    </div>
    <div class="kpi k-green">
      <div class="kpi-icon">🛒</div>
      <div class="kpi-label">Ventas</div>
      <div class="kpi-value">${fmt(d.total_ventas || d.ventas || 0)}</div>
    </div>
    <div class="kpi k-orange">
      <div class="kpi-icon">💵</div>
      <div class="kpi-label">Ingresos</div>
      <div class="kpi-value">${money(d.ingresos || d.total_ingresos || 0)}</div>
    </div>
  `;
}

function renderMasVendidos(d) {
  const c = $('rep-mas-vendidos'); if (!c) return;
  const arr = Array.isArray(d) ? d : (d?.productos || []);
  if (!arr.length) { c.innerHTML = '<p class="vacio">Aún no hay ventas</p>'; return; }
  const max = Math.max(...arr.map(p => p.total_vendido || p.cantidad || 0));
  c.innerHTML = arr.slice(0, 8).map((p, i) => {
    const vendidos = p.total_vendido || p.cantidad || 0;
    const pct = max ? (vendidos / max) * 100 : 0;
    return `
    <div class="bar-item">
      <span class="bar-rank">${i + 1}</span>
      <div class="bar-body">
        <div class="bar-title-row">
          <span class="bar-title">${esc(p.nombre || p.producto)}</span>
          <span class="bar-value">${fmt(vendidos)}</span>
        </div>
        <div class="bar-track"><div class="bar-fill" style="width:${pct}%"></div></div>
      </div>
    </div>`;
  }).join('');
}

function renderGanancias(d) {
  const c = $('rep-ganancias'); if (!c) return;
  const arr = Array.isArray(d) ? d : (d?.periodos || []);
  if (!arr.length) { c.innerHTML = '<p class="vacio">Sin datos para este período</p>'; return; }
  c.innerHTML = arr.map(g => `
    <div class="gan-item">
      <div>
        <div class="gan-periodo">${esc(g.periodo)}</div>
        <div class="gan-ventas">${g.cantidad_ventas} venta${g.cantidad_ventas !== 1 ? 's' : ''}</div>
      </div>
      <div class="gan-monto">${money(g.ingresos)}</div>
    </div>
  `).join('');
}

function renderStockBajo(d) {
  const c = $('rep-stock-bajo'); if (!c) return;
  const arr = Array.isArray(d) ? d : (d?.productos || []);
  const badge = $('rep-stock-count');
  if (badge) badge.textContent = arr.length;
  if (!arr.length) { c.innerHTML = '<p class="vacio">✅ Todos los productos tienen stock suficiente</p>'; return; }
  c.innerHTML = arr.map(p => {
    const critico = (p.stock_actual || 0) <= 0;
    return `
    <div class="stock-item ${critico ? 'critico' : ''}">
      <div>
        <div class="stock-name">${esc(p.nombre)}</div>
        <div class="stock-meta">SKU ${esc(p.sku)} · Mínimo ${p.stock_minimo}</div>
      </div>
      <span class="stock-badge">${p.stock_actual} u.</span>
    </div>`;
  }).join('');
}

/* ---------- USUARIOS ---------- */
async function cargarUsuarios() {
  if (!permisos().puedeCrearUsuarios) return;
  try {
    const res = await apiFetch('/auth/usuarios');
    if (!res.ok) return;
    usuariosCache = await res.json();
    renderUsuarios();
  } catch (ex) { console.error(ex); }
}

function renderUsuarios() {
  const cont = $('lista-usuarios');
  if (!cont) return;
  if (!usuariosCache.length) { cont.innerHTML = '<p class="vacio">No hay usuarios</p>'; return; }
  const yoId = getUsuario().id;
  cont.innerHTML = usuariosCache.map(u => {
    const inactivo = u.activo === 0;
    const inicial = (u.nombre || '?').trim().charAt(0).toUpperCase();
    const esYo = u.id === yoId;
    return `
    <div class="usuario-card ${inactivo ? 'inactivo' : ''}">
      <div class="usuario-head">
        <div class="usuario-avatar">${esc(inicial)}</div>
        <div class="usuario-info">
          <strong>${esc(u.nombre)}</strong>
          <small>${esc(u.email)}</small>
        </div>
      </div>
      <span class="usuario-rol rol-${esc(u.rol)}">${esc(u.rol)}</span>
      <div class="usuario-actions">
        ${!esYo ? (inactivo
          ? `<button class="btn btn-success btn-sm" onclick="activarUsuario(${u.id})">♻️ Activar</button>`
          : `<button class="btn btn-danger btn-sm" onclick="desactivarUsuario(${u.id})">🚫 Desactivar</button>`)
          : `<span class="muted" style="font-size:12px">Eres tú</span>`}
      </div>
    </div>`;
  }).join('');
}

async function crearUsuario(e) {
  e.preventDefault();
  const msg = $('us-msg');
  try {
    const res = await apiFetch('/auth/usuarios', {
      method: 'POST',
      body: JSON.stringify({
        nombre: $('us-nombre').value.trim(),
        email: $('us-email').value.trim(),
        password: $('us-password').value,
        rol: $('us-rol').value
      })
    });
    if (!res.ok) throw new Error(extraerMensaje(await res.json().catch(() => ({})), 'Error'));
    msg.textContent = '✅ Usuario creado'; msg.className = 'msg ok';
    e.target.reset();
    await cargarUsuarios();
    setTimeout(() => { msg.textContent = ''; }, 3000);
  } catch (ex) { msg.textContent = '❌ ' + ex.message; msg.className = 'msg err'; }
}

async function desactivarUsuario(id) {
  if (!confirm('¿Desactivar este usuario? No podrá iniciar sesión.')) return;
  try {
    const res = await apiFetch(`/auth/usuarios/${id}`, { method: 'DELETE' });
    if (!res.ok && res.status !== 204) throw new Error('Error al desactivar');
    await cargarUsuarios();
  } catch (ex) { alert(ex.message); }
}

async function activarUsuario(id) {
  try {
    const res = await apiFetch(`/auth/usuarios/${id}/activar`, { method: 'POST' });
    if (!res.ok) throw new Error('Error al activar');
    await cargarUsuarios();
  } catch (ex) { alert(ex.message); }
}

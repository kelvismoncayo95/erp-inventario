/* =====================================================
   proveedores.js — CRUD de proveedores
   ===================================================== */
console.log('📦 proveedores.js cargado');

window.proveedoresCache = [];

async function cargarProveedores() {
  try {
    const res = await apiFetch('/proveedores/');
    if (!res.ok) return;
    window.proveedoresCache = await res.json();
    renderProveedores();
    /* Refrescar select del form de órdenes si existe */
    if (typeof llenarSelectProveedores === 'function') {
      llenarSelectProveedores('oc-proveedor');
    }
  } catch (ex) { console.error(ex); }
}

function renderProveedores() {
  const cont = $('lista-proveedores');
  if (!cont) return;
  if (!window.proveedoresCache.length) {
    cont.innerHTML = '<p class="vacio">Aún no hay proveedores</p>';
    return;
  }
  cont.innerHTML = window.proveedoresCache.map(p => `
    <div class="categoria-card">
      <div class="cat-icon">🚚</div>
      <div class="cat-name">${esc(p.nombre)}</div>
      <div class="cat-desc">
        ${p.ruc ? `RUC: ${esc(p.ruc)}<br>` : ''}
        ${p.telefono ? `📞 ${esc(p.telefono)}<br>` : ''}
        ${p.email ? `✉️ ${esc(p.email)}<br>` : ''}
        ${p.contacto ? `👤 ${esc(p.contacto)}` : ''}
      </div>
      <div class="cat-actions">
        <span class="cat-count">ID #${p.id}</span>
        <button class="btn btn-danger btn-sm" onclick="eliminarProveedor(${p.id})">Eliminar</button>
      </div>
    </div>
  `).join('');
}

async function crearProveedor(e) {
  e.preventDefault();
  const msg = $('prov-msg');
  try {
    const body = {
      nombre: $('prov-nombre').value.trim(),
      ruc: $('prov-ruc').value.trim() || null,
      telefono: $('prov-telefono').value.trim() || null,
      email: $('prov-email').value.trim() || null,
      direccion: $('prov-direccion').value.trim() || null,
      contacto: $('prov-contacto').value.trim() || null
    };
    const res = await apiFetch('/proveedores/', {
      method: 'POST',
      body: JSON.stringify(body)
    });
    if (!res.ok) throw new Error(extraerMensaje(await res.json().catch(() => ({})), 'Error'));
    msg.textContent = '✅ Proveedor creado'; msg.className = 'msg ok';
    e.target.reset();
    await cargarProveedores();
    setTimeout(() => { msg.textContent = ''; }, 3000);
  } catch (ex) { msg.textContent = '❌ ' + ex.message; msg.className = 'msg err'; }
}

async function eliminarProveedor(id) {
  if (!confirm('¿Eliminar este proveedor?')) return;
  try {
    const res = await apiFetch(`/proveedores/${id}`, { method: 'DELETE' });
    if (!res.ok && res.status !== 204) {
      const data = await res.json().catch(() => ({}));
      throw new Error(extraerMensaje(data, 'Error al eliminar'));
    }
    await cargarProveedores();
  } catch (ex) { alert(ex.message); }
}

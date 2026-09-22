/* =====================================================
   auth.js — login, logout, sesión
   ===================================================== */
console.log('📦 auth.js cargado');

async function hacerLogin(e) {
  if (e && e.preventDefault) e.preventDefault();
  const email = $('login-email').value.trim();
  const password = $('login-password').value;
  const err = $('login-error');
  err.textContent = '';
  if (!email || !password) { err.textContent = 'Completa email y contraseña'; return; }
  try {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    const res = await fetch(API_URL + '/auth/login', { method: 'POST', body: formData });
    if (!res.ok) {
      let detalle = 'Credenciales inválidas';
      try { detalle = extraerMensaje(await res.json(), detalle); } catch (_) {}
      throw new Error(detalle);
    }
    const data = await res.json();
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('usuario', JSON.stringify(data.usuario || {}));
    await arrancarApp();
  } catch (ex) { err.textContent = ex.message; }
}

function cerrarSesion() {
  localStorage.removeItem('token');
  localStorage.removeItem('usuario');
  mostrarVista('login');
}

function mostrarVista(nombre) {
  const login = $('vista-login');
  const app = $('vista-app');
  if (nombre === 'login') {
    login.style.display = 'flex';
    app.classList.remove('visible');
  } else {
    login.style.display = 'none';
    app.classList.add('visible');
    const u = getUsuario();
    $('usuario-nombre').textContent = u.nombre || u.email || '—';
    $('usuario-rol').textContent = u.rol || '—';
  }
}

/* Muestra/oculta tabs según el rol del usuario */
function aplicarPermisos() {
  const misTabs = permisos().tabs;
  document.querySelectorAll('.nav-tab').forEach(btn => {
    if (misTabs.includes(btn.dataset.tab)) btn.classList.remove('hidden');
    else btn.classList.add('hidden');
  });
  /* Primer tab activo debe ser el primero permitido */
  const primerTab = document.querySelector('.nav-tab:not(.hidden)');
  if (primerTab) mostrarTab(primerTab.dataset.tab);
}

function mostrarTab(nombre) {
  if (!puedeTab(nombre)) return;
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  const el = $('tab-' + nombre);
  if (el) el.classList.add('active');
  document.querySelectorAll('.nav-tab').forEach(b => b.classList.remove('active'));
  const btn = document.querySelector(`.nav-tab[data-tab="${nombre}"]`);
  if (btn) btn.classList.add('active');

  if (nombre === 'productos') cargarProductos();
  else if (nombre === 'ventas') { cargarProductos(); cargarVentas(); }
  else if (nombre === 'reportes') cargarReportes();
  else if (nombre === 'categorias') cargarCategorias();
  else if (nombre === 'usuarios') cargarUsuarios();
}

async function arrancarApp() {
  mostrarVista('app');
  aplicarPermisos();
  /* Pre-carga de datos comunes */
  await Promise.all([cargarCategorias(), cargarProductos()]);
  if (puedeTab('ventas')) { renderVentaProductos(); cargarVentas(); }
}

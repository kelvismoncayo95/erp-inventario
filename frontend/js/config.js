/* =====================================================
   config.js — API_URL, helpers, apiFetch, permisos
   ===================================================== */
console.log('📦 config.js cargado');

const API_URL = `http://${window.location.hostname}:8000`;
const MONEDA = '$';

/* ---------- Helpers ---------- */
const $ = (id) => document.getElementById(id);
const esc = (s) => s == null ? '' : String(s).replace(/[&<>"']/g, c =>
  ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c]));

/* Formato pesos uruguayos: 1.234,56 */
const fmt = (n) => Number(n || 0).toLocaleString('es-UY', {
  minimumFractionDigits: 0,
  maximumFractionDigits: 2
});
const money = (n) => MONEDA + ' ' + fmt(n);

function extraerMensaje(d, fallback) {
  if (!d) return fallback;
  if (typeof d === 'string') return d;
  if (d.detail) {
    if (typeof d.detail === 'string') return d.detail;
    if (Array.isArray(d.detail)) return d.detail.map(e =>
      `${(e.loc || []).join('.')}: ${e.msg || JSON.stringify(e)}`).join(' | ');
    return JSON.stringify(d.detail);
  }
  return fallback;
}

/* ---------- apiFetch con JWT ---------- */
async function apiFetch(ep, opts = {}) {
  const token = localStorage.getItem('token');
  const headers = { 'Content-Type': 'application/json', ...(opts.headers || {}) };
  if (token) headers['Authorization'] = 'Bearer ' + token;
  let res;
  try { res = await fetch(API_URL + ep, { ...opts, headers }); }
  catch (e) { throw new Error('No se pudo conectar al servidor'); }
  if (res.status === 401) {
    localStorage.removeItem('token');
    localStorage.removeItem('usuario');
    if (typeof mostrarVista === 'function') mostrarVista('login');
    throw new Error('Sesión expirada');
  }
  return res;
}

/* ---------- Permisos por rol ---------- */
const PERMISOS = {
  admin: {
    tabs: ['productos', 'nuevo', 'ventas', 'reportes', 'categorias', 'usuarios'],
    puedeVender: false,
    puedeEliminarProducto: true,
    puedeReactivar: true,
    puedeCrearUsuarios: true,
    puedeVerReportes: true,
    puedeAnular: true,
    vendeSimulacro: true
  },
  encargado: {
    tabs: ['productos', 'nuevo', 'ventas', 'categorias'],
    puedeVender: true,
    puedeEliminarProducto: true,
    puedeReactivar: true,
    puedeCrearUsuarios: false,
    puedeVerReportes: false,
    puedeAnular: true,
    vendeSimulacro: false
  },
  vendedor: {
    tabs: ['productos', 'ventas'],
    puedeVender: true,
    puedeEliminarProducto: false,
    puedeReactivar: false,
    puedeCrearUsuarios: false,
    puedeVerReportes: false,
    puedeAnular: true,
    vendeSimulacro: false
  }
};

function getUsuario() {
  try { return JSON.parse(localStorage.getItem('usuario') || '{}'); }
  catch { return {}; }
}
function getRol() { return getUsuario().rol || ''; }
function permisos() { return PERMISOS[getRol()] || { tabs: [] }; }
function puedeTab(tab) { return permisos().tabs.includes(tab); }

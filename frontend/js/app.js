/* =====================================================
   app.js — arranque y enrutado
   ===================================================== */
console.log('🚀 app.js cargado');

function initApp() {
  const loginForm = $('login-form');
  if (loginForm) loginForm.addEventListener('submit', hacerLogin);
  document.querySelectorAll('.btn-logout').forEach(b => b.addEventListener('click', cerrarSesion));

  document.querySelectorAll('.nav-tab').forEach(b => {
    b.addEventListener('click', () => mostrarTab(b.dataset.tab));
  });

  /* Filtros de productos */
  document.querySelectorAll('.chip').forEach(ch => ch.addEventListener('click', () => {
    document.querySelectorAll('.chip').forEach(x => x.classList.remove('active'));
    ch.classList.add('active');
    filtroCampo = ch.dataset.campo;
    filtrarProductos();
  }));
  if ($('filtro-texto')) $('filtro-texto').addEventListener('input', filtrarProductos);
  document.querySelectorAll('input[name="filtro-estado"]').forEach(r =>
    r.addEventListener('change', filtrarProductos));

  /* Buscar en ventas — en vivo, sin esperar Enter */
  const ventaBuscar = $('venta-buscar');
  if (ventaBuscar) {
    ventaBuscar.addEventListener('input', renderVentaProductos);
    ventaBuscar.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') { ventaBuscar.value = ''; renderVentaProductos(); }
    });
  }

  /* Formularios */
  if ($('form-nuevo-producto')) $('form-nuevo-producto').addEventListener('submit', crearProducto);
  if ($('form-categoria')) $('form-categoria').addEventListener('submit', crearCategoria);
  if ($('form-usuario')) $('form-usuario').addEventListener('submit', crearUsuario);
  if ($('btn-confirmar-venta')) $('btn-confirmar-venta').addEventListener('click', confirmarVenta);

  /* Reportes — segmentado período */
  document.querySelectorAll('.seg-btn').forEach(b => b.addEventListener('click', () => {
    document.querySelectorAll('.seg-btn').forEach(x => x.classList.remove('active'));
    b.classList.add('active');
    periodoReporte = b.dataset.periodo;
    cargarReportes();
  }));

  configurarVistaPorRol();

  const token = localStorage.getItem('token');
  if (token) {
    arrancarApp();
  } else {
    mostrarVista('login');
  }
}

function configurarVistaPorRol() {
  const esAdmin = getRol() === 'admin';
  const esVendedor = getRol() === 'vendedor';

  const banner = $('banner-simulacro');
  if (banner) banner.classList.toggle('visible', esAdmin);

  if ($('ventas-titulo')) $('ventas-titulo').textContent = esAdmin ? 'Simulacro de Venta' : 'Nueva Venta';
  if ($('ventas-subtitulo')) $('ventas-subtitulo').textContent = esAdmin
    ? 'Practica el flujo de venta sin impactar la base de datos'
    : 'Busca por nombre o código y agrega productos';
  if ($('historial-subtitulo')) $('historial-subtitulo').textContent = esVendedor
    ? 'Solo tus ventas'
    : 'Últimas facturas de todos los vendedores';
  if ($('productos-subtitulo')) $('productos-subtitulo').textContent = esVendedor
    ? 'Consulta precios y disponibilidad'
    : 'Gestiona tu inventario';

  /* Vendedor: ocultar SOLO los chips de campo y pills de estado,
     pero MANTENER visible el buscador. */
  if (esVendedor) {
    if ($('chips-avanzados')) $('chips-avanzados').style.display = 'none';
    if ($('pills-estado')) $('pills-estado').style.display = 'none';
  }
}

window.hacerLogin = hacerLogin;
window.cerrarSesion = cerrarSesion;
window.mostrarTab = mostrarTab;
window.eliminarProducto = eliminarProducto;
window.reactivarProducto = reactivarProducto;
window.eliminarCategoria = eliminarCategoria;
window.quitarDelCarrito = quitarDelCarrito;
window.agregarAlCarrito = agregarAlCarrito;
window.verDetalleVenta = verDetalleVenta;
window.anularVenta = anularVenta;
window.desactivarUsuario = desactivarUsuario;
window.activarUsuario = activarUsuario;

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initApp);
else initApp();

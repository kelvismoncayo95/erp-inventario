# 📱 Comandos útiles desde el iPhone

## 🔌 Conectar a Ubuntu
- Abrir Termius
- Host: PC-Ubuntu (100.127.30.91:2222)
- Usuario: elvis_ictor

## 📂 Ir al proyecto ERP
cd ~/proyectos/erp-inventario/backend
source venv/bin/activate

## 🚀 Levantar el servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

## 🗄️ Ver la base de datos
psql -h 172.31.160.1 -U postgres -d erp_inventario

## 📊 Consultas útiles
# Ver productos
psql -h 172.31.160.1 -U postgres -d erp_inventario -c "SELECT id, nombre, sku, stock_actual FROM productos;"

# Ver usuarios
psql -h 172.31.160.1 -U postgres -d erp_inventario -c "SELECT id, nombre, email, rol FROM usuarios;"

# Ver tablas
psql -h 172.31.160.1 -U postgres -d erp_inventario -c "\dt"

## 🐍 Ejecutar scripts
python3 crear_tablas.py
python3 datos_prueba.py

## 🛑 Detener el servidor
Ctrl + C

## 🚪 Salir de SSH
exit

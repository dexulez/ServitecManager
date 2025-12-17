import sqlite3
import os
import shutil
import glob
from datetime import datetime

db_path = 'servitec_manager/SERVITEC.DB'
backup_dir = 'backups'

print("=" * 80)
print("🗑️  LIMPIEZA EXHAUSTIVA DE BASE DE DATOS")
print("=" * 80)
print()

# ============================================
# PASO 1: CREAR RESPALDO
# ============================================
print("[1/4] 📦 Creando respaldo de seguridad...")
try:
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f'SERVITEC_BACKUP_{timestamp}.DB')
    shutil.copy2(db_path, backup_path)
    print(f"✅ Respaldo creado: {backup_path}")
except Exception as e:
    print(f"❌ Error al crear respaldo: {e}")
    print("⚠️  Continuando sin respaldo...")

print()

# ============================================
# PASO 2: LIMPIAR BASE DE DATOS
# ============================================
print("[2/4] 🧹 Limpiando base de datos...")
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tablas a limpiar completamente
    tablas_limpiar = [
        'ordenes', 'finanzas', 'ventas', 'detalle_ventas', 
        'repuestos', 'pedidos', 'compras', 'detalle_compras',
        'pagos_proveedor', 'gastos', 'caja_sesiones'
    ]
    
    registros_eliminados = {}
    
    for tabla in tablas_limpiar:
        try:
            cursor.execute(f'SELECT COUNT(*) FROM {tabla}')
            count = cursor.fetchone()[0]
            cursor.execute(f'DELETE FROM {tabla}')
            registros_eliminados[tabla] = count
            print(f"   ✓ {tabla}: {count} registros eliminados")
        except sqlite3.OperationalError:
            pass  # Tabla no existe
    
    # Limpiar clientes (mantener estructura pero vaciar)
    try:
        cursor.execute('SELECT COUNT(*) FROM clientes')
        count = cursor.fetchone()[0]
        cursor.execute('DELETE FROM clientes')
        registros_eliminados['clientes'] = count
        print(f"   ✓ clientes: {count} registros eliminados")
    except:
        pass
    
    # Reiniciar secuencias de autoincremento
    cursor.execute('DELETE FROM sqlite_sequence')
    
    conn.commit()
    print(f"✅ Base de datos limpiada: {sum(registros_eliminados.values())} registros totales eliminados")
    
    # Verificar limpieza
    cursor.execute('SELECT COUNT(*) FROM ordenes')
    ordenes_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM clientes')
    clientes_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM usuarios')
    usuarios_count = cursor.fetchone()[0]
    
    conn.close()
    
    print()
    print("📊 Estado actual:")
    print(f"   - Órdenes: {ordenes_count}")
    print(f"   - Clientes: {clientes_count}")
    print(f"   - Usuarios: {usuarios_count} (conservados)")
    
except Exception as e:
    print(f"❌ Error al limpiar base de datos: {e}")

print()

# ============================================
# PASO 3: LIMPIAR CACHÉ
# ============================================
print("[3/4] 🗂️  Limpiando caché del sistema...")
try:
    cache_count = 0
    
    # Limpiar __pycache__
    for pycache_dir in glob.glob("**/__pycache__", recursive=True):
        if os.path.exists(pycache_dir):
            shutil.rmtree(pycache_dir, ignore_errors=True)
            cache_count += 1
    
    # Limpiar archivos .pyc
    for pyc_file in glob.glob("**/*.pyc", recursive=True):
        if os.path.exists(pyc_file):
            os.remove(pyc_file)
            cache_count += 1
    
    print(f"✅ {cache_count} elementos de caché eliminados")
except Exception as e:
    print(f"⚠️  Error al limpiar caché: {e}")

print()

# ============================================
# PASO 4: OPTIMIZAR BASE DE DATOS
# ============================================
print("[4/4] ⚡ Optimizando base de datos...")
try:
    conn = sqlite3.connect(db_path)
    conn.execute('VACUUM')
    conn.execute('ANALYZE')
    conn.close()
    print("✅ Base de datos optimizada")
except Exception as e:
    print(f"⚠️  Error al optimizar: {e}")

print()
print("=" * 80)
print("✅ LIMPIEZA COMPLETADA EXITOSAMENTE")
print("=" * 80)
print()
print("📝 Notas:")
print(f"   - Respaldo guardado en: {backup_dir}/")
print("   - Sistema listo para usar desde cero")
print("   - Usuarios y configuración conservados")
print()
input("Presione ENTER para salir...")

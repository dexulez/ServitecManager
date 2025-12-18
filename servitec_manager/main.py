import customtkinter as ctk
import os
import shutil
import glob
from database import GESTOR_BASE_DATOS
from logic import GESTOR_LOGICA
from cache_manager import CACHE_MANAGER, CACHE_INTELIGENTE
from ui.app import APLICACION

# CONSTANTES GLOBALES
MODO_APARIENCIA = "CLARO"
TEMA_COLOR_DEFECTO = "blue"
MENSAJE_INICIO = "SERVITEC MANAGER INICIADO CORRECTAMENTE."

def LIMPIAR_CACHE():
    """Limpia automáticamente todos los archivos de cache antes de iniciar"""
    try:
        # Limpiar carpetas __pycache__
        for pycache_dir in glob.glob("**/__pycache__", recursive=True):
            if os.path.exists(pycache_dir):
                shutil.rmtree(pycache_dir, ignore_errors=True)
        
        # Limpiar archivos .pyc
        for pyc_file in glob.glob("**/*.pyc", recursive=True):
            if os.path.exists(pyc_file):
                os.remove(pyc_file)
        
        print("🧹 Cache limpiado automáticamente")
    except Exception as e:
        print(f"⚠️ Error limpiando cache: {e}")

def EJECUTAR_MIGRACIONES():
    """Ejecuta migraciones de base de datos automáticamente"""
    import sqlite3
    import os
    
    db_path = 'SERVITEC.DB'
    
    # Si no existe la base de datos, no hacer nada (se creará con la estructura correcta)
    if not os.path.exists(db_path):
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si existe la columna descuento
        cursor.execute("PRAGMA table_info(ordenes)")
        columnas = cursor.fetchall()
        columnas_nombres = [col[1] for col in columnas]
        
        if 'descuento' not in columnas_nombres:
            print("🔧 Aplicando migración: agregando columna 'descuento'...")
            
            # Desactivar foreign keys temporalmente
            cursor.execute("PRAGMA foreign_keys = OFF")
            
            # Agregar columna con valor por defecto
            cursor.execute("ALTER TABLE ordenes ADD COLUMN descuento INTEGER DEFAULT 0")
            
            # Reactivar foreign keys
            cursor.execute("PRAGMA foreign_keys = ON")
            
            conn.commit()
            print("✅ Migración completada: columna 'descuento' agregada")
        
        # Crear tabla de cuentas bancarias si no existe
        try:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS cuentas_bancarias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                banco TEXT NOT NULL,
                numero_cuenta TEXT NOT NULL UNIQUE,
                tipo_cuenta TEXT,
                titular TEXT NOT NULL,
                rut_titular TEXT,
                notas TEXT,
                activa INTEGER DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            conn.commit()
            print("✅ Tabla 'cuentas_bancarias' lista")
        except Exception as e:
            print(f"⚠️ Error creando tabla cuentas_bancarias: {e}")
        
        # Crear tabla de boletas si no existe
        try:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS boletas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                orden_id INTEGER NOT NULL,
                numero_boleta TEXT UNIQUE,
                fecha_emision TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                monto_neto REAL,
                iva REAL,
                monto_total REAL,
                metodo_pago TEXT,
                estado TEXT DEFAULT 'EMITIDA',
                observaciones TEXT,
                FOREIGN KEY(orden_id) REFERENCES ordenes(id)
            )
            """)
            conn.commit()
            print("✅ Tabla 'boletas' lista")
        except Exception as e:
            print(f"⚠️ Error creando tabla boletas: {e}")
        
        # Crear tabla de detalles de orden si no existe
        try:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS detalles_orden (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                orden_id INTEGER NOT NULL,
                tipo_item TEXT NOT NULL,
                descripcion TEXT,
                costo REAL DEFAULT 0,
                cantidad INTEGER DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(orden_id) REFERENCES ordenes(id)
            )
            """)
            conn.commit()
            print("✅ Tabla 'detalles_orden' lista")
        except Exception as e:
            print(f"⚠️ Error creando tabla detalles_orden: {e}")
        
        conn.close()
    except Exception as e:
        print(f"⚠️ Error en migración: {e}")
        print(f"   Por favor, ejecute manualmente: python migrar_descuento.py")

def PRINCIPAL():
    # --- LIMPIEZA AUTOMÁTICA DE CACHE ---
    LIMPIAR_CACHE()
    
    # --- MIGRACIONES AUTOMÁTICAS ---
    EJECUTAR_MIGRACIONES()
    
    # --- CONFIGURACIÓN VISUAL ---
    ctk.set_appearance_mode("light") 
    ctk.set_default_color_theme("blue") 

    # --- INICIALIZACIÓN DE DATOS ---
    # 1. Conexión a Base de Datos (Persistente con WAL + MMAP)
    basedatos = GESTOR_BASE_DATOS()
    basedatos.INICIALIZAR_BD()

    # 2. Sistema de Caché en RAM (100x más rápido que disco)
    cache_manager = CACHE_MANAGER(max_age_hours=24, max_entries=500)
    cache_inteligente = CACHE_INTELIGENTE(basedatos, cache_manager)

    # 3. Carga de Lógica con Caché
    logica = GESTOR_LOGICA(basedatos, cache_inteligente)
    logica.SEMILLA_ADMINISTRADOR() 

    print(MENSAJE_INICIO)
    
    # Mostrar estadísticas de caché en RAM
    stats = cache_inteligente.obtener_estadisticas()
    if stats.get('entries', 0) > 0:
        print(f"📦 Caché RAM: {stats['entries']} entradas ({stats.get('usage_percent', 0)}% capacidad)")

    # --- LANZAMIENTO DE LA APP ---
    app = APLICACION(logica)
    app.mainloop()

if __name__ == "__main__":
    PRINCIPAL()
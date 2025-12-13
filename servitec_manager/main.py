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

def PRINCIPAL():
    # --- LIMPIEZA AUTOMÁTICA DE CACHE ---
    LIMPIAR_CACHE()
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
"""
Utilidad para gestionar el caché de ServitecManager
"""

import os
import sys
from cache_manager import CACHE_MANAGER, CACHE_INTELIGENTE
from database import GESTOR_BASE_DATOS

def mostrar_menu():
    print("\n" + "="*60)
    print("  GESTOR DE CACHÉ - SERVITEC MANAGER")
    print("="*60)
    print("\n1. Ver estadísticas del caché")
    print("2. Limpiar todo el caché")
    print("3. Regenerar caché completo")
    print("4. Ver tamaño del caché")
    print("5. Salir")
    print("\n" + "="*60)

def ver_estadisticas(cache_manager):
    """Muestra estadísticas detalladas del caché"""
    stats = cache_manager.get_stats()
    
    print("\n📊 ESTADÍSTICAS DEL CACHÉ")
    print("-" * 60)
    print(f"  Archivos en caché: {stats['files']}")
    print(f"  Tamaño total: {stats['size_mb']} MB")
    
    if stats['oldest']:
        print(f"  Archivo más antiguo: {stats['oldest']}")
    if stats['newest']:
        print(f"  Archivo más reciente: {stats['newest']}")
    
    # Calcular porcentaje de uso
    max_size_mb = 5
    porcentaje = (stats['size_mb'] / max_size_mb) * 100
    print(f"  Uso del caché: {porcentaje:.1f}% ({stats['size_mb']}/{max_size_mb} MB)")
    
    # Barra visual
    barras = int(porcentaje / 5)
    print(f"  [{'█' * barras}{'░' * (20 - barras)}] {porcentaje:.1f}%")
    
    print("-" * 60)

def limpiar_cache(cache_manager):
    """Limpia todo el caché"""
    print("\n🗑️  Limpiando caché...")
    cache_manager.invalidate_all()
    print("✅ Caché limpiado correctamente")
    
    # Verificar
    stats = cache_manager.get_stats()
    if stats['files'] == 0:
        print(f"   {stats['files']} archivos restantes")
    else:
        print(f"⚠  Advertencia: {stats['files']} archivos no se pudieron eliminar")

def regenerar_cache():
    """Regenera el caché completo desde la base de datos"""
    print("\n🔄 Regenerando caché...")
    
    try:
        # Conectar a BD
        bd = GESTOR_BASE_DATOS()
        
        # Crear caché nuevo
        cache_manager = CACHE_MANAGER(cache_dir=".cache", max_age_hours=24, max_size_mb=5)
        cache_inteligente = CACHE_INTELIGENTE(bd, cache_manager)
        
        # Limpiar caché anterior
        cache_manager.invalidate_all()
        
        print("  📦 Cargando inventario...")
        inv = cache_inteligente.cargar_inventario()
        print(f"     ✓ {len(inv) if inv else 0} productos")
        
        print("  🔧 Cargando repuestos...")
        rep = cache_inteligente.cargar_repuestos()
        print(f"     ✓ {len(rep) if rep else 0} repuestos")
        
        print("  ⚙️  Cargando servicios...")
        serv = cache_inteligente.cargar_servicios()
        print(f"     ✓ {len(serv) if serv else 0} servicios")
        
        print("  👥 Cargando clientes recientes...")
        cli = cache_inteligente.cargar_clientes_recientes(100)
        print(f"     ✓ {len(cli) if cli else 0} clientes")
        
        print("\n✅ Caché regenerado correctamente")
        
        # Mostrar estadísticas
        stats = cache_manager.get_stats()
        print(f"   Total: {stats['files']} archivos, {stats['size_mb']} MB")
        
    except Exception as e:
        print(f"❌ Error al regenerar caché: {e}")

def main():
    """Función principal"""
    cache_manager = CACHE_MANAGER(cache_dir=".cache", max_age_hours=24, max_size_mb=5)
    
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\nSeleccione una opción (1-5): ").strip()
            
            if opcion == "1":
                ver_estadisticas(cache_manager)
            elif opcion == "2":
                confirmar = input("\n⚠️  ¿Está seguro de limpiar todo el caché? (s/n): ").strip().lower()
                if confirmar == 's':
                    limpiar_cache(cache_manager)
            elif opcion == "3":
                confirmar = input("\n⚠️  ¿Regenerar caché completo? (s/n): ").strip().lower()
                if confirmar == 's':
                    regenerar_cache()
            elif opcion == "4":
                stats = cache_manager.get_stats()
                print(f"\n📁 Tamaño del caché: {stats['size_mb']} MB ({stats['files']} archivos)")
            elif opcion == "5":
                print("\n👋 Saliendo...")
                break
            else:
                print("\n❌ Opción inválida")
        
        except KeyboardInterrupt:
            print("\n\n👋 Saliendo...")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()

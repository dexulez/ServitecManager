"""
Script para asignar un proveedor por defecto a todos los repuestos y productos
que actualmente tienen proveedor_id = 0 (sin proveedor asignado)
"""
import sqlite3
import os

def asignar_proveedor_defecto():
    # Ruta de la base de datos
    db_path = os.path.join(os.path.dirname(__file__), "SERVITEC.DB")
    
    if not os.path.exists(db_path):
        print(f"❌ ERROR: No se encontró la base de datos en {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Verificar si existe algún proveedor
        cursor.execute("SELECT COUNT(*) FROM proveedores")
        count_proveedores = cursor.fetchone()[0]
        
        if count_proveedores == 0:
            print("❌ No hay proveedores creados en el sistema.")
            print("   Por favor, crea al menos un proveedor primero desde el módulo de Proveedores.")
            conn.close()
            return
        
        # 2. Listar proveedores disponibles
        cursor.execute("SELECT id, nombre FROM proveedores ORDER BY nombre")
        proveedores = cursor.fetchall()
        
        print("\n" + "="*60)
        print("ASIGNAR PROVEEDOR POR DEFECTO A REPUESTOS Y PRODUCTOS")
        print("="*60)
        print("\nProveedores disponibles:")
        for i, (prov_id, prov_nombre) in enumerate(proveedores, 1):
            print(f"  {i}. {prov_nombre} (ID: {prov_id})")
        
        # 3. Solicitar selección del proveedor por defecto
        while True:
            try:
                seleccion = input(f"\nSelecciona el número del proveedor por defecto (1-{len(proveedores)}): ")
                seleccion = int(seleccion)
                if 1 <= seleccion <= len(proveedores):
                    proveedor_id = proveedores[seleccion - 1][0]
                    proveedor_nombre = proveedores[seleccion - 1][1]
                    break
                else:
                    print(f"❌ Por favor ingresa un número entre 1 y {len(proveedores)}")
            except ValueError:
                print("❌ Por favor ingresa un número válido")
        
        # 4. Contar cuántos repuestos y productos necesitan actualización
        cursor.execute("SELECT COUNT(*) FROM repuestos WHERE proveedor_id = 0 OR proveedor_id IS NULL")
        repuestos_sin_proveedor = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM inventario WHERE proveedor_id = 0 OR proveedor_id IS NULL")
        productos_sin_proveedor = cursor.fetchone()[0]
        
        print(f"\n📊 Resumen:")
        print(f"   - Repuestos sin proveedor: {repuestos_sin_proveedor}")
        print(f"   - Productos sin proveedor: {productos_sin_proveedor}")
        print(f"   - Proveedor a asignar: {proveedor_nombre}")
        
        # 5. Confirmar
        confirmacion = input(f"\n¿Deseas continuar? (S/N): ").strip().upper()
        if confirmacion != 'S':
            print("❌ Operación cancelada")
            conn.close()
            return
        
        # 6. Actualizar repuestos
        cursor.execute(
            "UPDATE repuestos SET proveedor_id = ? WHERE proveedor_id = 0 OR proveedor_id IS NULL",
            (proveedor_id,)
        )
        repuestos_actualizados = cursor.rowcount
        
        # 7. Actualizar productos
        cursor.execute(
            "UPDATE inventario SET proveedor_id = ? WHERE proveedor_id = 0 OR proveedor_id IS NULL",
            (proveedor_id,)
        )
        productos_actualizados = cursor.rowcount
        
        # 8. Confirmar cambios
        conn.commit()
        
        print("\n" + "="*60)
        print("✅ ACTUALIZACIÓN COMPLETADA")
        print("="*60)
        print(f"   ✓ {repuestos_actualizados} repuestos actualizados")
        print(f"   ✓ {productos_actualizados} productos actualizados")
        print(f"   ✓ Proveedor asignado: {proveedor_nombre}")
        print("\nTodos los repuestos y productos ahora tienen un proveedor asignado.")
        print("Puedes cambiarlos individualmente desde el módulo de Inventario.")
        print("="*60 + "\n")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ ERROR durante la actualización: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    asignar_proveedor_defecto()

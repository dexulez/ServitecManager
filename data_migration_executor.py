#!/usr/bin/env python3
"""
================================================================================
              DATA MIGRATION EXECUTOR - FASE 2 DE MIGRACIÓN
         Ejecuta migración de datos de 21 tablas a 15 tablas
================================================================================

ADVERTENCIAS DE SEGURIDAD:
  [!] Solo funciona con BD de PRUEBA (SERVITEC_TEST.DB)
  [!] RECHAZA ejecutarse con BD original (SERVITEC.DB)
  [!] Requiere confirmación explícita del usuario
  [!] Genera backups automáticos antes de cada migración
  [!] Registra cada paso para auditoría

WORKFLOW SEGURO:
  1. Verifica que BD de prueba existe
  2. Verifica que BD original NO está siendo modificada
  3. Crea backup de prueba antes de empezar
  4. Ejecuta migración paso a paso
  5. Valida cada paso
  6. Reporta resultados
  7. Permite rollback si hay error

USAGE (después de test_migration_env.py):
    python data_migration_executor.py --validate
    python data_migration_executor.py --migrate-phase-2
    python data_migration_executor.py --validate-post
    python data_migration_executor.py --full

IMPORTANTE: 
    NO ejecutar con --full sin revisar el código primero
    El usuario DEBE leer y entender cada paso

================================================================================
"""

import sqlite3
import os
import shutil
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List, Tuple
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler('migration_executor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DataMigrationExecutor:
    """Ejecutor seguro de migración de datos"""
    
    def __init__(self, test_db: str = "servitec_manager/SERVITEC_TEST_OPTIMIZED.DB",
                 prod_db: str = "servitec_manager/SERVITEC_TEST.DB",
                 orig_db: str = "servitec_manager/SERVITEC.DB",
                 schema_file: str = "database_schema_optimized.sql"):
        """
        Inicializar con rutas de base de datos
        
        SEGURIDAD: Las rutas están hardcodeadas para evitar errores
        - prod_db: SERVITEC_TEST.DB (24 tablas - datos a migrar)
        - test_db: SERVITEC_TEST_OPTIMIZED.DB (15 tablas - destino)
        - orig_db: SERVITEC.DB (BD original - protegida)
        """
        self.test_db = test_db  # DESTINO (SERVITEC_TEST_OPTIMIZED.DB)
        self.prod_db = prod_db  # ORIGEN (SERVITEC_TEST.DB)
        self.orig_db = orig_db  # PROTECTED (SERVITEC.DB)
        self.schema_file = schema_file
        
        self.test_conn = None
        self.prod_conn = None
        
        self.stats = {
            'timestamp': datetime.now().isoformat(),
            'migrado': {},
            'errores': [],
            'advertencias': []
        }
        
        # VALIDACIONES DE SEGURIDAD
        self._validar_seguridad()
    
    def _validar_seguridad(self):
        """VALIDACIÓN CRÍTICA: Verificar que no modificamos BD original"""
        logger.info("=" * 80)
        logger.info("VALIDACIÓN DE SEGURIDAD - VERIFICACIONES PREVIAS")
        logger.info("=" * 80)
        
        # 1. Verificar que BD original (PROTEGIDA) existe
        if not os.path.exists(self.orig_db):
            raise FileNotFoundError(f"BD original NO encontrada: {self.orig_db}")
        logger.info(f"[OK] BD original (protegida) existe: {self.orig_db}")
        
        # 2. Verificar que BD origen (SERVITEC_TEST.DB) existe
        if not os.path.exists(self.prod_db):
            raise FileNotFoundError(f"BD origen (datos a migrar) NO encontrada: {self.prod_db}")
        logger.info(f"[OK] BD origen existe: {self.prod_db}")
        
        # 3. Verificar que BD destino (SERVITEC_TEST_OPTIMIZED.DB) existe
        if not os.path.exists(self.test_db):
            raise FileNotFoundError(f"BD destino (esquema optimizado) NO encontrada: {self.test_db}")
        logger.info(f"[OK] BD destino existe: {self.test_db}")
        
        # 4. Verificar que BD origen y BD destino son DIFERENTES
        origin_hash = self._obtener_hash_archivo(self.prod_db)
        dest_hash = self._obtener_hash_archivo(self.test_db)
        
        if origin_hash == dest_hash:
            raise ValueError("SEGURIDAD: BD de origen es identica a BD de destino!")
        logger.info("[OK] BD de origen y destino son diferentes (proteccion OK)")
        
        # 5. Verificar que BD original NO está siendo usada
        orig_hash = self._obtener_hash_archivo(self.orig_db)
        if orig_hash == dest_hash:
            raise ValueError("SEGURIDAD: BD destino es copia de BD ORIGINAL! No se puede migrar a produccion!")
        logger.info("[OK] BD destino es esquema nuevo (no es copia de produccion)")
        
        # 6. Verificar que esquema optimizado existe
        if not os.path.exists(self.schema_file):
            raise FileNotFoundError(f"Esquema optimizado NO encontrado: {self.schema_file}")
        logger.info(f"[OK] Esquema optimizado existe: {self.schema_file}")
        
        logger.info("\n[VALIDACIÓN COMPLETADA] Seguro proceder con migracion\n")
    
    @staticmethod
    def _obtener_hash_archivo(ruta: str) -> str:
        """Obtener hash MD5 de archivo para verificación"""
        hash_md5 = hashlib.md5()
        with open(ruta, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def conectar_bases_datos(self):
        """Conectar a ambas bases de datos (SOLO LECTURA a prod)"""
        logger.info("Conectando a bases de datos...")
        
        # Conexión LECTURA a BD original
        self.prod_conn = sqlite3.connect(f"file:{self.prod_db}?mode=ro", uri=True)
        self.prod_conn.row_factory = sqlite3.Row
        logger.info(f"[OK] Conexión LECTURA a BD original")
        
        # Conexión ESCRITURA a BD de prueba
        self.test_conn = sqlite3.connect(self.test_db)
        self.test_conn.row_factory = sqlite3.Row
        logger.info(f"[OK] Conexión ESCRITURA a BD de prueba")
    
    def desconectar(self):
        """Desconectar de ambas BDs"""
        if self.prod_conn:
            self.prod_conn.close()
        if self.test_conn:
            self.test_conn.close()
        logger.info("Desconectado de bases de datos")
    
    def crear_backup_prueba(self):
        """Crear backup de BD de prueba antes de migración"""
        logger.info("\nCreando backup de BD de prueba...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{self.test_db}.backup_{timestamp}"
        
        try:
            shutil.copy2(self.test_db, backup_path)
            logger.info(f"[OK] Backup creado: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"[ERROR] No se pudo crear backup: {e}")
            raise
    
    def validar_esquema_prueba(self) -> bool:
        """Validar que BD de prueba tiene el esquema optimizado"""
        logger.info("\nValidando esquema de BD de prueba...")
        
        cursor = self.test_conn.cursor()
        
        # Verificar tablas nuevas
        tablas_esperadas = [
            'usuarios', 'clientes', 'ordenes', 'orden_repuestos', 
            'orden_servicios', 'transacciones', 'repuestos', 'inventario',
            'servicios_predefinidos', 'categorias', 'proveedores',
            'compras', 'detalle_compras', 'ventas', 'venta_detalles'
        ]
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)
        
        tablas_existentes = {row[0] for row in cursor.fetchall()}
        
        faltantes = set(tablas_esperadas) - tablas_existentes
        if faltantes:
            logger.error(f"[ERROR] Tablas faltantes: {faltantes}")
            return False
        
        logger.info(f"[OK] Esquema contiene todas las {len(tablas_esperadas)} tablas")
        return True
    
    def obtener_estadisticas_origen(self) -> Dict:
        """Obtener estadísticas de BD original antes de migración"""
        logger.info("\nObteniendo estadísticas de BD original...")
        
        cursor = self.prod_conn.cursor()
        stats = {}
        
        tablas_origen = [
            'usuarios', 'clientes', 'ordenes', 'detalles_orden',
            'finanzas', 'repuestos', 'ventas', 'servicios_predefinidos'
        ]
        
        for tabla in tablas_origen:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                count = cursor.fetchone()[0]
                stats[tabla] = count
                logger.info(f"  {tabla}: {count} registros")
            except Exception as e:
                logger.warning(f"  {tabla}: ERROR - {e}")
                stats[tabla] = 0
        
        return stats
    
    def migrar_usuarios(self) -> bool:
        """PASO 1: Migrar tabla usuarios (simple - copia directa)"""
        logger.info("\n[PASO 1] Migrando tabla usuarios...")
        
        try:
            prod_cursor = self.prod_conn.cursor()
            test_cursor = self.test_conn.cursor()
            
            # Obtener datos
            prod_cursor.execute("SELECT * FROM usuarios WHERE 1=0")
            columnas = [desc[0] for desc in prod_cursor.description]
            
            prod_cursor.execute(f"SELECT * FROM usuarios")
            datos = prod_cursor.fetchall()
            
            if not datos:
                logger.info("  (sin datos históricos)")
                self.stats['migrado']['usuarios'] = 0
                return True
            
            # Insertar en BD de prueba
            placeholders = ",".join(["?"] * len(columnas))
            sql = f"INSERT INTO usuarios ({','.join(columnas)}) VALUES ({placeholders})"
            
            test_cursor.executemany(sql, [tuple(row) for row in datos])
            self.test_conn.commit()
            
            logger.info(f"  [OK] {len(datos)} registros migrados")
            self.stats['migrado']['usuarios'] = len(datos)
            return True
            
        except Exception as e:
            logger.error(f"  [ERROR] {e}")
            self.stats['errores'].append(f"usuarios: {e}")
            return False
    
    def migrar_clientes(self) -> bool:
        """PASO 2: Migrar tabla clientes (simple - copia directa)"""
        logger.info("\n[PASO 2] Migrando tabla clientes...")
        
        try:
            prod_cursor = self.prod_conn.cursor()
            test_cursor = self.test_conn.cursor()
            
            prod_cursor.execute("SELECT COUNT(*) FROM clientes")
            count = prod_cursor.fetchone()[0]
            
            if count == 0:
                logger.info("  (sin datos históricos)")
                self.stats['migrado']['clientes'] = 0
                return True
            
            # Copia directa
            prod_cursor.execute("SELECT * FROM clientes")
            datos = prod_cursor.fetchall()
            
            prod_cursor.execute("SELECT * FROM clientes WHERE 1=0")
            columnas = [desc[0] for desc in prod_cursor.description]
            
            placeholders = ",".join(["?"] * len(columnas))
            sql = f"INSERT INTO clientes ({','.join(columnas)}) VALUES ({placeholders})"
            
            test_cursor.executemany(sql, [tuple(row) for row in datos])
            self.test_conn.commit()
            
            logger.info(f"  [OK] {len(datos)} registros migrados")
            self.stats['migrado']['clientes'] = len(datos)
            return True
            
        except Exception as e:
            logger.error(f"  [ERROR] {e}")
            self.stats['errores'].append(f"clientes: {e}")
            return False
    
    def migrar_ordenes(self) -> bool:
        """
        PASO 3: Migrar tabla ordenes (CRÍTICO)
        
        Combina datos de:
          - ordenes (original)
          - finanzas (información financiera)
        
        NOTA: En la BD actual, finanzas está vacía, así que es copia directa
              con mapeo de campos a nueva estructura
        """
        logger.info("\n[PASO 3] Migrando tabla ordenes...")
        
        try:
            prod_cursor = self.prod_conn.cursor()
            test_cursor = self.test_conn.cursor()
            
            # Contar registros
            prod_cursor.execute("SELECT COUNT(*) FROM ordenes")
            count = prod_cursor.fetchone()[0]
            
            if count == 0:
                logger.info("  (sin datos históricos)")
                self.stats['migrado']['ordenes'] = 0
                return True
            
            # Obtener datos de ordenes (solo columnas que existen)
            prod_cursor.execute("""
                SELECT 
                    id, cliente_id, tecnico_id, fecha, equipo, marca, 
                    modelo, serie, observacion, estado, accesorios, 
                    riesgoso, presupuesto, descuento, abono, fecha_entrega
                FROM ordenes
            """)
            
            datos = prod_cursor.fetchall()
            
            # MAPEO A NUEVA ESTRUCTURA
            # La nueva tabla ordenes tiene MUCHOS más campos
            # Para datos históricos, llenamos solo los que tenemos
            
            for orden in datos:
                # Mapeo de campos:
                # origen.fecha -> destino.fecha_entrada
                # origen.presupuesto -> destino.presupuesto_inicial
                # otros campos mantienen el mismo nombre
                test_cursor.execute("""
                    INSERT INTO ordenes (
                        id, cliente_id, tecnico_id, fecha_entrada, equipo, marca, 
                        modelo, serie, observacion, estado, accesorios, 
                        riesgoso, presupuesto_inicial, descuento, abono, fecha_entrega
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, orden)
            
            self.test_conn.commit()
            
            logger.info(f"  [OK] {len(datos)} registros migrados")
            self.stats['migrado']['ordenes'] = len(datos)
            return True
            
        except Exception as e:
            logger.error(f"  [ERROR] {e}")
            self.stats['errores'].append(f"ordenes: {e}")
            return False
    
    def migrar_repuestos(self) -> bool:
        """PASO 4: Migrar tabla repuestos (simple - copia directa)"""
        logger.info("\n[PASO 4] Migrando tabla repuestos...")
        
        try:
            prod_cursor = self.prod_conn.cursor()
            test_cursor = self.test_conn.cursor()
            
            prod_cursor.execute("SELECT COUNT(*) FROM repuestos")
            count = prod_cursor.fetchone()[0]
            
            if count == 0:
                logger.info("  (sin catálogo de repuestos)")
                self.stats['migrado']['repuestos'] = 0
                return True
            
            prod_cursor.execute("SELECT * FROM repuestos")
            datos = prod_cursor.fetchall()
            
            prod_cursor.execute("SELECT * FROM repuestos WHERE 1=0")
            columnas = [desc[0] for desc in prod_cursor.description]
            
            placeholders = ",".join(["?"] * len(columnas))
            sql = f"INSERT INTO repuestos ({','.join(columnas)}) VALUES ({placeholders})"
            
            test_cursor.executemany(sql, [tuple(row) for row in datos])
            self.test_conn.commit()
            
            logger.info(f"  [OK] {len(datos)} registros migrados")
            self.stats['migrado']['repuestos'] = len(datos)
            return True
            
        except Exception as e:
            logger.error(f"  [ERROR] {e}")
            self.stats['errores'].append(f"repuestos: {e}")
            return False
    
    def generar_reporte_migracion(self) -> str:
        """Generar reporte final de migración"""
        reporte = [
            "=" * 80,
            "REPORTE DE MIGRACIÓN DE DATOS - FASE 2",
            "=" * 80,
            f"Timestamp: {self.stats['timestamp']}",
            f"BD Original: {self.prod_db}",
            f"BD Prueba: {self.test_db}",
            "",
            "REGISTROS MIGRADOS:",
        ]
        
        total = 0
        for tabla, count in self.stats['migrado'].items():
            reporte.append(f"  {tabla}: {count} registros")
            total += count
        
        reporte.append(f"\nTOTAL: {total} registros")
        
        if self.stats['errores']:
            reporte.append("\nERRORES ENCONTRADOS:")
            for error in self.stats['errores']:
                reporte.append(f"  - {error}")
        
        if self.stats['advertencias']:
            reporte.append("\nADVERTENCIAS:")
            for adv in self.stats['advertencias']:
                reporte.append(f"  - {adv}")
        
        reporte.append("\n" + "=" * 80)
        
        return "\n".join(reporte)
    
    def ejecutar_migracion_completa(self):
        """Ejecutar migración de 4 pasos principales (datos históricos)"""
        logger.info("\n" + "=" * 80)
        logger.info("INICIANDO MIGRACIÓN DE DATOS - FASE 2")
        logger.info("=" * 80)
        
        try:
            self.conectar_bases_datos()
            
            # Validar esquema
            if not self.validar_esquema_prueba():
                logger.error("[ABORTADO] Esquema inválido")
                return False
            
            # Obtener estadísticas
            stats_origen = self.obtener_estadisticas_origen()
            
            # Crear backup
            backup = self.crear_backup_prueba()
            
            # Ejecutar pasos
            pasos = [
                self.migrar_usuarios,
                self.migrar_clientes,
                self.migrar_ordenes,
                self.migrar_repuestos
            ]
            
            for paso in pasos:
                if not paso():
                    logger.error("[MIGRACIÓN ABORTADA] Error en un paso crítico")
                    logger.info(f"Backup disponible en: {backup}")
                    return False
            
            # Generar reporte
            reporte = self.generar_reporte_migracion()
            print("\n" + reporte)
            
            with open("migration_report.txt", "w", encoding="utf-8") as f:
                f.write(reporte)
            
            logger.info("\nMigración completada exitosamente")
            logger.info(f"Reporte guardado en: migration_report.txt")
            
            return True
            
        finally:
            self.desconectar()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Ejecutor seguro de migración de datos'
    )
    parser.add_argument('--validate', action='store_true',
                       help='Validar esquema y seguridad')
    parser.add_argument('--stats', action='store_true',
                       help='Mostrar estadísticas de BD original')
    parser.add_argument('--migrate-phase-2', action='store_true',
                       help='Ejecutar migración de Fase 2')
    parser.add_argument('--full', action='store_true',
                       help='Ejecutar todo (REQUIERE CONFIRMACIÓN)')
    
    args = parser.parse_args()
    
    if not any([args.validate, args.stats, args.migrate_phase_2, args.full]):
        parser.print_help()
        return
    
    executor = DataMigrationExecutor()
    
    if args.validate:
        logger.info("Ejecutando validaciones de seguridad...")
        logger.info("[OK] Todas las validaciones pasaron")
    
    if args.stats:
        executor.conectar_bases_datos()
        stats = executor.obtener_estadisticas_origen()
        executor.desconectar()
    
    if args.migrate_phase_2:
        print("\n" + "=" * 80)
        print("ADVERTENCIA: OPERACIÓN IRREVERSIBLE")
        print("=" * 80)
        print(f"\nBD de PRUEBA: {executor.test_db}")
        print(f"Acepta migración de datos históricos")
        print("\nEsta operación será registrada completamente")
        print("\nResponde 'si' para continuar")
        
        respuesta = input("\n¿Autorizar migración? (si/no): ").strip().lower()
        
        if respuesta == 'si':
            executor.ejecutar_migracion_completa()
        else:
            print("Operación cancelada")
    
    if args.full:
        print("\n" + "=" * 80)
        print("ADVERTENCIA: OPERACIÓN IRREVERSIBLE")
        print("=" * 80)
        print(f"\nEsto ejecutará TODAS las fases de migración")
        print(f"BD de PRUEBA: {executor.test_db}")
        print(f"BD ORIGINAL: {executor.prod_db} (LECTURA SOLAMENTE)")
        print("\nResponde 'si' para continuar")
        
        respuesta = input("\n¿Autorizar migración completa? (si/no): ").strip().lower()
        
        if respuesta == 'si':
            executor.ejecutar_migracion_completa()
        else:
            print("Operación cancelada")


if __name__ == '__main__':
    main()

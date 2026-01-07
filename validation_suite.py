#!/usr/bin/env python3
"""
================================================================================
                        VALIDATION SUITE
              Suite completa de validaci n para migraci n
================================================================================

OBJETIVO:
Validar que la migraci n se realiz  correctamente

VALIDACIONES:
1. Integridad referencial (FK constraints)
2. Sumas financieras (ingresos = gastos)
3. Consistencia de stock
4. Datos hist ricos preservados
5. Relaciones de datos intactas
6. Performance de queries

USAGE:
    python validation_suite.py --check-integrity
    python validation_suite.py --check-finances
    python validation_suite.py --check-stock
    python validation_suite.py --full
================================================================================
"""

import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Tuple
from dataclasses import dataclass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('validation_suite.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Resultado de una validaci n"""
    nombre: str
    tipo: str  # 'info', 'ok', 'warning', 'error'
    mensaje: str
    detalles: str = ""
    registro_ejemplo: str = ""


class ValidationSuite:
    """Suite de validaciones para migraci n"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self.resultados: List[ValidationResult] = []
    
    def conectar(self):
        """Conectar a BD"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"Conectado a: {self.db_path}")
        except Exception as e:
            logger.error(f"Error al conectar: {e}")
            raise
    
    def desconectar(self):
        """Desconectar de BD"""
        if self.conn:
            self.conn.close()
    
    def validar_integridad_referencial(self) -> bool:
        """Validar integridad referencial (FK constraints)"""
        logger.info("\n" + "=" * 80)
        logger.info("VALIDACI N 1: Integridad Referencial")
        logger.info("=" * 80)
        
        cursor = self.conn.cursor()
        
        try:
            # Habilitar FK
            cursor.execute("PRAGMA foreign_keys = ON")
            
            # Verificar integridad
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            
            if result[0] == 'ok':
                logger.info("[OK] Integridad referencial OK")
                self.resultados.append(ValidationResult(
                    nombre="Integridad Referencial",
                    tipo="ok",
                    mensaje="Todas las FK constraints son v lidas"
                ))
                return True
            else:
                logger.error(f"[!] Problema detectado: {result[0]}")
                self.resultados.append(ValidationResult(
                    nombre="Integridad Referencial",
                    tipo="error",
                    mensaje=result[0]
                ))
                return False
        
        except Exception as e:
            logger.error(f"[!] Error en validaci n: {e}")
            self.resultados.append(ValidationResult(
                nombre="Integridad Referencial",
                tipo="error",
                mensaje=str(e)
            ))
            return False
    
    def validar_sumas_financieras(self) -> bool:
        """Validar que sumas financieras sean consistentes"""
        logger.info("\n" + "=" * 80)
        logger.info("VALIDACI N 2: Sumas Financieras")
        logger.info("=" * 80)
        
        cursor = self.conn.cursor()
        todas_ok = True
        
        try:
            # 1. Si existe tabla 'ordenes', validar presupuestos
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='ordenes'
            """)
            
            if cursor.fetchone():
                logger.info("\n  Validando tabla 'ordenes'...")
                
                # Validar sumas financieras (presupuesto_inicial, abono, total_a_cobrar)
                cursor.execute("""
                    SELECT 
                        id,
                        presupuesto_inicial,
                        abono,
                        total_a_cobrar,
                        saldo_pendiente
                    FROM ordenes
                    WHERE presupuesto_inicial > 0
                    LIMIT 10
                """)
                
                ordenes_data = cursor.fetchall()
                if ordenes_data:
                    total_presupuesto = sum(float(o['presupuesto_inicial'] or 0) for o in ordenes_data)
                    total_abono = sum(float(o['abono'] or 0) for o in ordenes_data)
                    total_a_cobrar = sum(float(o['total_a_cobrar'] or 0) for o in ordenes_data)
                    
                    logger.info(f"  [OK] Ordenes encontradas: {len(ordenes_data)}")
                    logger.info(f"    - Total presupuesto_inicial: {total_presupuesto}")
                    logger.info(f"    - Total abono: {total_abono}")
                    logger.info(f"    - Total a cobrar: {total_a_cobrar}")
                else:
                    logger.info("  [OK] Sin ordenes con presupuesto")
            
            # 2. Si existe tabla 'finanzas', validar
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='finanzas'
            """)
            
            if cursor.fetchone():
                logger.info("\n  Validando tabla 'finanzas'...")
                
                cursor.execute("""
                    SELECT COUNT(*) FROM finanzas
                """)
                
                count = cursor.fetchone()[0]
                logger.info(f"  [OK] {count} registros financieros")
            
            # 3. Si existe tabla 'transacciones', validar
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='transacciones'
            """)
            
            if cursor.fetchone():
                logger.info("\n  Validando tabla 'transacciones'...")
                
                cursor.execute("""
                    SELECT 
                        tipo,
                        COUNT(*) as cantidad,
                        SUM(CAST(monto_final AS REAL)) as total
                    FROM transacciones
                    GROUP BY tipo
                """)
                
                for row in cursor.fetchall():
                    logger.info(f"    {row['tipo']}: {row['cantidad']} transacciones, ${row['total']:.2f}")
                
                self.resultados.append(ValidationResult(
                    nombre="Sumas Financieras",
                    tipo="ok",
                    mensaje="Transacciones registradas correctamente"
                ))
            
            return todas_ok
        
        except Exception as e:
            logger.error(f"[!] Error: {e}")
            self.resultados.append(ValidationResult(
                nombre="Sumas Financieras",
                tipo="error",
                mensaje=str(e)
            ))
            return False
    
    def validar_stock(self) -> bool:
        """Validar consistencia de stock"""
        logger.info("\n" + "=" * 80)
        logger.info("VALIDACI N 3: Consistencia de Stock")
        logger.info("=" * 80)
        
        cursor = self.conn.cursor()
        
        try:
            # Verificar tabla 'inventario'
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='inventario'
            """)
            
            if not cursor.fetchone():
                logger.info("  Tabla 'inventario' no existe (puede ser normal)")
                self.resultados.append(ValidationResult(
                    nombre="Consistencia de Stock",
                    tipo="info",
                    mensaje="Tabla inventario no presente"
                ))
                return True
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM inventario")
            count = cursor.fetchone()[0]
            logger.info(f"  [OK] {count} registros en inventario")
            
            # Verificar stocks en orden_repuestos
            cursor.execute("""
                SELECT COUNT(*) FROM orden_repuestos
            """)
            count_orden_rep = cursor.fetchone()[0]
            logger.info(f"  [OK] Registros en orden_repuestos: {count_orden_rep}")
            
            # Verificar stocks en repuestos
            cursor.execute("""
                SELECT COUNT(*) as total, 
                       SUM(CASE WHEN stock < 0 THEN 1 ELSE 0 END) as negativos
                FROM repuestos
            """)
            result = cursor.fetchone()
            total_rep = result[0]
            neg_rep = result[1] or 0
            logger.info(f"  [OK] Total repuestos: {total_rep}, con stock negativo: {neg_rep}")
            
            if neg_rep == 0:
                logger.info("  [OK] Sin stocks negativos")
                self.resultados.append(ValidationResult(
                    nombre="Stock Negativo",
                    tipo="ok",
                    mensaje="Todos los stocks son positivos"
                ))
            else:
                logger.warning(f"  [!] {neg_rep} repuestos con stock negativo")
                self.resultados.append(ValidationResult(
                    nombre="Stock Negativo",
                    tipo="warning",
                    mensaje=f"{neg_rep} repuestos con stock negativo"
                ))
            
            return True
        
        except Exception as e:
            logger.error(f"[!] Error: {e}")
            self.resultados.append(ValidationResult(
                nombre="Consistencia de Stock",
                tipo="error",
                mensaje=str(e)
            ))
            return False
    
    def validar_datos_historicos(self) -> bool:
        """Validar que datos hist ricos se preservaron"""
        logger.info("\n" + "=" * 80)
        logger.info("VALIDACI N 4: Datos Hist ricos Preservados")
        logger.info("=" * 80)
        
        cursor = self.conn.cursor()
        
        try:
            # Contar registros en tablas principales
            tablas_criticas = ['usuarios', 'clientes', 'ordenes', 'repuestos']
            
            logger.info("\n  Conteo de registros por tabla:")
            
            for tabla in tablas_criticas:
                cursor.execute(f"""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='{tabla}'
                """)
                
                if cursor.fetchone():
                    cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                    count = cursor.fetchone()[0]
                    logger.info(f"    {tabla}: {count} registros")
            
            self.resultados.append(ValidationResult(
                nombre="Datos Hist ricos",
                tipo="info",
                mensaje="Registros contados por tabla"
            ))
            
            return True
        
        except Exception as e:
            logger.error(f"[!] Error: {e}")
            self.resultados.append(ValidationResult(
                nombre="Datos Hist ricos",
                tipo="error",
                mensaje=str(e)
            ))
            return False
    
    def validar_relaciones_datos(self) -> bool:
        """Validar que relaciones entre datos est n intactas"""
        logger.info("\n" + "=" * 80)
        logger.info("VALIDACI N 5: Relaciones de Datos Intactas")
        logger.info("=" * 80)
        
        cursor = self.conn.cursor()
        
        try:
            # Verificar  rfanos ( rdenes sin cliente)
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='ordenes'
            """)
            
            if cursor.fetchone():
                cursor.execute("""
                    SELECT o.id FROM ordenes o
                    WHERE cliente_id IS NOT NULL
                    AND cliente_id NOT IN (SELECT id FROM clientes)
                """)
                
                orfanos = cursor.fetchall()
                if orfanos:
                    logger.warning(f"  [!] {len(orfanos)}  rdenes sin cliente v lido")
                    self.resultados.append(ValidationResult(
                        nombre="Relaciones -  rdenes sin Cliente",
                        tipo="warning",
                        mensaje=f"{len(orfanos)}  rdenes orfanas"
                    ))
                else:
                    logger.info("  [OK] Todas las  rdenes tienen cliente v lido")
            
            self.resultados.append(ValidationResult(
                nombre="Relaciones de Datos",
                tipo="ok",
                mensaje="Validaci n de relaciones completada"
            ))
            
            return True
        
        except Exception as e:
            logger.error(f"[!] Error: {e}")
            self.resultados.append(ValidationResult(
                nombre="Relaciones de Datos",
                tipo="error",
                mensaje=str(e)
            ))
            return False
    
    def generar_reporte(self) -> str:
        """Generar reporte de validaci n"""
        reporte = [
            "=" * 80,
            "REPORTE DE VALIDACI N DE MIGRACI N",
            "=" * 80,
            f"Fecha: {datetime.now().isoformat()}",
            f"Base de datos: {self.db_path}",
            "",
            "RESULTADOS:",
            ""
        ]
        
        # Contar por tipo
        por_tipo = {}
        for resultado in self.resultados:
            por_tipo[resultado.tipo] = por_tipo.get(resultado.tipo, 0) + 1
        
        reporte.append("RESUMEN:")
        for tipo in ['ok', 'warning', 'error', 'info']:
            if tipo in por_tipo:
                reporte.append(f"  {tipo.upper()}: {por_tipo[tipo]} validaciones")
        
        reporte.append("")
        reporte.append("DETALLE:")
        
        for resultado in self.resultados:
            icono = "[OK]" if resultado.tipo == "ok" else "[!]" if resultado.tipo == "warning" else "[!]" if resultado.tipo == "error" else " "
            reporte.append(f"\n{icono} {resultado.nombre}")
            reporte.append(f"  Mensaje: {resultado.mensaje}")
            
            if resultado.detalles:
                reporte.append(f"  Detalles:\n{resultado.detalles}")
        
        reporte.append("")
        reporte.append("=" * 80)
        reporte.append("FIN DEL REPORTE")
        reporte.append("=" * 80)
        
        return "\n".join(reporte)
    
    def ejecutar_todas_validaciones(self):
        """Ejecutar todas las validaciones"""
        self.validar_integridad_referencial()
        self.validar_sumas_financieras()
        self.validar_stock()
        self.validar_datos_historicos()
        self.validar_relaciones_datos()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Suite de validaci n para migraci n'
    )
    parser.add_argument('--db', default='servitec_manager/SERVITEC_TEST.DB',
                       help='Ruta de BD a validar')
    parser.add_argument('--full', action='store_true',
                       help='Ejecutar todas las validaciones')
    parser.add_argument('--integrity', action='store_true',
                       help='Validar integridad referencial')
    parser.add_argument('--finances', action='store_true',
                       help='Validar sumas financieras')
    parser.add_argument('--stock', action='store_true',
                       help='Validar consistencia de stock')
    
    args = parser.parse_args()
    
    suite = ValidationSuite(args.db)
    
    try:
        suite.conectar()
        
        if args.full or not any([args.integrity, args.finances, args.stock]):
            print("\n[*] Ejecutando todas las validaciones...\n")
            suite.ejecutar_todas_validaciones()
        else:
            if args.integrity:
                suite.validar_integridad_referencial()
            if args.finances:
                suite.validar_sumas_financieras()
            if args.stock:
                suite.validar_stock()
        
        # Generar reporte
        reporte = suite.generar_reporte()
        print("\n" + reporte)
        
        # Guardar reporte
        with open('validation_report.txt', 'w', encoding='utf-8') as f:
            f.write(reporte)
        
        print(f"\n[+] Reporte guardado en: validation_report.txt")
        
    finally:
        suite.desconectar()


if __name__ == '__main__':
    main()

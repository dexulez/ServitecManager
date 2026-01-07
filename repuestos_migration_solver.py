#!/usr/bin/env python3
"""
================================================================================
                    REPUESTOS MIGRATION SOLVER
                 Soluciona el problema de repuestos sin ID
================================================================================

PROBLEMA:
La tabla detalles_orden solo tiene descripcion (TEXT), no repuesto_id
Necesitamos mapear descripciones a repuestos existentes

SOLUCIÓN:
1. Fuzzy matching: Buscar coincidencias parciales
2. Crear repuestos faltantes si es necesario
3. Generar reporte de migraciones problemáticas
4. Permitir revisión manual antes de confirmar

USAGE:
    python repuestos_migration_solver.py --analyze
    python repuestos_migration_solver.py --create-mapping
    python repuestos_migration_solver.py --migrate
    python repuestos_migration_solver.py --report
================================================================================
"""

import sqlite3
import difflib
import os
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration_repuestos.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class RepuestoMapping:
    """Mapeo de un detalles_orden a un repuesto"""
    detalles_id: int
    descripcion_original: str
    repuesto_id: Optional[int]
    repuesto_nombre: Optional[str]
    confianza: float  # 0-1, 1=coincidencia exacta
    tipo_mapeo: str  # 'exacto', 'fuzzy', 'nuevo', 'manual', 'descartado'
    notas: str = ""


class RepuestosMigrationSolver:
    """Solucionador inteligente para mapear repuestos históricos"""
    
    def __init__(self, db_path: str = "servitec_manager/SERVITEC.DB"):
        self.db_path = db_path
        self.conn = None
        self.mappings: Dict[int, RepuestoMapping] = {}
        self.repuestos_nuevos: List[Dict] = []
        self.estadisticas = {
            'total_detalles': 0,
            'exactas': 0,
            'fuzzy': 0,
            'nuevas': 0,
            'descartadas': 0,
            'manual_review': 0
        }
    
    def conectar(self):
        """Conectar a la base de datos"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"Conectado a BD: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Error al conectar: {e}")
            raise
    
    def desconectar(self):
        """Desconectar de la base de datos"""
        if self.conn:
            self.conn.close()
            logger.info("Desconectado de BD")
    
    def obtener_detalles_orden(self) -> List[Dict]:
        """Obtener todos los registros de detalles_orden"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, orden_id, tipo_item, descripcion, costo, cantidad
            FROM detalles_orden
            WHERE tipo_item = 'REPUESTO'
            ORDER BY descripcion
        """)
        return [dict(row) for row in cursor.fetchall()]
    
    def obtener_repuestos_catalogo(self) -> Dict[int, Dict]:
        """Obtener catálogo de repuestos con sus nombres normalizados"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, nombre, categoria, costo, precio_sugerido, stock
            FROM repuestos
            ORDER BY nombre
        """)
        
        repuestos = {}
        for row in cursor.fetchall():
            row_dict = dict(row)
            row_dict['nombre_normalizado'] = self.normalizar_nombre(row_dict['nombre'])
            repuestos[row['id']] = row_dict
        
        return repuestos
    
    @staticmethod
    def normalizar_nombre(nombre: str) -> str:
        """Normalizar nombre para comparación"""
        if not nombre:
            return ""
        
        # Convertir a minúsculas, eliminar espacios extra
        nombre = nombre.lower().strip()
        
        # Eliminar caracteres especiales pero mantener guiones y números
        import re
        nombre = re.sub(r'[^\w\s\-]', '', nombre)
        
        # Eliminar espacios múltiples
        nombre = ' '.join(nombre.split())
        
        return nombre
    
    def encontrar_coincidencia(self, descripcion: str, repuestos: Dict[int, Dict]) -> Tuple[Optional[int], float, str]:
        """Encontrar coincidencia de descripción en catálogo de repuestos"""
        desc_norm = self.normalizar_nombre(descripcion)
        
        if not desc_norm:
            return None, 0.0, "descripcion_vacia"
        
        # Intentar coincidencia exacta primero
        for rep_id, rep_data in repuestos.items():
            if rep_data['nombre_normalizado'] == desc_norm:
                return rep_id, 1.0, 'exacto'
        
        # Intentar coincidencia parcial (fuzzy matching)
        mejores = []
        for rep_id, rep_data in repuestos.items():
            ratio = difflib.SequenceMatcher(
                None, 
                desc_norm, 
                rep_data['nombre_normalizado']
            ).ratio()
            if ratio >= 0.7:  # 70% de similitud
                mejores.append((rep_id, ratio))
        
        if mejores:
            mejores.sort(key=lambda x: x[1], reverse=True)
            rep_id, ratio = mejores[0]
            tipo_mapeo = 'fuzzy'
            return rep_id, ratio, tipo_mapeo
        
        # Sin coincidencia
        return None, 0.0, 'sin_coincidencia'
    
    def analizar_detalles(self) -> Dict:
        """Analizar detalles_orden y crear mapeos"""
        logger.info("Iniciando análisis de detalles_orden...")
        
        detalles = self.obtener_detalles_orden()
        repuestos = self.obtener_repuestos_catalogo()
        
        if not detalles:
            logger.warning("No hay detalles_orden con tipo REPUESTO")
            return self.estadisticas
        
        self.estadisticas['total_detalles'] = len(detalles)
        
        # Agrupar descripciones para análisis
        descripciones_unicas = defaultdict(list)
        
        for detalles_row in detalles:
            desc = detalles_row['descripcion']
            desc_id = detalles_row['id']
            descripciones_unicas[desc].append(desc_id)
            
            # Buscar coincidencia
            rep_id, confianza, tipo_mapeo = self.encontrar_coincidencia(desc, repuestos)
            
            if rep_id:
                self.mappings[desc_id] = RepuestoMapping(
                    detalles_id=desc_id,
                    descripcion_original=desc,
                    repuesto_id=rep_id,
                    repuesto_nombre=repuestos[rep_id]['nombre'],
                    confianza=confianza,
                    tipo_mapeo=tipo_mapeo
                )
                self.estadisticas[tipo_mapeo] += 1
            else:
                # Crear nuevo repuesto
                self.mappings[desc_id] = RepuestoMapping(
                    detalles_id=desc_id,
                    descripcion_original=desc,
                    repuesto_id=None,
                    repuesto_nombre=None,
                    confianza=0.0,
                    tipo_mapeo='nuevo'
                )
                
                # Agregar a lista de nuevos repuestos (si no existe ya)
                if desc not in [r['nombre'] for r in self.repuestos_nuevos]:
                    self.repuestos_nuevos.append({
                        'nombre': desc,
                        'categoria': 'MIGRACIÓN - SIN CATEGORÍA',
                        'costo': detalles_row['costo'],
                        'precio_sugerido': detalles_row['costo'] * 1.3,
                        'stock': 0,
                        'proveedor_id': None
                    })
                
                self.estadisticas['nuevas'] += 1
        
        logger.info(f"Análisis completado:")
        logger.info(f"  Total descripciones únicas: {len(descripciones_unicas)}")
        logger.info(f"  Mapeos encontrados: {self.estadisticas['exactas'] + self.estadisticas['fuzzy']}")
        logger.info(f"  Nuevos repuestos necesarios: {len(self.repuestos_nuevos)}")
        
        return self.estadisticas
    
    def generar_reporte_analisis(self) -> str:
        """Generar reporte de análisis"""
        reporte = [
            "=" * 80,
            "ANÁLISIS DE MIGRACIÓN DE REPUESTOS",
            "=" * 80,
            f"Fecha: {datetime.now().isoformat()}",
            f"Base de datos: {self.db_path}",
            "",
            "ESTADÍSTICAS:",
            f"  Total de items: {self.estadisticas['total_detalles']}",
            f"  Coincidencias exactas: {self.estadisticas['exactas']}",
            f"  Coincidencias fuzzy: {self.estadisticas['fuzzy']}",
            f"  Nuevos repuestos necesarios: {len(self.repuestos_nuevos)}",
            f"  Descartados: {self.estadisticas['descartadas']}",
            "",
            "NUEVOS REPUESTOS A CREAR:",
        ]
        
        for nuevo in self.repuestos_nuevos[:20]:  # Primeros 20
            reporte.append(f"  - {nuevo['nombre']}")
            reporte.append(f"    Categoría: {nuevo['categoria']}")
            reporte.append(f"    Costo: {nuevo['costo']}")
            reporte.append("")
        
        if len(self.repuestos_nuevos) > 20:
            reporte.append(f"  ... y {len(self.repuestos_nuevos) - 20} más")
        
        reporte.append("")
        reporte.append("MAPPINGS CON BAJA CONFIANZA (< 0.8):")
        
        mappings_bajos = [m for m in self.mappings.values() 
                         if m.confianza > 0 and m.confianza < 0.8]
        
        for mapping in mappings_bajos[:10]:
            reporte.append(f"  '{mapping.descripcion_original}'")
            reporte.append(f"    → {mapping.repuesto_nombre} (confianza: {mapping.confianza:.1%})")
            reporte.append("")
        
        if len(mappings_bajos) > 10:
            reporte.append(f"  ... y {len(mappings_bajos) - 10} más")
        
        return "\n".join(reporte)
    
    def crear_mapeo_json(self, archivo: str = "repuestos_mappings.json"):
        """Guardar mapeos en JSON para revisión manual"""
        mappings_dict = {}
        for desc_id, mapping in self.mappings.items():
            mappings_dict[str(desc_id)] = {
                'descripcion_original': mapping.descripcion_original,
                'repuesto_id': mapping.repuesto_id,
                'repuesto_nombre': mapping.repuesto_nombre,
                'confianza': round(mapping.confianza, 3),
                'tipo_mapeo': mapping.tipo_mapeo,
                'notas': mapping.notas
            }
        
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(mappings_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Mapeos guardados en: {archivo}")
    
    def ejecutar_completo(self):
        """Ejecutar análisis completo"""
        try:
            self.conectar()
            
            # Analizar
            self.analizar_detalles()
            
            # Generar reportes
            reporte = self.generar_reporte_analisis()
            logger.info("\n" + reporte)
            
            # Guardar JSON
            self.crear_mapeo_json()
            
            # Guardar reporte
            with open('reporte_migracion_repuestos.txt', 'w', encoding='utf-8') as f:
                f.write(reporte)
            logger.info("Reporte guardado en: reporte_migracion_repuestos.txt")
            
        finally:
            self.desconectar()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Solucionador de repuestos para migración de BD'
    )
    parser.add_argument('--analyze', action='store_true', 
                       help='Analizar detalles_orden')
    parser.add_argument('--db', default='servitec_manager/SERVITEC.DB',
                       help='Ruta de la base de datos')
    
    args = parser.parse_args()
    
    solver = RepuestosMigrationSolver(args.db)
    
    if args.analyze or not any([args.analyze]):
        print("Ejecutando análisis de detalles_orden...")
        solver.ejecutar_completo()
        print("\n✓ Análisis completado. Revisa los archivos generados:")
        print("  - reporte_migracion_repuestos.txt")
        print("  - repuestos_mappings.json")
        print("  - migration_repuestos.log")


if __name__ == '__main__':
    main()

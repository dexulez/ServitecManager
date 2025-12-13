"""
MÓDULO REPORTES AVANZADOS
Análisis detallado de ventas, ganancias, márgenes y comparativos
"""

from datetime import datetime, timedelta
import statistics


class REPORTES_AVANZADOS:
    """Generador de reportes analíticos avanzados"""
    
    def __init__(self, db_gestor):
        """
        Args:
            db_gestor: Instancia GESTOR_BASE_DATOS
        """
        self.db = db_gestor
    
    # --- 1. REPORTES DE VENTAS ---
    
    def OBTENER_REPORTE_VENTAS_PERÍODO(self, fecha_inicio, fecha_fin):
        """Reporte completo de ventas en período"""
        try:
            ventas = self.db.fetch_all(
                "SELECT id, cliente_id, presupuesto, abono, estado, fecha FROM ordenes WHERE fecha BETWEEN ? AND ? ORDER BY fecha DESC",
                (fecha_inicio, fecha_fin)
            )
            
            total_ventas = sum(v[2] for v in ventas)  # presupuesto
            total_cobrado = sum(v[3] if v[3] else 0 for v in ventas)  # abono
            pendiente = total_ventas - total_cobrado
            cantidad_ordenes = len(ventas)
            
            # Agrupar por estado
            por_estado = {}
            for venta in ventas:
                estado = venta[4]
                if estado not in por_estado:
                    por_estado[estado] = {"cantidad": 0, "total": 0}
                por_estado[estado]["cantidad"] += 1
                por_estado[estado]["total"] += venta[2]
            
            return {
                "período": f"{fecha_inicio} a {fecha_fin}",
                "total_ventas": total_ventas,
                "total_cobrado": total_cobrado,
                "pendiente": pendiente,
                "tasa_cobranza": (total_cobrado / total_ventas * 100) if total_ventas > 0 else 0,
                "cantidad_ordenes": cantidad_ordenes,
                "ticket_promedio": total_ventas / cantidad_ordenes if cantidad_ordenes > 0 else 0,
                "por_estado": por_estado,
                "datos_completos": ventas
            }
        except Exception as e:
            return {"error": str(e)}
    
    def OBTENER_REPORTE_VENTAS_DIARIAS(self, fecha_inicio, fecha_fin):
        """Desglose de ventas por día"""
        try:
            ventas = self.db.fetch_all(
                "SELECT DATE(fecha) as fecha, SUM(presupuesto) as total, COUNT(*) as cantidad FROM ordenes WHERE fecha BETWEEN ? AND ? GROUP BY DATE(fecha) ORDER BY fecha DESC",
                (fecha_inicio, fecha_fin)
            )
            
            resultado = []
            for venta in ventas:
                resultado.append({
                    "fecha": venta[0],
                    "total_ventas": venta[1],
                    "cantidad_ordenes": venta[2],
                    "promedio_por_orden": venta[1] / venta[2] if venta[2] > 0 else 0
                })
            
            return {
                "ventas_diarias": resultado,
                "promedio_diario": sum(v["total_ventas"] for v in resultado) / len(resultado) if resultado else 0,
                "día_mejor_ventas": max(resultado, key=lambda x: x["total_ventas"]) if resultado else None
            }
        except Exception as e:
            return {"error": str(e)}
    
    def OBTENER_REPORTE_VENTAS_POR_TÉCNICO(self, fecha_inicio, fecha_fin):
        """Ventas y comisiones por técnico"""
        try:
            # Obtener comisiones por técnico
            comisiones = self.db.fetch_all(
                "SELECT tecnico, COUNT(*) as cantidad, SUM(comision) as total_comisiones FROM comisiones WHERE fecha BETWEEN ? AND ? GROUP BY tecnico ORDER BY total_comisiones DESC",
                (fecha_inicio, fecha_fin)
            )
            
            resultado = []
            for com in comisiones:
                resultado.append({
                    "técnico": com[0],
                    "ordenes_realizadas": com[1],
                    "total_comisiones": com[2],
                    "comisión_promedio": com[2] / com[1] if com[1] > 0 else 0
                })
            
            return {
                "por_técnico": resultado,
                "total_comisiones": sum(c["total_comisiones"] for c in resultado),
                "técnico_top": resultado[0] if resultado else None
            }
        except Exception as e:
            return {"error": str(e)}
    
    # --- 2. REPORTES DE GANANCIAS ---
    
    def OBTENER_REPORTE_GANANCIAS(self, fecha_inicio, fecha_fin):
        """Análisis de ganancias y márgenes"""
        try:
            # Ventas
            ventas = self.db.fetch_one(
                "SELECT SUM(presupuesto) as total FROM ordenes WHERE fecha BETWEEN ? AND ?",
                (fecha_inicio, fecha_fin)
            )
            total_ventas = ventas[0] if ventas[0] else 0
            
            # Costos de servicios (mano de obra)
            costos_mo = self.db.fetch_one(
                "SELECT SUM(comision) as total FROM comisiones WHERE fecha BETWEEN ? AND ?",
                (fecha_inicio, fecha_fin)
            )
            total_mo = costos_mo[0] if costos_mo[0] else 0
            
            # Gastos operacionales
            gastos = self.db.fetch_one(
                "SELECT SUM(monto) as total FROM gastos_operacionales WHERE fecha BETWEEN ? AND ?",
                (fecha_inicio, fecha_fin)
            )
            total_gastos = gastos[0] if gastos[0] else 0
            
            # Costos de productos vendidos (si aplica)
            costos_productos = self._CALCULAR_COSTOS_PRODUCTOS(fecha_inicio, fecha_fin)
            
            # Cálculos
            costo_total = total_mo + total_gastos + costos_productos
            ganancia_bruta = total_ventas - total_mo
            ganancia_neta = total_ventas - costo_total
            margen_bruto = (ganancia_bruta / total_ventas * 100) if total_ventas > 0 else 0
            margen_neto = (ganancia_neta / total_ventas * 100) if total_ventas > 0 else 0
            
            return {
                "período": f"{fecha_inicio} a {fecha_fin}",
                "ingresos": {
                    "total_ventas": total_ventas
                },
                "costos": {
                    "mano_de_obra": total_mo,
                    "gastos_operacionales": total_gastos,
                    "productos": costos_productos,
                    "total": costo_total
                },
                "ganancias": {
                    "ganancia_bruta": ganancia_bruta,
                    "ganancia_neta": ganancia_neta,
                    "margen_bruto_pct": margen_bruto,
                    "margen_neto_pct": margen_neto
                }
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _CALCULAR_COSTOS_PRODUCTOS(self, fecha_inicio, fecha_fin):
        """Calcula costo de productos vendidos"""
        try:
            # Buscar ventas con detalles de productos
            costos = self.db.fetch_one(
                "SELECT COALESCE(SUM(costo_unitario * cantidad), 0) FROM detalles_ventas WHERE fecha BETWEEN ? AND ?",
                (fecha_inicio, fecha_fin)
            )
            return costos[0] if costos[0] else 0
        except:
            return 0
    
    # --- 3. ANÁLISIS COMPARATIVO ---
    
    def OBTENER_COMPARATIVA_PERÍODOS(self, fecha_inicio_1, fecha_fin_1, fecha_inicio_2, fecha_fin_2):
        """Compara resultados entre dos períodos"""
        try:
            período_1 = self.OBTENER_REPORTE_VENTAS_PERÍODO(fecha_inicio_1, fecha_fin_1)
            período_2 = self.OBTENER_REPORTE_VENTAS_PERÍODO(fecha_inicio_2, fecha_fin_2)
            
            if "error" in período_1 or "error" in período_2:
                return {"error": "No se pudo obtener datos comparativos"}
            
            variación_ventas = período_2["total_ventas"] - período_1["total_ventas"]
            variación_pct = (variación_ventas / período_1["total_ventas"] * 100) if período_1["total_ventas"] > 0 else 0
            
            variación_cobranza = período_2["total_cobrado"] - período_1["total_cobrado"]
            variación_cobranza_pct = (variación_cobranza / período_1["total_cobrado"] * 100) if período_1["total_cobrado"] > 0 else 0
            
            return {
                "período_1": {
                    "rango": f"{fecha_inicio_1} a {fecha_fin_1}",
                    "ventas": período_1["total_ventas"],
                    "cobrado": período_1["total_cobrado"],
                    "tasa_cobranza": período_1["tasa_cobranza"]
                },
                "período_2": {
                    "rango": f"{fecha_inicio_2} a {fecha_fin_2}",
                    "ventas": período_2["total_ventas"],
                    "cobrado": período_2["total_cobrado"],
                    "tasa_cobranza": período_2["tasa_cobranza"]
                },
                "variación": {
                    "ventas": variación_ventas,
                    "ventas_pct": variación_pct,
                    "cobranza": variación_cobranza,
                    "cobranza_pct": variación_cobranza_pct,
                    "mejora": "SÍ" if variación_pct > 0 else "NO"
                }
            }
        except Exception as e:
            return {"error": str(e)}
    
    # --- 4. TOP Y BOTTOM LISTS ---
    
    def OBTENER_CLIENTES_TOP(self, límite=10):
        """Clientes con más compras/gasto"""
        try:
            clientes = self.db.fetch_all(
                "SELECT c.nombre, COUNT(o.id) as cantidad, SUM(o.presupuesto) as total FROM clientes c LEFT JOIN ordenes o ON c.id = o.cliente_id GROUP BY c.id ORDER BY total DESC LIMIT ?",
                (límite,)
            )
            
            resultado = []
            for cliente in clientes:
                resultado.append({
                    "cliente": cliente[0],
                    "cantidad_ordenes": cliente[1],
                    "gasto_total": cliente[2] if cliente[2] else 0
                })
            
            return resultado
        except Exception as e:
            return {"error": str(e)}
    
    def OBTENER_PRODUCTOS_TOP(self, límite=10):
        """Productos más vendidos"""
        try:
            productos = self.db.fetch_all(
                "SELECT nombre, SUM(cantidad) as total_vendido, SUM(cantidad * precio) as ingresos FROM inventario GROUP BY id ORDER BY total_vendido DESC LIMIT ?",
                (límite,)
            )
            
            resultado = []
            for prod in productos:
                resultado.append({
                    "producto": prod[0],
                    "cantidad_vendida": prod[1] if prod[1] else 0,
                    "ingresos": prod[2] if prod[2] else 0
                })
            
            return resultado
        except Exception as e:
            return {"error": str(e)}
    
    def OBTENER_ALERTAS_CRÍTICAS(self):
        """Identifica situaciones críticas en el negocio"""
        alertas = []
        
        try:
            # Órdenes pendientes sin cobro
            pendientes = self.db.fetch_one(
                "SELECT COUNT(*) FROM ordenes WHERE estado = 'PENDIENTE' AND DATE(fecha) < DATE('now', '-15 days')"
            )
            if pendientes[0] > 5:
                alertas.append(f"⚠️ CRÍTICO: {pendientes[0]} órdenes pendientes vencidas (>15 días)")
            
            # Productos con bajo stock
            bajo_stock = self.db.fetch_one(
                "SELECT COUNT(*) FROM inventario WHERE cantidad < 5 AND cantidad > 0"
            )
            if bajo_stock[0] > 0:
                alertas.append(f"⚠️ ALERTA: {bajo_stock[0]} productos con bajo stock")
            
            # Productos sin stock
            sin_stock = self.db.fetch_one(
                "SELECT COUNT(*) FROM inventario WHERE cantidad = 0"
            )
            if sin_stock[0] > 0:
                alertas.append(f"🔴 CRÍTICO: {sin_stock[0]} productos agotados")
            
            # Técnicos sin actividad
            inactivos = self.db.fetch_one(
                "SELECT COUNT(DISTINCT tecnico) FROM comisiones WHERE DATE(fecha) < DATE('now', '-7 days')"
            )
            if inactivos[0] > 0:
                alertas.append(f"⚠️ ALERTA: {inactivos[0]} técnicos sin actividad en 7 días")
            
            return {
                "total_alertas": len(alertas),
                "alertas": alertas
            }
        except Exception as e:
            return {"error": str(e)}

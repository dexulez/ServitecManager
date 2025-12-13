"""
MÓDULO SISTEMA DE NOTIFICACIONES
Alertas inteligentes de eventos críticos, bajo stock, pagos vencidos, etc.
"""

from datetime import datetime, timedelta
import json
import os


class NOTIFICACIONES:
    """Sistema inteligente de notificaciones y alertas"""
    
    def __init__(self, db_gestor):
        """
        Args:
            db_gestor: Instancia GESTOR_BASE_DATOS
        """
        self.db = db_gestor
        self.archivo_notificaciones = "notificaciones.db.json"
        self._INICIALIZAR_ALMACENAMIENTO()
    
    def _INICIALIZAR_ALMACENAMIENTO(self):
        """Crea archivo de almacenamiento si no existe"""
        if not os.path.exists(self.archivo_notificaciones):
            with open(self.archivo_notificaciones, 'w') as f:
                json.dump({"notificaciones": [], "leídas": []}, f)
    
    # --- 1. REGISTRO DE NOTIFICACIONES ---
    
    def AGREGAR_NOTIFICACIÓN(self, tipo, título, mensaje, prioridad="NORMAL", datos_asociados=None):
        """Añade una notificación al sistema"""
        try:
            notificación = {
                "id": datetime.now().isoformat(),
                "tipo": tipo,  # "ORDEN", "STOCK", "PAGO", "TÉCNICO", "VENTA"
                "título": título,
                "mensaje": mensaje,
                "prioridad": prioridad,  # "BAJA", "NORMAL", "ALTA", "CRÍTICA"
                "fecha_creación": datetime.now().isoformat(),
                "leída": False,
                "datos": datos_asociados or {}
            }
            
            with open(self.archivo_notificaciones, 'r') as f:
                datos = json.load(f)
            
            datos["notificaciones"].insert(0, notificación)  # Más recientes al frente
            
            with open(self.archivo_notificaciones, 'w') as f:
                json.dump(datos, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error al agregar notificación: {e}")
            return False
    
    def OBTENER_NOTIFICACIONES_RECIENTES(self, límite=20):
        """Obtiene últimas notificaciones"""
        try:
            with open(self.archivo_notificaciones, 'r') as f:
                datos = json.load(f)
            
            notificaciones = datos["notificaciones"][:límite]
            
            # Agrupar por prioridad
            por_prioridad = {}
            for notif in notificaciones:
                prioridad = notif["prioridad"]
                if prioridad not in por_prioridad:
                    por_prioridad[prioridad] = []
                por_prioridad[prioridad].append(notif)
            
            # Contar no leídas
            no_leídas = sum(1 for n in datos["notificaciones"] if not n["leída"])
            
            return {
                "total_notificaciones": len(datos["notificaciones"]),
                "no_leídas": no_leídas,
                "recientes": notificaciones,
                "por_prioridad": por_prioridad
            }
        except Exception as e:
            return {"error": str(e)}
    
    def MARCAR_COMO_LEÍDA(self, notif_id):
        """Marca una notificación como leída"""
        try:
            with open(self.archivo_notificaciones, 'r') as f:
                datos = json.load(f)
            
            for notif in datos["notificaciones"]:
                if notif["id"] == notif_id:
                    notif["leída"] = True
                    break
            
            with open(self.archivo_notificaciones, 'w') as f:
                json.dump(datos, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error al marcar notificación: {e}")
            return False
    
    def LIMPIAR_NOTIFICACIONES_ANTIGUAS(self, días=30):
        """Elimina notificaciones más antiguas que N días"""
        try:
            with open(self.archivo_notificaciones, 'r') as f:
                datos = json.load(f)
            
            fecha_límite = (datetime.now() - timedelta(days=días)).isoformat()
            datos["notificaciones"] = [n for n in datos["notificaciones"] if n["fecha_creación"] > fecha_límite]
            
            with open(self.archivo_notificaciones, 'w') as f:
                json.dump(datos, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error al limpiar notificaciones: {e}")
            return False
    
    # --- 2. GENERADOR DE ALERTAS AUTOMÁTICAS ---
    
    def GENERAR_ALERTAS_STOCK(self):
        """Genera alertas de bajo/sin stock"""
        alertas_generadas = 0
        
        try:
            # Productos sin stock
            sin_stock = self.db.fetch_all(
                "SELECT id, nombre FROM inventario WHERE cantidad = 0"
            )
            
            for producto in sin_stock:
                self.AGREGAR_NOTIFICACIÓN(
                    tipo="STOCK",
                    título=f"PRODUCTO AGOTADO: {producto[1]}",
                    mensaje=f"El producto '{producto[1]}' no tiene inventario disponible",
                    prioridad="ALTA",
                    datos_asociados={"producto_id": producto[0]}
                )
                alertas_generadas += 1
            
            # Productos con bajo stock
            bajo_stock = self.db.fetch_all(
                "SELECT id, nombre, cantidad FROM inventario WHERE cantidad > 0 AND cantidad <= 5"
            )
            
            for producto in bajo_stock:
                self.AGREGAR_NOTIFICACIÓN(
                    tipo="STOCK",
                    título=f"BAJO STOCK: {producto[1]}",
                    mensaje=f"Quedan {producto[2]} unidades de '{producto[1]}'",
                    prioridad="NORMAL",
                    datos_asociados={"producto_id": producto[0], "cantidad": producto[2]}
                )
                alertas_generadas += 1
            
            return {"alertas_generadas": alertas_generadas}
        except Exception as e:
            return {"error": str(e)}
    
    def GENERAR_ALERTAS_PAGOS_VENCIDOS(self):
        """Genera alertas de pagos vencidos"""
        alertas_generadas = 0
        
        try:
            # Órdenes con abono pendiente hace más de 15 días
            vencidas = self.db.fetch_all(
                """
                SELECT o.id, o.cliente_id, c.nombre, o.presupuesto, o.abono, o.fecha
                FROM ordenes o
                JOIN clientes c ON o.cliente_id = c.id
                WHERE (o.presupuesto - COALESCE(o.abono, 0)) > 0
                AND DATE(o.fecha) < DATE('now', '-15 days')
                ORDER BY o.fecha DESC
                """
            )
            
            for orden in vencidas:
                pendiente = orden[3] - (orden[4] if orden[4] else 0)
                días_vencimiento = (datetime.now() - datetime.fromisoformat(orden[5].replace(' ', 'T'))).days
                
                self.AGREGAR_NOTIFICACIÓN(
                    tipo="PAGO",
                    título=f"PAGO VENCIDO: {orden[2]}",
                    mensaje=f"Orden #{orden[0]}: Vencida hace {días_vencimiento} días. Pendiente: ${pendiente:,.0f}",
                    prioridad="CRÍTICA" if días_vencimiento > 30 else "ALTA",
                    datos_asociados={"orden_id": orden[0], "cliente_id": orden[1], "pendiente": pendiente}
                )
                alertas_generadas += 1
            
            return {"alertas_generadas": alertas_generadas}
        except Exception as e:
            return {"error": str(e)}
    
    def GENERAR_ALERTAS_ÓRDENES_PENDIENTES(self):
        """Genera alertas de órdenes pendientes sin actividad"""
        alertas_generadas = 0
        
        try:
            # Órdenes pendientes sin cambios hace más de 7 días
            pendientes = self.db.fetch_all(
                """
                SELECT o.id, c.nombre, o.fecha, o.observacion
                FROM ordenes o
                JOIN clientes c ON o.cliente_id = c.id
                WHERE o.estado = 'PENDIENTE'
                AND DATE(o.fecha) < DATE('now', '-7 days')
                ORDER BY o.fecha ASC
                """
            )
            
            for orden in pendientes:
                días_sin_actividad = (datetime.now() - datetime.fromisoformat(orden[2].replace(' ', 'T'))).days
                
                self.AGREGAR_NOTIFICACIÓN(
                    tipo="ORDEN",
                    título=f"ORDEN ESTANCADA: {orden[1]}",
                    mensaje=f"Orden #{orden[0]} sin cambios hace {días_sin_actividad} días: {orden[3][:50]}",
                    prioridad="ALTA" if días_sin_actividad > 14 else "NORMAL",
                    datos_asociados={"orden_id": orden[0]}
                )
                alertas_generadas += 1
            
            return {"alertas_generadas": alertas_generadas}
        except Exception as e:
            return {"error": str(e)}
    
    def GENERAR_ALERTAS_DESEMPEÑO_TÉCNICO(self):
        """Genera alertas sobre desempeño de técnicos"""
        alertas_generadas = 0
        
        try:
            # Técnicos sin actividad en 7 días
            sin_actividad = self.db.fetch_all(
                """
                SELECT DISTINCT tecnico FROM comisiones
                WHERE DATE(fecha) >= DATE('now', '-30 days')
                GROUP BY tecnico
                HAVING MAX(DATE(fecha)) < DATE('now', '-7 days')
                """
            )
            
            for técnico in sin_actividad:
                self.AGREGAR_NOTIFICACIÓN(
                    tipo="TÉCNICO",
                    título=f"TÉCNICO INACTIVO: {técnico[0]}",
                    mensaje=f"El técnico '{técnico[0]}' no tiene registros en los últimos 7 días",
                    prioridad="NORMAL",
                    datos_asociados={"técnico": técnico[0]}
                )
                alertas_generadas += 1
            
            # Técnicos con baja productividad
            baja_productividad = self.db.fetch_all(
                """
                SELECT tecnico, COUNT(*) as cantidad, SUM(comision) as total
                FROM comisiones
                WHERE DATE(fecha) >= DATE('now', '-30 days')
                GROUP BY tecnico
                HAVING cantidad < 5
                """
            )
            
            for técnico in baja_productividad:
                self.AGREGAR_NOTIFICACIÓN(
                    tipo="TÉCNICO",
                    título=f"BAJA PRODUCTIVIDAD: {técnico[0]}",
                    mensaje=f"Solo {técnico[1]} órdenes completadas en 30 días (Total: ${técnico[2]:,.0f})",
                    prioridad="NORMAL",
                    datos_asociados={"técnico": técnico[0], "órdenes": técnico[1]}
                )
                alertas_generadas += 1
            
            return {"alertas_generadas": alertas_generadas}
        except Exception as e:
            return {"error": str(e)}
    
    def GENERAR_ALERTAS_VENTAS(self):
        """Genera alertas relacionadas con ventas"""
        alertas_generadas = 0
        
        try:
            # Día sin ventas
            ventas_hoy = self.db.fetch_one(
                "SELECT COUNT(*) FROM ordenes WHERE DATE(fecha) = DATE('now')"
            )
            
            if ventas_hoy[0] == 0:
                self.AGREGAR_NOTIFICACIÓN(
                    tipo="VENTA",
                    título="SIN VENTAS HOY",
                    mensaje="No se registraron órdenes en el día de hoy",
                    prioridad="NORMAL",
                    datos_asociados={}
                )
                alertas_generadas += 1
            
            # Caída en ventas vs promedio
            promedio_diario = self.db.fetch_one(
                "SELECT AVG(diario) FROM (SELECT COUNT(*) as diario FROM ordenes WHERE DATE(fecha) >= DATE('now', '-30 days') GROUP BY DATE(fecha))"
            )
            
            if promedio_diario[0]:
                ventas_hoy_valor = ventas_hoy[0]
                promedio = promedio_diario[0]
                
                if ventas_hoy_valor < promedio * 0.5:  # Menos del 50% del promedio
                    self.AGREGAR_NOTIFICACIÓN(
                        tipo="VENTA",
                        título="CAÍDA EN VENTAS",
                        mensaje=f"Hoy: {ventas_hoy_valor} órdenes. Promedio: {promedio:.1f}",
                        prioridad="ALTA",
                        datos_asociados={"hoy": ventas_hoy_valor, "promedio": promedio}
                    )
                    alertas_generadas += 1
            
            return {"alertas_generadas": alertas_generadas}
        except Exception as e:
            return {"error": str(e)}
    
    # --- 3. ESCANEO AUTOMÁTICO COMPLETO ---
    
    def ESCANEAR_TODAS_LAS_ALERTAS(self):
        """Ejecuta escaneo completo de todas las alertas del sistema"""
        resultados = {
            "stock": self.GENERAR_ALERTAS_STOCK(),
            "pagos_vencidos": self.GENERAR_ALERTAS_PAGOS_VENCIDOS(),
            "órdenes_pendientes": self.GENERAR_ALERTAS_ÓRDENES_PENDIENTES(),
            "desempeño_técnicos": self.GENERAR_ALERTAS_DESEMPEÑO_TÉCNICO(),
            "ventas": self.GENERAR_ALERTAS_VENTAS()
        }
        
        total_alertas = sum(r.get("alertas_generadas", 0) for r in resultados.values())
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_alertas_generadas": total_alertas,
            "detalles": resultados,
            "próximo_escaneo_sugerido": (datetime.now() + timedelta(hours=1)).isoformat()
        }
    
    # --- 4. RESUMEN DE ALERTAS ---
    
    def OBTENER_RESUMEN_ALERTAS(self):
        """Retorna resumen ejecutivo de alertas"""
        try:
            with open(self.archivo_notificaciones, 'r') as f:
                datos = json.load(f)
            
            notificaciones = datos["notificaciones"]
            
            # Contar por tipo y prioridad
            por_tipo = {}
            por_prioridad = {}
            
            for notif in notificaciones:
                # Por tipo
                tipo = notif["tipo"]
                if tipo not in por_tipo:
                    por_tipo[tipo] = 0
                por_tipo[tipo] += 1
                
                # Por prioridad
                prioridad = notif["prioridad"]
                if prioridad not in por_prioridad:
                    por_prioridad[prioridad] = 0
                por_prioridad[prioridad] += 1
            
            # Últimas de cada tipo
            últimas_por_tipo = {}
            for tipo in por_tipo.keys():
                últimas_por_tipo[tipo] = next((n for n in notificaciones if n["tipo"] == tipo), None)
            
            return {
                "total_notificaciones": len(notificaciones),
                "no_leídas": sum(1 for n in notificaciones if not n["leída"]),
                "por_tipo": por_tipo,
                "por_prioridad": por_prioridad,
                "últimas_por_tipo": últimas_por_tipo,
                "críticas": sum(1 for n in notificaciones if n["prioridad"] == "CRÍTICA"),
                "altas": sum(1 for n in notificaciones if n["prioridad"] == "ALTA")
            }
        except Exception as e:
            return {"error": str(e)}

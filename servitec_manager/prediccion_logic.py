"""
MÓDULO PREDICCIÓN DE VENTAS
Análisis de tendencias y predicciones usando series de tiempo
"""

from datetime import datetime, timedelta
import statistics


class PREDICCION_VENTAS:
    """Motor de predicción de ventas basado en datos históricos"""
    
    def __init__(self, db_gestor):
        """
        Args:
            db_gestor: Instancia GESTOR_BASE_DATOS
        """
        self.db = db_gestor
    
    # --- 1. ANÁLISIS DE TENDENCIAS ---
    
    def ANALIZAR_TENDENCIA_VENTAS(self, días_históricos=90):
        """Analiza tendencia de ventas últimos N días"""
        try:
            fecha_inicio = (datetime.now() - timedelta(days=días_históricos)).strftime("%Y-%m-%d")
            
            # Obtener ventas diarias
            ventas_diarias = self.db.fetch_all(
                "SELECT DATE(fecha_entrada), SUM(presupuesto_inicial) FROM ordenes WHERE DATE(fecha_entrada) >= ? GROUP BY DATE(fecha_entrada) ORDER BY fecha_entrada ASC",
                (fecha_inicio,)
            )
            
            if not ventas_diarias:
                return {"error": "No hay datos históricos"}
            
            valores = [v[1] for v in ventas_diarias]
            fechas = [v[0] for v in ventas_diarias]
            
            # Estadísticas
            promedio = statistics.mean(valores) if valores else 0
            mediana = statistics.median(valores) if valores else 0
            desv_estándar = statistics.stdev(valores) if len(valores) > 1 else 0
            mínimo = min(valores) if valores else 0
            máximo = max(valores) if valores else 0
            
            # Calcular tendencia (pendiente simple)
            tendencia = self._CALCULAR_TENDENCIA_LINEAL(valores)
            
            # Dividir en terciles para ver evolución
            primer_tercio = valores[:len(valores)//3]
            tercer_tercio = valores[-len(valores)//3:] if len(valores)//3 > 0 else valores
            
            promedio_inicio = statistics.mean(primer_tercio) if primer_tercio else 0
            promedio_final = statistics.mean(tercer_tercio) if tercer_tercio else 0
            
            cambio_pct = ((promedio_final - promedio_inicio) / promedio_inicio * 100) if promedio_inicio > 0 else 0
            
            return {
                "período_analizado": f"Últimos {días_históricos} días ({fechas[0]} a {fechas[-1]})",
                "estadísticas": {
                    "promedio_diario": promedio,
                    "mediana": mediana,
                    "desviación_estándar": desv_estándar,
                    "mínimo": mínimo,
                    "máximo": máximo,
                    "rango": máximo - mínimo
                },
                "tendencia": {
                    "tipo": "CRECIENTE" if tendencia > 0 else "DECRECIENTE",
                    "pendiente": tendencia,
                    "cambio_inicial_final_pct": cambio_pct
                },
                "datos_completos": [(f, v) for f, v in zip(fechas, valores)]
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _CALCULAR_TENDENCIA_LINEAL(self, valores):
        """Calcula la pendiente de tendencia lineal usando mínimos cuadrados"""
        if len(valores) < 2:
            return 0
        
        n = len(valores)
        x_valores = list(range(n))
        
        sum_x = sum(x_valores)
        sum_y = sum(valores)
        sum_xy = sum(x * y for x, y in zip(x_valores, valores))
        sum_x2 = sum(x ** 2 for x in x_valores)
        
        pendiente = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2) if (n * sum_x2 - sum_x ** 2) != 0 else 0
        return pendiente
    
    # --- 2. PREDICCIÓN SIMPLE ---
    
    def PREDECIR_VENTAS_PRÓXIMAS_SEMANAS(self, semanas=4):
        """Predice ventas para próximas semanas"""
        try:
            # Obtener datos históricos de 12 semanas
            fecha_inicio = (datetime.now() - timedelta(weeks=12)).strftime("%Y-%m-%d")
            
            ventas_semanales = self.db.fetch_all(
                """
                SELECT STRFTIME('%Y-W%W', fecha_entrada) as semana, SUM(presupuesto_inicial) 
                FROM ordenes 
                WHERE DATE(fecha_entrada) >= ? 
                GROUP BY semana 
                ORDER BY semana ASC
                """,
                (fecha_inicio,)
            )
            
            if len(ventas_semanales) < 4:
                return {"error": "Datos históricos insuficientes (se requieren al menos 4 semanas)"}
            
            valores = [v[1] for v in ventas_semanales]
            
            # Promedio móvil de 4 semanas
            promedio_móvil = statistics.mean(valores[-4:]) if len(valores) >= 4 else statistics.mean(valores)
            
            # Crecimiento promedio
            crecimiento = self._CALCULAR_TENDENCIA_LINEAL(valores)
            
            # Predicciones
            predicciones = []
            fecha_próxima = datetime.now()
            
            for i in range(semanas):
                fecha_próxima = fecha_próxima + timedelta(weeks=1)
                # Predicción = promedio móvil + tendencia
                predicción = promedio_móvil + (crecimiento * i)
                predicción = max(predicción, 0)  # No negativos
                
                predicciones.append({
                    "semana": fecha_próxima.strftime("%W/%Y"),
                    "período": f"{fecha_próxima.strftime('%d/%m')} a {(fecha_próxima + timedelta(days=6)).strftime('%d/%m')}",
                    "venta_predicha": predicción,
                    "confianza": "MEDIA" if i <= 2 else "BAJA"
                })
            
            return {
                "predicciones_semanales": predicciones,
                "promedio_histórico": promedio_móvil,
                "tendencia_detectada": "CRECIENTE" if crecimiento > 0 else "DECRECIENTE",
                "nota": "Predicciones basadas en últimas 12 semanas. Confiabilidad decrece con el tiempo."
            }
        except Exception as e:
            return {"error": str(e)}
    
    def PREDECIR_VENTAS_PRÓXIMOS_MESES(self, meses=6):
        """Predice ventas para próximos meses"""
        try:
            # Datos de 12 meses anteriores
            fecha_inicio = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
            
            ventas_mensuales = self.db.fetch_all(
                """
                SELECT STRFTIME('%Y-%m', fecha_entrada) as mes, SUM(presupuesto_inicial) 
                FROM ordenes 
                WHERE DATE(fecha_entrada) >= ? 
                GROUP BY mes 
                ORDER BY mes ASC
                """,
                (fecha_inicio,)
            )
            
            if len(ventas_mensuales) < 3:
                return {"error": "Datos históricos insuficientes"}
            
            valores = [v[1] for v in ventas_mensuales]
            promedio = statistics.mean(valores)
            
            predicciones = []
            fecha_próxima = datetime.now()
            
            for i in range(meses):
                fecha_próxima = fecha_próxima + timedelta(days=30)
                predicción = promedio * (1 + self._CALCULAR_TENDENCIA_LINEAL(valores) / 100)
                predicción = max(predicción, 0)
                
                predicciones.append({
                    "mes": fecha_próxima.strftime("%m/%Y"),
                    "mes_nombre": fecha_próxima.strftime("%B %Y"),
                    "venta_predicha": predicción,
                    "confianza": "ALTA" if i <= 1 else "MEDIA" if i <= 3 else "BAJA"
                })
            
            return {
                "predicciones_mensuales": predicciones,
                "promedio_mensual_histórico": promedio,
                "total_predicho_período": sum(p["venta_predicha"] for p in predicciones)
            }
        except Exception as e:
            return {"error": str(e)}
    
    # --- 3. ANÁLISIS ESTACIONAL ---
    
    def ANALIZAR_ESTACIONALIDAD(self):
        """Detecta patrones estacionales en ventas"""
        try:
            # Ventas por mes (todos los años)
            ventas_por_mes = self.db.fetch_all(
                """
                SELECT STRFTIME('%m', fecha_entrada) as mes, SUM(presupuesto_inicial) as total, COUNT(*) as cantidad
                FROM ordenes
                GROUP BY mes
                ORDER BY mes ASC
                """
            )
            
            if not ventas_por_mes:
                return {"error": "No hay datos"}
            
            meses_nombre = [
                "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
                "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"
            ]
            
            resultados = []
            totales = [v[1] for v in ventas_por_mes]
            promedio_general = statistics.mean(totales) if totales else 0
            
            for mes_num, venta in ventas_por_mes:
                mes_idx = int(mes_num) - 1
                índice_estacionalidad = (venta[1] / promedio_general * 100) if promedio_general > 0 else 0
                
                resultados.append({
                    "mes": meses_nombre[mes_idx],
                    "total_ventas": venta[1],
                    "cantidad_órdenes": venta[2],
                    "índice_estacionalidad": índice_estacionalidad,
                    "clasificación": "PICO" if índice_estacionalidad > 110 else "NORMAL" if índice_estacionalidad > 90 else "BAJO"
                })
            
            meses_pico = [m for m in resultados if m["clasificación"] == "PICO"]
            meses_bajo = [m for m in resultados if m["clasificación"] == "BAJO"]
            
            return {
                "análisis_por_mes": resultados,
                "meses_con_mayor_venta": [m["mes"] for m in meses_pico],
                "meses_con_menor_venta": [m["mes"] for m in meses_bajo],
                "recomendación": "Preparar stock para meses de pico. Promover ofertas en meses bajos."
            }
        except Exception as e:
            return {"error": str(e)}
    
    # --- 4. SCORE DE SALUD EMPRESARIAL ---
    
    def CALCULAR_SCORE_SALUD(self):
        """Calcula indicador de salud del negocio (0-100)"""
        try:
            score = 0
            factores = []
            
            # 1. Crecimiento de ventas (0-25 puntos)
            tendencia = self.ANALIZAR_TENDENCIA_VENTAS(30)
            if "tendencia" in tendencia:
                if tendencia["tendencia"]["tipo"] == "CRECIENTE":
                    score += 25
                    factores.append("✓ Ventas en crecimiento (+25)")
                else:
                    score += 12
                    factores.append("⚠️ Ventas estables/decrecientes (+12)")
            
            # 2. Tasa de cobranza (0-25 puntos)
            mes_actual = datetime.now().strftime("%Y-%m-01")
            mes_anterior = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-01")
            
            cobranza = self.db.fetch_one(
                "SELECT SUM(presupuesto_inicial), SUM(abono) FROM ordenes WHERE DATE(fecha_entrada) >= ?",
                (mes_anterior,)
            )
            
            if cobranza[0]:
                tasa_cobranza = (cobranza[1] / cobranza[0] * 100) if cobranza[0] > 0 else 0
                if tasa_cobranza >= 80:
                    score += 25
                    factores.append(f"✓ Cobranza excelente {tasa_cobranza:.1f}% (+25)")
                elif tasa_cobranza >= 60:
                    score += 18
                    factores.append(f"⚠️ Cobranza moderada {tasa_cobranza:.1f}% (+18)")
                else:
                    score += 8
                    factores.append(f"🔴 Cobranza baja {tasa_cobranza:.1f}% (+8)")
            
            # 3. Inventario (0-20 puntos)
            sin_stock = self.db.fetch_one("SELECT COUNT(*) FROM inventario WHERE cantidad = 0")
            total_items = self.db.fetch_one("SELECT COUNT(*) FROM inventario")
            
            if total_items[0] > 0:
                pct_sin_stock = (sin_stock[0] / total_items[0] * 100)
                if pct_sin_stock < 10:
                    score += 20
                    factores.append("✓ Inventario bien surtido (+20)")
                elif pct_sin_stock < 25:
                    score += 12
                    factores.append("⚠️ Algunos productos agotados (+12)")
                else:
                    score += 5
                    factores.append(f"🔴 Muchos agotados {pct_sin_stock:.0f}% (+5)")
            
            # 4. Diversificación (0-15 puntos)
            clientes_activos = self.db.fetch_one("SELECT COUNT(DISTINCT cliente_id) FROM ordenes WHERE DATE(fecha) >= DATE('now', '-30 days')")
            if clientes_activos[0] >= 20:
                score += 15
                factores.append("✓ Buena diversificación de clientes (+15)")
            elif clientes_activos[0] >= 10:
                score += 10
                factores.append("⚠️ Dependencia moderada (+10)")
            else:
                score += 5
                factores.append("🔴 Alta dependencia de pocos clientes (+5)")
            
            # 5. Cumplimiento (0-15 puntos)
            ordenes_pendientes = self.db.fetch_one("SELECT COUNT(*) FROM ordenes WHERE estado = 'PENDIENTE'")
            if ordenes_pendientes[0] <= 5:
                score += 15
                factores.append("✓ Bajo nivel de órdenes pendientes (+15)")
            elif ordenes_pendientes[0] <= 20:
                score += 8
                factores.append("⚠️ Algunas órdenes pendientes (+8)")
            else:
                score += 2
                factores.append(f"🔴 Muchas órdenes pendientes {ordenes_pendientes[0]} (+2)")
            
            return {
                "score_salud": min(score, 100),
                "clasificación": "EXCELENTE" if score >= 85 else "BUENO" if score >= 70 else "REGULAR" if score >= 50 else "CRÍTICO",
                "factores": factores,
                "análisis": f"Empresa en situación {'EXCELENTE - Continuar así' if score >= 85 else 'BUENA - Mejorar área débil' if score >= 70 else 'REGULAR - Atender problemas' if score >= 50 else 'CRÍTICA - ACCIÓN URGENTE'}"
            }
        except Exception as e:
            return {"error": str(e)}

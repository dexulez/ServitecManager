"""
Módulo de gestión de pagos y cuentas bancarias
Maneja débito, crédito, transferencias, boletas e IVA
"""

class PaymentManager:
    def __init__(self, database):
        self.db = database
        self.IVA = 0.19  # 19% de IVA en Chile
    
    def crear_tabla_cuentas_bancarias(self):
        """Crea la tabla de cuentas bancarias si no existe"""
        query = """
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
        """
        self.db.EJECUTAR(query)
    
    def crear_tabla_boletas(self):
        """Crea la tabla de boletas si no existe"""
        query = """
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
        """
        self.db.EJECUTAR(query)
    
    def crear_boleta_automatica(self, orden_id, monto_total, metodo_pago="DEBITO"):
        """
        Crea una boleta automáticamente cuando el pago es por débito/crédito
        Calcula y aplica IVA automáticamente
        """
        try:
            # Calcular neto e IVA
            monto_neto = round(monto_total / (1 + self.IVA), 2)
            monto_iva = round(monto_total - monto_neto, 2)
            
            # Generar número de boleta (YYYYMMDD00001)
            from datetime import datetime
            hoy = datetime.now().strftime("%Y%m%d")
            
            # Obtener último número de boleta del día
            query_last = f"SELECT MAX(numero_boleta) FROM boletas WHERE numero_boleta LIKE '{hoy}%'"
            result = self.db.OBTENER_UNO(query_last)
            
            if result and result[0]:
                last_num = int(result[0][8:])  # Últimos 5 dígitos
                next_num = last_num + 1
            else:
                next_num = 1
            
            numero_boleta = f"{hoy}{str(next_num).zfill(5)}"
            
            # Insertar boleta
            query_insert = """
            INSERT INTO boletas (orden_id, numero_boleta, monto_neto, iva, monto_total, metodo_pago)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            
            self.db.EJECUTAR(query_insert, (orden_id, numero_boleta, monto_neto, monto_iva, monto_total, metodo_pago))
            
            print(f"✅ Boleta #{numero_boleta} creada automáticamente")
            print(f"   Neto: ${monto_neto:,.0f}")
            print(f"   IVA (19%): ${monto_iva:,.0f}")
            print(f"   Total: ${monto_total:,.0f}")
            
            return numero_boleta
        
        except Exception as e:
            print(f"❌ Error creando boleta: {e}")
            return None
    
    def procesar_pago(self, orden_id, monto_total, metodo_pago, cuenta_bancaria_id=None):
        """
        Procesa un pago y crea la boleta si es necesario
        
        metodo_pago: 'DEBITO', 'CREDITO', 'TRANSFERENCIA', 'EFECTIVO'
        """
        
        # Si es débito o crédito, crear boleta automáticamente
        if metodo_pago in ['DEBITO', 'CREDITO']:
            boleta = self.crear_boleta_automatica(orden_id, monto_total, metodo_pago)
            return {
                'success': True,
                'boleta': boleta,
                'metodo': metodo_pago,
                'monto': monto_total,
                'iva_aplicado': True
            }
        
        # Si es transferencia, registrar cuenta destino
        elif metodo_pago == 'TRANSFERENCIA':
            if not cuenta_bancaria_id:
                return {
                    'success': False,
                    'error': 'Debe seleccionar cuenta bancaria para transferencia'
                }
            
            # Registrar transferencia
            query = """
            INSERT INTO transferencias_recibidas (orden_id, cuenta_bancaria_id, monto, fecha)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """
            self.db.EJECUTAR(query, (orden_id, cuenta_bancaria_id, monto_total))
            
            return {
                'success': True,
                'metodo': 'TRANSFERENCIA',
                'monto': monto_total,
                'cuenta_id': cuenta_bancaria_id
            }
        
        # Si es efectivo, solo registrar
        elif metodo_pago == 'EFECTIVO':
            return {
                'success': True,
                'metodo': 'EFECTIVO',
                'monto': monto_total
            }
        
        return {'success': False, 'error': 'Método de pago no válido'}
    
    def obtener_cuentas_activas(self):
        """Obtiene todas las cuentas bancarias activas"""
        query = "SELECT id, banco, numero_cuenta, tipo_cuenta, titular FROM cuentas_bancarias WHERE activa = 1 ORDER BY banco"
        return self.db.OBTENER_TODOS(query)
    
    def obtener_boleta(self, numero_boleta):
        """Obtiene información de una boleta"""
        query = "SELECT * FROM boletas WHERE numero_boleta = ?"
        return self.db.OBTENER_UNO(query, (numero_boleta,))

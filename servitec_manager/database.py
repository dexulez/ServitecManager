import sqlite3
from functools import lru_cache
import threading
import atexit

# CONSTANTES GLOBALES
NOMBRE_BD = "SERVITEC.DB"

class DictRow(dict):
    """
    Clase híbrida que permite acceso tanto por clave como por índice
    Compatibilidad con código antiguo (tuplas) y nuevo (diccionarios)
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._keys_list = list(self.keys())
    
    def __getitem__(self, key):
        if isinstance(key, int):
            # Acceso por índice (tupla-style)
            return super().__getitem__(self._keys_list[key])
        # Acceso por clave (dict-style)
        return super().__getitem__(key)
    
    def __iter__(self):
        # Al iterar (para desempaquetar), devolver valores en orden, no claves
        for key in self._keys_list:
            yield super().__getitem__(key)
    
    def __len__(self):
        return super().__len__()

class GESTOR_BASE_DATOS:
    """
    Gestor de Base de Datos con Conexión Persistente (Singleton Pattern)
    Optimizado para rendimiento con:
    - Conexión única reutilizable
    - Row factory para acceso tipo diccionario
    - Caché interno de consultas
    """
    
    def __init__(self, ruta_bd=None, nombre_bd=NOMBRE_BD):
        if isinstance(ruta_bd, str):
            self.nombre_bd = ruta_bd
        else:
            self.nombre_bd = nombre_bd
        
        # Caché de consultas en memoria
        self._cache_enabled = True
        self._query_cache = {}
        self._cache_lock = threading.Lock()
        
        # Conexión persistente (Singleton)
        self.conexion = None
        self._conexion_lock = threading.Lock()
        
        # Conectar y configurar
        self._conectar()
        
        # Registrar cierre automático al finalizar
        atexit.register(self._cerrar_conexion)
    
    def _conectar(self):
        """
        Establece una conexión persistente a la base de datos
        Optimizaciones aplicadas:
        - check_same_thread=False para uso en múltiples hilos
        - row_factory=sqlite3.Row para acceso tipo diccionario
        - PRAGMAs de rendimiento configurados
        """
        if self.conexion is None:
            with self._conexion_lock:
                if self.conexion is None:  # Double-check locking
                    self.conexion = sqlite3.connect(
                        self.nombre_bd,
                        timeout=30.0,
                        check_same_thread=False,
                        isolation_level=None  # Autocommit mode para mejor rendimiento
                    )
                    
                    # OPTIMIZACIÓN: Row factory para acceso tipo diccionario
                    self.conexion.row_factory = sqlite3.Row
                    
                    # Configurar PRAGMAs de optimización
                    cursor = self.conexion.cursor()
                    cursor.execute("PRAGMA journal_mode=WAL")
                    cursor.execute("PRAGMA synchronous=NORMAL")
                    cursor.execute("PRAGMA cache_size=-64000")  # 64MB
                    cursor.execute("PRAGMA temp_store=MEMORY")
                    cursor.execute("PRAGMA mmap_size=268435456")  # 256MB
                    cursor.execute("PRAGMA page_size=4096")
                    cursor.close()
    
    def _cerrar_conexion(self):
        """Cierra la conexión persistente al finalizar"""
        if self.conexion:
            try:
                self.conexion.close()
                self.conexion = None
            except:
                pass
    
    def _asegurar_conexion(self):
        """Verifica que la conexión esté activa, reconecta si es necesario"""
        try:
            if self.conexion:
                # Test de conexión
                self.conexion.execute("SELECT 1")
        except sqlite3.Error:
            # Reconectar si la conexión está cerrada
            self.conexion = None
            self._conectar()

    def INICIALIZAR_BD(self):
        """INICIALIZA LA BASE DE DATOS CON TODAS LAS TABLAS NECESARIAS"""
        consultas = [
            """CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE,
                password TEXT,
                rol TEXT,
                porcentaje_comision REAL DEFAULT 50
            )""",
            """CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rut TEXT UNIQUE,
                nombre TEXT,
                telefono TEXT,
                email TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL,
                tipo TEXT CHECK(tipo IN ('PRODUCTO', 'REPUESTO')) NOT NULL
            )""",
            """CREATE TABLE IF NOT EXISTS inventario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE,
                categoria TEXT,
                costo REAL,
                precio REAL,
                stock INTEGER,
                proveedor_id INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (proveedor_id) REFERENCES proveedores (id)
            )""",
            """CREATE TABLE IF NOT EXISTS repuestos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE,
                categoria TEXT,
                costo REAL,
                precio_sugerido REAL,
                stock INTEGER,
                proveedor_id INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (proveedor_id) REFERENCES proveedores (id)
            )""",
            """CREATE TABLE IF NOT EXISTS servicios_predefinidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_servicio TEXT UNIQUE,
                categoria TEXT,
                costo_mano_obra REAL
            )""",
            """CREATE TABLE IF NOT EXISTS ordenes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER,
                tecnico_id INTEGER,
                fecha TEXT,
                equipo TEXT,
                marca TEXT,
                modelo TEXT,
                serie TEXT,
                observacion TEXT,
                estado TEXT CHECK(estado IN ('Pendiente', 'En Proceso', 'Reparado', 'Entregado', 'Sin solución')) DEFAULT 'Pendiente',
                accesorios TEXT,
                riesgoso INTEGER,
                presupuesto REAL DEFAULT 0,
                abono REAL DEFAULT 0,
                fecha_entrega TEXT,
                FOREIGN KEY(cliente_id) REFERENCES clientes(id)
            )""",
            """CREATE TABLE IF NOT EXISTS finanzas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                orden_id INTEGER,
                total_cobrado REAL,
                costo_repuesto REAL,
                costo_envio REAL,
                monto_efectivo REAL DEFAULT 0,
                monto_transferencia REAL DEFAULT 0,
                monto_debito REAL DEFAULT 0,
                monto_credito REAL DEFAULT 0,
                descuento REAL DEFAULT 0,
                aplicó_iva INTEGER,
                utilidad_real REAL,
                monto_comision_tecnico REAL,
                fecha_cierre TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS caja_sesiones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                fecha_apertura TEXT,
                fecha_cierre TEXT,
                monto_inicial REAL,
                monto_final_sistema REAL,
                monto_final_real REAL,
                real_efectivo REAL DEFAULT 0,
                real_transferencia REAL DEFAULT 0,
                real_debito REAL DEFAULT 0,
                real_credito REAL DEFAULT 0,
                total_gastos REAL DEFAULT 0,
                diferencia REAL,
                estado TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sesion_id INTEGER,
                descripcion TEXT,
                monto REAL,
                fecha TEXT,
                FOREIGN KEY(sesion_id) REFERENCES caja_sesiones(id)
            )""",
            """CREATE TABLE IF NOT EXISTS modelos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_dispositivo TEXT,
                marca TEXT,
                modelo TEXT,
                UNIQUE(tipo_dispositivo, marca, modelo)
            )""",
            """CREATE TABLE IF NOT EXISTS marcas_personalizadas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE,
                fecha_creacion TEXT DEFAULT (DATETIME('NOW'))
            )""",
            """CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                cliente_id INTEGER,
                fecha TEXT,
                total REAL,
                descuento REAL DEFAULT 0,
                pago_efectivo REAL DEFAULT 0,
                pago_transferencia REAL DEFAULT 0,
                pago_debito REAL DEFAULT 0,
                pago_credito REAL DEFAULT 0
            )""",
            """CREATE TABLE IF NOT EXISTS detalle_ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id INTEGER,
                producto_id INTEGER,
                orden_id INTEGER,
                cantidad INTEGER,
                precio_unitario REAL,
                subtotal REAL,
                FOREIGN KEY(venta_id) REFERENCES ventas(id)
            )""",
            """CREATE TABLE IF NOT EXISTS proveedores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE,
                telefono TEXT,
                email TEXT,
                direccion TEXT,
                saldo_pendiente REAL DEFAULT 0
            )""",
            """CREATE TABLE IF NOT EXISTS precios_proveedor (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proveedor_id INTEGER,
                repuesto_id INTEGER,
                precio REAL,
                fecha_actualizacion TEXT DEFAULT (DATETIME('NOW')),
                FOREIGN KEY(proveedor_id) REFERENCES proveedores(id),
                FOREIGN KEY(repuesto_id) REFERENCES repuestos(id)
            )""",
            """CREATE TABLE IF NOT EXISTS compras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proveedor_id INTEGER,
                fecha TEXT,
                total REAL,
                estado TEXT,
                tipo_documento TEXT,
                numero_documento TEXT,
                observacion TEXT,
                FOREIGN KEY(proveedor_id) REFERENCES proveedores(id)
            )""",
            """CREATE TABLE IF NOT EXISTS detalle_compras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                compra_id INTEGER,
                producto_id INTEGER,
                tipo_producto TEXT,
                cantidad INTEGER,
                costo_unitario REAL,
                subtotal REAL,
                FOREIGN KEY(compra_id) REFERENCES compras(id)
            )""",
            """CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                orden_id INTEGER,
                producto_id INTEGER,
                repuesto_id INTEGER,
                proveedor_id INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                estado TEXT DEFAULT 'PENDIENTE',
                fecha_solicitud TEXT,
                fecha_pedido TEXT,
                fecha_recepcion TEXT,
                notas TEXT,
                usuario_solicita TEXT,
                FOREIGN KEY(orden_id) REFERENCES ordenes(id),
                FOREIGN KEY(producto_id) REFERENCES inventario(id),
                FOREIGN KEY(repuesto_id) REFERENCES repuestos(id),
                FOREIGN KEY(proveedor_id) REFERENCES proveedores(id)
            )""",
            """CREATE TABLE IF NOT EXISTS pagos_proveedor (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proveedor_id INTEGER,
                fecha TEXT,
                monto REAL,
                metodo_pago TEXT,
                referencia TEXT,
                observacion TEXT,
                FOREIGN KEY(proveedor_id) REFERENCES proveedores(id)
            )"""
        ]
        
        # ÍNDICES PARA OPTIMIZACIÓN DE CONSULTAS
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_clientes_rut ON clientes(rut)",
            "CREATE INDEX IF NOT EXISTS idx_clientes_nombre ON clientes(nombre)",
            "CREATE INDEX IF NOT EXISTS idx_ordenes_cliente ON ordenes(cliente_id)",
            "CREATE INDEX IF NOT EXISTS idx_ordenes_estado ON ordenes(estado)",
            "CREATE INDEX IF NOT EXISTS idx_ordenes_fecha ON ordenes(fecha)",
            "CREATE INDEX IF NOT EXISTS idx_ordenes_tecnico ON ordenes(tecnico_id)",
            "CREATE INDEX IF NOT EXISTS idx_finanzas_orden ON finanzas(orden_id)",
            "CREATE INDEX IF NOT EXISTS idx_ventas_usuario ON ventas(usuario_id)",
            "CREATE INDEX IF NOT EXISTS idx_ventas_fecha ON ventas(fecha)",
            "CREATE INDEX IF NOT EXISTS idx_detalle_ventas_venta ON detalle_ventas(venta_id)",
            "CREATE INDEX IF NOT EXISTS idx_precios_proveedor_repuesto ON precios_proveedor(repuesto_id)",
            "CREATE INDEX IF NOT EXISTS idx_precios_proveedor_proveedor ON precios_proveedor(proveedor_id)",
            "CREATE INDEX IF NOT EXISTS idx_compras_proveedor ON compras(proveedor_id)",
            "CREATE INDEX IF NOT EXISTS idx_compras_fecha ON compras(fecha)",
            "CREATE INDEX IF NOT EXISTS idx_detalle_compras_compra ON detalle_compras(compra_id)",
            "CREATE INDEX IF NOT EXISTS idx_pagos_proveedor_proveedor ON pagos_proveedor(proveedor_id)",
            "CREATE INDEX IF NOT EXISTS idx_gastos_sesion ON gastos(sesion_id)",
            "CREATE INDEX IF NOT EXISTS idx_caja_sesiones_usuario ON caja_sesiones(usuario_id)",
            "CREATE INDEX IF NOT EXISTS idx_modelos_lookup ON modelos(tipo_dispositivo, marca)",
            # ÍNDICES CRÍTICOS PARA INVENTARIO Y REPUESTOS (OPTIMIZACIÓN DE BÚSQUEDAS)
            "CREATE INDEX IF NOT EXISTS idx_inventario_nombre ON inventario(nombre)",
            "CREATE INDEX IF NOT EXISTS idx_inventario_categoria ON inventario(categoria)",
            "CREATE INDEX IF NOT EXISTS idx_repuestos_nombre ON repuestos(nombre)",
            "CREATE INDEX IF NOT EXISTS idx_repuestos_categoria ON repuestos(categoria)",
            "CREATE INDEX IF NOT EXISTS idx_servicios_nombre ON servicios_predefinidos(nombre_servicio)"
        ]
        
        try:
            # Usar conexión persistente
            self._asegurar_conexion()
            cursor = self.conexion.cursor()
            
            # Crear tablas
            for consulta in consultas:
                cursor.execute(consulta)
            
            # Crear índices
            for indice in indices:
                cursor.execute(indice)
            
            # Optimizar base de datos
            cursor.execute("ANALYZE")
            
            # Insertar categorías por defecto si no existen
            categorias_default = [
                # Categorías de PRODUCTOS
                ("FUNDAS", "PRODUCTO"),
                ("CARGADORES", "PRODUCTO"),
                ("MICAS", "PRODUCTO"),
                ("AUDIFONOS", "PRODUCTO"),
                ("CABLES", "PRODUCTO"),
                ("OTROS", "PRODUCTO"),
                # Categorías de REPUESTOS
                ("PANTALLAS", "REPUESTO"),
                ("BATERIAS", "REPUESTO"),
                ("PINES CARGA", "REPUESTO"),
                ("FLEX", "REPUESTO"),
                ("CAMARAS", "REPUESTO"),
                ("OTROS", "REPUESTO")
            ]
            
            for nombre, tipo in categorias_default:
                try:
                    cursor.execute("INSERT OR IGNORE INTO categorias (nombre, tipo) VALUES (?, ?)", (nombre, tipo))
                except:
                    pass
            
            cursor.close()
        except Exception as error:
            print(f"ERROR BD: {error}")

    def EJECUTAR_CONSULTA(self, consulta, parámetros=()):
        """
        EJECUTA UNA CONSULTA DE MODIFICACIÓN (INSERT/UPDATE/DELETE)
        Usa conexión persistente para mejor rendimiento
        """
        try:
            self._asegurar_conexion()
            
            with self._conexion_lock:
                cursor = self.conexion.cursor()
                cursor.execute(consulta, parámetros)
                last_id = cursor.lastrowid
                cursor.close()
                
                # Limpiar caché después de modificaciones
                with self._cache_lock:
                    self._query_cache.clear()
                
                return last_id
        except sqlite3.Error as e:
            print(f"Error en EJECUTAR_CONSULTA: {e}")
            return None

    def OBTENER_TODOS(self, consulta, parámetros=(), use_cache=False, limit=None, offset=None):
        """
        OBTIENE TODOS LOS REGISTROS DE UNA CONSULTA
        
        OPTIMIZACIONES:
        - Usa conexión persistente (no abre/cierra cada vez)
        - row_factory=sqlite3.Row para acceso tipo diccionario
        - Caché opcional en memoria
        - Paginación con LIMIT/OFFSET para lazy loading
        
        Args:
            consulta: SQL query
            parámetros: Parámetros de la consulta
            use_cache: Si usar caché en memoria
            limit: Número máximo de registros (paginación)
            offset: Desplazamiento inicial (paginación)
        
        Returns:
            Lista de sqlite3.Row (accesibles como diccionarios)
        """
        # Aplicar paginación si se especifica
        if limit is not None:
            consulta_original = consulta
            consulta = f"{consulta_original} LIMIT {limit}"
            if offset is not None:
                consulta = f"{consulta} OFFSET {offset}"
        
        # Verificar caché
        if use_cache:
            cache_key = (consulta, parámetros)
            with self._cache_lock:
                if cache_key in self._query_cache:
                    return self._query_cache[cache_key]
        
        try:
            self._asegurar_conexion()
            
            with self._conexion_lock:
                cursor = self.conexion.cursor()
                cursor.execute(consulta, parámetros)
                resultado = cursor.fetchall()
                cursor.close()
            
            # Convertir sqlite3.Row a DictRow (accesible por índice y clave)
            resultado_lista = [DictRow(dict(row)) for row in resultado]
            
            # Guardar en caché si está habilitado
            if use_cache:
                with self._cache_lock:
                    self._query_cache[cache_key] = resultado_lista
                    # Limitar tamaño del caché (max 100 consultas)
                    if len(self._query_cache) > 100:
                        # Eliminar la entrada más antigua (FIFO)
                        self._query_cache.pop(next(iter(self._query_cache)))
            
            return resultado_lista
            
        except sqlite3.Error as e:
            print(f"Error en OBTENER_TODOS: {e}")
            print(f"Query que falló: {consulta}")
            import traceback
            traceback.print_exc()
            return []

    def OBTENER_UNO(self, consulta, parámetros=()):
        """
        OBTIENE UN ÚNICO REGISTRO DE UNA CONSULTA
        Usa conexión persistente para mejor rendimiento
        
        Returns:
            dict o None (gracias a row_factory)
        """
        try:
            self._asegurar_conexion()
            
            with self._conexion_lock:
                cursor = self.conexion.cursor()
                cursor.execute(consulta, parámetros)
                resultado = cursor.fetchone()
                cursor.close()
            
            # Convertir sqlite3.Row a DictRow (accesible por índice y clave)
            return DictRow(resultado) if resultado else None
            
        except sqlite3.Error as e:
            print(f"Error en OBTENER_UNO: {e}")
            return None

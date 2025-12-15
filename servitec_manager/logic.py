from database import GESTOR_BASE_DATOS
import sqlite3
try:
    from importador_logic import IMPORTADOR_DATOS
except ImportError:
    IMPORTADOR_DATOS = None
try:
    from reportes_avanzados_logic import REPORTES_AVANZADOS
except ImportError:
    REPORTES_AVANZADOS = None
try:
    from prediccion_logic import PREDICCION_VENTAS
except ImportError:
    PREDICCION_VENTAS = None
try:
    from notificaciones_logic import NOTIFICACIONES
except ImportError:
    NOTIFICACIONES = None
try:
    from mensajeria_logic import GESTOR_MENSAJERIA
except ImportError:
    GESTOR_MENSAJERIA = None

# --- GESTORES ---

# GESTOR DE CLIENTES
class GESTOR_CLIENTES:
    def __init__(self, gestor_bd):
        self.bd = gestor_bd
    def AGREGAR_CLIENTE(self, rut, nombre, teléfono, correo):
        try: return self.bd.EJECUTAR_CONSULTA("INSERT INTO clientes (rut, nombre, telefono, email) VALUES (?, ?, ?, ?)", (rut.upper(), nombre.upper(), teléfono, correo.upper()))
        except: return False
    def ACTUALIZAR_CLIENTE(self, rut, nombre, teléfono, correo):
        try:
            self.bd.EJECUTAR_CONSULTA("UPDATE clientes SET nombre = ?, telefono = ?, email = ? WHERE rut = ?", (nombre.upper(), teléfono, correo.upper(), rut.upper()))
            return True
        except: return False
    def OBTENER_CLIENTE(self, rut): return self.bd.OBTENER_UNO("SELECT * FROM clientes WHERE rut = ?", (rut.upper(),))
    def BUSCAR_CLIENTES(self, consulta):
        q = consulta.upper(); qc = ''.join(filter(lambda x: x.isalnum(), q))
        return self.bd.OBTENER_TODOS("SELECT * FROM clientes WHERE NOMBRE LIKE ? OR REPLACE(REPLACE(rut, '.', ''), '-', '') LIKE ? LIMIT 50", (f"%{q}%", f"%{qc}%"))
    BUSCAR_CLIENTE = OBTENER_CLIENTE
    # Compatibilidad
    add_client = AGREGAR_CLIENTE
    update_client = ACTUALIZAR_CLIENTE
    get_client = OBTENER_CLIENTE
    search_clients = BUSCAR_CLIENTES

# --- MODELOS ---
class GESTOR_MODELOS:
    def __init__(self, gestor_bd): 
        self.bd = gestor_bd
    
    def OBTENER_MODELOS_POR_MARCA(self, marca, tipo_dispositivo=None):
        """Obtiene modelos filtrados por marca y opcionalmente por tipo de dispositivo"""
        if tipo_dispositivo:
            res = self.bd.OBTENER_TODOS(
                "SELECT modelo FROM modelos WHERE marca = ? AND tipo_dispositivo = ? ORDER BY modelo ASC", 
                (marca.upper(), tipo_dispositivo.upper())
            )
        else:
            # Compatibilidad con código antiguo
            res = self.bd.OBTENER_TODOS(
                "SELECT modelo FROM modelos WHERE marca = ? ORDER BY modelo ASC", 
                (marca.upper(),)
            )
        return [r[0] for r in res]
    
    def REGISTRAR_MODELO(self, marca, modelo, tipo_dispositivo="CELULAR"):
        """Registra un nuevo modelo con su tipo de dispositivo y marca"""
        try:
            if marca and modelo:
                self.bd.EJECUTAR_CONSULTA(
                    "INSERT OR IGNORE INTO modelos (tipo_dispositivo, marca, modelo) VALUES (?, ?, ?)", 
                    (tipo_dispositivo.upper(), marca.upper(), modelo.upper())
                )
        except Exception as e:
            print(f"Error al registrar modelo: {e}")
    
    def OBTENER_TODOS_MODELOS(self):
        """Obtiene todos los modelos con su tipo de dispositivo y marca"""
        return self.bd.OBTENER_TODOS(
            "SELECT tipo_dispositivo, marca, modelo FROM modelos ORDER BY tipo_dispositivo, marca, modelo"
        )
    
    def SEMILLA_MODELOS(self):
        """Inicializa la base de datos con modelos de ejemplo"""
        if self.bd.OBTENER_UNO("SELECT * FROM modelos LIMIT 1"): 
            return
        
        # Datos organizados por tipo de dispositivo
        data = {
            "CELULAR": {
                "APPLE": ["IPHONE 11", "IPHONE 12", "IPHONE 13", "IPHONE 14", "IPHONE 15", "IPHONE SE"],
                "SAMSUNG": ["GALAXY S21", "GALAXY S22", "GALAXY S23", "GALAXY A14", "GALAXY A54", "GALAXY A34"],
                "XIAOMI": ["REDMI NOTE 11", "REDMI NOTE 12", "REDMI 13", "POCO X5", "POCO F5"],
                "MOTOROLA": ["MOTO G14", "MOTO G54", "EDGE 40", "MOTO G73"]
            },
            "NOTEBOOK": {
                "HP": ["PAVILION", "ENVY", "OMEN", "ELITEBOOK"],
                "DELL": ["INSPIRON", "XPS", "LATITUDE", "VOSTRO"],
                "LENOVO": ["IDEAPAD", "THINKPAD", "LEGION"],
                "ASUS": ["VIVOBOOK", "ZENBOOK", "ROG"]
            },
            "TABLET": {
                "APPLE": ["IPAD AIR", "IPAD PRO", "IPAD MINI"],
                "SAMSUNG": ["GALAXY TAB S8", "GALAXY TAB A8", "GALAXY TAB S9"]
            }
        }
        
        for tipo, marcas in data.items():
            for marca, modelos in marcas.items():
                for modelo in modelos:
                    self.bd.EJECUTAR_CONSULTA(
                        "INSERT OR IGNORE INTO modelos (tipo_dispositivo, marca, modelo) VALUES (?, ?, ?)", 
                        (tipo, marca, modelo)
                    )
    
    # Compatibilidad con código antiguo
    get_models_by_brand = OBTENER_MODELOS_POR_MARCA
    learn_model = REGISTRAR_MODELO
    seed_models = SEMILLA_MODELOS

class GESTOR_MARCAS:
    def __init__(self, gestor_bd):
        self.bd = gestor_bd
    
    def OBTENER_MARCAS_PERSONALIZADAS(self):
        """Obtiene todas las marcas personalizadas guardadas"""
        res = self.bd.OBTENER_TODOS("SELECT nombre FROM marcas_personalizadas ORDER BY nombre ASC")
        return [r[0] for r in res]
    
    def AGREGAR_MARCA(self, nombre):
        """Agrega una nueva marca personalizada"""
        try:
            self.bd.EJECUTAR_CONSULTA(
                "INSERT OR IGNORE INTO marcas_personalizadas (nombre) VALUES (?)",
                (nombre.upper(),)
            )
            return True
        except:
            return False
    
    def ELIMINAR_MARCA(self, nombre):
        """Elimina una marca personalizada"""
        try:
            self.bd.EJECUTAR_CONSULTA(
                "DELETE FROM marcas_personalizadas WHERE nombre = ?",
                (nombre.upper(),)
            )
            return True
        except:
            return False
    
    # Alias de compatibilidad
    get_custom_brands = OBTENER_MARCAS_PERSONALIZADAS
    add_brand = AGREGAR_MARCA
    delete_brand = ELIMINAR_MARCA

# --- SERVICIOS ---
class GESTOR_SERVICIOS:
    def __init__(self, gestor_bd, cache_inteligente=None): 
        self.bd = gestor_bd
        self._cache_inteligente = cache_inteligente
    
    def AGREGAR_SERVICIO(self, nombre, costo_mo, cat="GENERAL"):
        try: 
            result = self.bd.EJECUTAR_CONSULTA("INSERT INTO servicios_predefinidos (nombre_servicio, categoria, costo_mano_obra) VALUES (?, ?, ?)", (nombre.upper(), cat.upper(), costo_mo))
            # Invalidar caché
            if self._cache_inteligente:
                self._cache_inteligente.invalidar_servicios()
            return result
        except: return False
    
    def ACTUALIZAR_SERVICIO(self, sid, nombre, cat, costo_mo):
        self.bd.EJECUTAR_CONSULTA("UPDATE servicios_predefinidos SET nombre_servicio=?, categoria=?, costo_mano_obra=? WHERE id=?", (nombre.upper(), cat.upper(), costo_mo, sid))
        # Invalidar caché
        if self._cache_inteligente:
            self._cache_inteligente.invalidar_servicios()
        return True
    
    def OBTENER_TODOS_SERVICIOS(self): 
        # Intentar caché persistente primero
        if self._cache_inteligente:
            data = self._cache_inteligente.cargar_servicios()
            if data:
                return data
        
        # Fallback a caché en memoria de BD
        return self.bd.OBTENER_TODOS("SELECT * FROM servicios_predefinidos ORDER BY nombre_servicio ASC", use_cache=True)
    
    def ELIMINAR_SERVICIO(self, sid): 
        result = self.bd.EJECUTAR_CONSULTA("DELETE FROM servicios_predefinidos WHERE id = ?", (sid,))
        # Invalidar caché
        if self._cache_inteligente:
            self._cache_inteligente.invalidar_servicios()
        return result
    
    def BUSCAR_SERVICIO(self, consulta):
        q = f"%{consulta.upper()}%"
        # Limitar resultados a 100 para evitar congelamiento
        return self.bd.OBTENER_TODOS("SELECT id, nombre_servicio, COSTO_MANO_OBRA FROM servicios_predefinidos WHERE NOMBRE_SERVICIO LIKE ? LIMIT 100", (q,))
    # Compatibilidad
    add_service = AGREGAR_SERVICIO
    update_service = ACTUALIZAR_SERVICIO
    get_all_services = OBTENER_TODOS_SERVICIOS
    delete_service = ELIMINAR_SERVICIO
    search_service = BUSCAR_SERVICIO

# --- REPUESTOS ---
class GESTOR_REPUESTOS:
    def __init__(self, gestor_bd, cache_inteligente=None): 
        self.bd = gestor_bd
        self._cache_inteligente = cache_inteligente
    
    def OBTENER_TODOS_REPUESTOS(self): 
        # Intentar caché persistente primero
        if self._cache_inteligente:
            data = self._cache_inteligente.cargar_repuestos()
            if data:
                return data
        
        # Fallback a caché en memoria de BD
        return self.bd.OBTENER_TODOS("SELECT * FROM repuestos ORDER BY nombre ASC", use_cache=True)
    
    def OBTENER_TODOS_REPUESTOS_CON_PROVEEDOR(self):
        """Obtiene todos los repuestos con información del proveedor"""
        query = """
            SELECT r.*, 
                   p.nombre as proveedor_nombre,
                   p.id as proveedor_id
            FROM repuestos r
            LEFT JOIN proveedores p ON r.proveedor_id = p.id
            ORDER BY r.nombre ASC
        """
        return self.bd.OBTENER_TODOS(query, use_cache=True)
    
    def get_parts_with_provider(self):
        """Alias para compatibilidad snake_case"""
        return self.OBTENER_TODOS_REPUESTOS_CON_PROVEEDOR()
    
    def OBTENER_REPUESTO_POR_ID(self, repuesto_id): 
        return self.bd.OBTENER_UNO("SELECT * FROM repuestos WHERE id = ?", (repuesto_id,))
    
    def BUSCAR_REPUESTO(self, consulta):
        q = f"%{consulta.upper()}%"
        # Limitar resultados a 100 para evitar congelamiento
        return self.bd.OBTENER_TODOS("SELECT id, nombre, precio_sugerido, stock, categoria, costo FROM repuestos WHERE nombre LIKE ? LIMIT 100", (q,))
    
    def AGREGAR_REPUESTO(self, nombre, costo, precio_sug, stock, cat="GENERAL", proveedor_id=None):
        try:
            result = self.bd.EJECUTAR_CONSULTA(
                "INSERT INTO repuestos (nombre, categoria, costo, precio_sugerido, stock, proveedor_id) VALUES (?, ?, ?, ?, ?, ?)", 
                (nombre.upper(), cat.upper(), costo, precio_sug, stock, proveedor_id)
            )
            # Invalidar caché
            if self._cache_inteligente:
                self._cache_inteligente.invalidar_repuestos()
            return result
        except sqlite3.IntegrityError as e:
            if "UNIQUE" in str(e):
                from tkinter import messagebox
                messagebox.showerror("Error", "Ya existe un repuesto con ese nombre")
            else:
                print(f"Error de integridad al agregar repuesto: {e}")
            return False
        except Exception as e:
            print(f"Error al agregar repuesto: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def ACTUALIZAR_REPUESTO(self, repuesto_id, nombre, cat, costo, precio_sug, stock, proveedor_id=None):
        try:
            self.bd.EJECUTAR_CONSULTA(
                "UPDATE repuestos SET nombre=?, categoria=?, costo=?, precio_sugerido=?, stock=?, proveedor_id=? WHERE id=?", 
                (nombre.upper(), cat.upper(), costo, precio_sug, stock, proveedor_id, repuesto_id)
            )
            # Invalidar caché
            if self._cache_inteligente:
                self._cache_inteligente.invalidar_repuestos()
            return True
        except Exception as e:
            print(f"Error al actualizar repuesto: {e}")
            return False
    def update_part(self, repuesto_id, nombre, cat, costo, precio_sug, stock):
        """Actualizar repuesto sin requerir proveedor_id (mantiene el actual)"""
        try:
            self.bd.EJECUTAR_CONSULTA(
                "UPDATE repuestos SET nombre=?, categoria=?, costo=?, precio_sugerido=?, stock=? WHERE id=?", 
                (nombre.upper(), cat.upper(), costo, precio_sug, stock, repuesto_id)
            )
            # Invalidar caché
            if self._cache_inteligente:
                self._cache_inteligente.invalidar_repuestos()
            return True
        except Exception as e:
            print(f"Error al actualizar repuesto: {e}")
            return False
    
    def ACTUALIZAR_PRECIO_REPUESTO(self, repuesto_id, nuevo_precio):
        try:
            self.bd.EJECUTAR_CONSULTA("UPDATE repuestos SET precio_sugerido = ? WHERE id = ?", (nuevo_precio, repuesto_id))
            return True
        except:
            return False
    def ACTUALIZAR_COSTO_REPUESTO(self, repuesto_id, nuevo_costo):
        try:
            self.bd.EJECUTAR_CONSULTA("UPDATE repuestos SET costo = ? WHERE id = ?",(nuevo_costo, repuesto_id))
            return True
        except:
            return False
    def ELIMINAR_REPUESTO(self, repuesto_id): 
        result = self.bd.EJECUTAR_CONSULTA("DELETE FROM repuestos WHERE id = ?", (repuesto_id,))
        # Invalidar caché
        if self._cache_inteligente:
            self._cache_inteligente.invalidar_repuestos()
        return result
    # Compatibilidad
    get_all_parts = OBTENER_TODOS_REPUESTOS
    get_all_parts_with_provider = OBTENER_TODOS_REPUESTOS_CON_PROVEEDOR
    get_part_by_id = OBTENER_REPUESTO_POR_ID
    search_part = BUSCAR_REPUESTO
    add_part = AGREGAR_REPUESTO
    update_part = ACTUALIZAR_REPUESTO
    update_part_price = ACTUALIZAR_PRECIO_REPUESTO
    update_part_cost = ACTUALIZAR_COSTO_REPUESTO
    delete_part = ELIMINAR_REPUESTO


# --- PROVEEDORES ---
class GESTOR_PROVEEDORES:
    def __init__(self, gestor_bd): self.bd = gestor_bd
    
    # --- CRUD Proveedores ---
    def OBTENER_TODOS_PROVEEDORES(self):
        return self.bd.OBTENER_TODOS("SELECT * FROM proveedores ORDER BY NOMBRE ASC")
    
    def get_all_providers(self):
        """Alias snake_case para compatibilidad"""
        return self.OBTENER_TODOS_PROVEEDORES()
    
    def AGREGAR_PROVEEDOR(self, nombre, telefono, email, direccion):
        try:
            return self.bd.EJECUTAR_CONSULTA(
                "INSERT INTO proveedores (nombre, telefono, email, direccion, saldo_pendiente) VALUES (?, ?, ?, ?, 0)",
                (nombre.upper(), telefono, email, direccion.upper())
            )
        except: return False
    
    def add_provider(self, nombre, telefono, email, direccion):
        """Alias snake_case para compatibilidad"""
        return self.AGREGAR_PROVEEDOR(nombre, telefono, email, direccion)

    def ACTUALIZAR_PROVEEDOR(self, proveedor_id, nombre, telefono, email, direccion):
        try:
            self.bd.EJECUTAR_CONSULTA(
                "UPDATE proveedores SET nombre=?, telefono=?, email=?, direccion=? WHERE id=?",
                (nombre.upper(), telefono, email, direccion.upper(), proveedor_id)
            )
            return True
        except: return False

    def OBTENER_PROVEEDOR(self, proveedor_id):
        return self.bd.OBTENER_UNO("SELECT * FROM proveedores WHERE id=?", (proveedor_id,))

    def OBTENER_SALDO_PROVEEDOR(self, proveedor_id):
        res = self.bd.OBTENER_UNO("SELECT saldo_pendiente FROM proveedores WHERE id=?", (proveedor_id,))
        return res[0] if res else 0.0

    # --- Compras ---
    def REGISTRAR_COMPRA(self, proveedor_id, tipo_doc, num_doc, items, observacion=""):
        # items = [(prod_id, type, qty, cost), ...] where type is 'REPUESTO' or 'INVENTARIO'
        total = sum(item[2] * item[3] for item in items)
        
        # 1. Crear Compra
        compra_id = self.bd.EJECUTAR_CONSULTA(
            "INSERT INTO compras (proveedor_id, fecha, total, estado, tipo_documento, numero_documento, observacion) VALUES (?, datetime('now'), ?, 'RECIBIDA', ?, ?, ?)",
            (proveedor_id, total, tipo_doc, num_doc, observacion)
        )
        if not compra_id: return False

        # 2. Registrar Detalle y Actualizar Stock/Costo
        for prod_id, tipo_prod, cantidad, costo in items:
            subtotal = cantidad * costo
            self.bd.EJECUTAR_CONSULTA(
                "INSERT INTO detalle_compras (compra_id, producto_id, tipo_producto, cantidad, costo_unitario, subtotal) VALUES (?, ?, ?, ?, ?, ?)",
                (compra_id, prod_id, tipo_prod, cantidad, costo, subtotal)
            )
            
            # Actualizar Stock y Costo (Promedio o Último? Usaremos Último Costo por simplicidad MVP)
            if tipo_prod == 'REPUESTO':
                self.bd.EJECUTAR_CONSULTA("UPDATE repuestos SET stock = stock + ?, costo = ? WHERE id = ?", (cantidad, costo, prod_id))
            elif tipo_prod == 'INVENTARIO':
                self.bd.EJECUTAR_CONSULTA("UPDATE inventario SET stock = stock + ?, costo = ? WHERE id = ?", (cantidad, costo, prod_id))

        # 3. Actualizar Saldo Proveedor (Deuda aumenta)
        self.bd.EJECUTAR_CONSULTA("UPDATE proveedores SET saldo_pendiente = saldo_pendiente + ? WHERE id = ?", (total, proveedor_id))
        
        return compra_id

    def OBTENER_COMPRAS_POR_PROVEEDOR(self, proveedor_id):
        return self.bd.OBTENER_TODOS("SELECT * FROM compras WHERE proveedor_id = ? ORDER BY fecha DESC", (proveedor_id,))

    # --- Pagos ---
    def REGISTRAR_PAGO(self, proveedor_id, monto, metodo, referencia, observacion):
        # 1. Registrar Pago
        pago_id = self.bd.EJECUTAR_CONSULTA(
            "INSERT INTO pagos_proveedor (proveedor_id, fecha, monto, metodo_pago, referencia, observacion) VALUES (?, datetime('now'), ?, ?, ?, ?)",
            (proveedor_id, monto, metodo, referencia, observacion)
        )
        if not pago_id: return False

        # 2. Descontar Saldo (Deuda disminuye)
        self.bd.EJECUTAR_CONSULTA("UPDATE proveedores SET saldo_pendiente = saldo_pendiente - ? WHERE id = ?", (monto, proveedor_id))
        return True

    def OBTENER_PAGOS_POR_PROVEEDOR(self, proveedor_id):
        return self.bd.OBTENER_TODOS("SELECT * FROM pagos_proveedor WHERE proveedor_id = ? ORDER BY fecha DESC", (proveedor_id,))

    # --- LISTAS DE PRECIOS ---
    def AGREGAR_PRECIO_PROVEEDOR(self, proveedor_id, repuesto_id, precio):
        try:
            return self.bd.EJECUTAR_CONSULTA(
                "INSERT OR REPLACE INTO precios_proveedor (proveedor_id, repuesto_id, precio) VALUES (?, ?, ?)",
                (proveedor_id, repuesto_id, precio)
            )
        except:
            return False
    
    def OBTENER_PRECIOS_PROVEEDOR(self, proveedor_id):
        """Obtiene todos los precios de un proveedor específico"""
        query = """
            SELECT pp.id, pp.proveedor_id, pp.repuesto_id, pp.precio, r.nombre as repuesto_nombre
            FROM precios_proveedor pp
            LEFT JOIN repuestos r ON pp.repuesto_id = r.id
            WHERE pp.proveedor_id = ?
            ORDER BY r.nombre ASC
        """
        return self.bd.OBTENER_TODOS(query, (proveedor_id,))
    
    def ACTUALIZAR_PRECIO_PROVEEDOR(self, precio_id, nuevo_precio):
        """Actualiza un precio específico"""
        try:
            self.bd.EJECUTAR_CONSULTA(
                "UPDATE precios_proveedor SET precio = ? WHERE id = ?",
                (nuevo_precio, precio_id)
            )
            return True
        except:
            return False
    
    def ELIMINAR_PRECIO_PROVEEDOR(self, precio_id):
        """Elimina un precio de proveedor"""
        try:
            self.bd.EJECUTAR_CONSULTA("DELETE FROM precios_proveedor WHERE id = ?", (precio_id,))
            return True
        except:
            return False
    
    # --- Métodos alias para compatibilidad snake_case ---
    def register_purchase(self, proveedor_id, tipo_doc, num_doc, items, observacion=""):
        """Alias snake_case"""
        return self.REGISTRAR_COMPRA(proveedor_id, tipo_doc, num_doc, items, observacion)
    
    def get_purchases_by_provider(self, proveedor_id):
        """Alias snake_case"""
        return self.OBTENER_COMPRAS_POR_PROVEEDOR(proveedor_id)
    
    def get_provider_balance(self, proveedor_id):
        """Alias snake_case"""
        return self.OBTENER_SALDO_PROVEEDOR(proveedor_id)
    
    def register_payment(self, proveedor_id, monto, metodo, referencia, observacion):
        """Alias snake_case"""
        return self.REGISTRAR_PAGO(proveedor_id, monto, metodo, referencia, observacion)
    
    def get_payments_by_provider(self, proveedor_id):
        """Alias snake_case"""
        return self.OBTENER_PAGOS_POR_PROVEEDOR(proveedor_id)
    
    def add_provider_price(self, proveedor_id, repuesto_id, precio):
        """Alias snake_case"""
        return self.AGREGAR_PRECIO_PROVEEDOR(proveedor_id, repuesto_id, precio)
    
    def get_provider_prices(self, proveedor_id):
        """Alias snake_case"""
        return self.OBTENER_PRECIOS_PROVEEDOR(proveedor_id)
    
    def update_provider_price(self, precio_id, nuevo_precio):
        """Alias snake_case"""
        return self.ACTUALIZAR_PRECIO_PROVEEDOR(precio_id, nuevo_precio)
    
    def delete_provider_price(self, precio_id):
        """Alias snake_case"""
        return self.ELIMINAR_PRECIO_PROVEEDOR(precio_id)


# ============== GESTOR_PEDIDOS ==============
class GESTOR_PEDIDOS:
    """
    Gestiona solicitudes/pedidos de productos y repuestos a proveedores.
    Los pedidos pueden crearse desde órdenes de trabajo o de forma independiente.
    """
    def __init__(self, gestor_bd): 
        self.bd = gestor_bd
    
    def CREAR_PEDIDO(self, proveedor_id, cantidad, tipo_item, item_id, orden_id=None, notas="", usuario=""):
        """
        Crea una solicitud de pedido a un proveedor.
        
        Args:
            proveedor_id: ID del proveedor
            cantidad: Cantidad solicitada
            tipo_item: 'PRODUCTO' o 'REPUESTO'
            item_id: ID del producto o repuesto
            orden_id: ID de la orden asociada (opcional)
            notas: Notas adicionales
            usuario: Usuario que solicita
        """
        from datetime import datetime
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        producto_id = item_id if tipo_item == 'PRODUCTO' else None
        repuesto_id = item_id if tipo_item == 'REPUESTO' else None
        
        try:
            pedido_id = self.bd.EJECUTAR_CONSULTA(
                """INSERT INTO pedidos 
                   (orden_id, producto_id, repuesto_id, proveedor_id, cantidad, estado, 
                    fecha_solicitud, notas, usuario_solicita) 
                   VALUES (?, ?, ?, ?, ?, 'PENDIENTE', ?, ?, ?)""",
                (orden_id, producto_id, repuesto_id, proveedor_id, cantidad, fecha_actual, notas, usuario)
            )
            return pedido_id
        except Exception as e:
            print(f"Error al crear pedido: {e}")
            return False
    
    def OBTENER_PEDIDOS_PENDIENTES(self):
        """Obtiene todos los pedidos pendientes y pedidos (en espera de recepción) con información de proveedor, producto/repuesto."""
        query = """
            SELECT 
                p.*,
                prov.nombre AS proveedor_nombre,
                CASE 
                    WHEN p.producto_id IS NOT NULL THEN inv.nombre
                    WHEN p.repuesto_id IS NOT NULL THEN rep.nombre
                END AS item_nombre,
                CASE 
                    WHEN p.producto_id IS NOT NULL THEN 'PRODUCTO'
                    WHEN p.repuesto_id IS NOT NULL THEN 'REPUESTO'
                END AS tipo_item,
                o.equipo AS orden_equipo
            FROM pedidos p
            LEFT JOIN proveedores prov ON p.proveedor_id = prov.id
            LEFT JOIN inventario inv ON p.producto_id = inv.id
            LEFT JOIN repuestos rep ON p.repuesto_id = rep.id
            LEFT JOIN ordenes o ON p.orden_id = o.id
            WHERE p.estado IN ('PENDIENTE', 'PEDIDO')
            ORDER BY p.fecha_solicitud DESC
        """
        return self.bd.OBTENER_TODOS(query)
    
    def OBTENER_PEDIDOS_POR_PROVEEDOR(self, proveedor_id, solo_pendientes=True):
        """Obtiene pedidos de un proveedor específico."""
        filtro_estado = "AND p.estado = 'PENDIENTE'" if solo_pendientes else ""
        
        query = f"""
            SELECT 
                p.*,
                prov.nombre AS proveedor_nombre,
                CASE 
                    WHEN p.producto_id IS NOT NULL THEN inv.nombre
                    WHEN p.repuesto_id IS NOT NULL THEN rep.nombre
                END AS item_nombre,
                CASE 
                    WHEN p.producto_id IS NOT NULL THEN 'PRODUCTO'
                    WHEN p.repuesto_id IS NOT NULL THEN 'REPUESTO'
                END AS tipo_item,
                o.equipo AS orden_equipo
            FROM pedidos p
            LEFT JOIN proveedores prov ON p.proveedor_id = prov.id
            LEFT JOIN inventario inv ON p.producto_id = inv.id
            LEFT JOIN repuestos rep ON p.repuesto_id = rep.id
            LEFT JOIN ordenes o ON p.orden_id = o.id
            WHERE p.proveedor_id = ? {filtro_estado}
            ORDER BY p.fecha_solicitud DESC
        """
        return self.bd.OBTENER_TODOS(query, (proveedor_id,))
    
    def OBTENER_PEDIDOS_POR_ORDEN(self, orden_id):
        """Obtiene todos los pedidos asociados a una orden de trabajo."""
        query = """
            SELECT 
                p.*,
                prov.nombre AS proveedor_nombre,
                CASE 
                    WHEN p.producto_id IS NOT NULL THEN inv.nombre
                    WHEN p.repuesto_id IS NOT NULL THEN rep.nombre
                END AS item_nombre,
                CASE 
                    WHEN p.producto_id IS NOT NULL THEN 'PRODUCTO'
                    WHEN p.repuesto_id IS NOT NULL THEN 'REPUESTO'
                END AS tipo_item
            FROM pedidos p
            LEFT JOIN proveedores prov ON p.proveedor_id = prov.id
            LEFT JOIN inventario inv ON p.producto_id = inv.id
            LEFT JOIN repuestos rep ON p.repuesto_id = rep.id
            WHERE p.orden_id = ?
            ORDER BY p.fecha_solicitud DESC
        """
        return self.bd.OBTENER_TODOS(query, (orden_id,))
    
    def ACTUALIZAR_ESTADO(self, pedido_id, nuevo_estado):
        """
        Actualiza el estado de un pedido.
        Estados: 'PENDIENTE', 'PEDIDO', 'RECIBIDO', 'CANCELADO'
        """
        from datetime import datetime
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        campo_fecha = None
        if nuevo_estado == 'PEDIDO':
            campo_fecha = 'fecha_pedido'
        elif nuevo_estado == 'RECIBIDO':
            campo_fecha = 'fecha_recepcion'
        
        try:
            self.bd.EJECUTAR_CONSULTA(
                "UPDATE pedidos SET estado = ? WHERE id = ?",
                (nuevo_estado, pedido_id)
            )
            
            if campo_fecha:
                self.bd.EJECUTAR_CONSULTA(
                    f"UPDATE pedidos SET {campo_fecha} = ? WHERE id = ?",
                    (fecha_actual, pedido_id)
                )
            
            return True
        except:
            return False
    
    def MARCAR_COMO_PEDIDO(self, pedido_id):
        """Marca un pedido como PEDIDO (ya fue solicitado al proveedor)."""
        return self.ACTUALIZAR_ESTADO(pedido_id, 'PEDIDO')
    
    def MARCAR_COMO_RECIBIDO(self, pedido_id, actualizar_stock=True):
        """
        Marca un pedido como RECIBIDO.
        Opcionalmente actualiza el stock del producto/repuesto.
        """
        if not self.ACTUALIZAR_ESTADO(pedido_id, 'RECIBIDO'):
            return False
        
        if actualizar_stock:
            pedido = self.bd.OBTENER_UNO("SELECT * FROM pedidos WHERE id = ?", (pedido_id,))
            if pedido:
                if pedido['producto_id']:
                    self.bd.EJECUTAR_CONSULTA(
                        "UPDATE inventario SET stock = stock + ? WHERE id = ?",
                        (pedido['cantidad'], pedido['producto_id'])
                    )
                elif pedido['repuesto_id']:
                    self.bd.EJECUTAR_CONSULTA(
                        "UPDATE repuestos SET stock = stock + ? WHERE id = ?",
                        (pedido['cantidad'], pedido['repuesto_id'])
                    )
        
        return True
    
    def CANCELAR_PEDIDO(self, pedido_id):
        """Cancela un pedido."""
        return self.ACTUALIZAR_ESTADO(pedido_id, 'CANCELADO')
    
    def RECIBIR_LOTE_PEDIDOS(self, lista_pedido_ids, actualizar_stock=True):
        """
        Marca múltiples pedidos como RECIBIDOS y actualiza stock.
        
        Args:
            lista_pedido_ids: Lista de IDs de pedidos a marcar como recibidos
            actualizar_stock: Si debe actualizar el stock (default: True)
            
        Returns:
            Tuple (exitosos, errores) con cantidad de pedidos procesados
        """
        exitosos = 0
        errores = 0
        
        for pedido_id in lista_pedido_ids:
            try:
                if self.MARCAR_COMO_RECIBIDO(pedido_id, actualizar_stock=actualizar_stock):
                    exitosos += 1
                else:
                    errores += 1
            except Exception as e:
                print(f"Error recibiendo pedido {pedido_id}: {e}")
                errores += 1
        
        return (exitosos, errores)
    
    def OBTENER_PEDIDO(self, pedido_id):
        """Obtiene la información completa de un pedido."""
        query = """
            SELECT 
                p.*,
                prov.nombre AS proveedor_nombre,
                prov.telefono AS proveedor_telefono,
                CASE 
                    WHEN p.producto_id IS NOT NULL THEN inv.nombre
                    WHEN p.repuesto_id IS NOT NULL THEN rep.nombre
                END AS item_nombre,
                CASE 
                    WHEN p.producto_id IS NOT NULL THEN 'PRODUCTO'
                    WHEN p.repuesto_id IS NOT NULL THEN 'REPUESTO'
                END AS tipo_item,
                CASE 
                    WHEN p.producto_id IS NOT NULL THEN inv.costo
                    WHEN p.repuesto_id IS NOT NULL THEN rep.costo
                END AS costo_estimado,
                o.equipo AS orden_equipo,
                o.cliente_id AS orden_cliente_id
            FROM pedidos p
            LEFT JOIN proveedores prov ON p.proveedor_id = prov.id
            LEFT JOIN inventario inv ON p.producto_id = inv.id
            LEFT JOIN repuestos rep ON p.repuesto_id = rep.id
            LEFT JOIN ordenes o ON p.orden_id = o.id
            WHERE p.id = ?
        """
        return self.bd.OBTENER_UNO(query, (pedido_id,))
    
    def GENERAR_ORDEN_COMPRA(self, proveedor_id, solo_pendientes=True):
        """
        Genera un PDF de orden de compra con todos los pedidos de un proveedor.
        Incluye solo pedidos PENDIENTES por defecto, pero puede incluir todos.
        """
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import mm
        from reportlab.lib.colors import HexColor
        from reportlab.lib.utils import ImageReader
        import os
        from datetime import datetime
        
        # Obtener datos del proveedor
        proveedor = self.bd.OBTENER_UNO("SELECT * FROM proveedores WHERE id = ?", (proveedor_id,))
        if not proveedor:
            return None
        
        # Obtener pedidos del proveedor
        pedidos = self.OBTENER_PEDIDOS_POR_PROVEEDOR(proveedor_id, solo_pendientes=solo_pendientes)
        if not pedidos:
            return None
        
        # Convertir tuplas a diccionarios
        pedidos_dict = []
        for p in pedidos:
            pedidos_dict.append({
                'id': p[0],
                'orden_id': p[1],
                'producto_id': p[2],
                'repuesto_id': p[3],
                'proveedor_id': p[4],
                'cantidad': p[5],
                'estado': p[6],
                'fecha_solicitud': p[7],
                'fecha_pedido': p[8],
                'fecha_recepcion': p[9],
                'notas': p[10],
                'usuario_solicita': p[11],
                'proveedor_nombre': p[12],
                'item_nombre': p[13],
                'tipo_item': p[14],
                'orden_equipo': p[15]
            })
        
        # Obtener costos de items
        for pedido in pedidos_dict:
            if pedido['producto_id']:
                item = self.bd.OBTENER_UNO("SELECT costo, precio FROM inventario WHERE id = ?", (pedido['producto_id'],))
                if item:
                    pedido['costo'] = item[0] or 0
                    pedido['precio'] = item[1] or 0
                else:
                    pedido['costo'] = 0
                    pedido['precio'] = 0
            elif pedido['repuesto_id']:
                # Repuestos solo tienen costo, no precio
                item = self.bd.OBTENER_UNO("SELECT costo FROM repuestos WHERE id = ?", (pedido['repuesto_id'],))
                if item:
                    pedido['costo'] = item[0] or 0
                    pedido['precio'] = 0
                else:
                    pedido['costo'] = 0
                    pedido['precio'] = 0
            else:
                pedido['costo'] = 0
                pedido['precio'] = 0
        
        # Crear directorio de reportes si no existe
        reports_dir = "reports"
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        
        fecha_dir = datetime.now().strftime("%Y-%m-%d")
        full_dir = os.path.join(reports_dir, fecha_dir)
        if not os.path.exists(full_dir):
            os.makedirs(full_dir)
        
        # Nombre del archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ORDEN_COMPRA_{proveedor['nombre'].replace(' ', '_')}_{timestamp}.pdf"
        filepath = os.path.join(full_dir, filename)
        
        # Crear PDF
        c = canvas.Canvas(filepath, pagesize=letter)
        width, height = letter
        
        # Colores
        COLOR_PRIMARIO = HexColor('#0055cc')
        COLOR_TEXTO = HexColor('#1a1a1a')
        COLOR_GRIS = HexColor('#666666')
        
        # Cargar logo si existe
        try:
            config = self.bd.OBTENER_UNO("SELECT logo FROM empresa_config LIMIT 1", ())
            if config and config[0]:
                logo_path = os.path.join("assets", config[0])
                if os.path.exists(logo_path):
                    img = ImageReader(logo_path)
                    c.drawImage(img, 40, height - 100, width=80, height=60, preserveAspectRatio=True, mask='auto')
        except:
            pass
        
        # Título
        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(COLOR_PRIMARIO)
        c.drawString(140, height - 50, "ORDEN DE COMPRA")
        
        # Fecha y número
        c.setFont("Helvetica", 10)
        c.setFillColor(COLOR_TEXTO)
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
        c.drawRightString(width - 40, height - 50, f"Fecha: {fecha_actual}")
        c.drawRightString(width - 40, height - 65, f"N° {timestamp}")
        
        # Información del proveedor
        y_pos = height - 130
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(COLOR_PRIMARIO)
        c.drawString(40, y_pos, "PROVEEDOR:")
        
        c.setFont("Helvetica", 10)
        c.setFillColor(COLOR_TEXTO)
        y_pos -= 18
        c.drawString(40, y_pos, f"Nombre: {proveedor['nombre']}")
        y_pos -= 15
        c.drawString(40, y_pos, f"Teléfono: {proveedor.get('telefono', 'N/A')}")
        y_pos -= 15
        c.drawString(40, y_pos, f"Correo: {proveedor.get('correo', 'N/A')}")
        
        # Tabla de pedidos
        y_pos -= 40
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(COLOR_PRIMARIO)
        
        # Header de tabla
        x_item = 40
        x_tipo = 280
        x_cant = 360
        x_costo = 420
        x_subtotal = 500
        
        c.drawString(x_item, y_pos, "ITEM")
        c.drawString(x_tipo, y_pos, "TIPO")
        c.drawString(x_cant, y_pos, "CANT.")
        c.drawString(x_costo, y_pos, "COSTO")
        c.drawString(x_subtotal, y_pos, "SUBTOTAL")
        
        # Línea separadora
        y_pos -= 5
        c.setStrokeColor(COLOR_PRIMARIO)
        c.setLineWidth(1)
        c.line(40, y_pos, width - 40, y_pos)
        
        y_pos -= 15
        c.setFont("Helvetica", 9)
        c.setFillColor(COLOR_TEXTO)
        
        total_general = 0
        
        for pedido in pedidos_dict:
            # Verificar si hay espacio, si no crear nueva página
            if y_pos < 100:
                c.showPage()
                y_pos = height - 80
                c.setFont("Helvetica", 9)
                c.setFillColor(COLOR_TEXTO)
            
            # Item (truncar si es muy largo)
            item_nombre = pedido['item_nombre'][:35] if pedido['item_nombre'] else 'N/A'
            c.drawString(x_item, y_pos, item_nombre)
            
            # Tipo
            c.drawString(x_tipo, y_pos, pedido['tipo_item'][:10] if pedido['tipo_item'] else '-')
            
            # Cantidad
            c.drawString(x_cant, y_pos, str(pedido['cantidad']))
            
            # Costo
            costo = pedido['costo']
            c.drawString(x_costo, y_pos, f"${costo:,.0f}")
            
            # Subtotal
            subtotal = costo * pedido['cantidad']
            total_general += subtotal
            c.drawString(x_subtotal, y_pos, f"${subtotal:,.0f}")
            
            y_pos -= 15
        
        # Total
        y_pos -= 10
        c.setStrokeColor(COLOR_PRIMARIO)
        c.setLineWidth(2)
        c.line(420, y_pos, width - 40, y_pos)
        
        y_pos -= 20
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(COLOR_PRIMARIO)
        c.drawString(420, y_pos, "TOTAL:")
        c.drawString(500, y_pos, f"${total_general:,.0f}")
        
        # Pie de página
        c.setFont("Helvetica", 8)
        c.setFillColor(COLOR_GRIS)
        c.drawCentredString(width / 2, 40, f"Cantidad de items: {len(pedidos_dict)}")
        c.drawCentredString(width / 2, 28, "Generado por SERVITEC MANAGER")
        
        c.save()
        
        return filepath
    
    def ELIMINAR_PEDIDO(self, pedido_id):
        """Elimina un pedido (solo si está PENDIENTE)."""
        try:
            pedido = self.bd.OBTENER_UNO("SELECT estado FROM pedidos WHERE id = ?", (pedido_id,))
            if pedido and pedido['estado'] == 'PENDIENTE':
                return self.bd.EJECUTAR_CONSULTA("DELETE FROM pedidos WHERE id = ?", (pedido_id,))
            return False
        except:
            return False
    
    def OBTENER_ESTADISTICAS(self):
        """Obtiene estadísticas generales de pedidos."""
        stats = {
            'pendientes': 0,
            'pedidos': 0,
            'recibidos': 0,
            'cancelados': 0
        }
        
        resultados = self.bd.OBTENER_TODOS(
            "SELECT estado, COUNT(*) as total FROM pedidos GROUP BY estado"
        )
        
        for row in resultados:
            estado = row['estado'].lower()
            stats[estado] = row['total']
        
        return stats


# Continúa con las clases existentes...
    def AGREGAR_PRECIO_PROVEEDOR(self, proveedor_id, repuesto_id, precio):
        """Agregar o actualizar precio de repuesto para un proveedor"""
        try:
            # Verificar si ya existe
            existing = self.bd.OBTENER_UNO(
                "SELECT ID FROM precios_proveedor WHERE PROVEEDOR_ID = ? AND REPUESTO_ID = ?",
                (proveedor_id, repuesto_id)
            )
            
            if existing:
                # Actualizar
                self.bd.EJECUTAR_CONSULTA(
                    "UPDATE precios_proveedor SET PRECIO = ?, FECHA_ACTUALIZACION = datetime('now') WHERE PROVEEDOR_ID = ? AND REPUESTO_ID = ?",
                    (precio, proveedor_id, repuesto_id)
                )
            else:
                # Crear nuevo
                self.bd.EJECUTAR_CONSULTA(
                    "INSERT INTO precios_proveedor (proveedor_id, repuesto_id, precio, fecha_actualizacion) VALUES (?, ?, ?, datetime('now'))",
                    (proveedor_id, repuesto_id, precio)
                )
            return True
        except:
            return False

    def OBTENER_PRECIOS_PROVEEDOR(self, proveedor_id):
        """Obtener todos los precios registrados para un proveedor"""
        return self.bd.OBTENER_TODOS(
            "SELECT id, proveedor_id, repuesto_id, precio, FECHA_ACTUALIZACION FROM precios_proveedor WHERE PROVEEDOR_ID = ? ORDER BY FECHA_ACTUALIZACION DESC",
            (proveedor_id,)
        )

    def ACTUALIZAR_PRECIO_PROVEEDOR(self, precio_id, nuevo_precio):
        """Actualizar precio de un repuesto para un proveedor"""
        try:
            self.bd.EJECUTAR_CONSULTA(
                "UPDATE precios_proveedor SET PRECIO = ?, FECHA_ACTUALIZACION = datetime('now') WHERE ID = ?",
                (nuevo_precio, precio_id)
            )
            return True
        except:
            return False

    def ELIMINAR_PRECIO_PROVEEDOR(self, precio_id):
        """Eliminar entrada de precio"""
        try:
            self.bd.EJECUTAR_CONSULTA("DELETE FROM precios_proveedor WHERE ID = ?", (precio_id,))
            return True
        except:
            return False


# --- ÓRDENES ---
class GESTOR_ORDENES:
    def __init__(self, gestor_bd): self.bd = gestor_bd
    def OBTENER_ÓRDENES_POR_TÉCNICO(self, datos_usuario):
        uid, _, _, rol, _ = datos_usuario
        sql = "SELECT o.*, c.nombre FROM ordenes o LEFT JOIN clientes c ON o.cliente_id = c.id WHERE (o.tecnico_id = ? OR UPPER(o.estado) = 'PENDIENTE' OR o.estado IS NULL) AND (UPPER(o.estado) != 'ENTREGADO') ORDER BY o.id DESC LIMIT 200"
        if rol in ['GERENTE', 'ADMINISTRADOR', 'RECEPCIONISTA']:
             return self.bd.OBTENER_TODOS("SELECT o.*, c.nombre FROM ordenes o LEFT JOIN clientes c ON o.cliente_id = c.id WHERE UPPER(o.estado) != 'ENTREGADO' ORDER BY o.id DESC LIMIT 200")
        return self.bd.OBTENER_TODOS(sql, (uid,))
    def OBTENER_ORDEN_POR_ID(self, orden_id): return self.bd.OBTENER_UNO("SELECT o.*, c.nombre FROM ordenes o LEFT JOIN clientes c ON o.cliente_id = c.id WHERE o.id = ?", (orden_id,))
    def OBTENER_DATOS_TICKET(self, orden_id):
        return self.bd.OBTENER_UNO("SELECT o.*, c.rut, c.nombre, c.telefono, c.email FROM ordenes o JOIN clientes c ON o.cliente_id = c.id WHERE o.id = ?", (orden_id,))
    def OBTENER_HISTORIAL_CLIENTE(self, cid): return self.bd.OBTENER_TODOS("SELECT * FROM ordenes WHERE CLIENTE_ID = ? ORDER BY ID DESC LIMIT 10", (cid,))
    def OBTENER_ÓRDENES_DASHBOARD(self): return self.bd.OBTENER_TODOS("SELECT o.id, o.equipo, o.modelo, o.estado, u.nombre AS tecnico, c.nombre AS cliente FROM ordenes o LEFT JOIN usuarios u ON o.tecnico_id = u.id LEFT JOIN clientes c ON o.cliente_id = c.id WHERE UPPER(o.estado) != 'ENTREGADO' ORDER BY o.id DESC LIMIT 100")
    def OBTENER_ESTADÍSTICAS_ÓRDENES(self): return self.bd.OBTENER_TODOS("SELECT estado, COUNT(*) AS cantidad FROM ordenes GROUP BY ESTADO")
    def VERIFICAR_GARANTÍA(self, serie):
        if not serie: return []
        return self.bd.OBTENER_TODOS("SELECT o.*, c.nombre FROM ordenes o LEFT JOIN clientes c ON o.cliente_id = c.id WHERE o.serie = ? ORDER BY o.id DESC LIMIT 5", (serie.upper(),))
    def CREAR_ORDEN(self, cid, tid, tipo, marca, modelo, serie, falla, obs, accesorios, riesgoso, presupuesto, descuento, abono, fecha_entrega=None):
        if isinstance(accesorios, list): accesorios_str = ", ".join(accesorios)
        else: accesorios_str = ", ".join([k for k, v in accesorios.items() if v])
        obs_completa = f"FALLA: {falla.upper()} | {obs.upper()}"
        return self.bd.EJECUTAR_CONSULTA("INSERT INTO ordenes (cliente_id, tecnico_id, fecha, equipo, marca, modelo, serie, observacion, estado, accesorios, riesgoso, presupuesto, descuento, abono, fecha_entrega) VALUES (?, ?, datetime('now'), ?, ?, ?, ?, ?, 'Pendiente', ?, ?, ?, ?, ?, ?)", (cid, tid, tipo.upper(), marca.upper(), modelo.upper(), serie.upper(), obs_completa, accesorios_str.upper(), 1 if riesgoso else 0, presupuesto, descuento, abono, fecha_entrega))
    def ACTUALIZAR_ESTADO(self, orden_id, estado, condicion=None):
        if condicion is not None:
            return self.bd.EJECUTAR_CONSULTA("UPDATE ordenes SET estado = ?, condicion = ? WHERE id = ?", (estado, condicion, orden_id))
        else:
            return self.bd.EJECUTAR_CONSULTA("UPDATE ordenes SET estado = ? WHERE id = ?", (estado, orden_id))
    def ACTUALIZAR_TÉCNICO_ORDEN(self, orden_id, técnico_id): return self.bd.EJECUTAR_CONSULTA("UPDATE ordenes SET tecnico_id = ? WHERE id = ?", (técnico_id, orden_id))
    
    def PUEDE_EDITAR_ORDEN(self, orden_id):
        """Verifica si una orden puede ser editada (no tiene finanzas cerradas ni está entregada)"""
        orden = self.bd.OBTENER_UNO("SELECT estado FROM ordenes WHERE id = ?", (orden_id,))
        if not orden: return False
        # Verificar si ya tiene finanzas cerradas
        finanzas = self.bd.OBTENER_UNO("SELECT id FROM finanzas WHERE orden_id = ?", (orden_id,))
        if finanzas: return False
        # Verificar si ya fue entregada
        if orden[0] == "ENTREGADO": return False
        return True
    
    def ACTUALIZAR_ORDEN(self, orden_id, tid, tipo, marca, modelo, serie, falla, obs, accesorios, riesgoso, presupuesto, descuento, abono, fecha_entrega=None):
        """Actualiza una orden existente si aún no ha sido cobrada o entregada"""
        if not self.PUEDE_EDITAR_ORDEN(orden_id): return False
        if isinstance(accesorios, list): accesorios_str = ", ".join(accesorios)
        else: accesorios_str = ", ".join([k for k, v in accesorios.items() if v])
        obs_completa = f"FALLA: {falla.upper()} | {obs.upper()}"
        self.bd.EJECUTAR_CONSULTA(
            """UPDATE ordenes SET tecnico_id=?, equipo=?, marca=?, modelo=?, serie=?, 
               observacion=?, accesorios=?, riesgoso=?, presupuesto=?, descuento=?, abono=?, fecha_entrega=? 
               WHERE id=?""",
            (tid, tipo.upper(), marca.upper(), modelo.upper(), serie.upper(), 
             obs_completa, accesorios_str.upper(), 1 if riesgoso else 0, presupuesto, descuento, abono, fecha_entrega, orden_id)
        )
        return True  # Si llegamos aquí, la actualización fue exitosa
    
    def CERRAR_ORDEN_FINANZAS(self, orden_id, total, repuestos, envío, efectivo, transferencia, tarjeta, con_iva, pct_tec):
        if self.bd.OBTENER_UNO("SELECT ID FROM finanzas WHERE ORDEN_ID = ?", (orden_id,)): return False
        if pct_tec == 0:
            odata = self.bd.OBTENER_UNO("SELECT tecnico_id FROM ordenes WHERE id = ?", (orden_id,))
            if odata:
                tdata = self.bd.OBTENER_UNO("SELECT PORCENTAJE_COMISION FROM usuarios WHERE ID = ?", (odata[0],))
                if tdata: pct_tec = tdata[0]
        m_iva = total * 0.19 if con_iva else 0
        m_banco = tarjeta * 0.0295
        util = (total - m_banco) - repuestos - envío
        util_com = util * 0.81 if con_iva else util
        com_tec = max(0, util_com * (pct_tec / 100))
        self.ACTUALIZAR_ESTADO(orden_id, "ENTREGADO")
        return self.bd.EJECUTAR_CONSULTA("INSERT INTO finanzas (orden_id, total_cobrado, costo_repuesto, costo_envio, monto_efectivo, monto_transferencia, monto_debito, monto_credito, aplicó_iva, utilidad_real, monto_comision_tecnico, fecha_cierre) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))", (orden_id, total, repuestos, envío, efectivo, transferencia, tarjeta, 0, 1 if con_iva else 0, util_com, com_tec))
    
    # Compatibilidad
    get_orders_by_tech = OBTENER_ÓRDENES_POR_TÉCNICO
    get_order_by_id = OBTENER_ORDEN_POR_ID
    get_ticket_data = OBTENER_DATOS_TICKET
    get_client_history = OBTENER_HISTORIAL_CLIENTE
    get_dashboard_orders = OBTENER_ÓRDENES_DASHBOARD
    get_order_stats = OBTENER_ESTADÍSTICAS_ÓRDENES
    check_warranty = VERIFICAR_GARANTÍA
    create_order = CREAR_ORDEN
    update_status = ACTUALIZAR_ESTADO
    update_order_tech = ACTUALIZAR_TÉCNICO_ORDEN
    can_edit_order = PUEDE_EDITAR_ORDEN
    update_order = ACTUALIZAR_ORDEN
    close_order_finances = CERRAR_ORDEN_FINANZAS

# --- INVENTARIO Y VENTAS ---
class GESTOR_INVENTARIO:
    def __init__(self, gestor_bd, cache_inteligente=None): 
        self.bd = gestor_bd
        self._cache_inteligente = cache_inteligente
        self._productos_cache = None
        self._cache_timestamp = 0
    
    def OBTENER_PRODUCTOS(self): 
        # Intentar caché persistente primero
        if self._cache_inteligente:
            data = self._cache_inteligente.cargar_inventario()
            if data:
                return data
        
        # Fallback a caché en memoria de BD
        return self.bd.OBTENER_TODOS("SELECT * FROM inventario ORDER BY nombre ASC", use_cache=True)
    
    def OBTENER_PRODUCTOS_CON_PROVEEDOR(self):
        """Obtiene todos los productos con información del proveedor"""
        query = """
            SELECT * FROM inventario
            ORDER BY nombre ASC
        """
        return self.bd.OBTENER_TODOS(query, use_cache=True)
    
    def get_products_with_provider(self):
        """Alias para compatibilidad snake_case"""
        return self.OBTENER_PRODUCTOS_CON_PROVEEDOR()
    
    def BUSCAR_PRODUCTOS(self, consulta):
        q = f"%{consulta.upper()}%"
        # Limitar resultados para evitar congelamiento
        return self.bd.OBTENER_TODOS("SELECT * FROM inventario WHERE nombre LIKE ? LIMIT 100", (q,))
    
    def AGREGAR_PRODUCTO(self, nombre, costo, precio, stock, cat="GENERAL", proveedor_id=None): 
        try:
            if proveedor_id is None or proveedor_id == 0:
                messagebox.showerror("Error", "Debe seleccionar un proveedor")
                return False
            result = self.bd.EJECUTAR_CONSULTA(
                "INSERT INTO inventario (nombre, categoria, costo, precio, stock, proveedor_id) VALUES (?, ?, ?, ?, ?, ?)", 
                (nombre.upper(), cat.upper(), costo, precio, stock, proveedor_id)
            )
            # Invalidar caché
            if self._cache_inteligente:
                self._cache_inteligente.invalidar_inventario()
            return result
        except Exception as e:
            print(f"Error al agregar producto: {e}")
            return False
    
    def ACTUALIZAR_PRODUCTO(self, producto_id, nombre, cat, costo, precio, stock, proveedor_id=None):
        try:
            if proveedor_id is None or proveedor_id == 0:
                from tkinter import messagebox
                messagebox.showerror("Error", "Debe seleccionar un proveedor")
                return False
            self.bd.EJECUTAR_CONSULTA(
                "UPDATE inventario SET nombre=?, categoria=?, costo=?, precio=?, stock=?, proveedor_id=? WHERE id=?", 
                (nombre.upper(), cat.upper(), costo, precio, stock, proveedor_id, producto_id)
            )
            # Invalidar caché
            if self._cache_inteligente:
                self._cache_inteligente.invalidar_inventario()
            return True
        except Exception as e:
            print(f"Error al actualizar producto: {e}")
            return False
    def ACTUALIZAR_PRECIO_PRODUCTO(self, producto_id, nuevo_precio):
        try:
            self.bd.EJECUTAR_CONSULTA("UPDATE inventario SET precio = ? WHERE id = ?", (nuevo_precio, producto_id))
            return True
        except:
            return False
    def ELIMINAR_PRODUCTO(self, producto_id): 
        result = self.bd.EJECUTAR_CONSULTA("DELETE FROM inventario WHERE id=?", (producto_id,))
        # Invalidar caché
        if self._cache_inteligente:
            self._cache_inteligente.invalidar_inventario()
        return result
    def PROCESAR_VENTA(self, usuario_id, carrito, pagos, total_venta, descuento):
        venta_id = self.bd.EJECUTAR_CONSULTA("INSERT INTO ventas (usuario_id, fecha, total, descuento, pago_efectivo, pago_transferencia, pago_debito, pago_credito) VALUES (?, datetime('now'), ?, ?, ?, ?, ?, ?)", (usuario_id, total_venta, descuento, pagos['efectivo'], pagos['transferencia'], pagos['debito'], pagos['credito']))
        if not venta_id: return False
        for item in carrito:
            producto_id, nombre, cantidad, precio, es_servicio, detalles = item
            subtotal = cantidad * precio
            if not es_servicio:
                self.bd.EJECUTAR_CONSULTA("UPDATE inventario SET STOCK = STOCK - ? WHERE ID = ?", (cantidad, producto_id))
                self.bd.EJECUTAR_CONSULTA("INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?)", (venta_id, producto_id, cantidad, precio, subtotal))
            else:
                orden_id = producto_id
                self.bd.EJECUTAR_CONSULTA("INSERT INTO detalle_ventas (venta_id, orden_id, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?)", (venta_id, orden_id, cantidad, precio, subtotal))
                odata = self.bd.OBTENER_UNO("SELECT tecnico_id FROM ordenes WHERE id = ?", (orden_id,))
                pct_tec = 0
                if odata:
                    tdata = self.bd.OBTENER_UNO("SELECT PORCENTAJE_COMISION FROM usuarios WHERE ID = ?", (odata[0],))
                    if tdata: pct_tec = tdata[0]
                tot = precio; rep = detalles.get('rep', 0); env = detalles.get('env', 0); con_iva = detalles.get('iva', False); 
                con_tarjeta = detalles.get('card', False)
                m_tarjeta_calc = tot if con_tarjeta else 0
                
                # Insertamos solo si no existe (protección doble)
                if not self.bd.OBTENER_UNO("SELECT ID FROM finanzas WHERE ORDEN_ID = ?", (orden_id,)):
                    m_iva = tot * 0.19 if con_iva else 0; m_banco = m_tarjeta_calc * 0.0295; util = (tot - m_banco) - rep - env
        return venta_id
    
    # Compatibilidad
    get_products = OBTENER_PRODUCTOS
    get_products_with_provider = OBTENER_PRODUCTOS_CON_PROVEEDOR
    search_products = BUSCAR_PRODUCTOS
    add_product = AGREGAR_PRODUCTO
    update_product = ACTUALIZAR_PRODUCTO
    update_product_price = ACTUALIZAR_PRECIO_PRODUCTO
    delete_product = ELIMINAR_PRODUCTO
    process_sale = PROCESAR_VENTA

class GESTOR_CAJA:
    def __init__(self, gestor_bd): self.bd = gestor_bd
    def OBTENER_SESIÓN_ACTIVA(self, usuario_id): return self.bd.OBTENER_UNO("SELECT * FROM caja_sesiones WHERE usuario_id = ? AND estado = 'ABIERTA'", (usuario_id,))
    def ABRIR_TURNO(self, usuario_id, monto):
        if self.OBTENER_SESIÓN_ACTIVA(usuario_id): return False
        return self.bd.EJECUTAR_CONSULTA("INSERT INTO caja_sesiones (usuario_id, fecha_apertura, monto_inicial, estado) VALUES (?, datetime('now'), ?, 'ABIERTA')", (usuario_id, monto))
    
    def AGREGAR_GASTO(self, usuario_id, descripción, monto):
        sesión = self.OBTENER_SESIÓN_ACTIVA(usuario_id)
        if not sesión: return False
        return self.bd.EJECUTAR_CONSULTA("INSERT INTO gastos (sesion_id, descripcion, monto, fecha) VALUES (?, ?, ?, datetime('now'))", (sesión[0], descripción.upper(), monto))
    
    def OBTENER_GASTOS_SESIÓN(self, usuario_id):
        sesión = self.OBTENER_SESIÓN_ACTIVA(usuario_id)
        if not sesión: return []
        return self.bd.OBTENER_TODOS("SELECT * FROM gastos WHERE SESION_ID = ? ORDER BY ID DESC", (sesión[0],))

    def OBTENER_VENTAS_TURNO_ACTUAL(self, usuario_id):
        sesión = self.OBTENER_SESIÓN_ACTIVA(usuario_id)
        if not sesión: return (0,0,0,0)
        # Finanzas (Órdenes) - No filtramos por usuario_id porque las órdenes pueden ser de varios técnicos
        res_t = self.bd.OBTENER_UNO("SELECT SUM(monto_efectivo), SUM(monto_transferencia), SUM(monto_debito), SUM(monto_credito) FROM finanzas WHERE FECHA_CIERRE >= ?", (sesión[2],))
        # Ventas (POS) - Filtramos por usuario_id para obtener solo las ventas del cajero actual
        res_p = self.bd.OBTENER_UNO("SELECT SUM(pago_efectivo), SUM(pago_transferencia), SUM(pago_debito), SUM(pago_credito) FROM ventas WHERE usuario_id = ? AND FECHA >= ?", (usuario_id, sesión[2],))
        
        return ((res_t[0] or 0)+(res_p[0] or 0), (res_t[1] or 0)+(res_p[1] or 0), (res_t[2] or 0)+(res_p[2] or 0), (res_t[3] or 0)+(res_p[3] or 0))

    def CERRAR_TURNO(self, usuario_id, r_efec, r_trf, r_deb, r_cred):
        sesión = self.OBTENER_SESIÓN_ACTIVA(usuario_id)
        if not sesión: return False
        
        # Ventas Sistema
        ventas = self.OBTENER_VENTAS_TURNO_ACTUAL(usuario_id) # (Efec, Trf, Deb, Cred)
        
        # Gastos
        gastos = self.bd.OBTENER_UNO("SELECT SUM(monto) FROM gastos WHERE SESION_ID = ?", (sesión[0],))
        total_gastos = gastos[0] or 0
        
        # Calculo Final Sistema (Solo Efectivo se ve afectado por gastos en caja fisica, pero el sistema debe cuadrar todo)
        # Sistema dice: Tienes X en efectivo. Menos gastos Y. Total esperado en caja = X - Y + Fondo
        sys_efectivo_esperado = (sesión[4] + ventas[0]) - total_gastos
        
        # Totales Sistema
        sys_total_monetario = sys_efectivo_esperado + ventas[1] + ventas[2] + ventas[3]
        
        # Totales Reales
        real_total = r_efec + r_trf + r_deb + r_cred
        
        diff = real_total - sys_total_monetario
        
        return self.bd.EJECUTAR_CONSULTA("""
            UPDATE caja_sesiones SET 
            FECHA_CIERRE = datetime('now'), 
            MONTO_FINAL_SISTEMA = ?, 
            MONTO_FINAL_REAL = ?, 
            REAL_EFECTIVO = ?, 
            REAL_TRANSFERENCIA = ?, 
            REAL_DEBITO = ?, 
            REAL_CREDITO = ?, 
            TOTAL_GASTOS = ?, 
            DIFERENCIA = ?, 
            ESTADO = 'CERRADA' 
            WHERE ID = ?""", 
            (sys_total_monetario, real_total, r_efec, r_trf, r_deb, r_cred, total_gastos, diff, sesión[0]))
    
    # Compatibilidad
    get_active_session = OBTENER_SESIÓN_ACTIVA
    open_shift = ABRIR_TURNO
    add_expense = AGREGAR_GASTO
    get_session_expenses = OBTENER_GASTOS_SESIÓN
    get_current_shift_sales = OBTENER_VENTAS_TURNO_ACTUAL
    close_shift = CERRAR_TURNO

class GESTOR_REPORTES:
    def __init__(self, gestor_bd): self.bd = gestor_bd
    def OBTENER_HISTORIAL_TECNICO(self, tecnico_id, fecha_inicio=None, fecha_fin=None):
        consulta = "SELECT o.id, o.equipo, o.modelo, f.fecha_cierre, f.total_cobrado, f.costo_repuesto, f.monto_comision_tecnico, f.monto_debito, f.monto_credito, f.aplicó_iva, f.costo_envio FROM ORDENES o JOIN finanzas f ON o.id = f.orden_id WHERE o.tecnico_id = ?"
        parámetros = [tecnico_id]
        if fecha_inicio and fecha_fin:
            consulta += " AND date(f.fecha_cierre) BETWEEN ? AND ?"
            parámetros.extend([fecha_inicio, fecha_fin])
        consulta += " ORDER BY f.fecha_cierre DESC"
        return self.bd.OBTENER_TODOS(consulta, tuple(parámetros))
    def OBTENER_VENTAS_DIARIAS(self): return self.bd.OBTENER_TODOS("SELECT f.id, o.id, o.equipo, u.nombre, f.total_cobrado, f.utilidad_real, f.fecha_cierre, f.monto_comision_tecnico FROM finanzas f JOIN ORDENES o ON f.orden_id = o.id JOIN usuarios u ON o.tecnico_id = u.id WHERE date(f.fecha_cierre) = date('now')")

    def OBTENER_HISTORIAL_COMPLETO_ORDENES(self):
        return self.bd.OBTENER_TODOS("""
            SELECT o.id, o.fecha, c.nombre AS cliente_nombre, o.equipo || ' ' || o.modelo AS equipo_completo, u.nombre AS tecnico_nombre, o.estado, o.condicion, o.observacion, o.fecha_entrega, o.presupuesto, f.fecha_cierre
            FROM ORDENES o
            LEFT JOIN clientes c ON o.cliente_id = c.id
            LEFT JOIN usuarios u ON o.tecnico_id = u.id
            LEFT JOIN finanzas f ON o.id = f.orden_id
            ORDER BY o.id DESC
        """)

    def OBTENER_FINANZAS_ORDEN(self, orden_id):
        return self.bd.OBTENER_UNO("SELECT * FROM finanzas WHERE ORDEN_ID = ?", (orden_id,))

    def OBTENER_HISTORIAL_COMPLETO_VENTAS(self):
        return self.bd.OBTENER_TODOS("""
            SELECT v.id, v.fecha, u.nombre, v.total, v.pago_efectivo, v.pago_transferencia, v.pago_debito, v.pago_credito
            FROM ventas v
            LEFT JOIN usuarios u ON v.usuario_id = u.id
            ORDER BY v.id DESC
        """)

    def OBTENER_DETALLES_VENTA(self, venta_id):
        return self.bd.OBTENER_TODOS("""
            SELECT COALESCE(i.nombre, 'ORDEN #' || d.orden_id), d.cantidad, d.precio_unitario, d.subtotal
            FROM detalle_ventas d
            LEFT JOIN inventario i ON d.producto_id = i.id
            WHERE d.venta_id = ?
        """, (venta_id,))
    
    # Compatibilidad
    get_tech_history = OBTENER_HISTORIAL_TECNICO
    get_daily_sales = OBTENER_VENTAS_DIARIAS
    get_full_history_orders = OBTENER_HISTORIAL_COMPLETO_ORDENES
    get_order_financials = OBTENER_FINANZAS_ORDEN
    get_full_history_sales = OBTENER_HISTORIAL_COMPLETO_VENTAS
    get_sale_details = OBTENER_DETALLES_VENTA

class GESTOR_LOGICA:
    def __init__(self, gestor_bd, cache_inteligente=None):
        self.bd = gestor_bd
        self._cache = cache_inteligente
        
        # Inicializar gestores con caché
        self.clientes = GESTOR_CLIENTES(gestor_bd)
        self.ordenes = GESTOR_ORDENES(gestor_bd)
        self.inventario = GESTOR_INVENTARIO(gestor_bd, cache_inteligente)
        self.caja = GESTOR_CAJA(gestor_bd)
        self.reportes = GESTOR_REPORTES(gestor_bd)
        self.modelos = GESTOR_MODELOS(gestor_bd)
        self.marcas = GESTOR_MARCAS(gestor_bd)
        self.servicios = GESTOR_SERVICIOS(gestor_bd, cache_inteligente)
        self.repuestos = GESTOR_REPUESTOS(gestor_bd, cache_inteligente)
        self.proveedores = GESTOR_PROVEEDORES(gestor_bd)
        self.pedidos = GESTOR_PEDIDOS(gestor_bd)  # 🆕 Sistema de pedidos
        
        # --- NUEVOS MÓDULOS (v2.2.0) ---
        self.importador = IMPORTADOR_DATOS(gestor_bd, self) if IMPORTADOR_DATOS else None
        self.reportes_avanzados = REPORTES_AVANZADOS(gestor_bd) if REPORTES_AVANZADOS else None
        self.predicción = PREDICCION_VENTAS(gestor_bd) if PREDICCION_VENTAS else None
        self.notificaciones = NOTIFICACIONES(gestor_bd) if NOTIFICACIONES else None
        self.mensajeria = GESTOR_MENSAJERIA(gestor_bd) if GESTOR_MENSAJERIA else None  # 🆕 WhatsApp y Email
        
        # Precargar datos en segundo plano si hay caché
        if cache_inteligente:
            import threading
            thread = threading.Thread(target=cache_inteligente.precargar_datos_inicio, daemon=True)
            thread.start()

    def SEMILLA_ADMINISTRADOR(self):
        if not self.bd.OBTENER_UNO("SELECT * FROM usuarios WHERE nombre = ?", ('ADMIN',)): self.CREAR_USUARIO('ADMIN', 'admin123', 'GERENTE', 0)
        if not self.bd.OBTENER_UNO("SELECT * FROM usuarios WHERE nombre = ?", ('TÉCNICO1',)): self.CREAR_USUARIO('TÉCNICO1', '1234', 'TÉCNICO', 50)
        self.modelos.SEMILLA_MODELOS()

    def INICIAR_SESIÓN(self, usuario, contraseña): return self.bd.OBTENER_UNO("SELECT * FROM usuarios WHERE nombre = ? AND password = ?", (usuario.upper(), contraseña))
    def OBTENER_TODOS_USUARIOS(self): return self.bd.OBTENER_TODOS("SELECT * FROM usuarios")
    def OBTENER_TÉCNICOS(self): return self.bd.OBTENER_TODOS("SELECT id, nombre, porcentaje_comision FROM usuarios WHERE rol IN ('TÉCNICO', 'GERENTE', 'ADMINISTRADOR')")
    def CREAR_USUARIO(self, usuario, contraseña, rol, comisión):
        try: return self.bd.EJECUTAR_CONSULTA("INSERT INTO usuarios (nombre, password, rol, porcentaje_comision) VALUES (?, ?, ?, ?)", (usuario.upper(), contraseña, rol.upper(), comisión))
        except: return False
    def ELIMINAR_USUARIO(self, usuario_id): return self.bd.EJECUTAR_CONSULTA("DELETE FROM usuarios WHERE ID = ?", (usuario_id,))
    
    # --- COMPATIBILIDAD TEMPORAL (snake_case minúsculas) ---
    # GESTORES
    clients = property(lambda s: s.clientes)
    orders = property(lambda s: s.ordenes)
    inventory = property(lambda s: s.inventario)
    cash = property(lambda s: s.caja)
    reports = property(lambda s: s.reportes)
    models = property(lambda s: s.modelos)
    services = property(lambda s: s.servicios)
    parts = property(lambda s: s.repuestos)
    providers = property(lambda s: s.proveedores)
    
    # NUEVOS MÓDULOS (v2.2.0)
    importer = property(lambda s: s.importador)
    advanced_reports = property(lambda s: s.reportes_avanzados)
    sales_prediction = property(lambda s: s.predicción)
    notifications = property(lambda s: s.notificaciones)
    messaging = property(lambda s: s.mensajeria)  # 🆕 WhatsApp y Email
    # MÉTODOS ALIAS
    login = INICIAR_SESIÓN
    get_all_users = OBTENER_TODOS_USUARIOS
    get_technicians = OBTENER_TÉCNICOS
    create_user = CREAR_USUARIO
    delete_user = ELIMINAR_USUARIO
-- ========================================================================================
-- ESQUEMA DE BASE DE DATOS OPTIMIZADO - ServitecManager PRO v2.0
-- ========================================================================================
-- Fecha: December 18, 2025
-- Descripción: Estructura optimizada de 15 tablas (vs 21 anteriores)
-- Cambios: Eliminación de redundancias, unificación de finanzas, relaciones claras
-- ========================================================================================

-- ========================================================================================
-- CONFIGURACIÓN INICIAL
-- ========================================================================================

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = -64000;
PRAGMA busy_timeout = 5000;

-- ========================================================================================
-- TABLAS PRINCIPALES
-- ========================================================================================

-- 1. USUARIOS (MANTENER)
-- ─────────────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    rol TEXT NOT NULL,
    porcentaje_comision REAL DEFAULT 50.0,
    activo INTEGER DEFAULT 1,
    fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_usuarios_nombre ON usuarios(nombre);
CREATE INDEX IF NOT EXISTS idx_usuarios_rol ON usuarios(rol);

-- 2. CLIENTES (MANTENER)
-- ─────────────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cedula TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    telefono TEXT,
    email TEXT,
    fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_clientes_cedula ON clientes(cedula);
CREATE INDEX IF NOT EXISTS idx_clientes_nombre ON clientes(nombre);

-- 3. ORDENES (REESTRUCTURADA - TABLA CENTRAL COMPLETA)
-- ─────────────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ordenes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    tecnico_id INTEGER,
    
    -- INFORMACIÓN DEL EQUIPO
    fecha_entrada TEXT DEFAULT CURRENT_TIMESTAMP,
    fecha_entrega TEXT,
    equipo TEXT,
    marca TEXT,
    modelo TEXT,
    serie TEXT,
    observacion TEXT,
    accesorios TEXT,
    riesgoso INTEGER DEFAULT 0,
    
    -- ESTADOS
    estado TEXT CHECK(estado IN ('Pendiente', 'En Proceso', 'Reparado', 'Entregado', 'Sin solución')) DEFAULT 'Pendiente',
    condicion TEXT CHECK(condicion IN ('PENDIENTE', 'SOLUCIONADO', 'SIN SOLUCIÓN')) DEFAULT 'PENDIENTE',
    
    -- FINANZAS INTEGRADAS (TODO EN UNA TABLA)
    presupuesto_inicial REAL DEFAULT 0,
    costo_total_repuestos REAL DEFAULT 0,
    costo_total_servicios REAL DEFAULT 0,
    costo_envio REAL DEFAULT 0,
    descuento REAL DEFAULT 0,
    total_a_cobrar REAL DEFAULT 0,
    abono REAL DEFAULT 0,
    saldo_pendiente REAL DEFAULT 0,
    utilidad_bruta REAL DEFAULT 0,
    comision_tecnico REAL DEFAULT 0,
    
    -- MÉTODOS DE PAGO (PARA REPARACIONES)
    pago_efectivo REAL DEFAULT 0,
    pago_transferencia REAL DEFAULT 0,
    pago_debito REAL DEFAULT 0,
    pago_credito REAL DEFAULT 0,
    
    -- AUDITORÍA
    fecha_cierre TEXT,
    usuario_cierre_id INTEGER,
    
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE RESTRICT,
    FOREIGN KEY (tecnico_id) REFERENCES usuarios(id) ON DELETE SET NULL,
    FOREIGN KEY (usuario_cierre_id) REFERENCES usuarios(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_ordenes_cliente ON ordenes(cliente_id);
CREATE INDEX IF NOT EXISTS idx_ordenes_estado ON ordenes(estado);
CREATE INDEX IF NOT EXISTS idx_ordenes_fecha ON ordenes(fecha_entrada);
CREATE INDEX IF NOT EXISTS idx_ordenes_tecnico ON ordenes(tecnico_id);
CREATE INDEX IF NOT EXISTS idx_ordenes_saldo ON ordenes(saldo_pendiente);

-- 4. ORDEN_REPUESTOS (NUEVA - RELACIÓN ESPECÍFICA)
-- ─────────────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS orden_repuestos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    orden_id INTEGER NOT NULL,
    repuesto_id INTEGER NOT NULL,
    cantidad INTEGER DEFAULT 1,
    costo_unitario REAL,
    precio_cobrado REAL,
    utilizado INTEGER DEFAULT 1,
    fecha_agregado TEXT DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (orden_id) REFERENCES ordenes(id) ON DELETE CASCADE,
    FOREIGN KEY (repuesto_id) REFERENCES repuestos(id) ON DELETE RESTRICT
);
CREATE INDEX IF NOT EXISTS idx_orden_repuestos_orden ON orden_repuestos(orden_id);
CREATE INDEX IF NOT EXISTS idx_orden_repuestos_repuesto ON orden_repuestos(repuesto_id);

-- 5. ORDEN_SERVICIOS (NUEVA)
-- ─────────────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS orden_servicios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    orden_id INTEGER NOT NULL,
    servicio_id INTEGER,
    descripcion_custom TEXT,
    costo REAL,
    fecha_agregado TEXT DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (orden_id) REFERENCES ordenes(id) ON DELETE CASCADE,
    FOREIGN KEY (servicio_id) REFERENCES servicios_predefinidos(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_orden_servicios_orden ON orden_servicios(orden_id);

-- 6. TRANSACCIONES (NUEVA - UNIFICADA PARA TODO)
-- ─────────────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS transacciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT DEFAULT CURRENT_TIMESTAMP,
    tipo TEXT CHECK(tipo IN ('VENTA_PRODUCTO', 'COBRO_REPARACION', 'GASTO', 'PAGO_PROVEEDOR', 'COMPRA', 'ABONO')),
    
    -- REFERENCIA A LA OPERACIÓN
    referencia_id INTEGER,  -- orden_id, venta_id, compra_id, etc.
    referencia_tipo TEXT,   -- 'orden', 'venta', 'compra'
    
    -- INFORMACIÓN FINANCIERA
    monto_total REAL,
    descuento REAL DEFAULT 0,
    monto_final REAL,
    
    -- DESGLOSE DE PAGO
    monto_efectivo REAL DEFAULT 0,
    monto_transferencia REAL DEFAULT 0,
    monto_debito REAL DEFAULT 0,
    monto_credito REAL DEFAULT 0,
    
    -- CONTEXTO
    descripcion TEXT,
    sesion_caja_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    
    FOREIGN KEY (sesion_caja_id) REFERENCES caja_sesiones(id) ON DELETE RESTRICT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE RESTRICT
);
CREATE INDEX IF NOT EXISTS idx_transacciones_fecha ON transacciones(fecha);
CREATE INDEX IF NOT EXISTS idx_transacciones_tipo ON transacciones(tipo);
CREATE INDEX IF NOT EXISTS idx_transacciones_sesion ON transacciones(sesion_caja_id);
CREATE INDEX IF NOT EXISTS idx_transacciones_usuario ON transacciones(usuario_id);

-- 7. VENTAS (SIMPLIFICADA - SOLO PARA PRODUCTOS)
-- ─────────────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT DEFAULT CURRENT_TIMESTAMP,
    cliente_id INTEGER,
    usuario_id INTEGER NOT NULL,
    orden_id INTEGER,  -- Si está asociada a una orden
    
    -- RESUMEN
    total_productos REAL,
    descuento REAL DEFAULT 0,
    total_final REAL,
    
    -- RELACIONES
    transaccion_id INTEGER UNIQUE,  -- Enlace a transacciones
    
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE SET NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE RESTRICT,
    FOREIGN KEY (orden_id) REFERENCES ordenes(id) ON DELETE SET NULL,
    FOREIGN KEY (transaccion_id) REFERENCES transacciones(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_ventas_fecha ON ventas(fecha);
CREATE INDEX IF NOT EXISTS idx_ventas_usuario ON ventas(usuario_id);
CREATE INDEX IF NOT EXISTS idx_ventas_cliente ON ventas(cliente_id);

-- 8. VENTA_DETALLES (SOLO PARA PRODUCTOS)
-- ─────────────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS venta_detalles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venta_id INTEGER NOT NULL,
    producto_id INTEGER NOT NULL,
    cantidad INTEGER DEFAULT 1,
    precio_unitario REAL,
    subtotal REAL,
    
    FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES inventario(id) ON DELETE RESTRICT
);
CREATE INDEX IF NOT EXISTS idx_venta_detalles_venta ON venta_detalles(venta_id);

-- ========================================================================================
-- TABLAS DE SOPORTE
-- ========================================================================================

-- 9. REPUESTOS (MANTENER)
-- ─────────────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS repuestos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL,
    categoria TEXT,
    costo REAL,
    precio_sugerido REAL,
    stock INTEGER DEFAULT 0,
    proveedor_id INTEGER,
    fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_repuestos_nombre ON repuestos(nombre);
CREATE INDEX IF NOT EXISTS idx_repuestos_categoria ON repuestos(categoria);
CREATE INDEX IF NOT EXISTS idx_repuestos_stock ON repuestos(stock);

-- 10. INVENTARIO (MANTENER)
-- ─────────────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS inventario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL,
    categoria TEXT,
    costo REAL,
    precio REAL,
    stock INTEGER DEFAULT 0,
    proveedor_id INTEGER,
    fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_inventario_nombre ON inventario(nombre);
CREATE INDEX IF NOT EXISTS idx_inventario_categoria ON inventario(categoria);
CREATE INDEX IF NOT EXISTS idx_inventario_stock ON inventario(stock);

-- 11. SERVICIOS_PREDEFINIDOS (MANTENER)
-- ─────────────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS servicios_predefinidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_servicio TEXT UNIQUE NOT NULL,
    categoria TEXT,
    costo_mano_obra REAL,
    fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_servicios_nombre ON servicios_predefinidos(nombre_servicio);

-- 12. CAJA_SESIONES (MANTENER CON MEJORAS)
-- ─────────────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS caja_sesiones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    fecha_apertura TEXT DEFAULT CURRENT_TIMESTAMP,
    fecha_cierre TEXT,
    monto_inicial REAL DEFAULT 0,
    monto_final_sistema REAL DEFAULT 0,
    monto_final_real REAL DEFAULT 0,
    estado TEXT DEFAULT 'ABIERTO' CHECK(estado IN ('ABIERTO', 'CERRADO', 'EN_REVISION')),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE RESTRICT
);
CREATE INDEX IF NOT EXISTS idx_caja_sesiones_usuario ON caja_sesiones(usuario_id);
CREATE INDEX IF NOT EXISTS idx_caja_sesiones_estado ON caja_sesiones(estado);
CREATE INDEX IF NOT EXISTS idx_caja_sesiones_fecha ON caja_sesiones(fecha_apertura);

-- 13. GASTOS (SIMPLIFICADA)
-- ─────────────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS gastos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sesion_id INTEGER NOT NULL,
    descripcion TEXT NOT NULL,
    monto REAL NOT NULL,
    fecha TEXT DEFAULT CURRENT_TIMESTAMP,
    transaccion_id INTEGER UNIQUE,
    FOREIGN KEY (sesion_id) REFERENCES caja_sesiones(id) ON DELETE CASCADE,
    FOREIGN KEY (transaccion_id) REFERENCES transacciones(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_gastos_sesion ON gastos(sesion_id);
CREATE INDEX IF NOT EXISTS idx_gastos_fecha ON gastos(fecha);

-- 14. PROVEEDORES (MANTENER)
-- ─────────────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS proveedores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL,
    telefono TEXT,
    email TEXT,
    direccion TEXT,
    saldo_pendiente REAL DEFAULT 0,
    fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_proveedores_nombre ON proveedores(nombre);

-- 15. CATEGORIAS (MANTENER)
-- ─────────────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL,
    tipo TEXT CHECK(tipo IN ('PRODUCTO', 'REPUESTO')),
    fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_categorias_tipo ON categorias(tipo);

-- ========================================================================================
-- TABLAS OPCIONALES (PARA CATÁLOGOS)
-- ========================================================================================

-- MODELOS
CREATE TABLE IF NOT EXISTS modelos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_dispositivo TEXT,
    marca TEXT,
    modelo TEXT,
    UNIQUE(tipo_dispositivo, marca, modelo)
);
CREATE INDEX IF NOT EXISTS idx_modelos_lookup ON modelos(tipo_dispositivo, marca);

-- MARCAS PERSONALIZADAS
CREATE TABLE IF NOT EXISTS marcas_personalizadas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL,
    fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
);

-- COMPRAS
CREATE TABLE IF NOT EXISTS compras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proveedor_id INTEGER NOT NULL,
    fecha_compra TEXT DEFAULT CURRENT_TIMESTAMP,
    total REAL DEFAULT 0,
    estado TEXT CHECK(estado IN ('PENDIENTE', 'RECIBIDA', 'CANCELADA')) DEFAULT 'PENDIENTE',
    notas TEXT,
    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
);
CREATE INDEX IF NOT EXISTS idx_compras_proveedor ON compras(proveedor_id);
CREATE INDEX IF NOT EXISTS idx_compras_fecha ON compras(fecha_compra);

-- DETALLE_COMPRAS
CREATE TABLE IF NOT EXISTS detalle_compras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    compra_id INTEGER NOT NULL,
    repuesto_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    costo_unitario REAL NOT NULL,
    subtotal REAL DEFAULT 0,
    FOREIGN KEY (compra_id) REFERENCES compras(id),
    FOREIGN KEY (repuesto_id) REFERENCES repuestos(id)
);
CREATE INDEX IF NOT EXISTS idx_detalle_compras_compra ON detalle_compras(compra_id);
CREATE INDEX IF NOT EXISTS idx_detalle_compras_repuesto ON detalle_compras(repuesto_id);

-- ========================================================================================
-- TRIGGERS PARA INTEGRIDAD DE DATOS
-- ========================================================================================

-- 1. ACTUALIZAR STOCK AL USAR REPUESTOS
-- ─────────────────────────────────────────────────────────────────────────────────────
DROP TRIGGER IF EXISTS tr_orden_repuestos_insert;
CREATE TRIGGER tr_orden_repuestos_insert
AFTER INSERT ON orden_repuestos
BEGIN
    UPDATE repuestos 
    SET stock = stock - NEW.cantidad 
    WHERE id = NEW.repuesto_id AND NEW.utilizado = 1;
END;

-- 2. ACTUALIZAR STOCK AL CANCELAR REPUESTO
-- ─────────────────────────────────────────────────────────────────────────────────────
DROP TRIGGER IF EXISTS tr_orden_repuestos_delete;
CREATE TRIGGER tr_orden_repuestos_delete
AFTER DELETE ON orden_repuestos
BEGIN
    UPDATE repuestos 
    SET stock = stock + OLD.cantidad 
    WHERE id = OLD.repuesto_id AND OLD.utilizado = 1;
END;

-- 3. ACTUALIZAR STOCK EN VENTAS
-- ─────────────────────────────────────────────────────────────────────────────────────
DROP TRIGGER IF EXISTS tr_venta_detalles_insert;
CREATE TRIGGER tr_venta_detalles_insert
AFTER INSERT ON venta_detalles
BEGIN
    UPDATE inventario 
    SET stock = stock - NEW.cantidad 
    WHERE id = NEW.producto_id;
END;

-- 4. RESTITUIR STOCK AL ELIMINAR VENTA
-- ─────────────────────────────────────────────────────────────────────────────────────
DROP TRIGGER IF EXISTS tr_venta_detalles_delete;
CREATE TRIGGER tr_venta_detalles_delete
AFTER DELETE ON venta_detalles
BEGIN
    UPDATE inventario 
    SET stock = stock + OLD.cantidad 
    WHERE id = OLD.producto_id;
END;

-- 5. CALCULAR COSTO TOTAL REPUESTOS EN ÓRDENES
-- ─────────────────────────────────────────────────────────────────────────────────────
DROP TRIGGER IF EXISTS tr_orden_repuestos_update_costo_insert;
CREATE TRIGGER tr_orden_repuestos_update_costo_insert
AFTER INSERT ON orden_repuestos
BEGIN
    UPDATE ordenes 
    SET costo_total_repuestos = (
        SELECT COALESCE(SUM(costo_unitario * cantidad), 0)
        FROM orden_repuestos 
        WHERE orden_id = NEW.orden_id AND utilizado = 1
    ),
    total_a_cobrar = COALESCE((SELECT presupuesto_inicial FROM ordenes WHERE id = NEW.orden_id), 0) - 
                     COALESCE((SELECT descuento FROM ordenes WHERE id = NEW.orden_id), 0)
    WHERE id = NEW.orden_id;
END;

DROP TRIGGER IF EXISTS tr_orden_repuestos_update_costo_delete;
CREATE TRIGGER tr_orden_repuestos_update_costo_delete
AFTER DELETE ON orden_repuestos
BEGIN
    UPDATE ordenes 
    SET costo_total_repuestos = (
        SELECT COALESCE(SUM(costo_unitario * cantidad), 0)
        FROM orden_repuestos 
        WHERE orden_id = OLD.orden_id AND utilizado = 1
    ),
    total_a_cobrar = COALESCE((SELECT presupuesto_inicial FROM ordenes WHERE id = OLD.orden_id), 0) - 
                     COALESCE((SELECT descuento FROM ordenes WHERE id = OLD.orden_id), 0)
    WHERE id = OLD.orden_id;
END;

-- 6. CALCULAR COSTO TOTAL SERVICIOS EN ÓRDENES
-- ─────────────────────────────────────────────────────────────────────────────────────
DROP TRIGGER IF EXISTS tr_orden_servicios_update_costo_insert;
CREATE TRIGGER tr_orden_servicios_update_costo_insert
AFTER INSERT ON orden_servicios
BEGIN
    UPDATE ordenes 
    SET costo_total_servicios = (
        SELECT COALESCE(SUM(costo), 0)
        FROM orden_servicios 
        WHERE orden_id = NEW.orden_id
    )
    WHERE id = NEW.orden_id;
END;

DROP TRIGGER IF EXISTS tr_orden_servicios_update_costo_delete;
CREATE TRIGGER tr_orden_servicios_update_costo_delete
AFTER DELETE ON orden_servicios
BEGIN
    UPDATE ordenes 
    SET costo_total_servicios = (
        SELECT COALESCE(SUM(costo), 0)
        FROM orden_servicios 
        WHERE orden_id = OLD.orden_id
    )
    WHERE id = OLD.orden_id;
END;

-- 7. CALCULAR SALDO PENDIENTE
-- ─────────────────────────────────────────────────────────────────────────────────────
DROP TRIGGER IF EXISTS tr_ordenes_update_saldo;
CREATE TRIGGER tr_ordenes_update_saldo
AFTER UPDATE OF abono, total_a_cobrar ON ordenes
BEGIN
    UPDATE ordenes 
    SET saldo_pendiente = CASE 
        WHEN (total_a_cobrar - COALESCE(abono, 0)) < 0 THEN 0
        ELSE (total_a_cobrar - COALESCE(abono, 0))
    END,
    utilidad_bruta = CASE
        WHEN total_a_cobrar > 0 THEN total_a_cobrar - COALESCE(costo_total_repuestos, 0) - COALESCE(costo_total_servicios, 0) - COALESCE(costo_envio, 0)
        ELSE 0
    END
    WHERE id = NEW.id;
END;

-- ========================================================================================
-- VISTAS PARA REPORTES Y CONSULTAS COMPLEJAS
-- ========================================================================================

-- VISTA 1: ÓRDENES COMPLETAS CON INFORMACIÓN RELACIONADA
-- ─────────────────────────────────────────────────────────────────────────────────────
DROP VIEW IF EXISTS vista_ordenes_completas;
CREATE VIEW vista_ordenes_completas AS
SELECT 
    o.id,
    o.cliente_id,
    c.cedula as cliente_cedula,
    c.nombre as cliente_nombre,
    c.telefono as cliente_telefono,
    c.email as cliente_email,
    o.tecnico_id,
    u.nombre as tecnico_nombre,
    o.fecha_entrada,
    o.fecha_entrega,
    o.equipo,
    o.marca,
    o.modelo,
    o.serie,
    o.observacion,
    o.accesorios,
    o.riesgoso,
    o.estado,
    o.presupuesto_inicial,
    o.costo_total_repuestos,
    o.costo_total_servicios,
    o.costo_envio,
    o.descuento,
    o.total_a_cobrar,
    o.abono,
    o.saldo_pendiente,
    o.utilidad_bruta,
    o.comision_tecnico,
    (SELECT COUNT(*) FROM orden_repuestos WHERE orden_id = o.id AND utilizado = 1) as total_repuestos,
    (SELECT COUNT(*) FROM orden_servicios WHERE orden_id = o.id) as total_servicios,
    o.fecha_cierre,
    CASE WHEN o.saldo_pendiente <= 0 THEN 'PAGADO' ELSE 'PENDIENTE' END as estado_pago
FROM ordenes o
LEFT JOIN clientes c ON o.cliente_id = c.id
LEFT JOIN usuarios u ON o.tecnico_id = u.id;

-- VISTA 2: RESUMEN FINANCIERO DIARIO
-- ─────────────────────────────────────────────────────────────────────────────────────
DROP VIEW IF EXISTS vista_resumen_diario;
CREATE VIEW vista_resumen_diario AS
SELECT 
    DATE(t.fecha) as dia,
    COUNT(DISTINCT CASE WHEN t.tipo = 'COBRO_REPARACION' THEN t.referencia_id END) as ordenes_cobradas,
    COUNT(DISTINCT CASE WHEN t.tipo = 'VENTA_PRODUCTO' THEN t.referencia_id END) as ventas_productos,
    SUM(CASE WHEN t.tipo IN ('COBRO_REPARACION', 'VENTA_PRODUCTO', 'ABONO') THEN t.monto_final ELSE 0 END) as ingresos_totales,
    SUM(CASE WHEN t.tipo = 'GASTO' THEN t.monto_final ELSE 0 END) as gastos_totales,
    SUM(CASE WHEN t.tipo = 'PAGO_PROVEEDOR' THEN t.monto_final ELSE 0 END) as pagos_proveedores,
    cs.usuario_id,
    u.nombre as usuario_nombre,
    cs.id as sesion_id
FROM transacciones t
JOIN caja_sesiones cs ON t.sesion_caja_id = cs.id
JOIN usuarios u ON cs.usuario_id = u.id
GROUP BY DATE(t.fecha), cs.usuario_id, cs.id;

-- VISTA 3: REPUESTOS MÁS USADOS
-- ─────────────────────────────────────────────────────────────────────────────────────
DROP VIEW IF EXISTS vista_repuestos_mas_usados;
CREATE VIEW vista_repuestos_mas_usados AS
SELECT 
    r.id,
    r.nombre,
    r.categoria,
    COUNT(*) as veces_usado,
    SUM(ore.cantidad) as total_unidades,
    SUM(ore.cantidad * ore.costo_unitario) as costo_total,
    r.stock as stock_actual
FROM orden_repuestos ore
JOIN repuestos r ON ore.repuesto_id = r.id
WHERE ore.utilizado = 1
GROUP BY r.id
ORDER BY veces_usado DESC;

-- VISTA 4: INVENTARIO BAJO STOCK
-- ─────────────────────────────────────────────────────────────────────────────────────
DROP VIEW IF EXISTS vista_inventario_bajo_stock;
CREATE VIEW vista_inventario_bajo_stock AS
SELECT 
    'REPUESTO' as tipo,
    r.id,
    r.nombre,
    r.categoria,
    r.stock,
    r.precio_sugerido as precio,
    p.nombre as proveedor
FROM repuestos r
LEFT JOIN proveedores p ON r.proveedor_id = p.id
WHERE r.stock < 5
UNION ALL
SELECT 
    'PRODUCTO' as tipo,
    i.id,
    i.nombre,
    i.categoria,
    i.stock,
    i.precio,
    p.nombre as proveedor
FROM inventario i
LEFT JOIN proveedores p ON i.proveedor_id = p.id
WHERE i.stock < 5;

-- VISTA 5: CLIENTES CON MÁS ÓRDENES
-- ─────────────────────────────────────────────────────────────────────────────────────
DROP VIEW IF EXISTS vista_clientes_mas_activos;
CREATE VIEW vista_clientes_mas_activos AS
SELECT 
    c.id,
    c.cedula,
    c.nombre,
    c.telefono,
    c.email,
    COUNT(o.id) as total_ordenes,
    SUM(o.total_a_cobrar) as total_gastado,
    SUM(o.abono) as total_pagado,
    SUM(o.saldo_pendiente) as saldo_pendiente,
    MAX(o.fecha_entrada) as ultima_orden
FROM clientes c
LEFT JOIN ordenes o ON c.id = o.cliente_id
GROUP BY c.id
ORDER BY total_ordenes DESC;

-- VISTA 6: RENDIMIENTO POR TÉCNICO
-- ─────────────────────────────────────────────────────────────────────────────────────
DROP VIEW IF EXISTS vista_rendimiento_tecnicos;
CREATE VIEW vista_rendimiento_tecnicos AS
SELECT 
    u.id,
    u.nombre,
    COUNT(o.id) as ordenes_reparadas,
    COUNT(CASE WHEN o.estado = 'Entregado' THEN 1 END) as ordenes_entregadas,
    SUM(o.total_a_cobrar) as total_cobrado,
    SUM(o.comision_tecnico) as comision_total,
    AVG(o.utilidad_bruta) as utilidad_promedio,
    COUNT(CASE WHEN o.estado = 'Sin solución' THEN 1 END) as sin_solucion
FROM usuarios u
LEFT JOIN ordenes o ON u.id = o.tecnico_id
WHERE u.rol = 'TECNICO'
GROUP BY u.id
ORDER BY ordenes_reparadas DESC;

-- ========================================================================================
-- DATOS INICIALES (CATEGORÍAS)
-- ========================================================================================

INSERT OR IGNORE INTO categorias (nombre, tipo) VALUES
-- PRODUCTOS
('FUNDAS', 'PRODUCTO'),
('CARGADORES', 'PRODUCTO'),
('MICAS', 'PRODUCTO'),
('AUDIFONOS', 'PRODUCTO'),
('CABLES', 'PRODUCTO'),
('OTROS', 'PRODUCTO'),
-- REPUESTOS
('PANTALLAS', 'REPUESTO'),
('BATERIAS', 'REPUESTO'),
('PINES CARGA', 'REPUESTO'),
('FLEX', 'REPUESTO'),
('CAMARAS', 'REPUESTO'),
('OTROS', 'REPUESTO');

-- ========================================================================================
-- PROCEDIMIENTOS ALMACENADOS (FUNCIONES DE NEGOCIO)
-- ========================================================================================

-- NOTA: SQLite no soporta procedimientos almacenados completos.
-- Las operaciones se realizan desde Python usando transacciones.
-- A continuación se detallan las operaciones críticas:

/*
OPERACIÓN 1: CREAR REPARACIÓN COMPLETA
────────────────────────────────────────
1. INSERT ordenes (sin repuestos/servicios aún)
2. INSERT orden_repuestos (para cada repuesto)
3. INSERT orden_servicios (para cada servicio)
4. Los triggers actualizan automáticamente costo_total_* y totales

OPERACIÓN 2: COBRAR REPARACIÓN
───────────────────────────────
1. UPDATE ordenes SET abono, pago_efectivo, etc.
2. INSERT transacciones (tipo: 'COBRO_REPARACION')
3. UPDATE ordenes.saldo_pendiente (vía trigger)
4. Si saldo_pendiente <= 0: UPDATE ordenes.estado = 'Entregado'

OPERACIÓN 3: VENDER PRODUCTOS
──────────────────────────────
1. INSERT ventas
2. INSERT venta_detalles (para cada producto)
3. INSERT transacciones (tipo: 'VENTA_PRODUCTO')
4. UPDATE transacciones.transaccion_id = venta_id
5. Los triggers actualizan stock automáticamente

OPERACIÓN 4: CIERRE DE CAJA
────────────────────────────
1. UPDATE caja_sesiones SET fecha_cierre, monto_final_real, estado = 'CERRADO'
2. SELECT SUM(monto_final) FROM transacciones WHERE sesion_caja_id = $session_id AND tipo IN (...)
3. Validar diferencias
4. Si hay discrepancias: UPDATE caja_sesiones.estado = 'EN_REVISION'
*/

-- ========================================================================================
-- ANÁLISIS DE CAMBIOS RESPECTO A ESTRUCTURA ANTERIOR
-- ========================================================================================

/*
TABLAS ELIMINADAS (6):
❌ detalles_orden         → Integrado en orden_repuestos, orden_servicios, transacciones
❌ finanzas              → Integrado en tabla ordenes
❌ detalle_ventas (vieja)→ Reemplazado por venta_detalles
❌ compras              → NO USADO ACTUALMENTE (se puede recuperar si es necesario)
❌ detalle_compras      → NO USADO ACTUALMENTE
❌ pagos_proveedor      → NO USADO ACTUALMENTE (se puede recuperar si es necesario)
❌ precios_proveedor    → NO USADO ACTUALMENTE
❌ pedidos              → NO USADO ACTUALMENTE

TABLAS MODIFICADAS (4):
✏️ ordenes              → Ahora contiene TODA la información financiera
✏️ caja_sesiones        → Mejorada con más estados
✏️ gastos               → Ahora enlazada con transacciones
✏️ (nueva) transacciones → Central de auditoría financiera

TABLAS NUEVAS (3):
✨ orden_repuestos      → Relación clara 1:N entre orden y repuestos
✨ orden_servicios      → Relación clara 1:N entre orden y servicios
✨ transacciones        → Registro unificado de movimientos financieros

TABLAS NUEVAS (2):
✨ venta_detalles       → Reemplazo mejorado de detalle_ventas

VENTAJAS DE LA NUEVA ESTRUCTURA:
✅ Menos tablas (15 vs 21)
✅ Menos redundancias (no se duplica info financiera)
✅ Relaciones más claras
✅ Triggers automáticos para integridad
✅ Vistas para reportes complejos
✅ Auditoría centralizada (tabla transacciones)
✅ Más eficiente (menos JOINs)
✅ Más fácil de mantener
✅ Más escalable para nuevas funciones

IMPACTO EN CÓDIGO PYTHON:
• Módulo reparaciones: Trabaja con ordenes + orden_repuestos + orden_servicios
• Módulo POS: Trabaja con ventas + venta_detalles + transacciones
• Módulo finanzas: Consulta directamente tabla ordenes (no finanzas aparte)
• Módulo caja: Trabaja con transacciones + caja_sesiones
• Reportes: Usa vistas en lugar de queries complejas
*/

-- ========================================================================================
-- FIN DEL ESQUEMA
-- ========================================================================================

-- Verificar que todas las tablas se crearon correctamente
PRAGMA table_list;
PRAGMA foreign_key_list(ordenes);
PRAGMA foreign_key_list(transacciones);

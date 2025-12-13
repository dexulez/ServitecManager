"""
API REST Server para ServitecManager
Centraliza la base de datos para múltiples clientes
"""
from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import sqlite3
import json
import asyncio
from contextlib import contextmanager

app = FastAPI(title="ServitecManager API", version="1.0.0")

# CORS para permitir conexiones desde cualquier cliente
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gestión de conexiones WebSocket para actualizaciones en tiempo real
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Envía actualizaciones a todos los clientes conectados"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# Contexto de base de datos
@contextmanager
def get_db():
    conn = sqlite3.connect('SERVITEC.DB', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def dict_factory(cursor, row):
    """Convierte rows a diccionarios"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# ==================== MODELOS PYDANTIC ====================

class Cliente(BaseModel):
    nombre: str
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None

class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None

class Producto(BaseModel):
    nombre: str
    categoria: str
    precio: float
    stock: int
    stock_minimo: Optional[int] = 5
    descripcion: Optional[str] = None

class Orden(BaseModel):
    cliente_id: int
    equipo: str
    marca: str
    modelo: str
    problema: str
    estado: str = "Pendiente"
    total: float = 0.0
    anticipo: float = 0.0

class Venta(BaseModel):
    cliente_id: Optional[int] = None
    total: float
    metodo_pago: str = "Efectivo"
    productos: List[Dict[str, Any]]

# ==================== ENDPOINTS - CLIENTES ====================

@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "ServitecManager API",
        "version": "1.0.0",
        "endpoints": [
            "/clientes", "/inventario", "/ordenes", 
            "/ventas", "/finanzas", "/ws"
        ]
    }

@app.get("/clientes")
async def get_clientes(
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """Obtiene lista de clientes con búsqueda opcional"""
    with get_db() as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        
        if search:
            cursor.execute("""
                SELECT * FROM clientes 
                WHERE nombre LIKE ? OR telefono LIKE ?
                LIMIT ? OFFSET ?
            """, (f"%{search}%", f"%{search}%", limit, offset))
        else:
            cursor.execute("SELECT * FROM clientes LIMIT ? OFFSET ?", (limit, offset))
        
        return cursor.fetchall()

@app.get("/clientes/{cliente_id}")
async def get_cliente(cliente_id: int):
    """Obtiene un cliente específico"""
    with get_db() as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
        cliente = cursor.fetchone()
        
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        return cliente

@app.post("/clientes")
async def create_cliente(cliente: Cliente):
    """Crea un nuevo cliente"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO clientes (nombre, telefono, email, direccion)
            VALUES (?, ?, ?, ?)
        """, (cliente.nombre, cliente.telefono, cliente.email, cliente.direccion))
        conn.commit()
        
        nuevo_id = cursor.lastrowid
        
        # Notificar a todos los clientes conectados
        await manager.broadcast({
            "event": "cliente_creado",
            "data": {"id": nuevo_id, **cliente.dict()}
        })
        
        return {"id": nuevo_id, **cliente.dict()}

@app.put("/clientes/{cliente_id}")
async def update_cliente(cliente_id: int, cliente: ClienteUpdate):
    """Actualiza un cliente existente"""
    updates = {k: v for k, v in cliente.dict().items() if v is not None}
    
    if not updates:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Verificar que existe
        cursor.execute("SELECT id FROM clientes WHERE id = ?", (cliente_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        # Construir query dinámica
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [cliente_id]
        
        cursor.execute(f"UPDATE clientes SET {set_clause} WHERE id = ?", values)
        conn.commit()
        
        # Notificar actualización
        await manager.broadcast({
            "event": "cliente_actualizado",
            "data": {"id": cliente_id, **updates}
        })
        
        return {"id": cliente_id, **updates}

@app.delete("/clientes/{cliente_id}")
async def delete_cliente(cliente_id: int):
    """Elimina un cliente"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        await manager.broadcast({
            "event": "cliente_eliminado",
            "data": {"id": cliente_id}
        })
        
        return {"message": "Cliente eliminado"}

# ==================== ENDPOINTS - INVENTARIO ====================

@app.get("/inventario")
async def get_inventario(
    categoria: Optional[str] = None,
    stock_bajo: bool = False,
    limit: int = 100,
    offset: int = 0
):
    """Obtiene inventario con filtros opcionales"""
    with get_db() as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        
        query = "SELECT * FROM inventario WHERE 1=1"
        params = []
        
        if categoria:
            query += " AND categoria = ?"
            params.append(categoria)
        
        if stock_bajo:
            query += " AND stock <= stock_minimo"
        
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        return cursor.fetchall()

@app.post("/inventario")
async def create_producto(producto: Producto):
    """Agrega un producto al inventario"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO inventario 
            (nombre, categoria, precio, stock, stock_minimo, descripcion)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            producto.nombre, producto.categoria, producto.precio,
            producto.stock, producto.stock_minimo, producto.descripcion
        ))
        conn.commit()
        
        nuevo_id = cursor.lastrowid
        
        await manager.broadcast({
            "event": "producto_creado",
            "data": {"id": nuevo_id, **producto.dict()}
        })
        
        return {"id": nuevo_id, **producto.dict()}

@app.put("/inventario/{producto_id}/stock")
async def update_stock(producto_id: int, cantidad: int, operacion: str = "set"):
    """Actualiza el stock de un producto
    operacion: 'set' (establece), 'add' (suma), 'subtract' (resta)
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        if operacion == "set":
            cursor.execute("UPDATE inventario SET stock = ? WHERE id = ?", 
                         (cantidad, producto_id))
        elif operacion == "add":
            cursor.execute("UPDATE inventario SET stock = stock + ? WHERE id = ?", 
                         (cantidad, producto_id))
        elif operacion == "subtract":
            cursor.execute("UPDATE inventario SET stock = stock - ? WHERE id = ?", 
                         (cantidad, producto_id))
        else:
            raise HTTPException(status_code=400, detail="Operación no válida")
        
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        # Obtener stock actualizado
        cursor.execute("SELECT stock FROM inventario WHERE id = ?", (producto_id,))
        nuevo_stock = cursor.fetchone()[0]
        
        await manager.broadcast({
            "event": "stock_actualizado",
            "data": {"id": producto_id, "stock": nuevo_stock}
        })
        
        return {"id": producto_id, "stock": nuevo_stock}

# ==================== ENDPOINTS - ÓRDENES ====================

@app.get("/ordenes")
async def get_ordenes(
    estado: Optional[str] = None,
    cliente_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0
):
    """Obtiene órdenes con filtros opcionales"""
    with get_db() as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        
        query = "SELECT * FROM ordenes WHERE 1=1"
        params = []
        
        if estado:
            query += " AND estado = ?"
            params.append(estado)
        
        if cliente_id:
            query += " AND cliente_id = ?"
            params.append(cliente_id)
        
        query += " ORDER BY fecha_ingreso DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        return cursor.fetchall()

@app.post("/ordenes")
async def create_orden(orden: Orden):
    """Crea una nueva orden de servicio"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ordenes 
            (cliente_id, equipo, marca, modelo, problema, estado, total, anticipo, fecha_ingreso)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            orden.cliente_id, orden.equipo, orden.marca, orden.modelo,
            orden.problema, orden.estado, orden.total, orden.anticipo
        ))
        conn.commit()
        
        nuevo_id = cursor.lastrowid
        
        await manager.broadcast({
            "event": "orden_creada",
            "data": {"id": nuevo_id, **orden.dict()}
        })
        
        return {"id": nuevo_id, **orden.dict()}

@app.put("/ordenes/{orden_id}/estado")
async def update_estado_orden(orden_id: int, estado: str):
    """Actualiza el estado de una orden"""
    estados_validos = ["Pendiente", "En Proceso", "Reparado", "Entregado", "Cancelado"]
    
    if estado not in estados_validos:
        raise HTTPException(
            status_code=400, 
            detail=f"Estado inválido. Válidos: {', '.join(estados_validos)}"
        )
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE ordenes SET estado = ? WHERE id = ?", (estado, orden_id))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Orden no encontrada")
        
        await manager.broadcast({
            "event": "orden_actualizada",
            "data": {"id": orden_id, "estado": estado}
        })
        
        return {"id": orden_id, "estado": estado}

# ==================== ENDPOINTS - VENTAS ====================

@app.post("/ventas")
async def create_venta(venta: Venta):
    """Registra una nueva venta y actualiza inventario"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Iniciar transacción
        cursor.execute("BEGIN TRANSACTION")
        
        try:
            # Insertar venta
            cursor.execute("""
                INSERT INTO ventas (cliente_id, total, metodo_pago, fecha)
                VALUES (?, ?, ?, datetime('now'))
            """, (venta.cliente_id, venta.total, venta.metodo_pago))
            
            venta_id = cursor.lastrowid
            
            # Insertar detalles y actualizar stock
            for producto in venta.productos:
                cursor.execute("""
                    INSERT INTO detalle_ventas 
                    (venta_id, producto_id, cantidad, precio_unitario, subtotal)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    venta_id,
                    producto['id'],
                    producto['cantidad'],
                    producto['precio'],
                    producto['subtotal']
                ))
                
                # Descontar stock
                cursor.execute("""
                    UPDATE inventario 
                    SET stock = stock - ? 
                    WHERE id = ?
                """, (producto['cantidad'], producto['id']))
            
            conn.commit()
            
            await manager.broadcast({
                "event": "venta_creada",
                "data": {"id": venta_id, **venta.dict()}
            })
            
            return {"id": venta_id, "message": "Venta registrada"}
            
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# ==================== WEBSOCKET - TIEMPO REAL ====================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket para actualizaciones en tiempo real"""
    await manager.connect(websocket)
    try:
        while True:
            # Mantener conexión activa
            data = await websocket.receive_text()
            
            # Echo de ping/pong para keep-alive
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ==================== ESTADÍSTICAS ====================

@app.get("/stats/dashboard")
async def get_dashboard_stats():
    """Obtiene estadísticas para el dashboard"""
    with get_db() as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        
        # Total clientes
        cursor.execute("SELECT COUNT(*) as total FROM clientes")
        total_clientes = cursor.fetchone()['total']
        
        # Órdenes pendientes
        cursor.execute("SELECT COUNT(*) as total FROM ordenes WHERE estado = 'Pendiente'")
        ordenes_pendientes = cursor.fetchone()['total']
        
        # Productos con stock bajo
        cursor.execute("SELECT COUNT(*) as total FROM inventario WHERE stock <= stock_minimo")
        stock_bajo = cursor.fetchone()['total']
        
        # Ventas del día
        cursor.execute("""
            SELECT COALESCE(SUM(total), 0) as total 
            FROM ventas 
            WHERE DATE(fecha) = DATE('now')
        """)
        ventas_hoy = cursor.fetchone()['total']
        
        return {
            "clientes": total_clientes,
            "ordenes_pendientes": ordenes_pendientes,
            "productos_stock_bajo": stock_bajo,
            "ventas_hoy": ventas_hoy
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

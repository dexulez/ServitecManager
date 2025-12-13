"""
Cliente API para ServitecManager
Conecta la aplicación de escritorio con el servidor centralizado
"""
import requests
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
import threading
import websocket
import logging

logger = logging.getLogger(__name__)

class ServitecAPIClient:
    """Cliente para comunicarse con la API central de ServitecManager"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.ws = None
        self.ws_thread = None
        self.callbacks = {}
        
    def _get(self, endpoint: str, params: Optional[Dict] = None):
        """Petición GET"""
        try:
            response = requests.get(f"{self.base_url}{endpoint}", params=params, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error GET {endpoint}: {e}")
            raise
    
    def _post(self, endpoint: str, data: Dict):
        """Petición POST"""
        try:
            response = requests.post(
                f"{self.base_url}{endpoint}", 
                json=data,
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error POST {endpoint}: {e}")
            raise
    
    def _put(self, endpoint: str, data: Dict):
        """Petición PUT"""
        try:
            response = requests.put(
                f"{self.base_url}{endpoint}",
                json=data,
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error PUT {endpoint}: {e}")
            raise
    
    def _delete(self, endpoint: str):
        """Petición DELETE"""
        try:
            response = requests.delete(f"{self.base_url}{endpoint}", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error DELETE {endpoint}: {e}")
            raise
    
    # ==================== CLIENTES ====================
    
    def get_clientes(self, search: Optional[str] = None, limit: int = 100, offset: int = 0):
        """Obtiene lista de clientes"""
        params = {"limit": limit, "offset": offset}
        if search:
            params["search"] = search
        return self._get("/clientes", params)
    
    def get_cliente(self, cliente_id: int):
        """Obtiene un cliente específico"""
        return self._get(f"/clientes/{cliente_id}")
    
    def create_cliente(self, nombre: str, telefono: str = None, 
                       email: str = None, direccion: str = None):
        """Crea un nuevo cliente"""
        data = {
            "nombre": nombre,
            "telefono": telefono,
            "email": email,
            "direccion": direccion
        }
        return self._post("/clientes", data)
    
    def update_cliente(self, cliente_id: int, **kwargs):
        """Actualiza un cliente"""
        return self._put(f"/clientes/{cliente_id}", kwargs)
    
    def delete_cliente(self, cliente_id: int):
        """Elimina un cliente"""
        return self._delete(f"/clientes/{cliente_id}")
    
    # ==================== INVENTARIO ====================
    
    def get_inventario(self, categoria: Optional[str] = None, 
                       stock_bajo: bool = False, limit: int = 100):
        """Obtiene inventario"""
        params = {"limit": limit}
        if categoria:
            params["categoria"] = categoria
        if stock_bajo:
            params["stock_bajo"] = stock_bajo
        return self._get("/inventario", params)
    
    def create_producto(self, nombre: str, categoria: str, precio: float,
                        stock: int, stock_minimo: int = 5, descripcion: str = None):
        """Agrega producto al inventario"""
        data = {
            "nombre": nombre,
            "categoria": categoria,
            "precio": precio,
            "stock": stock,
            "stock_minimo": stock_minimo,
            "descripcion": descripcion
        }
        return self._post("/inventario", data)
    
    def update_stock(self, producto_id: int, cantidad: int, operacion: str = "set"):
        """Actualiza stock de un producto
        operacion: 'set', 'add', 'subtract'
        """
        params = {"cantidad": cantidad, "operacion": operacion}
        return self._put(f"/inventario/{producto_id}/stock", params)
    
    # ==================== ÓRDENES ====================
    
    def get_ordenes(self, estado: Optional[str] = None, 
                    cliente_id: Optional[int] = None, limit: int = 100):
        """Obtiene órdenes de servicio"""
        params = {"limit": limit}
        if estado:
            params["estado"] = estado
        if cliente_id:
            params["cliente_id"] = cliente_id
        return self._get("/ordenes", params)
    
    def create_orden(self, cliente_id: int, equipo: str, marca: str,
                     modelo: str, problema: str, estado: str = "Pendiente",
                     total: float = 0.0, anticipo: float = 0.0):
        """Crea una orden de servicio"""
        data = {
            "cliente_id": cliente_id,
            "equipo": equipo,
            "marca": marca,
            "modelo": modelo,
            "problema": problema,
            "estado": estado,
            "total": total,
            "anticipo": anticipo
        }
        return self._post("/ordenes", data)
    
    def update_estado_orden(self, orden_id: int, estado: str):
        """Actualiza estado de una orden"""
        params = {"estado": estado}
        return self._put(f"/ordenes/{orden_id}/estado", params)
    
    # ==================== VENTAS ====================
    
    def create_venta(self, total: float, productos: List[Dict], 
                     cliente_id: Optional[int] = None, metodo_pago: str = "Efectivo"):
        """Registra una venta"""
        data = {
            "total": total,
            "productos": productos,
            "cliente_id": cliente_id,
            "metodo_pago": metodo_pago
        }
        return self._post("/ventas", data)
    
    # ==================== ESTADÍSTICAS ====================
    
    def get_dashboard_stats(self):
        """Obtiene estadísticas del dashboard"""
        return self._get("/stats/dashboard")
    
    # ==================== WEBSOCKET - TIEMPO REAL ====================
    
    def connect_realtime(self, on_message_callback):
        """Conecta al WebSocket para actualizaciones en tiempo real"""
        ws_url = self.base_url.replace("http://", "ws://").replace("https://", "wss://")
        
        def on_message(ws, message):
            try:
                data = json.loads(message)
                event = data.get("event")
                
                # Ejecutar callback si está registrado
                if event in self.callbacks:
                    self.callbacks[event](data.get("data"))
                
                # Callback general
                if on_message_callback:
                    on_message_callback(data)
                    
            except Exception as e:
                logger.error(f"Error procesando mensaje WebSocket: {e}")
        
        def on_error(ws, error):
            logger.error(f"WebSocket error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            logger.info("WebSocket cerrado")
        
        def on_open(ws):
            logger.info("WebSocket conectado")
            # Keep-alive ping cada 30 segundos
            def ping():
                while True:
                    try:
                        ws.send("ping")
                        threading.Event().wait(30)
                    except:
                        break
            threading.Thread(target=ping, daemon=True).start()
        
        self.ws = websocket.WebSocketApp(
            f"{ws_url}/ws",
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )
        
        # Ejecutar en thread separado
        self.ws_thread = threading.Thread(target=self.ws.run_forever, daemon=True)
        self.ws_thread.start()
    
    def register_callback(self, event: str, callback):
        """Registra callback para un evento específico
        Eventos: cliente_creado, cliente_actualizado, orden_creada, stock_actualizado, etc.
        """
        self.callbacks[event] = callback
    
    def disconnect_realtime(self):
        """Desconecta del WebSocket"""
        if self.ws:
            self.ws.close()
    
    # ==================== HEALTH CHECK ====================
    
    def is_online(self) -> bool:
        """Verifica si el servidor está disponible"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=2)
            return response.status_code == 200
        except:
            return False


# ==================== EJEMPLO DE USO ====================

if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Crear cliente
    client = ServitecAPIClient("http://localhost:8000")
    
    # Verificar conexión
    if client.is_online():
        print("✓ Conectado al servidor")
        
        # Obtener clientes
        clientes = client.get_clientes(limit=10)
        print(f"\nClientes: {len(clientes)}")
        for c in clientes[:3]:
            print(f"  - {c['nombre']}")
        
        # Obtener estadísticas
        stats = client.get_dashboard_stats()
        print(f"\nEstadísticas:")
        print(f"  Clientes: {stats['clientes']}")
        print(f"  Órdenes pendientes: {stats['ordenes_pendientes']}")
        print(f"  Ventas hoy: ${stats['ventas_hoy']}")
        
        # Conectar WebSocket para tiempo real
        def on_update(data):
            print(f"\n🔔 Actualización: {data['event']}")
            print(f"   Datos: {data['data']}")
        
        client.connect_realtime(on_update)
        print("\n✓ WebSocket conectado (escuchando actualizaciones...)")
        
        # Mantener vivo
        import time
        time.sleep(60)
        
    else:
        print("✗ No se pudo conectar al servidor")
        print("  Asegúrate de que el servidor esté corriendo:")
        print("  python servitec_manager/api_server.py")

import customtkinter as ctk
from tkinter import messagebox
from .theme import Theme
from datetime import datetime


class PedidosFrame(ctk.CTkFrame):
    """
    Módulo para gestión de pedidos a proveedores.
    Permite crear, visualizar y administrar solicitudes de productos/repuestos.
    """
    def __init__(self, parent, logic, current_user):
        super().__init__(parent, fg_color=Theme.BACKGROUND)
        self.logic = logic
        self.current_user = current_user
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=Theme.PADDING_LARGE, padx=Theme.PADDING_LARGE)
        ctk.CTkLabel(
            header, 
            text="📦 GESTIÓN DE PEDIDOS A PROVEEDORES", 
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H1, "bold"), 
            text_color=Theme.PRIMARY
        ).pack()
        
        ctk.CTkFrame(self, height=2, fg_color=Theme.DIVIDER).pack(fill="x", pady=(0, Theme.PADDING_MEDIUM))
        
        # Tabs
        self.tabview = ctk.CTkTabview(
            self,
            fg_color=Theme.SURFACE,
            segmented_button_fg_color=Theme.BACKGROUND_LIGHT,
            segmented_button_selected_color=Theme.PRIMARY,
            text_color=Theme.TEXT_PRIMARY,
            corner_radius=Theme.RADIUS_LARGE,
            border_width=2,
            border_color=Theme.BORDER
        )
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_pendientes = self.tabview.add("PENDIENTES")
        self.tab_historial = self.tabview.add("HISTORIAL")
        self.tab_por_proveedor = self.tabview.add("POR PROVEEDOR")
        
        # Configurar comando para actualizar al cambiar de tab
        self.tabview.configure(command=self.on_tab_change)
        
        self.setup_tab_pendientes()
        self.setup_tab_historial()
        self.setup_tab_por_proveedor()
        
        # Cargar datos inicial
        self.refresh()
    
    def setup_tab_pendientes(self):
        """Tab de pedidos pendientes"""
        # Toolbar
        toolbar = ctk.CTkFrame(self.tab_pendientes, **Theme.get_card_style())
        toolbar.pack(fill="x", pady=Theme.PADDING_MEDIUM, padx=Theme.PADDING_MEDIUM)
        
        ctk.CTkLabel(
            toolbar, 
            text="📋 PEDIDOS PENDIENTES", 
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold"), 
            text_color=Theme.TEXT_PRIMARY
        ).pack(side="left", padx=15, pady=10)
        
        ctk.CTkButton(
            toolbar, 
            text="🔄 ACTUALIZAR", 
            command=self.refresh, 
            **Theme.get_button_style("secondary"),
            width=45,
            height=35
        ).pack(side="right", padx=5, pady=5)
        
        ctk.CTkButton(
            toolbar,
            text="➕ NUEVO PEDIDO",
            command=self.crear_pedido_manual,
            **Theme.get_button_style("success"),
            height=35
        ).pack(side="right", padx=5, pady=5)
        
        # Lista scrollable
        self.scroll_pendientes = ctk.CTkScrollableFrame(self.tab_pendientes, fg_color="transparent")
        self.scroll_pendientes.pack(fill="both", expand=True, padx=Theme.PADDING_MEDIUM, pady=Theme.PADDING_SMALL)
    
    def setup_tab_historial(self):
        """Tab de historial completo"""
        toolbar = ctk.CTkFrame(self.tab_historial, **Theme.get_card_style())
        toolbar.pack(fill="x", pady=Theme.PADDING_MEDIUM, padx=Theme.PADDING_MEDIUM)
        
        ctk.CTkLabel(
            toolbar,
            text="📚 HISTORIAL COMPLETO",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold"),
            text_color=Theme.TEXT_PRIMARY
        ).pack(side="left", padx=15, pady=10)
        
        # Filtro de estado
        self.filtro_estado = ctk.StringVar(value="TODOS")
        ctk.CTkComboBox(
            toolbar,
            variable=self.filtro_estado,
            values=["TODOS", "PENDIENTE", "PEDIDO", "RECIBIDO", "CANCELADO"],
            command=lambda _: self.cargar_historial(),
            width=150,
            height=35
        ).pack(side="right", padx=10, pady=5)
        
        ctk.CTkLabel(toolbar, text="Filtrar:", text_color=Theme.TEXT_SECONDARY).pack(side="right", padx=5)
        
        self.scroll_historial = ctk.CTkScrollableFrame(self.tab_historial, fg_color="transparent")
        self.scroll_historial.pack(fill="both", expand=True, padx=Theme.PADDING_MEDIUM, pady=Theme.PADDING_SMALL)
    
    def setup_tab_por_proveedor(self):
        """Tab organizado por proveedor"""
        toolbar = ctk.CTkFrame(self.tab_por_proveedor, **Theme.get_card_style())
        toolbar.pack(fill="x", pady=Theme.PADDING_MEDIUM, padx=Theme.PADDING_MEDIUM)
        
        ctk.CTkLabel(
            toolbar,
            text="🏭 PEDIDOS POR PROVEEDOR",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold"),
            text_color=Theme.TEXT_PRIMARY
        ).pack(side="left", padx=15, pady=10)
        
        # Selector de proveedor
        proveedores = self.logic.proveedores.OBTENER_TODOS_PROVEEDORES()
        self.proveedor_nombres = {p['id']: p['nombre'] for p in proveedores}
        proveedor_values = ["TODOS"] + list(self.proveedor_nombres.values())
        
        self.filtro_proveedor = ctk.StringVar(value="TODOS")
        ctk.CTkComboBox(
            toolbar,
            variable=self.filtro_proveedor,
            values=proveedor_values,
            command=lambda _: self.cargar_por_proveedor(),
            width=200,
            height=35
        ).pack(side="right", padx=10, pady=5)
        
        ctk.CTkLabel(toolbar, text="Proveedor:", text_color=Theme.TEXT_SECONDARY).pack(side="right", padx=5)
        
        self.scroll_proveedor = ctk.CTkScrollableFrame(self.tab_por_proveedor, fg_color="transparent")
        self.scroll_proveedor.pack(fill="both", expand=True, padx=Theme.PADDING_MEDIUM, pady=Theme.PADDING_SMALL)
    
    def on_tab_change(self):
        """Callback cuando cambia de tab - actualiza datos automáticamente"""
        self.refresh()
    
    def refresh(self):
        """Refresca todos los datos"""
        tab_actual = self.tabview.get()
        if tab_actual == "PENDIENTES":
            self.cargar_pendientes()
        elif tab_actual == "HISTORIAL":
            self.cargar_historial()
        elif tab_actual == "POR PROVEEDOR":
            self.cargar_por_proveedor()
    
    def cargar_pendientes(self):
        """Carga pedidos pendientes"""
        # Limpiar
        for widget in self.scroll_pendientes.winfo_children():
            widget.destroy()
        
        pedidos_raw = self.logic.pedidos.OBTENER_PEDIDOS_PENDIENTES()
        
        if not pedidos_raw:
            ctk.CTkLabel(
                self.scroll_pendientes,
                text="✅ No hay pedidos pendientes",
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
                text_color=Theme.TEXT_SECONDARY
            ).pack(pady=50)
            return
        
        # Convertir tuplas a diccionarios
        pedidos = []
        for p in pedidos_raw:
            pedido = {
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
                'orden_equipo': p[15] if len(p) > 15 else None
            }
            pedidos.append(pedido)
        
        # Header
        header = ctk.CTkFrame(self.scroll_pendientes, fg_color=Theme.PRIMARY, corner_radius=Theme.RADIUS_SMALL)
        header.pack(fill="x", pady=(0, 5))
        
        self.make_cell(header, "ÍTEM", 200, Theme.WHITE, True)
        self.make_cell(header, "TIPO", 80, Theme.WHITE, True)
        self.make_cell(header, "PROVEEDOR", 150, Theme.WHITE, True)
        self.make_cell(header, "CANT.", 50, Theme.WHITE, True)
        self.make_cell(header, "FECHA", 100, Theme.WHITE, True)
        self.make_cell(header, "ORDEN", 80, Theme.WHITE, True)
        
        # Rows
        for p in pedidos:
            self.render_pedido_row(self.scroll_pendientes, p, es_pendiente=True)
    
    def cargar_historial(self):
        """Carga historial completo"""
        for widget in self.scroll_historial.winfo_children():
            widget.destroy()
        
        # Obtener todos los pedidos
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
            ORDER BY p.fecha_solicitud DESC
        """
        
        todos_pedidos_raw = self.logic.bd.OBTENER_TODOS(query)
        
        # Convertir tuplas a diccionarios
        todos_pedidos = []
        for p in todos_pedidos_raw:
            pedido = {
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
                'tipo_item': p[14]
            }
            todos_pedidos.append(pedido)
        
        # Filtrar por estado
        estado_filtro = self.filtro_estado.get()
        if estado_filtro != "TODOS":
            pedidos = [p for p in todos_pedidos if p['estado'] == estado_filtro]
        else:
            pedidos = todos_pedidos
        
        if not pedidos:
            ctk.CTkLabel(
                self.scroll_historial,
                text=f"📭 No hay pedidos con estado: {estado_filtro}",
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
                text_color=Theme.TEXT_SECONDARY
            ).pack(pady=50)
            return
        
        # Header
        header = ctk.CTkFrame(self.scroll_historial, fg_color=Theme.PRIMARY, corner_radius=Theme.RADIUS_SMALL)
        header.pack(fill="x", pady=(0, 5))
        
        self.make_cell(header, "ÍTEM", 180, Theme.WHITE, True)
        self.make_cell(header, "PROVEEDOR", 130, Theme.WHITE, True)
        self.make_cell(header, "CANT.", 50, Theme.WHITE, True)
        self.make_cell(header, "ESTADO", 90, Theme.WHITE, True)
        self.make_cell(header, "FECHA", 100, Theme.WHITE, True)
        
        # Rows
        for p in pedidos:
            self.render_pedido_row(self.scroll_historial, p, es_pendiente=False)
    
    def cargar_por_proveedor(self):
        """Carga pedidos filtrados por proveedor"""
        for widget in self.scroll_proveedor.winfo_children():
            widget.destroy()
        
        proveedor_nombre = self.filtro_proveedor.get()
        
        if proveedor_nombre == "TODOS":
            # Agrupar por proveedor
            proveedores = self.logic.proveedores.OBTENER_TODOS_PROVEEDORES()
            for prov in proveedores:
                pedidos = self.logic.pedidos.OBTENER_PEDIDOS_POR_PROVEEDOR(prov['id'], solo_pendientes=False)
                if pedidos:
                    self.render_grupo_proveedor(prov, pedidos)
        else:
            # Buscar ID del proveedor
            proveedor_id = None
            for pid, pname in self.proveedor_nombres.items():
                if pname == proveedor_nombre:
                    proveedor_id = pid
                    break
            
            if proveedor_id:
                pedidos = self.logic.pedidos.OBTENER_PEDIDOS_POR_PROVEEDOR(proveedor_id, solo_pendientes=False)
                if pedidos:
                    proveedor = self.logic.proveedores.OBTENER_PROVEEDOR(proveedor_id)
                    self.render_grupo_proveedor(proveedor, pedidos)
                else:
                    ctk.CTkLabel(
                        self.scroll_proveedor,
                        text=f"📭 No hay pedidos para: {proveedor_nombre}",
                        font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
                        text_color=Theme.TEXT_SECONDARY
                    ).pack(pady=50)
    
    def render_grupo_proveedor(self, proveedor, pedidos):
        """Renderiza un grupo de pedidos por proveedor"""
        # Card del proveedor
        card = ctk.CTkFrame(self.scroll_proveedor, **Theme.get_card_style())
        card.pack(fill="x", pady=10, padx=5)
        
        # Header del proveedor
        prov_header = ctk.CTkFrame(card, fg_color=Theme.ACCENT, corner_radius=Theme.RADIUS_SMALL)
        prov_header.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            prov_header,
            text=f"🏭 {proveedor['nombre']}",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold"),
            text_color=Theme.WHITE
        ).pack(side="left", padx=15, pady=10)
        
        # Contador de pedidos
        pendientes = sum(1 for p in pedidos if p['estado'] == 'PENDIENTE')
        pedido_estado = sum(1 for p in pedidos if p['estado'] == 'PEDIDO')
        ctk.CTkLabel(
            prov_header,
            text=f"{len(pedidos)} pedidos ({pendientes} pendientes, {pedido_estado} en camino)",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
            text_color=Theme.WHITE
        ).pack(side="left", padx=15, pady=10)
        
        # Botón RECIBIR MERCANCIA (solo si hay pedidos en estado PEDIDO)
        if pedido_estado > 0:
            ctk.CTkButton(
                prov_header,
                text="📦 RECIBIR MERCANCIA",
                **Theme.get_button_style("success"),
                command=lambda pid=proveedor['id']: self.recibir_mercancia(pid)
            ).pack(side="right", padx=5, pady=5)
        
        # Botón GENERAR ORDEN DE COMPRA
        ctk.CTkButton(
            prov_header,
            text="📄 GENERAR ORDEN DE COMPRA",
            **Theme.get_button_style("success"),
            command=lambda pid=proveedor['id']: self.generar_orden_compra(pid)
        ).pack(side="right", padx=15, pady=5)
        
        # Lista de pedidos
        for pedido in pedidos:
            self.render_pedido_mini(card, pedido)
    
    def render_pedido_mini(self, parent, pedido):
        """Renderiza una fila mini de pedido"""
        row = ctk.CTkFrame(parent, fg_color=Theme.BACKGROUND_LIGHT, corner_radius=Theme.RADIUS_SMALL)
        row.pack(fill="x", padx=10, pady=3)
        
        # Info principal
        info_frame = ctk.CTkFrame(row, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=10, pady=8)
        
        ctk.CTkLabel(
            info_frame,
            text=f"• {pedido.get('item_nombre', 'N/A')}",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w"
        ).pack(side="left", padx=5)
        
        ctk.CTkLabel(
            info_frame,
            text=f"Cant: {pedido['cantidad']}",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL),
            text_color=Theme.TEXT_SECONDARY
        ).pack(side="left", padx=15)
        
        # Estado
        color_estado = {
            'PENDIENTE': Theme.WARNING,
            'PEDIDO': Theme.ACCENT,
            'RECIBIDO': Theme.SUCCESS,
            'CANCELADO': Theme.ERROR
        }.get(pedido['estado'], Theme.TEXT_SECONDARY)
        
        ctk.CTkLabel(
            row,
            text=pedido['estado'],
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"),
            text_color=color_estado
        ).pack(side="right", padx=10)
    
    def render_pedido_row(self, parent, pedido, es_pendiente=True):
        """Renderiza una fila de pedido completa"""
        row = ctk.CTkFrame(parent, fg_color=Theme.SURFACE, corner_radius=Theme.RADIUS_SMALL)
        row.pack(fill="x", pady=2)
        
        if es_pendiente:
            self.make_cell(row, pedido.get('item_nombre', 'N/A'), 200)
            self.make_cell(row, pedido.get('tipo_item', '-'), 80, Theme.ACCENT)
            self.make_cell(row, pedido.get('proveedor_nombre', 'N/A'), 150)
            self.make_cell(row, str(pedido['cantidad']), 50, Theme.PRIMARY, True)
            
            fecha = pedido.get('fecha_solicitud', '')
            if fecha:
                fecha_corta = fecha.split(' ')[0] if ' ' in fecha else fecha
            else:
                fecha_corta = '-'
            self.make_cell(row, fecha_corta, 100)
            
            orden = pedido.get('orden_equipo', '-') if pedido.get('orden_id') else '-'
            self.make_cell(row, orden, 80, Theme.TEXT_SECONDARY)
            
            # Botones
            # Desactivar botón PEDIDO si ya fue marcado como PEDIDO
            estado_actual = pedido.get('estado', '')
            btn_pedido = ctk.CTkButton(
                row, text="✓ PEDIDO", width=80,
                **Theme.get_button_style("accent"),
                command=lambda p=pedido: self.marcar_como_pedido(p['id']),
                state="disabled" if estado_actual == 'PEDIDO' else "normal"
            )
            btn_pedido.pack(side="right", padx=2, pady=3)
            
            ctk.CTkButton(
                row, text="✓ RECIBIDO", width=80,
                **Theme.get_button_style("success"),
                command=lambda p=pedido: self.marcar_como_recibido(p['id'])
            ).pack(side="right", padx=2, pady=3)
            
            ctk.CTkButton(
                row, text="✕", width=40,
                **Theme.get_button_style("error"),
                command=lambda p=pedido: self.cancelar_pedido(p['id'])
            ).pack(side="right", padx=2, pady=3)
        else:
            self.make_cell(row, pedido.get('item_nombre', 'N/A'), 180)
            self.make_cell(row, pedido.get('proveedor_nombre', 'N/A'), 130)
            self.make_cell(row, str(pedido['cantidad']), 50, Theme.PRIMARY, True)
            
            # Color según estado
            color_estado = {
                'PENDIENTE': Theme.WARNING,
                'PEDIDO': Theme.ACCENT,
                'RECIBIDO': Theme.SUCCESS,
                'CANCELADO': Theme.ERROR
            }.get(pedido['estado'], Theme.TEXT_SECONDARY)
            
            self.make_cell(row, pedido['estado'], 90, color_estado, True)
            
            fecha = pedido.get('fecha_solicitud', '')
            if fecha:
                fecha_corta = fecha.split(' ')[0] if ' ' in fecha else fecha
            else:
                fecha_corta = '-'
            self.make_cell(row, fecha_corta, 100)
            
            # Botón detalles
            ctk.CTkButton(
                row, text="👁", width=40,
                **Theme.get_button_style("secondary"),
                command=lambda p=pedido: self.ver_detalles(p['id'])
            ).pack(side="right", padx=2, pady=3)
    
    def make_cell(self, parent, text, width, color=None, bold=False):
        """Helper para crear celdas"""
        font_style = (Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold" if bold else "normal")
        color = color or Theme.TEXT_PRIMARY
        
        ctk.CTkLabel(
            parent,
            text=str(text),
            width=width,
            font=font_style,
            text_color=color,
            anchor="center"
        ).pack(side="left", padx=2, pady=5)
    
    def marcar_como_pedido(self, pedido_id):
        """Marca un pedido como PEDIDO (ya solicitado al proveedor) y actualiza la orden a ESPERA"""
        if messagebox.askyesno("Confirmar", "¿Marcar como PEDIDO (ya solicitado al proveedor)?\n\nLa orden de servicio asociada pasará a estado ESPERA DE REPUESTO."):
            # Obtener información del pedido
            pedido = self.logic.pedidos.OBTENER_PEDIDO(pedido_id)
            if not pedido:
                messagebox.showerror("Error", "No se encontró el pedido")
                return
            
            # Marcar como pedido
            if self.logic.pedidos.MARCAR_COMO_PEDIDO(pedido_id):
                # Actualizar estado de la orden a ESPERA DE REPUESTO si existe orden_id
                if pedido.get('orden_id'):
                    try:
                        self.logic.bd.EJECUTAR_CONSULTA(
                            "UPDATE ordenes SET estado = 'ESPERA DE REPUESTO' WHERE id = ?",
                            (pedido['orden_id'],)
                        )
                        messagebox.showinfo("Éxito", "Pedido marcado como PEDIDO\nOrden actualizada a ESPERA DE REPUESTO")
                    except Exception as e:
                        messagebox.showwarning("Advertencia", f"Pedido marcado pero no se pudo actualizar la orden: {e}")
                else:
                    messagebox.showinfo("Éxito", "Pedido marcado como PEDIDO")
                self.refresh()
            else:
                messagebox.showerror("Error", "No se pudo actualizar el estado")
    
    def marcar_como_recibido(self, pedido_id):
        """Marca un pedido como RECIBIDO y actualiza stock"""
        if messagebox.askyesno("Confirmar", "¿Marcar como RECIBIDO? (Actualizará el stock)"):
            if self.logic.pedidos.MARCAR_COMO_RECIBIDO(pedido_id, actualizar_stock=True):
                messagebox.showinfo("Éxito", "Pedido marcado como RECIBIDO y stock actualizado")
                self.refresh()
            else:
                messagebox.showerror("Error", "No se pudo actualizar el estado")
    
    def cancelar_pedido(self, pedido_id):
        """Cancela un pedido solicitando una razón"""
        from tkinter import simpledialog
        
        # Solicitar razón de cancelación
        razon = simpledialog.askstring(
            "Razón de Cancelación",
            "Por favor ingrese la razón de la cancelación:",
            parent=self
        )
        
        if not razon or razon.strip() == "":
            messagebox.showwarning("Cancelación Abortada", "Debe ingresar una razón para cancelar el pedido")
            return
        
        # Confirmar cancelación
        if messagebox.askyesno("Confirmar", f"¿Cancelar este pedido?\n\nRazón: {razon}"):
            # Actualizar notas con la razón de cancelación
            pedido = self.logic.pedidos.OBTENER_PEDIDO(pedido_id)
            if pedido:
                notas_actualizadas = f"{pedido.get('notas', '')}\n\n[CANCELADO] Razón: {razon}"
                self.logic.bd.EJECUTAR_CONSULTA(
                    "UPDATE pedidos SET notas = ? WHERE id = ?",
                    (notas_actualizadas, pedido_id)
                )
            
            if self.logic.pedidos.CANCELAR_PEDIDO(pedido_id):
                messagebox.showinfo("Éxito", "Pedido cancelado")
                self.refresh()
            else:
                messagebox.showerror("Error", "No se pudo cancelar el pedido")
    
    def ver_detalles(self, pedido_id):
        """Muestra detalles completos de un pedido"""
        pedido = self.logic.pedidos.OBTENER_PEDIDO(pedido_id)
        if not pedido:
            messagebox.showerror("Error", "No se encontró el pedido")
            return
        
        # Ventana de detalles
        win = ctk.CTkToplevel(self)
        win.title("Detalles del Pedido")
        win.geometry("500x600")
        win.attributes("-topmost", True)
        win.configure(fg_color=Theme.BACKGROUND)
        
    def generar_orden_compra(self, proveedor_id):
        """Genera orden de compra en PDF para un proveedor con opción de agregar items adicionales"""
        import os
        import subprocess
        
        # Primero preguntar si desea agregar items adicionales
        agregar_items = messagebox.askyesno(
            "Orden de Compra",
            "¿Desea agregar productos o repuestos adicionales a esta orden de compra antes de generarla?"
        )
        
        if agregar_items:
            self.agregar_items_a_orden(proveedor_id)
            return
        
        # Si no desea agregar, proceder con la generación
        if messagebox.askyesno(
            "Generar Orden de Compra", 
            "¿Generar orden de compra en PDF?\n\n⚠️ Se incluirán todos los pedidos PENDIENTES del proveedor seleccionado.\n\n✓ Los pedidos se marcarán automáticamente como PEDIDO."
        ):
            try:
                # Obtener pedidos pendientes antes de generar PDF
                pedidos_pendientes = self.logic.pedidos.OBTENER_PEDIDOS_POR_PROVEEDOR(proveedor_id, solo_pendientes=True)
                ids_pedidos_pendientes = [p[0] for p in pedidos_pendientes if p[6] == 'PENDIENTE']  # p[6] es estado
                
                # Generar PDF
                filepath = self.logic.pedidos.GENERAR_ORDEN_COMPRA(proveedor_id, solo_pendientes=True)
                
                if filepath:
                    # Marcar todos los pedidos PENDIENTES como PEDIDO
                    for pedido_id in ids_pedidos_pendientes:
                        # Obtener información del pedido para actualizar orden
                        pedido_info = self.logic.pedidos.OBTENER_PEDIDO(pedido_id)
                        
                        # Marcar como PEDIDO
                        self.logic.pedidos.MARCAR_COMO_PEDIDO(pedido_id)
                        
                        # Actualizar estado de la orden asociada si existe
                        if pedido_info and pedido_info.get('orden_id'):
                            try:
                                self.logic.bd.EJECUTAR_CONSULTA(
                                    "UPDATE ordenes SET estado = 'ESPERA DE REPUESTO' WHERE id = ?",
                                    (pedido_info['orden_id'],)
                                )
                            except Exception as e:
                                print(f"Error actualizando orden {pedido_info['orden_id']}: {e}")
                    
                    # Refrescar vista
                    self.refresh()
                    
                    # Preguntar si desea enviar por WhatsApp o Email
                    if self.logic.mensajeria:
                        enviar_msg = messagebox.askyesno(
                            "Enviar Orden de Compra",
                            f"Orden generada exitosamente.\n\n¿Desea enviar la orden al proveedor?\n\nSeleccione SÍ para elegir método de envío."
                        )
                        
                        if enviar_msg:
                            self.mostrar_opciones_envio(proveedor_id, filepath)
                    else:
                        messagebox.showinfo("Éxito", f"Orden de compra generada:\n{filepath}\n\n✓ {len(ids_pedidos_pendientes)} pedidos marcados como PEDIDO")
                    
                    # Abrir PDF automáticamente
                    if os.path.exists(filepath):
                        try:
                            os.startfile(filepath)  # Windows
                        except AttributeError:
                            try:
                                subprocess.call(['open', filepath])  # macOS
                            except:
                                subprocess.call(['xdg-open', filepath])  # Linux
                else:
                    messagebox.showwarning("Sin Pedidos", "No hay pedidos PENDIENTES para este proveedor")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo generar la orden de compra:\n{e}")
        
    def mostrar_opciones_envio(self, proveedor_id, pdf_path):
        """Muestra ventana con opciones para enviar orden de compra"""
        win = ctk.CTkToplevel(self)
        win.title("📤 Enviar Orden de Compra")
        win.geometry("500x400")
        win.attributes("-topmost", True)
        win.configure(fg_color=Theme.BACKGROUND)
        win.grab_set()
        
        # Centrar ventana
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (500 // 2)
        y = (win.winfo_screenheight() // 2) - (400 // 2)
        win.geometry(f"500x400+{x}+{y}")
        
        # Header
        header = ctk.CTkFrame(win, fg_color=Theme.PRIMARY, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(
            header,
            text="📤 ENVIAR ORDEN DE COMPRA",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"),
            text_color=Theme.WHITE
        ).pack(pady=20)
        
        # Contenido
        content = ctk.CTkFrame(win, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=20)
        
        ctk.CTkLabel(
            content,
            text="Seleccione el método de envío:",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
            text_color=Theme.TEXT_PRIMARY
        ).pack(pady=(0, 20))
        
        # Botón WhatsApp
        def enviar_whatsapp():
            if not self.logic.mensajeria:
                messagebox.showerror("Error", "Módulo de mensajería no disponible")
                return
            
            try:
                exito, mensaje = self.logic.mensajeria.ENVIAR_ORDEN_COMPRA_WHATSAPP(proveedor_id, pdf_path)
                if exito:
                    messagebox.showinfo("WhatsApp", f"✓ {mensaje}\n\nSe abrirá WhatsApp Web en unos segundos.")
                    win.destroy()
                else:
                    messagebox.showerror("Error", f"No se pudo enviar por WhatsApp:\n{mensaje}")
            except Exception as e:
                messagebox.showerror("Error", f"Error enviando WhatsApp:\n{e}")
        
        ctk.CTkButton(
            content,
            text="📱 ENVIAR POR WHATSAPP",
            **Theme.get_button_style("success"),
            command=enviar_whatsapp,
            height=50
        ).pack(fill="x", pady=5)
        
        # Botón Email
        def enviar_email():
            if not self.logic.mensajeria:
                messagebox.showerror("Error", "Módulo de mensajería no disponible")
                return
            
            if not self.logic.mensajeria.ESTA_CONFIGURADO_EMAIL():
                messagebox.showwarning(
                    "Email No Configurado",
                    "Por favor configure las credenciales de email en el archivo .env\n\n" +
                    "Consulte .env.example para más información."
                )
                return
            
            try:
                exito, mensaje = self.logic.mensajeria.ENVIAR_ORDEN_COMPRA_EMAIL(proveedor_id, pdf_path)
                if exito:
                    messagebox.showinfo("Email", "✓ Email enviado correctamente")
                    win.destroy()
                else:
                    messagebox.showerror("Error", f"No se pudo enviar email:\n{mensaje}")
            except Exception as e:
                messagebox.showerror("Error", f"Error enviando email:\n{e}")
        
        ctk.CTkButton(
            content,
            text="📧 ENVIAR POR EMAIL",
            **Theme.get_button_style("accent"),
            command=enviar_email,
            height=50
        ).pack(fill="x", pady=5)
        
        # Botón Cancelar
        ctk.CTkButton(
            content,
            text="✕ CANCELAR",
            **Theme.get_button_style("secondary"),
            command=win.destroy,
            height=40
        ).pack(fill="x", pady=(15, 0))
    
    def recibir_mercancia(self, proveedor_id):
        """Muestra ventana para recibir mercancía de pedidos en estado PEDIDO"""
        # Obtener pedidos en estado PEDIDO del proveedor
        pedidos_raw = self.logic.pedidos.OBTENER_PEDIDOS_POR_PROVEEDOR(proveedor_id, solo_pendientes=False)
        pedidos_pedido = [p for p in pedidos_raw if p[6] == 'PEDIDO']  # p[6] es estado
        
        if not pedidos_pedido:
            messagebox.showinfo("Sin Pedidos", "No hay pedidos en estado PEDIDO para recibir")
            return
        
        # Convertir a diccionarios
        pedidos = []
        for p in pedidos_pedido:
            pedidos.append({
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
                'orden_equipo': p[15] if len(p) > 15 else None
            })
        
        # Crear ventana modal
        win = ctk.CTkToplevel(self)
        win.title("📦 Recepción de Mercancía")
        win.geometry("700x600")
        win.attributes("-topmost", True)
        win.configure(fg_color=Theme.BACKGROUND)
        win.grab_set()
        
        # Header
        header = ctk.CTkFrame(win, fg_color=Theme.PRIMARY, corner_radius=Theme.RADIUS_SMALL)
        header.pack(fill="x", padx=20, pady=20)
        
        proveedor = self.logic.proveedores.OBTENER_PROVEEDOR(proveedor_id)
        ctk.CTkLabel(
            header,
            text=f"📦 RECEPCIÓN DE MERCANCÍA - {proveedor['nombre']}",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"),
            text_color=Theme.WHITE
        ).pack(pady=15)
        
        # Instrucciones
        ctk.CTkLabel(
            win,
            text="Seleccione los items recibidos. Se actualizará el stock automáticamente.",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
            text_color=Theme.TEXT_SECONDARY
        ).pack(pady=10)
        
        # Scroll para lista de pedidos
        scroll_frame = ctk.CTkScrollableFrame(
            win,
            fg_color=Theme.SURFACE,
            corner_radius=Theme.RADIUS_MEDIUM
        )
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Checkboxes para cada pedido
        check_vars = {}
        for pedido in pedidos:
            item_frame = ctk.CTkFrame(scroll_frame, fg_color=Theme.BACKGROUND_LIGHT, corner_radius=Theme.RADIUS_SMALL)
            item_frame.pack(fill="x", pady=5, padx=10)
            
            # Checkbox
            var = ctk.BooleanVar(value=True)  # Seleccionado por defecto
            check_vars[pedido['id']] = var
            
            check = ctk.CTkCheckBox(
                item_frame,
                text="",
                variable=var,
                **Theme.get_button_style("primary")
            )
            check.pack(side="left", padx=10, pady=10)
            
            # Info del pedido
            info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True, padx=10, pady=10)
            
            ctk.CTkLabel(
                info_frame,
                text=f"• {pedido['item_nombre']}",
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
                text_color=Theme.TEXT_PRIMARY,
                anchor="w"
            ).pack(anchor="w")
            
            ctk.CTkLabel(
                info_frame,
                text=f"Cantidad: {pedido['cantidad']} | Tipo: {pedido['tipo_item']} | Pedido: {pedido.get('fecha_pedido', 'N/A')[:10] if pedido.get('fecha_pedido') else 'N/A'}",
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL),
                text_color=Theme.TEXT_SECONDARY,
                anchor="w"
            ).pack(anchor="w")
        
        # Campo de notas
        notas_frame = ctk.CTkFrame(win, **Theme.get_card_style())
        notas_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            notas_frame,
            text="📝 Notas de Recepción (opcional):",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w"
        ).pack(fill="x", padx=15, pady=(10, 5))
        
        notas_text = ctk.CTkTextbox(
            notas_frame,
            height=80,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
            fg_color=Theme.BACKGROUND,
            border_width=1,
            border_color=Theme.BORDER
        )
        notas_text.pack(fill="x", padx=15, pady=(0, 10))
        notas_text.insert("1.0", "Ej: Items recibidos en buen estado / Faltante de 2 unidades / etc.")
        
        # Footer con botones
        footer = ctk.CTkFrame(win, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=20)
        
        def confirmar_recepcion():
            # Obtener IDs de pedidos seleccionados
            ids_seleccionados = [pid for pid, var in check_vars.items() if var.get()]
            
            if not ids_seleccionados:
                messagebox.showwarning("Sin Selección", "Debe seleccionar al menos un item para recibir")
                return
            
            if messagebox.askyesno(
                "Confirmar Recepción",
                f"¿Confirmar recepción de {len(ids_seleccionados)} items?\n\n✓ Se actualizará el stock automáticamente\n✓ Los pedidos se marcarán como RECIBIDOS\n✓ Se registrará la compra al proveedor"
            ):
                try:
                    # Preparar items para registrar compra
                    items_compra = []
                    total_compra = 0
                    
                    for pedido_id in ids_seleccionados:
                        # Buscar el pedido en la lista
                        pedido = next((p for p in pedidos if p['id'] == pedido_id), None)
                        if pedido:
                            # Obtener costo del item
                            if pedido['producto_id']:
                                item_db = self.logic.bd.OBTENER_UNO("SELECT costo FROM inventario WHERE id = ?", (pedido['producto_id'],))
                                costo = item_db[0] if item_db else 0
                            elif pedido['repuesto_id']:
                                item_db = self.logic.bd.OBTENER_UNO("SELECT costo FROM repuestos WHERE id = ?", (pedido['repuesto_id'],))
                                costo = item_db[0] if item_db else 0
                            else:
                                costo = 0
                            
                            subtotal = costo * pedido['cantidad']
                            total_compra += subtotal
                            
                            # Agregar a lista de items
                            items_compra.append({
                                'descripcion': f"{pedido['item_nombre']} ({pedido['tipo_item']})",
                                'cantidad': pedido['cantidad'],
                                'precio_unitario': costo,
                                'subtotal': subtotal
                            })
                    
                    # Recibir lote de pedidos
                    exitosos, errores = self.logic.pedidos.RECIBIR_LOTE_PEDIDOS(ids_seleccionados, actualizar_stock=True)
                    
                    if exitosos > 0:
                        # Registrar compra al proveedor
                        try:
                            from datetime import datetime
                            num_doc = f"PEDIDO-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                            
                            # Obtener notas del TextBox
                            notas_recepcion = notas_text.get("1.0", "end").strip()
                            if notas_recepcion.startswith("Ej: Items recibidos"):
                                notas_recepcion = ""
                            
                            observacion = f"Recepción de {exitosos} items del pedido"
                            if notas_recepcion:
                                observacion += f" | Notas: {notas_recepcion}"
                            
                            self.logic.proveedores.register_purchase(
                                proveedor_id=proveedor_id,
                                tipo_doc="FACTURA",
                                num_doc=num_doc,
                                items=items_compra,
                                observacion=observacion
                            )
                        except Exception as e:
                            print(f"Error registrando compra al proveedor: {e}")
                        
                        messagebox.showinfo(
                            "Recepción Completada",
                            f"✓ {exitosos} items recibidos correctamente\n✓ Stock actualizado\n✓ Compra registrada al proveedor\n\n{f'⚠ {errores} errores' if errores > 0 else ''}"
                        )
                        win.destroy()
                        self.refresh()
                    else:
                        messagebox.showerror("Error", "No se pudo recibir ningún item")
                except Exception as e:
                    messagebox.showerror("Error", f"Error al recibir mercancía:\n{e}")
        
        ctk.CTkButton(
            footer,
            text="✓ CONFIRMAR RECEPCIÓN",
            **Theme.get_button_style("success"),
            command=confirmar_recepcion,
            width=200,
            height=40
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            footer,
            text="✕ CANCELAR",
            **Theme.get_button_style("error"),
            command=win.destroy,
            width=120,
            height=40
        ).pack(side="right", padx=5)
        
        # Header
        header = ctk.CTkFrame(win, fg_color=Theme.PRIMARY, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(
            header,
            text=f"📋 PEDIDO #{pedido['id']}",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"),
            text_color=Theme.WHITE
        ).pack(pady=20)
        
        # Contenido
        scroll = ctk.CTkScrollableFrame(win, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        datos = [
            ("ÍTEM:", pedido.get('item_nombre', 'N/A')),
            ("TIPO:", pedido.get('tipo_item', 'N/A')),
            ("PROVEEDOR:", pedido.get('proveedor_nombre', 'N/A')),
            ("TELÉFONO:", pedido.get('proveedor_telefono', 'N/A')),
            ("CANTIDAD:", str(pedido['cantidad'])),
            ("ESTADO:", pedido['estado']),
            ("COSTO ESTIMADO:", f"${int(pedido.get('costo_estimado', 0) * pedido['cantidad']):,}".replace(",", ".")),
            ("FECHA SOLICITUD:", pedido.get('fecha_solicitud', '-')),
            ("FECHA PEDIDO:", pedido.get('fecha_pedido') or 'N/A'),
            ("FECHA RECEPCIÓN:", pedido.get('fecha_recepcion') or 'N/A'),
            ("SOLICITADO POR:", pedido.get('usuario_solicita', 'N/A')),
            ("ORDEN ASOCIADA:", pedido.get('orden_equipo') or 'N/A'),
            ("NOTAS:", pedido.get('notas') or 'Sin notas'),
        ]
        
        for label, value in datos:
            frame = ctk.CTkFrame(scroll, **Theme.get_card_style())
            frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(
                frame,
                text=label,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
                text_color=Theme.TEXT_SECONDARY,
                anchor="w"
            ).pack(fill="x", padx=15, pady=(10, 0))
            
            ctk.CTkLabel(
                frame,
                text=value,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
                text_color=Theme.TEXT_PRIMARY,
                anchor="w"
            ).pack(fill="x", padx=15, pady=(0, 10))
        
        # Botón cerrar
        ctk.CTkButton(
            win,
            text="CERRAR",
            command=win.destroy,
            **Theme.get_button_style("secondary"),
            height=45
        ).pack(padx=20, pady=(0, 20), fill="x")
    
    def crear_pedido_manual(self):
        """Formulario para crear un pedido manualmente"""
        win = ctk.CTkToplevel(self)
        win.title("Nuevo Pedido")
        win.geometry("550x750")
        win.attributes("-topmost", True)
        win.configure(fg_color=Theme.BACKGROUND)
        
        # Header
        header = ctk.CTkFrame(win, fg_color=Theme.SUCCESS, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(
            header,
            text="➕ NUEVO PEDIDO A PROVEEDOR",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"),
            text_color=Theme.WHITE
        ).pack(pady=20)
        
        # Form
        container = ctk.CTkScrollableFrame(win, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Tipo de ítem
        tipo_var = ctk.StringVar(value="PRODUCTO")
        self.make_form_field(container, "TIPO DE ÍTEM:", tipo_var, is_combo=True, values=["PRODUCTO", "REPUESTO"])
        
        # Obtener productos y repuestos
        productos = self.logic.inventory.OBTENER_PRODUCTOS()
        repuestos = self.logic.parts.OBTENER_TODOS_REPUESTOS()
        proveedores = self.logic.proveedores.OBTENER_TODOS_PROVEEDORES()
        
        item_var = ctk.StringVar()
        proveedor_var = ctk.StringVar()
        cantidad_var = ctk.StringVar(value="1")
        notas_var = ctk.StringVar()
        
        # Frame para selección de ítem (cambia según tipo)
        item_frame = ctk.CTkFrame(container, **Theme.get_card_style())
        item_frame.pack(fill="x", pady=8)
        
        item_label = ctk.CTkLabel(
            item_frame,
            text="PRODUCTO:",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w"
        )
        item_label.pack(fill="x", padx=15, pady=(10, 5))
        
        producto_nombres = {str(p['id']): p['nombre'] for p in productos}
        repuesto_nombres = {str(r['id']): r['nombre'] for r in repuestos}
        
        item_combo = ctk.CTkComboBox(
            item_frame,
            variable=item_var,
            values=list(producto_nombres.values()),
            height=40,
            border_color=Theme.BORDER,
            button_color=Theme.PRIMARY,
            dropdown_fg_color=Theme.SURFACE
        )
        item_combo.pack(fill="x", padx=15, pady=(0, 10))
        
        def cambiar_tipo(*args):
            if tipo_var.get() == "PRODUCTO":
                item_label.configure(text="PRODUCTO:")
                item_combo.configure(values=list(producto_nombres.values()))
                if producto_nombres:
                    item_var.set(list(producto_nombres.values())[0])
            else:
                item_label.configure(text="REPUESTO:")
                item_combo.configure(values=list(repuesto_nombres.values()))
                if repuesto_nombres:
                    item_var.set(list(repuesto_nombres.values())[0])
        
        tipo_var.trace("w", cambiar_tipo)
        cambiar_tipo()  # Inicializar
        
        # Proveedor
        proveedor_nombres = {str(p['id']): p['nombre'] for p in proveedores}
        self.make_form_field(
            container,
            "PROVEEDOR:",
            proveedor_var,
            is_combo=True,
            values=list(proveedor_nombres.values())
        )
        
        # Cantidad
        self.make_form_field(container, "CANTIDAD:", cantidad_var)
        
        # Notas
        self.make_form_field(container, "NOTAS:", notas_var)
        
        def guardar():
            try:
                tipo = tipo_var.get()
                item_nombre = item_var.get()
                proveedor_nombre = proveedor_var.get()
                cantidad = int(cantidad_var.get())
                notas = notas_var.get()
                
                # Obtener IDs
                if tipo == "PRODUCTO":
                    item_id = None
                    for pid, pname in producto_nombres.items():
                        if pname == item_nombre:
                            item_id = int(pid)
                            break
                else:
                    item_id = None
                    for rid, rname in repuesto_nombres.items():
                        if rname == item_nombre:
                            item_id = int(rid)
                            break
                
                proveedor_id = None
                for prov_id, prov_name in proveedor_nombres.items():
                    if prov_name == proveedor_nombre:
                        proveedor_id = int(prov_id)
                        break
                
                if not item_id or not proveedor_id:
                    messagebox.showerror("Error", "Debe seleccionar ítem y proveedor válidos")
                    return
                
                if cantidad <= 0:
                    messagebox.showerror("Error", "La cantidad debe ser mayor a 0")
                    return
                
                # Crear pedido
                pedido_id = self.logic.pedidos.CREAR_PEDIDO(
                    proveedor_id=proveedor_id,
                    cantidad=cantidad,
                    tipo_item=tipo,
                    item_id=item_id,
                    orden_id=None,
                    notas=notas,
                    usuario=self.current_user.get('nombre', 'SISTEMA')
                )
                
                if pedido_id:
                    messagebox.showinfo("Éxito", f"Pedido #{pedido_id} creado correctamente")
                    win.destroy()
                    self.refresh()
                else:
                    messagebox.showerror("Error", "No se pudo crear el pedido")
            
            except ValueError:
                messagebox.showerror("Error", "La cantidad debe ser un número entero")
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")
        
        # Botones
        btn_frame = ctk.CTkFrame(win, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkButton(
            btn_frame,
            text="💾 GUARDAR",
            command=guardar,
            **Theme.get_button_style("success"),
            height=50
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ctk.CTkButton(
            btn_frame,
            text="CANCELAR",
            command=win.destroy,
            **Theme.get_button_style("error"),
            height=50
        ).pack(side="right", fill="x", expand=True, padx=(5, 0))
    
    def agregar_items_a_orden(self, proveedor_id):
        """Permite agregar múltiples items a la orden de compra antes de generarla"""
        win = ctk.CTkToplevel(self)
        win.title("Agregar Items a Orden")
        win.geometry("700x800")
        win.attributes("-topmost", True)
        win.configure(fg_color=Theme.BACKGROUND)
        win.grab_set()
        
        # Header
        header = ctk.CTkFrame(win, fg_color=Theme.PRIMARY, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(
            header,
            text="➕ AGREGAR ITEMS A ORDEN DE COMPRA",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"),
            text_color=Theme.WHITE
        ).pack(pady=20)
        
        # Obtener info del proveedor
        proveedores = self.logic.proveedores.OBTENER_TODOS_PROVEEDORES()
        proveedor_info = next((p for p in proveedores if p['id'] == proveedor_id), None)
        proveedor_nombre = proveedor_info['nombre'] if proveedor_info else "Desconocido"
        
        # Info del proveedor
        info_frame = ctk.CTkFrame(win, **Theme.get_card_style())
        info_frame.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(
            info_frame,
            text=f"🏢 Proveedor: {proveedor_nombre}",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold"),
            text_color=Theme.PRIMARY
        ).pack(pady=10)
        
        # Form para agregar items
        form_container = ctk.CTkFrame(win, **Theme.get_card_style())
        form_container.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            form_container,
            text="Agregar Nuevo Item:",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
            text_color=Theme.TEXT_PRIMARY
        ).pack(pady=(15, 10))
        
        # Grid para formulario
        form_grid = ctk.CTkFrame(form_container, fg_color="transparent")
        form_grid.pack(fill="x", padx=15, pady=(0, 15))
        
        # Tipo de ítem
        tipo_var = ctk.StringVar(value="PRODUCTO")
        tipo_frame = ctk.CTkFrame(form_grid, fg_color="transparent")
        tipo_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(tipo_frame, text="Tipo:", width=100, anchor="w").pack(side="left")
        tipo_combo = ctk.CTkComboBox(
            tipo_frame,
            variable=tipo_var,
            values=["PRODUCTO", "REPUESTO"],
            width=150,
            height=35
        )
        tipo_combo.pack(side="left", padx=5)
        
        # Item
        item_var = ctk.StringVar()
        item_frame = ctk.CTkFrame(form_grid, fg_color="transparent")
        item_frame.pack(fill="x", pady=5)
        item_label = ctk.CTkLabel(item_frame, text="Item:", width=100, anchor="w")
        item_label.pack(side="left")
        
        productos = self.logic.inventory.OBTENER_PRODUCTOS()
        repuestos = self.logic.parts.OBTENER_TODOS_REPUESTOS()
        producto_nombres = {str(p['id']): p['nombre'] for p in productos}
        repuesto_nombres = {str(r['id']): r['nombre'] for r in repuestos}
        
        item_combo = ctk.CTkComboBox(
            item_frame,
            variable=item_var,
            values=list(producto_nombres.values()),
            width=320,
            height=35
        )
        item_combo.pack(side="left", padx=5)
        
        def buscar_item():
            """Abre ventana de búsqueda de items"""
            search_win = ctk.CTkToplevel(win)
            search_win.title("🔍 Buscar Item")
            search_win.geometry("500x600")
            search_win.attributes("-topmost", True)
            search_win.configure(fg_color=Theme.BACKGROUND)
            search_win.grab_set()
            
            # Header
            search_header = ctk.CTkFrame(search_win, fg_color=Theme.PRIMARY, corner_radius=0)
            search_header.pack(fill="x")
            ctk.CTkLabel(
                search_header,
                text="🔍 BUSCAR ITEM",
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"),
                text_color=Theme.WHITE
            ).pack(pady=15)
            
            # Campo de búsqueda
            search_frame = ctk.CTkFrame(search_win, **Theme.get_card_style())
            search_frame.pack(fill="x", padx=20, pady=20)
            
            search_var = ctk.StringVar()
            search_entry = ctk.CTkEntry(
                search_frame,
                textvariable=search_var,
                placeholder_text="Escriba para buscar...",
                height=40,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL)
            )
            search_entry.pack(fill="x", padx=15, pady=15)
            search_entry.focus()
            
            # Resultados
            results_scroll = ctk.CTkScrollableFrame(search_win, fg_color="transparent")
            results_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
            
            def actualizar_resultados(*args):
                # Limpiar resultados
                for widget in results_scroll.winfo_children():
                    widget.destroy()
                
                query = search_var.get().lower()
                tipo = tipo_var.get()
                
                # Filtrar items según tipo y búsqueda
                if tipo == "PRODUCTO":
                    items = [(pid, pname) for pid, pname in producto_nombres.items() if query in pname.lower()]
                else:
                    items = [(rid, rname) for rid, rname in repuesto_nombres.items() if query in rname.lower()]
                
                if not items:
                    ctk.CTkLabel(
                        results_scroll,
                        text="No se encontraron resultados",
                        text_color=Theme.TEXT_SECONDARY
                    ).pack(pady=20)
                    return
                
                # Mostrar resultados
                for item_id, item_name in items[:50]:  # Limitar a 50 resultados
                    def select_item(name=item_name):
                        item_var.set(name)
                        search_win.destroy()
                    
                    btn = ctk.CTkButton(
                        results_scroll,
                        text=item_name,
                        command=select_item,
                        **Theme.get_button_style("secondary"),
                        anchor="w",
                        height=40
                    )
                    btn.pack(fill="x", pady=2)
            
            search_var.trace("w", actualizar_resultados)
            actualizar_resultados()
        
        ctk.CTkButton(
            item_frame,
            text="🔍",
            command=buscar_item,
            **Theme.get_button_style("primary"),
            width=40,
            height=35
        ).pack(side="left", padx=5)
        
        def cambiar_tipo(*args):
            if tipo_var.get() == "PRODUCTO":
                item_combo.configure(values=list(producto_nombres.values()))
                if producto_nombres:
                    item_var.set(list(producto_nombres.values())[0])
            else:
                item_combo.configure(values=list(repuesto_nombres.values()))
                if repuesto_nombres:
                    item_var.set(list(repuesto_nombres.values())[0])
        
        tipo_var.trace("w", cambiar_tipo)
        cambiar_tipo()
        
        # Cantidad
        cantidad_var = ctk.StringVar(value="1")
        cantidad_frame = ctk.CTkFrame(form_grid, fg_color="transparent")
        cantidad_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(cantidad_frame, text="Cantidad:", width=100, anchor="w").pack(side="left")
        ctk.CTkEntry(cantidad_frame, textvariable=cantidad_var, width=100, height=35).pack(side="left", padx=5)
        
        # Botón agregar
        def agregar_item():
            try:
                tipo = tipo_var.get()
                item_nombre = item_var.get()
                cantidad = int(cantidad_var.get())
                
                if cantidad <= 0:
                    messagebox.showerror("Error", "La cantidad debe ser mayor a 0")
                    return
                
                # Obtener ID del item
                if tipo == "PRODUCTO":
                    item_id = None
                    for pid, pname in producto_nombres.items():
                        if pname == item_nombre:
                            item_id = int(pid)
                            break
                else:
                    item_id = None
                    for rid, rname in repuesto_nombres.items():
                        if rname == item_nombre:
                            item_id = int(rid)
                            break
                
                if not item_id:
                    messagebox.showerror("Error", "Debe seleccionar un item válido")
                    return
                
                # Crear pedido
                pedido_id = self.logic.pedidos.CREAR_PEDIDO(
                    proveedor_id=proveedor_id,
                    cantidad=cantidad,
                    tipo_item=tipo,
                    item_id=item_id,
                    orden_id=None,
                    notas="Item agregado a orden de compra",
                    usuario=self.current_user.get('nombre', 'SISTEMA')
                )
                
                if pedido_id:
                    messagebox.showinfo("✓", f"{tipo}: {item_nombre} agregado (x{cantidad})")
                    cantidad_var.set("1")
                    actualizar_lista()
                else:
                    messagebox.showerror("Error", "No se pudo agregar el item")
            
            except ValueError:
                messagebox.showerror("Error", "La cantidad debe ser un número entero")
            except Exception as e:
                messagebox.showerror("Error", f"Error: {str(e)}")
        
        ctk.CTkButton(
            form_grid,
            text="➕ AGREGAR A ORDEN",
            command=agregar_item,
            **Theme.get_button_style("success"),
            height=40
        ).pack(pady=10)
        
        # Lista de items agregados
        lista_frame = ctk.CTkFrame(win, **Theme.get_card_style())
        lista_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(
            lista_frame,
            text="📋 Items en esta Orden:",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
            text_color=Theme.TEXT_PRIMARY
        ).pack(pady=(15, 10))
        
        scroll_items = ctk.CTkScrollableFrame(lista_frame, fg_color="transparent")
        scroll_items.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        def actualizar_lista():
            # Limpiar lista
            for widget in scroll_items.winfo_children():
                widget.destroy()
            
            # Obtener pedidos pendientes del proveedor
            pedidos = self.logic.pedidos.OBTENER_PEDIDOS_POR_PROVEEDOR(proveedor_id, solo_pendientes=True)
            
            if not pedidos:
                ctk.CTkLabel(
                    scroll_items,
                    text="No hay items en esta orden",
                    text_color=Theme.TEXT_SECONDARY
                ).pack(pady=20)
                return
            
            for pedido in pedidos:
                if pedido[6] == 'PENDIENTE':  # Solo PENDIENTES
                    item_card = ctk.CTkFrame(scroll_items, **Theme.get_card_style())
                    item_card.pack(fill="x", pady=5)
                    
                    item_info = ctk.CTkLabel(
                        item_card,
                        text=f"• {pedido[4]} - {pedido[7]} (x{pedido[2]})",
                        font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
                        text_color=Theme.TEXT_PRIMARY,
                        anchor="w"
                    )
                    item_info.pack(side="left", padx=15, pady=10, fill="x", expand=True)
        
        actualizar_lista()
        
        # Botones finales
        btn_frame = ctk.CTkFrame(win, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        def generar_orden():
            win.destroy()
            # Llamar al método original pero omitiendo la pregunta inicial
            self.generar_orden_compra_directa(proveedor_id)
        
        ctk.CTkButton(
            btn_frame,
            text="📄 GENERAR ORDEN DE COMPRA",
            command=generar_orden,
            **Theme.get_button_style("primary"),
            height=50
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ctk.CTkButton(
            btn_frame,
            text="CANCELAR",
            command=win.destroy,
            **Theme.get_button_style("error"),
            height=50
        ).pack(side="right", fill="x", expand=True, padx=(5, 0))
    
    def generar_orden_compra_directa(self, proveedor_id):
        """Genera la orden de compra sin preguntar por items adicionales"""
        import os
        import subprocess
        
        if messagebox.askyesno(
            "Generar Orden de Compra", 
            "¿Generar orden de compra en PDF?\n\n⚠️ Se incluirán todos los pedidos PENDIENTES del proveedor seleccionado.\n\n✓ Los pedidos se marcarán automáticamente como PEDIDO."
        ):
            try:
                # Obtener pedidos pendientes antes de generar PDF
                pedidos_pendientes = self.logic.pedidos.OBTENER_PEDIDOS_POR_PROVEEDOR(proveedor_id, solo_pendientes=True)
                ids_pedidos_pendientes = [p[0] for p in pedidos_pendientes if p[6] == 'PENDIENTE']
                
                # Generar PDF
                filepath = self.logic.pedidos.GENERAR_ORDEN_COMPRA(proveedor_id, solo_pendientes=True)
                
                if filepath:
                    # Marcar todos los pedidos PENDIENTES como PEDIDO
                    for pedido_id in ids_pedidos_pendientes:
                        pedido_info = self.logic.pedidos.OBTENER_PEDIDO(pedido_id)
                        self.logic.pedidos.MARCAR_COMO_PEDIDO(pedido_id)
                        
                        if pedido_info and pedido_info.get('orden_id'):
                            try:
                                self.logic.bd.EJECUTAR_CONSULTA(
                                    "UPDATE ordenes SET estado = 'ESPERA DE REPUESTO' WHERE id = ?",
                                    (pedido_info['orden_id'],)
                                )
                            except Exception as e:
                                print(f"Error actualizando orden {pedido_info['orden_id']}: {e}")
                    
                    self.refresh()
                    
                    # Preguntar si desea enviar
                    if self.logic.mensajeria:
                        enviar_msg = messagebox.askyesno(
                            "Enviar Orden de Compra",
                            f"Orden generada exitosamente.\n\n¿Desea enviar la orden al proveedor?\n\nSeleccione SÍ para elegir método de envío."
                        )
                        
                        if enviar_msg:
                            self.mostrar_opciones_envio(proveedor_id, filepath)
                    else:
                        messagebox.showinfo("Éxito", f"Orden de compra generada:\n{filepath}\n\n✓ {len(ids_pedidos_pendientes)} pedidos marcados como PEDIDO")
                    
                    # Abrir PDF
                    if os.path.exists(filepath):
                        try:
                            os.startfile(filepath)
                        except AttributeError:
                            try:
                                subprocess.call(['open', filepath])
                            except:
                                subprocess.call(['xdg-open', filepath])
                else:
                    messagebox.showwarning("Sin Pedidos", "No hay pedidos PENDIENTES para este proveedor")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo generar la orden de compra:\n{e}")
    
    def make_form_field(self, parent, label, variable, is_combo=False, values=None):
        """Helper para crear campos de formulario"""
        frame = ctk.CTkFrame(parent, **Theme.get_card_style())
        frame.pack(fill="x", pady=8)
        
        ctk.CTkLabel(
            frame,
            text=label,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w"
        ).pack(fill="x", padx=15, pady=(10, 5))
        
        if is_combo:
            ctk.CTkComboBox(
                frame,
                variable=variable,
                values=values or [],
                height=40,
                border_color=Theme.BORDER,
                button_color=Theme.PRIMARY,
                dropdown_fg_color=Theme.SURFACE
            ).pack(fill="x", padx=15, pady=(0, 10))
        else:
            ctk.CTkEntry(
                frame,
                textvariable=variable,
                height=40,
                border_color=Theme.BORDER,
                corner_radius=Theme.RADIUS_SMALL
            ).pack(fill="x", padx=15, pady=(0, 10))

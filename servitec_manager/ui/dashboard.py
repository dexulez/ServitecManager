import customtkinter as ctk
from tkinter import messagebox, Canvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .theme import Theme

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, logic, current_user):
        super().__init__(parent, fg_color=Theme.BACKGROUND)
        self.logic = logic
        
        # Configuración de Grid (2 Columnas)
        self.grid_columnconfigure(0, weight=4) # Columna Izquierda (Lista) - 40%
        self.grid_columnconfigure(1, weight=6) # Columna Derecha (Gráfico) - 60%
        self.grid_rowconfigure(0, weight=1)

        # --- IZQUIERDA: GESTIÓN RÁPIDA ---
        left_panel = ctk.CTkFrame(
            self, 
            corner_radius=Theme.RADIUS_LARGE,
            fg_color=Theme.SURFACE,
            border_width=1,
            border_color=Theme.BORDER
        )
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(20,10), pady=20)
        
        header = ctk.CTkFrame(left_panel, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20,10))
        
        ctk.CTkLabel(
            header,
            text="ÚLTIMOS SERVICIOS",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold"),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w"
        ).pack(side="left")
        
        self.scroll_orders = ctk.CTkScrollableFrame(left_panel, fg_color="transparent")
        self.scroll_orders.pack(fill="both", expand=True, padx=15, pady=(0,15))

        # --- DERECHA: ESTADÍSTICAS ---
        right_panel = ctk.CTkFrame(
            self,
            corner_radius=Theme.RADIUS_LARGE,
            fg_color=Theme.SURFACE,
            border_width=1,
            border_color=Theme.BORDER
        )
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10,20), pady=20)
        
        header_right = ctk.CTkFrame(right_panel, fg_color="transparent")
        header_right.pack(fill="x", padx=20, pady=(20,10))
        
        ctk.CTkLabel(
            header_right,
            text="ESTADO GLOBAL DEL TALLER",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold"),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w"
        ).pack(side="left")
        
        self.chart_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        self.chart_frame.pack(fill="both", expand=True, padx=20, pady=(0,20))

        self.load_recent_orders()
        self.draw_chart()

    def refresh(self):
        self.refresh_all()

    def refresh_all(self):
        self.load_recent_orders()
        self.refresh_chart()

    # --- CAMBIO DE ESTADO RÁPIDO (Al seleccionar en el ComboBox) ---
    def quick_status_change(self, new_status, order_id):
        # Obtener orden antes del cambio para comparar
        orden = self.logic.orders.get_order_by_id(order_id)
        if not orden:
            return
        
        estado_anterior = orden[9] if len(orden) > 9 else None
        
        # Guardamos en BD
        self.logic.orders.update_status(order_id, new_status)
        
        # Refrescar toda la vista para actualizar badges inmediatamente
        self.load_recent_orders()
        self.refresh_chart()
        
        # Si cambió el estado, preguntar si desea notificar
        if estado_anterior and estado_anterior != new_status:
            if messagebox.askyesno("Notificar Cliente", 
                                  f"Estado actualizado a '{new_status}'.\n\n¿Desea notificar al cliente?"):
                self.mostrar_opciones_notificacion_cliente(order_id, new_status)
    
    def navigate_to_workshop(self, order_id):
        """Navega al taller con la orden seleccionada"""
        app = self.winfo_toplevel()
        app.mostrar_frame("Workshop", order_id)
    
    def mostrar_opciones_notificacion_cliente(self, order_id, estado):
        """Muestra ventana con opciones para notificar al cliente sobre cambio de estado"""
        # Obtener datos de la orden y cliente
        orden = self.logic.orders.get_order_by_id(order_id)
        if not orden:
            return
        
        cliente_id = orden[1]
        cliente_data = self.logic.bd.OBTENER_TODOS("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
        
        if not cliente_data or len(cliente_data) == 0:
            messagebox.showwarning("Sin Cliente", "No se encontró información del cliente")
            return
        
        cliente = cliente_data[0]
        nombre_cliente = cliente[2] if len(cliente) > 2 else "Cliente"
        telefono = cliente[3] if len(cliente) > 3 else ""
        email = cliente[4] if len(cliente) > 4 else ""
        
        # Datos de la orden
        tipo_dispositivo = orden[4]
        marca = orden[5]
        modelo = orden[6]
        
        # Crear ventana de opciones
        win = ctk.CTkToplevel(self)
        win.title("📢 Notificar Cliente")
        win.geometry("600x650")
        win.attributes("-topmost", True)
        win.configure(fg_color=Theme.BACKGROUND)
        win.grab_set()
        
        # Centrar ventana
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (600 // 2)
        y = (win.winfo_screenheight() // 2) - (650 // 2)
        win.geometry(f"600x650+{x}+{y}")
        
        # Header
        header = ctk.CTkFrame(win, fg_color=Theme.PRIMARY, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(
            header,
            text=f"📢 NOTIFICAR A {nombre_cliente}",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"),
            text_color=Theme.WHITE
        ).pack(pady=20)
        
        # Contenido
        content = ctk.CTkFrame(win, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Información
        info_frame = ctk.CTkFrame(content, **Theme.get_card_style())
        info_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            info_frame,
            text=f"Orden #{order_id}: {tipo_dispositivo} {marca} {modelo}",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
            text_color=Theme.TEXT_PRIMARY
        ).pack(pady=10, padx=10)
        
        ctk.CTkLabel(
            info_frame,
            text=f"Nuevo estado: {estado}",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
            text_color=Theme.PRIMARY
        ).pack(pady=(0, 10), padx=10)
        
        # Campo para notas adicionales
        notas_frame = ctk.CTkFrame(content, fg_color="transparent")
        notas_frame.pack(fill="x", pady=(10, 10))
        
        ctk.CTkLabel(
            notas_frame,
            text="Nota adicional para el cliente (opcional):",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w"
        ).pack(fill="x")
        
        nota_text = ctk.CTkTextbox(notas_frame, height=100, font=(Theme.FONT_FAMILY, 12))
        nota_text.pack(fill="x", pady=(5, 0))
        nota_text.insert("1.0", "")
        
        # Botones de notificación
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))
        
        if telefono:
            ctk.CTkButton(
                btn_frame,
                text="📱 Enviar WhatsApp",
                command=lambda: [win.destroy(), self.enviar_whatsapp_cambio_estado(orden, cliente, estado, nota_text.get("1.0", "end").strip())],
                **Theme.get_button_style("success"),
                height=50
            ).pack(fill="x", pady=5)
        else:
            ctk.CTkLabel(
                btn_frame,
                text="❌ Cliente sin teléfono registrado",
                text_color=Theme.TEXT_SECONDARY
            ).pack(pady=5)
        
        if email:
            ctk.CTkButton(
                btn_frame,
                text="📧 Enviar Email",
                command=lambda: [win.destroy(), self.enviar_email_cambio_estado(orden, cliente, estado, nota_text.get("1.0", "end").strip())],
                **Theme.get_button_style("primary"),
                height=50
            ).pack(fill="x", pady=5)
        else:
            ctk.CTkLabel(
                btn_frame,
                text="❌ Cliente sin email registrado",
                text_color=Theme.TEXT_SECONDARY
            ).pack(pady=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=win.destroy,
            **Theme.get_button_style("secondary"),
            height=40
        ).pack(fill="x", pady=(20, 0))
    
    def enviar_whatsapp_cambio_estado(self, orden, cliente, estado, nota_adicional=""):
        """Envía WhatsApp al cliente informando cambio de estado"""
        if not self.logic.mensajeria:
            messagebox.showerror("Error", "Módulo de mensajería no disponible")
            return
        
        from datetime import datetime
        
        nombre_cliente = cliente[2] if len(cliente) > 2 else "Cliente"
        telefono = cliente[3] if len(cliente) > 3 else ""
        
        # Datos de la orden
        order_id = orden[0]
        tipo_dispositivo = orden[4]
        marca = orden[5]
        modelo = orden[6]
        
        # Generar mensaje según el estado
        mensajes_estado = {
            "PENDIENTE": "Su equipo está en cola de espera para ser revisado.",
            "EN REPARACION": "Su equipo está siendo reparado por nuestro equipo técnico.",
            "ESPERA DE REPUESTO": "Su equipo está esperando la llegada de un repuesto necesario para la reparación.",
            "REPARADO": "¡Buenas noticias! Su equipo ha sido reparado exitosamente y está listo para ser retirado.",
            "SIN SOLUCION": "Lamentablemente, no se pudo encontrar una solución viable para su equipo. Puede pasar a retirarlo.",
            "ENTREGADO": "Su equipo ha sido entregado. Gracias por confiar en nosotros."
        }
        
        mensaje_estado = mensajes_estado.get(estado, "El estado de su equipo ha sido actualizado.")
        
        mensaje = f"Estimado/a {nombre_cliente},\n\n"
        mensaje += f"Le informamos sobre su equipo:\n\n"
        mensaje += f"📱 {tipo_dispositivo} {marca} {modelo}\n"
        mensaje += f"📋 Orden #{order_id}\n\n"
        mensaje += f"📊 Estado actual: {estado}\n\n"
        mensaje += f"{mensaje_estado}\n\n"
        
        if nota_adicional:
            mensaje += f"📝 Nota adicional:\n{nota_adicional}\n\n"
        
        if estado == "REPARADO":
            mensaje += "Por favor, comuníquese con nosotros para coordinar la entrega.\n\n"
        
        mensaje += "Saludos cordiales,\nServitec Manager"
        
        # Enviar WhatsApp
        try:
            exito = self.logic.mensajeria.ENVIAR_WHATSAPP_WEB(telefono, mensaje)
            if exito:
                messagebox.showinfo("✓ Enviado", "Notificación enviada por WhatsApp")
            else:
                messagebox.showerror("Error", "No se pudo enviar el mensaje")
        except Exception as e:
            messagebox.showerror("Error", f"Error al enviar: {str(e)}")
    
    def enviar_email_cambio_estado(self, orden, cliente, estado, nota_adicional=""):
        """Envía Email al cliente informando cambio de estado"""
        if not self.logic.mensajeria:
            messagebox.showerror("Error", "Módulo de mensajería no disponible")
            return
        
        from datetime import datetime
        
        nombre_cliente = cliente[2] if len(cliente) > 2 else "Cliente"
        email = cliente[4] if len(cliente) > 4 else ""
        
        # Datos de la orden
        order_id = orden[0]
        tipo_dispositivo = orden[4]
        marca = orden[5]
        modelo = orden[6]
        
        # Generar mensaje según el estado
        mensajes_estado = {
            "PENDIENTE": "Su equipo está en cola de espera para ser revisado.",
            "EN REPARACION": "Su equipo está siendo reparado por nuestro equipo técnico.",
            "ESPERA DE REPUESTO": "Su equipo está esperando la llegada de un repuesto necesario para la reparación.",
            "REPARADO": "¡Buenas noticias! Su equipo ha sido reparado exitosamente y está listo para ser retirado.",
            "SIN SOLUCION": "Lamentablemente, no se pudo encontrar una solución viable para su equipo. Puede pasar a retirarlo.",
            "ENTREGADO": "Su equipo ha sido entregado. Gracias por confiar en nosotros."
        }
        
        mensaje_estado = mensajes_estado.get(estado, "El estado de su equipo ha sido actualizado.")
        
        asunto = f"Actualización Orden #{order_id} - {estado}"
        
        mensaje = f"Estimado/a {nombre_cliente},\n\n"
        mensaje += f"Le informamos sobre su equipo:\n\n"
        mensaje += f"Equipo: {tipo_dispositivo} {marca} {modelo}\n"
        mensaje += f"Orden: #{order_id}\n\n"
        mensaje += f"Estado actual: {estado}\n\n"
        mensaje += f"{mensaje_estado}\n\n"
        
        if nota_adicional:
            mensaje += f"Nota adicional:\n{nota_adicional}\n\n"
        
        if estado == "REPARADO":
            mensaje += "Por favor, comuníquese con nosotros para coordinar la entrega.\n\n"
        
        mensaje += "Saludos cordiales,\nServitec Manager"
        
        # Enviar Email
        try:
            mensaje_html = f"<html><body><pre style='font-family: Arial; font-size: 14px;'>{mensaje}</pre></body></html>"
            exito = self.logic.mensajeria.ENVIAR_EMAIL([email], asunto, mensaje_html)
            if exito:
                messagebox.showinfo("✓ Enviado", "Notificación enviada por Email")
            else:
                messagebox.showerror("Error", "No se pudo enviar el email")
        except Exception as e:
            messagebox.showerror("Error", f"Error al enviar: {str(e)}")

    # --- CARGA DE TARJETAS ---
    def load_recent_orders(self):
        for w in self.scroll_orders.winfo_children(): w.destroy()
        
        try: orders = self.logic.orders.get_dashboard_orders()
        except AttributeError: return
        
        if not orders:
            ctk.CTkLabel(
                self.scroll_orders, 
                text="NO HAY ÓRDENES ACTIVAS", 
                text_color=Theme.TEXT_LIGHT,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL)
            ).pack(pady=40)
            return

        for idx, o in enumerate(orders):
            # Compatibilidad con diccionarios (row_factory) y tuplas
            if isinstance(o, dict):
                oid = o['id']
                equipo = o['equipo']
                modelo = o['modelo']
                estado = o['estado']
                tecnico = o['tecnico']
                cliente = o['cliente']
            else:
                oid, equipo, modelo, estado, tecnico, cliente = o
            
            # Línea separadora ondulada entre servicios (excepto antes del primero)
            if idx > 0:
                separator_container = ctk.CTkFrame(
                    self.scroll_orders,
                    fg_color="transparent",
                    height=40
                )
                separator_container.pack(fill="x", pady=(Theme.PADDING_SMALL, Theme.PADDING_SMALL))
                
                # Canvas para dibujar la línea ondulada
                canvas = Canvas(
                    separator_container,
                    height=40,
                    bg=Theme.BACKGROUND if hasattr(Theme, 'BACKGROUND') else "#f5f5f5",
                    highlightthickness=0
                )
                canvas.pack(fill="x", padx=Theme.PADDING_MEDIUM)
                
                # Crear la curva ondulada
                def draw_wave(event=None):
                    canvas.delete("all")
                    width = canvas.winfo_width()
                    if width > 1:
                        # Dibujar línea ondulada suave (curva bezier simulada)
                        points = []
                        amplitude = 8  # Altura de la onda
                        frequency = 0.03  # Frecuencia de la onda
                        y_center = 20
                        
                        for x in range(0, width, 2):
                            import math
                            y = y_center + amplitude * math.sin(frequency * x)
                            points.extend([x, y])
                        
                        if len(points) > 2:
                            canvas.create_line(
                                points,
                                fill=Theme.DIVIDER if hasattr(Theme, 'DIVIDER') else "#e0e0e0",
                                width=1.5,
                                smooth=True
                            )
                
                canvas.bind("<Configure>", draw_wave)
                separator_container.after(10, draw_wave)
            
            # Card con borde fino - cada servicio en su propia tarjeta
            card = ctk.CTkFrame(
                self.scroll_orders,
                fg_color=Theme.SURFACE,
                corner_radius=Theme.RADIUS_MEDIUM,
                border_width=1,
                border_color=Theme.BORDER
            )
            card.pack(fill="x", pady=(0, Theme.PADDING_MEDIUM), padx=Theme.PADDING_MEDIUM)
            
            # Contenido de la card con más espacio
            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(fill="both", expand=True, padx=Theme.PADDING_LARGE, pady=Theme.PADDING_MEDIUM)
            
            # Header: Orden # y técnico
            header = ctk.CTkFrame(content, fg_color="transparent")
            header.pack(fill="x", pady=(0, Theme.PADDING_SMALL))
            
            ctk.CTkLabel(
                header, 
                text=f"#{oid}", 
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"), 
                text_color=Theme.PRIMARY
            ).pack(side="left")
            
            ctk.CTkLabel(
                header, 
                text=tecnico, 
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL), 
                text_color=Theme.TEXT_LIGHT
            ).pack(side="right")
            
            # Info del equipo
            ctk.CTkLabel(
                content, 
                text=f"{equipo} {modelo}", 
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_MEDIUM, "bold"), 
                text_color=Theme.TEXT_PRIMARY, 
                anchor="w"
            ).pack(fill="x", pady=(0, 4))
            
            ctk.CTkLabel(
                content, 
                text=cliente, 
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL), 
                text_color=Theme.TEXT_SECONDARY, 
                anchor="w"
            ).pack(fill="x", pady=(0, Theme.PADDING_MEDIUM))
            
            # Badge de estado tipo píldora
            badge_frame = ctk.CTkFrame(content, fg_color="transparent")
            badge_frame.pack(fill="x", pady=(0, Theme.PADDING_SMALL))
            
            badge = ctk.CTkLabel(
                badge_frame,
                text=f"  {estado}  ",
                **Theme.get_badge_style(estado)
            )
            badge.pack(side="left")
            
            # Separador sutil
            ctk.CTkFrame(content, height=1, fg_color=Theme.DIVIDER).pack(fill="x", pady=Theme.PADDING_SMALL)
            
            # Área de acciones
            actions = ctk.CTkFrame(content, fg_color="transparent")
            actions.pack(fill="x", pady=(Theme.PADDING_SMALL, 0))
            
            # Combo de cambio de estado (más sutil)
            combo = ctk.CTkComboBox(
                actions, 
                values=["PENDIENTE", "EN REPARACION", "ESPERA DE REPUESTO", "REPARADO", "SIN SOLUCION", "ENTREGADO"],
                width=180,
                height=32,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL),
                corner_radius=Theme.RADIUS_MEDIUM,
                border_width=1,
                border_color=Theme.BORDER,
                button_color=Theme.PRIMARY_LIGHT,
                button_hover_color=Theme.PRIMARY,
                command=lambda val, id=oid: self.quick_status_change(val, id)
            )
            combo.set(estado)
            combo.pack(side="left")
            
            # Botón ghost sutil tipo flecha
            btn_go = ctk.CTkButton(
                actions, 
                text="→ Gestionar", 
                width=100, 
                height=32,
                fg_color="transparent",
                hover_color=Theme.HOVER,
                text_color=Theme.PRIMARY,
                corner_radius=Theme.RADIUS_MEDIUM,
                border_width=1,
                border_color=Theme.PRIMARY_LIGHT,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"),
                command=lambda id=oid: self.navigate_to_workshop(id)
            )
            btn_go.pack(side="right")

    # --- GRÁFICO ---
    def draw_chart(self):
        for w in self.chart_frame.winfo_children(): w.destroy()
        stats = self.logic.orders.get_order_stats()
        
        if not stats:
            ctk.CTkLabel(self.chart_frame, text="SIN DATOS", text_color="gray").pack(pady=50)
            return

        # Compatibilidad con diccionarios (row_factory) y tuplas
        if stats and isinstance(stats[0], dict):
            labels = [s['estado'] for s in stats]
            sizes = [s['cantidad'] for s in stats]
        else:
            labels = [s[0] for s in stats]
            sizes = [s[1] for s in stats]
        
        # Colores pasteles suaves para el gráfico
        colors_map = {
            "PENDIENTE": "#FFF4BA",           # Amarillo pastel suave
            "EN REPARACION": "#BAD9F5",      # Azul pastel cielo
            "ESPERA DE REPUESTO": "#FFD9BA", # Naranja pastel suave
            "REPARADO": "#BAE8D1",           # Verde menta pastel
            "ENTREGADO": "#BAE5F5",          # Azul cielo pastel
            "SIN SOLUCION": "#F5BACC"        # Rosa pastel suave
        }
        colors = [colors_map.get(l, "#F5F5F5") for l in labels]

        fig = Figure(figsize=(5, 5), dpi=100)
        fig.patch.set_facecolor(Theme.SURFACE)
        ax = fig.add_subplot(111)
        
        # Gráfico tipo DONA (donut) con círculo blanco en el centro
        wedges, texts, autotexts = ax.pie(
            sizes, 
            labels=None, 
            autopct='%1.1f%%', 
            startangle=90, 
            colors=colors,
            wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2)  # Grosor de dona y bordes blancos
        )
        
        # Estilos de texto más sutiles
        for autotext in autotexts: 
            autotext.set_color(Theme.TEXT_PRIMARY)
            autotext.set_weight('600')  # Semi-bold
            autotext.set_fontsize(11)
            autotext.set_fontfamily(Theme.FONT_FAMILY)
        
        ax.axis('equal')

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, pady=(0,10))
        
        # Leyenda con porcentajes debajo del gráfico
        legend_frame = ctk.CTkFrame(self.chart_frame, fg_color="transparent")
        legend_frame.pack(fill="x", padx=Theme.PADDING_LARGE, pady=(0,10))
        
        total = sum(sizes)
        for i, (label, size, color) in enumerate(zip(labels, sizes, colors)):
            percentage = (size / total * 100) if total > 0 else 0
            
            item_frame = ctk.CTkFrame(legend_frame, fg_color="transparent")
            item_frame.pack(fill="x", pady=4)
            
            # Color box redondeado
            color_box = ctk.CTkFrame(
                item_frame, 
                width=16, 
                height=16, 
                fg_color=color, 
                corner_radius=4,
                border_width=1,
                border_color=Theme.BORDER
            )
            color_box.pack(side="left", padx=(0,12))
            
            # Texto con jerarquía visual - fuente aumentada al 80%
            ctk.CTkLabel(
                item_frame, 
                text=f"{label}: {size} ({percentage:.1f}%)",
                font=(Theme.FONT_FAMILY, int(Theme.FONT_SIZE_SMALL * 1.8)),
                text_color=Theme.TEXT_SECONDARY,
                anchor="w"
            ).pack(side="left", fill="x", expand=True)
        
        self.canvas = canvas

    def refresh_chart(self):
        self.draw_chart()
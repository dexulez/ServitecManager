import customtkinter as ctk
from tkinter import ttk, messagebox
import traceback
from .theme import Theme

class HistoryFrame(ctk.CTkFrame):
    def __init__(self, parent, logic, current_user, app_ref=None):
        super().__init__(parent, fg_color=Theme.BACKGROUND)
        self.logic = logic
        self.current_user = current_user
        self.app_ref = app_ref  # Referencia al app principal para actualizar todo
        self.configure(fg_color="transparent")
        self.filtro_estado = None  # Filtro de estado para las órdenes
        
        # Título
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=Theme.PADDING_LARGE, padx=Theme.PADDING_LARGE)
        ctk.CTkLabel(header, text="📋 HISTORIAL COMPLETO DE TRANSACCIONES", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H1, "bold"), text_color=Theme.TEXT_PRIMARY).pack()
        
        # Separator
        ctk.CTkFrame(self, height=2, fg_color=Theme.DIVIDER).pack(fill="x", pady=(0, Theme.PADDING_MEDIUM))
        
        # Tabs
        self.tabview = ctk.CTkTabview(self, fg_color=Theme.SURFACE, segmented_button_fg_color=Theme.BACKGROUND_LIGHT, segmented_button_selected_color=Theme.PRIMARY, text_color=Theme.TEXT_PRIMARY, corner_radius=Theme.RADIUS_LARGE, border_width=2, border_color=Theme.BORDER)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        self.tab_orders = self.tabview.add("ÓRDENES DE SERVICIO")
        self.tab_sales = self.tabview.add("VENTAS DE PRODUCTOS")
        self.tab_commissions = self.tabview.add("💰 COMISIONES TÉCNICO")
        
        self.setup_orders_tab()
        self.setup_sales_tab()
        self.setup_commissions_tab()

    def refresh(self):
        self.load_orders()
        self.load_sales()
        self.load_commissions()
    
    def set_filtro(self, estado):
        """Establecer filtro de estado para las órdenes"""
        self.filtro_estado = estado if estado else None
    
    def on_filtro_change(self, choice):
        """Callback cuando cambia el filtro de estado"""
        if choice == "Todos":
            self.filtro_estado = None
        else:
            self.filtro_estado = choice
        self.load_orders()

    def setup_orders_tab(self):
        # Filtros
        top = ctk.CTkFrame(self.tab_orders, fg_color="transparent"); top.pack(fill="x", pady=5)
        
        # Filtro por estado
        ctk.CTkLabel(top, text="Filtrar por estado:", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"), text_color=Theme.TEXT_PRIMARY).pack(side="left", padx=5)
        self.var_filtro_estado = ctk.StringVar(value="Todos")
        estados_filtro = ["Todos", "Pendiente", "En Proceso", "Reparado", "Entregado", "Sin solución"]
        self.combo_estado = ctk.CTkComboBox(top, values=estados_filtro, variable=self.var_filtro_estado, 
                                            width=200, height=40, command=self.on_filtro_change,
                                            border_color=Theme.BORDER, button_color=Theme.PRIMARY)
        self.combo_estado.pack(side="left", padx=5)
        
        # Búsqueda
        self.search_order = ctk.CTkEntry(top, placeholder_text="🔍 Buscar por Cliente, Equipo o ID...", width=300, height=40, corner_radius=Theme.RADIUS_MEDIUM, border_color=Theme.BORDER)
        self.search_order.pack(side="left", padx=5)
        self.search_order.bind("<Return>", lambda e: self.load_orders(filter_txt=self.search_order.get()))
        ctk.CTkButton(top, text="🔍", width=50, command=lambda: self.load_orders(filter_txt=self.search_order.get()), **Theme.get_button_style("secondary"), height=40).pack(side="left")
        
        ctk.CTkButton(top, text="🔄 ACTUALIZAR", width=140, command=self.load_orders, **Theme.get_button_style("primary"), height=40).pack(side="right", padx=5)

        # Tabla Headers
        h = ctk.CTkFrame(self.tab_orders, fg_color=Theme.PRIMARY, height=40, corner_radius=Theme.RADIUS_SMALL); h.pack(fill="x", pady=5)
        cols = [("ID", 50), ("FECHA", 70), ("CLIENTE", 200), ("EQUIPO", 170), ("TÉCNICO", 90), ("OBSERVACIONES", 390), ("ESTADO", 120), ("CONDICIÓN", 130), ("F.ENTREGA", 100), ("TOTAL", 80), ("VER", 80)]
        for c, w in cols: ctk.CTkLabel(h, text=c, width=w, font=(Theme.FONT_FAMILY, 11, "bold"), text_color=Theme.WHITE, anchor="center").pack(side="left", padx=3)
        
        self.scroll_orders = ctk.CTkScrollableFrame(self.tab_orders, fg_color=Theme.BACKGROUND_LIGHT, corner_radius=Theme.RADIUS_MEDIUM); self.scroll_orders.pack(fill="both", expand=True)
        self.load_orders()

    def load_orders(self, filter_txt=""):
        for w in self.scroll_orders.winfo_children(): w.destroy()
        data = self.logic.reports.get_full_history_orders()

        filter_txt = filter_txt.upper()
        ESTADOS = ['Pendiente', 'En Proceso', 'Reparado', 'Entregado', 'Sin solución']
        CONDICIONES = ['PENDIENTE', 'SOLUCIONADO', 'SIN SOLUCIÓN']
        for row in data:
            # Índices: 0:ID, 1:FECHA, 2:CLIENTE, 3:EQUIPO, 4:TÉCNICO, 5:OBSERVACIONES, 6:ESTADO, 7:CONDICIÓN, 8:F.ENTREGA, 9:TOTAL
            oid = row[0]
            # Filtros
            if self.filtro_estado and row[6] != self.filtro_estado:
                continue
            if filter_txt and (filter_txt not in str(row[0]) and filter_txt not in str(row[2] or "") and filter_txt not in str(row[3])): continue

            f = ctk.CTkFrame(self.scroll_orders, **Theme.get_card_style()); f.pack(fill="x", pady=2)
            # ID
            ctk.CTkLabel(f, text=f"#{row[0]}", width=50, text_color=Theme.PRIMARY, font=(Theme.FONT_FAMILY, 11, "bold"), anchor="w").pack(side="left", padx=3)
            # FECHA
            ctk.CTkLabel(f, text=row[1][:10] if row[1] else "-", width=70, text_color=Theme.TEXT_PRIMARY, font=(Theme.FONT_FAMILY, 11), anchor="w").pack(side="left", padx=3)
            # CLIENTE
            ctk.CTkLabel(f, text=row[2] or "---", width=200, text_color=Theme.TEXT_PRIMARY, font=(Theme.FONT_FAMILY, 11), anchor="w").pack(side="left", padx=3)
            # EQUIPO
            ctk.CTkLabel(f, text=row[3], width=170, text_color=Theme.TEXT_PRIMARY, font=(Theme.FONT_FAMILY, 11), anchor="w").pack(side="left", padx=3)
            # TÉCNICO
            ctk.CTkLabel(f, text=row[4] or "---", width=90, text_color=Theme.TEXT_SECONDARY, font=(Theme.FONT_FAMILY, 11), anchor="w").pack(side="left", padx=3)
            
            # OBSERVACIONES
            obs_raw = row[5] or "-"
            obs_clean = obs_raw.replace("FALLA: |", "").replace("FALLA:", "").replace("|", "").strip()
            ctk.CTkLabel(f, text=obs_clean, width=390, text_color=Theme.TEXT_PRIMARY, font=(Theme.FONT_FAMILY, 11), anchor="nw", wraplength=380, justify="left").pack(side="left", padx=3)

            # ESTADO (ComboBox editable)
            estado_var = ctk.StringVar(value=row[6])
            estado_cb = ctk.CTkComboBox(f, values=ESTADOS, variable=estado_var, width=120)
            estado_cb.pack(side="left", padx=3, pady=4)

            # Evento de cambio de estado
            def on_estado_change(choice, oid=oid, cond_cb=None):
                self.logic.orders.ACTUALIZAR_ESTADO(oid, choice)
                # Si cambia a Entregado, habilitar selector de condición
                if choice == 'Entregado' and cond_cb:
                    cond_cb.configure(state="normal")
                if self.app_ref:
                    self.app_ref.refresh_all_frames()

            # CONDICIÓN (ComboBox)
            condicion_var = ctk.StringVar(value=row[7] if row[7] else "PENDIENTE")
            condicion_cb = ctk.CTkComboBox(f, values=CONDICIONES, variable=condicion_var, width=130, state="readonly" if row[6] != 'Entregado' else "normal")
            condicion_cb.pack(side="left", padx=3, pady=4)
            
            # Evento de cambio de condición
            def on_condicion_change(choice, oid=oid):
                self.logic.orders.ACTUALIZAR_CONDICION(oid, choice)
                # Si es SIN SOLUCIÓN, poner total_a_cobrar y abono en 0
                if choice == 'SIN SOLUCIÓN':
                    self.logic.orders.ANULAR_COBRO_ORDEN(oid)
                if self.app_ref:
                    self.app_ref.refresh_all_frames()
            
            condicion_cb.configure(command=on_condicion_change)
            estado_cb.configure(command=lambda choice, oid=oid, cb=condicion_cb: on_estado_change(choice, oid, cb))
            
            # F. ENTREGA
            fecha_ent = row[8][:10] if row[8] else "-"
            ctk.CTkLabel(f, text=fecha_ent, width=100, text_color=Theme.TEXT_PRIMARY, font=(Theme.FONT_FAMILY, 11), anchor="w").pack(side="left", padx=3)

            # TOTAL
            total = f"${int(row[9]):,}".replace(",", ".") if row[9] else "$0"
            ctk.CTkLabel(f, text=total, width=80, text_color=Theme.TEXT_PRIMARY, font=(Theme.FONT_FAMILY, 11, "bold"), anchor="w").pack(side="left", padx=3)

            # Botón ver
            ctk.CTkButton(f, text="👁️", width=80, height=30, **Theme.get_button_style("secondary"), command=lambda oid=row[0]: self.show_order_detail(oid)).pack(side="left", padx=3)

    def show_order_detail(self, oid):
        # Popup con detalles
        win = ctk.CTkToplevel(self)
        win.title(f"DETALLES ORDEN #{oid}")
        win.geometry("700x800")
        win.attributes("-topmost", True)
        win.grab_set()
        win.configure(fg_color=Theme.BACKGROUND)
        # Centrar ventana
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (700 // 2)
        y = (win.winfo_screenheight() // 2) - (800 // 2)
        win.geometry(f"700x800+{x}+{y}")
        
        try:
            # Header
            header = ctk.CTkFrame(win, fg_color=Theme.PRIMARY, corner_radius=0)
            header.pack(fill="x")
            ctk.CTkLabel(header, text=f"📋 ORDEN DE SERVICIO #{oid}", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H1, "bold"), text_color=Theme.WHITE).pack(pady=20)
            
            # Datos Básicos
            tdata = self.logic.orders.get_ticket_data(oid) # o.*, rut, nom, tel, mail
            
            scroll = ctk.CTkScrollableFrame(win, fg_color="transparent")
            scroll.pack(fill="both", expand=True, padx=Theme.PADDING_LARGE, pady=Theme.PADDING_LARGE)
            
            def add_sec(title, content):
                sec = ctk.CTkFrame(scroll, **Theme.get_card_style()); sec.pack(fill="x", pady=8)
                ctk.CTkLabel(sec, text=title, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"), text_color=Theme.PRIMARY, anchor="w").pack(fill="x", pady=(10, 5), padx=15)
                ctk.CTkFrame(sec, height=1, fg_color=Theme.DIVIDER).pack(fill="x", padx=15)
                ctk.CTkLabel(sec, text=content, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL), text_color=Theme.TEXT_PRIMARY, justify="left", anchor="w", wraplength=580).pack(fill="x", padx=15, pady=(5, 10))
                
            add_sec("CLIENTE", f"Nombre: {tdata[18]}\nRUT: {tdata[17]}\nTeléfono: {tdata[19]}\nEmail: {tdata[20]}")
            add_sec("EQUIPO", f"Tipo: {tdata[4]}\nMarca: {tdata[5]}\nModelo: {tdata[6]}\nSerie/IMEI: {tdata[7]}\nAccesorios: {tdata[10]}\nRiesgoso: {'SÍ' if tdata[11] else 'NO'}")
            add_sec("FALLA / DIAGNÓSTICO", tdata[8])
            add_sec("ESTADO Y FECHAS", f"Estado: {tdata[9]}\nIngreso: {tdata[3]}")
            
            # Finanzas
            fin = self.logic.reports.get_order_financials(oid)
            if fin:
                # 0:id, 1:oid, 2:tot, 3:rep, 4:env, 5:efec, 6:trf, 7:deb, 8:cred, 9:iva, 10:util, 11:com_tec, 12:fecha_cierre
                txt = f"Total Cobrado: ${int(fin[2]):,}\n"
                txt += f"Costo Repuesto: -${int(fin[3]):,}\n"
                txt += f"Costo Envío: -${int(fin[4]):,}\n"
                txt += f"Comisión Técnico: -${int(fin[11]):,}\n"
                txt += f"Utilidad Real Tienda: ${int(fin[10]):,}\n\n"
                txt += "--- PAGOS ---\n"
                if fin[5]: txt += f"Efectivo: ${int(fin[5]):,}\n"
                if fin[6]: txt += f"Transferencia: ${int(fin[6]):,}\n"
                if fin[7]: txt += f"Débito: ${int(fin[7]):,}\n"
                if fin[8]: txt += f"Crédito: ${int(fin[8]):,}\n"
                
                add_sec("FINANZAS Y CIERRE", txt + f"\nFecha Cierre: {fin[12]}")
            else:
                add_sec("FINANZAS", f"Presupuesto: ${int(tdata[12] or 0):,}\nAbono: ${int(tdata[13] or 0):,}\nPendiente: ${int((tdata[12] or 0) - (tdata[13] or 0)):,}")
            
            # Botones de acción
            btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
            btn_frame.pack(fill="x", pady=15, padx=0)
            
            # Botón Imprimir Ticket
            from pdf_generator_v2 import PDFGeneratorV2
            def print_ticket():
                pdf = PDFGeneratorV2(self.logic)
                filepath = pdf.generar_orden_ingreso(tdata)
                pdf.abrir_pdf(filepath)
            
            ctk.CTkButton(btn_frame, text="🖨️ IMPRIMIR TICKET", command=print_ticket, 
                         **Theme.get_button_style("primary"), height=45).pack(side="left", padx=3, expand=True, fill="x")
            
            # Botón Editar (solo si se puede editar)
            if self.logic.orders.can_edit_order(oid):
                def edit_order():
                    win.destroy()
                    # Obtener referencia a la aplicación principal
                    app = self.master.master
                    # Cambiar a recepción
                    app.mostrar_frame("Reception")
                    # Cargar la orden en el frame de recepción
                    reception_frame = app.frames.get("Reception")
                    if reception_frame and hasattr(reception_frame, 'load_order_for_edit'):
                        reception_frame.load_order_for_edit(oid)
                
                ctk.CTkButton(btn_frame, text="✏️ EDITAR ORDEN", command=edit_order,
                             **Theme.get_button_style("accent"), height=45).pack(side="left", padx=3, expand=True, fill="x")
            
            # Botón Gestionar en Taller (solo si no está entregada)
            if tdata[9] != "ENTREGADO":
                def go_to_workshop():
                    win.destroy()
                    # Obtener referencia a la aplicación principal
                    app = self.master.master
                    # Cambiar a taller con el ID de la orden
                    app.mostrar_frame("Workshop", datos=oid)
                
                ctk.CTkButton(btn_frame, text="🔧 GESTIONAR EN TALLER", command=go_to_workshop,
                             **Theme.get_button_style("success"), height=45).pack(side="left", padx=3, expand=True, fill="x")
        
        except Exception as e:
            error_msg = f"Error al cargar detalles:\n{str(e)}\n\n{traceback.format_exc()}"
            ctk.CTkLabel(win, text=error_msg, font=("Arial", 10), text_color="red", wraplength=550, justify="left").pack(padx=20, pady=20)
            print(error_msg)

    def change_order_status(self, oid):
        """Permitir cambiar el estado de una orden de servicio"""
        # Obtener datos de la orden
        orden = self.logic.bd.OBTENER_UNO("SELECT id, estado FROM ordenes WHERE id = ?", (oid,))
        if not orden:
            messagebox.showerror("Error", "Orden no encontrada")
            return
        
        current_status = orden[1]
        
        # Ventana para cambiar estado
        win = ctk.CTkToplevel(self)
        win.title(f"Cambiar Estado - Orden #{oid}")
        win.geometry("450x450")
        win.attributes("-topmost", True)
        win.grab_set()
        win.configure(fg_color=Theme.BACKGROUND)
        
        # Centrar
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (225)
        y = (win.winfo_screenheight() // 2) - (225)
        win.geometry(f"450x450+{x}+{y}")
        
        # Header
        header = ctk.CTkFrame(win, fg_color=Theme.ACCENT, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text=f"🔄 CAMBIAR ESTADO ORDEN #{oid}", 
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"), 
                    text_color=Theme.WHITE).pack(pady=20)
        
        # Container
        container = ctk.CTkFrame(win, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=Theme.PADDING_LARGE, pady=Theme.PADDING_LARGE)
        
        # Estado actual con badge de color
        current_frame = ctk.CTkFrame(container, **Theme.get_card_style())
        current_frame.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(current_frame, text="Estado Actual:", 
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
                    text_color=Theme.TEXT_SECONDARY).pack(pady=(10, 5))
        
        # Badge con color de fondo según el estado
        col_st = Theme.get_status_color(current_status)
        text_col_st = Theme.get_status_text_color(current_status)
        badge = ctk.CTkLabel(current_frame, text=current_status, 
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold"),
                    fg_color=col_st, text_color=text_col_st,
                    corner_radius=8, width=250, height=50)
        badge.pack(pady=(0, 10), padx=20)
        
        # Nuevo estado
        select_frame = ctk.CTkFrame(container, **Theme.get_card_style())
        select_frame.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(select_frame, text="Nuevo Estado:", 
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
                    text_color=Theme.TEXT_PRIMARY, anchor="w").pack(fill="x", padx=15, pady=(10, 5))
        
        estados = ["Pendiente", "En Proceso", "Reparado", "Entregado", "Sin solución"]
        v_estado = ctk.StringVar(value=current_status)
        
        combo = ctk.CTkComboBox(select_frame, values=estados, variable=v_estado, height=45,
                               font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
                               border_color=Theme.BORDER, button_color=Theme.PRIMARY,
                               dropdown_fg_color=Theme.SURFACE)
        combo.pack(fill="x", padx=15, pady=(0, 10))
        
        def guardar():
            nuevo_estado = v_estado.get()
            if nuevo_estado == current_status:
                messagebox.showinfo("Info", "El estado no ha cambiado")
                return
            
            if messagebox.askyesno("Confirmar", f"¿Cambiar estado de '{current_status}' a '{nuevo_estado}'?"):
                try:
                    self.logic.bd.EJECUTAR_CONSULTA("UPDATE ordenes SET estado = ? WHERE id = ?", (nuevo_estado, oid))
                    messagebox.showinfo("Éxito", f"Estado actualizado a '{nuevo_estado}'")
                    win.destroy()
                    self.load_orders()
                    # Actualizar todos los frames del sistema
                    if self.app_ref:
                        self.app_ref.refresh_all_frames()
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo actualizar el estado:\n{str(e)}")
        
        # Botones
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkButton(btn_frame, text="💾 GUARDAR", command=guardar,
                     **Theme.get_button_style("success"), height=50).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(btn_frame, text="❌ CANCELAR", command=win.destroy,
                     **Theme.get_button_style("danger"), height=50).pack(side="left", fill="x", expand=True, padx=(5, 0))

    def setup_sales_tab(self):
        top = ctk.CTkFrame(self.tab_sales, fg_color="transparent"); top.pack(fill="x", pady=5)
        ctk.CTkButton(top, text="🔄 ACTUALIZAR", width=140, command=self.load_sales, **Theme.get_button_style("primary"), height=40).pack(side="right", padx=5)
        self.search_sale = ctk.CTkEntry(top, placeholder_text="🔍 Buscar por ID o Vendedor...", width=300, height=40, corner_radius=Theme.RADIUS_MEDIUM, border_color=Theme.BORDER)
        self.search_sale.pack(side="left", padx=5)
        self.search_sale.bind("<Return>", lambda e: self.load_sales(filter_txt=self.search_sale.get()))
        ctk.CTkButton(top, text="🔍", width=50, command=lambda: self.load_sales(filter_txt=self.search_sale.get()), **Theme.get_button_style("secondary"), height=40).pack(side="left")

        h = ctk.CTkFrame(self.tab_sales, fg_color=Theme.PRIMARY, height=40, corner_radius=Theme.RADIUS_SMALL); h.pack(fill="x", pady=5)
        cols = [("ID", 60), ("FECHA", 120), ("VENDEDOR", 150), ("TOTAL", 100), ("PAGOS", 250), ("OPCIONES", 100)]
        for c, w in cols: ctk.CTkLabel(h, text=c, width=w, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"), text_color=Theme.WHITE).pack(side="left", padx=2)
        
        self.scroll_sales = ctk.CTkScrollableFrame(self.tab_sales, fg_color=Theme.BACKGROUND_LIGHT, corner_radius=Theme.RADIUS_MEDIUM); self.scroll_sales.pack(fill="both", expand=True)
        self.load_sales()

    def load_sales(self, filter_txt=""):
        for w in self.scroll_sales.winfo_children(): w.destroy()
        data = self.logic.reports.get_full_history_sales()
        
        filter_txt = filter_txt.upper()
        for row in data:
            # 0:id, 1:fecha, 2:vendedor, 3:total, 4:efec, 5:trf, 6:deb, 7:cred
            if filter_txt and (filter_txt not in str(row[0]) and filter_txt not in str(row[2] or "")): continue
            
            f = ctk.CTkFrame(self.scroll_sales, **Theme.get_card_style()); f.pack(fill="x", pady=2)
            
            ctk.CTkLabel(f, text=f"#{row[0]}", width=60, text_color=Theme.PRIMARY, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold")).pack(side="left", padx=2)
            ctk.CTkLabel(f, text=row[1][:16], width=120, text_color=Theme.TEXT_PRIMARY).pack(side="left", padx=2)
            ctk.CTkLabel(f, text=row[2] or "---", width=150, text_color=Theme.TEXT_PRIMARY).pack(side="left", padx=2)
            ctk.CTkLabel(f, text=f"${int(row[3]):,}".replace(",", "."), width=100, text_color=Theme.TEXT_PRIMARY, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold")).pack(side="left", padx=2)
            
            pagos = []
            if row[4]: pagos.append("EF")
            if row[5]: pagos.append("TR")
            if row[6]: pagos.append("DB")
            if row[7]: pagos.append("CR")
            ctk.CTkLabel(f, text=", ".join(pagos), width=250, text_color=Theme.TEXT_SECONDARY).pack(side="left", padx=2)
            
            ctk.CTkButton(f, text="📊 VER ITEMS", width=120, height=30, **Theme.get_button_style("secondary"), command=lambda vid=row[0]: self.show_sale_detail(vid)).pack(side="left", padx=5)

    def show_sale_detail(self, vid):
        win = ctk.CTkToplevel(self)
        win.title(f"DETALLE VENTA #{vid}")
        win.geometry("700x650")
        win.attributes("-topmost", True)
        win.grab_set()
        # Centrar ventana
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (700 // 2)
        y = (win.winfo_screenheight() // 2) - (650 // 2)
        win.geometry(f"700x650+{x}+{y}")
        win.configure(fg_color=Theme.BACKGROUND)
        
        try:
            # Header
            header = ctk.CTkFrame(win, fg_color=Theme.SUCCESS, corner_radius=0)
            header.pack(fill="x")
            ctk.CTkLabel(header, text=f"🛒 DETALLE VENTA #{vid}", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H1, "bold"), text_color=Theme.WHITE).pack(pady=20)
            
            # Headers de tabla
            h = ctk.CTkFrame(win, fg_color=Theme.PRIMARY, corner_radius=Theme.RADIUS_SMALL); h.pack(fill="x", padx=Theme.PADDING_LARGE, pady=(Theme.PADDING_LARGE, 0))
            ctk.CTkLabel(h, text="PRODUCTO / SERVICIO", width=280, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"), text_color=Theme.WHITE, anchor="w").pack(side="left", padx=(10, 0), pady=8)
            ctk.CTkLabel(h, text="CANT", width=50, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"), text_color=Theme.WHITE).pack(side="left", padx=5, pady=8)
            ctk.CTkLabel(h, text="PRECIO", width=90, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"), text_color=Theme.WHITE).pack(side="left", padx=5, pady=8)
            ctk.CTkLabel(h, text="SUBTOTAL", width=90, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"), text_color=Theme.WHITE).pack(side="left", padx=5, pady=8)
            
            scroll = ctk.CTkScrollableFrame(win, fg_color="transparent"); scroll.pack(fill="both", expand=True, padx=Theme.PADDING_LARGE, pady=Theme.PADDING_MEDIUM)
            
            items = self.logic.reports.get_sale_details(vid)
            for i in items:
                # 0:nombre, 1:cant, 2:precio, 3:sub
                r = ctk.CTkFrame(scroll, **Theme.get_card_style()); r.pack(fill="x", pady=3)
                ctk.CTkLabel(r, text=i[0], width=280, text_color=Theme.TEXT_PRIMARY, anchor="w", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL)).pack(side="left", padx=(10, 0), pady=8)
                ctk.CTkLabel(r, text=str(i[1]), width=50, text_color=Theme.TEXT_PRIMARY, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL)).pack(side="left", padx=5, pady=8)
                ctk.CTkLabel(r, text=f"${int(i[2]):,}".replace(",", "."), width=90, text_color=Theme.TEXT_PRIMARY, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL)).pack(side="left", padx=5, pady=8)
                ctk.CTkLabel(r, text=f"${int(i[3]):,}".replace(",", "."), width=90, text_color=Theme.PRIMARY, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold")).pack(side="left", padx=5, pady=8)
        
        except Exception as e:
            error_msg = f"Error al cargar detalles:\n{str(e)}\n\n{traceback.format_exc()}"
            ctk.CTkLabel(win, text=error_msg, font=("Arial", 10), text_color="red", wraplength=450, justify="left").pack(padx=20, pady=20)
            print(error_msg)

    def setup_commissions_tab(self):
        """Tab para calcular comisiones y gastos de técnicos"""
        # Filtros superiores
        top = ctk.CTkFrame(self.tab_commissions, fg_color="transparent")
        top.pack(fill="x", pady=10, padx=10)
        
        # Selector de técnico
        ctk.CTkLabel(top, text="Técnico:", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"), 
                    text_color=Theme.TEXT_PRIMARY).pack(side="left", padx=(0, 5))
        
        # Obtener lista de técnicos
        tecnicos = self.logic.bd.OBTENER_TODOS("SELECT id, nombre, porcentaje_comision FROM usuarios WHERE rol IN ('Técnico', 'Admin')")
        self.tecnicos_map = {f"{t[1]} ({t[2]}%)": t[0] for t in tecnicos}
        
        self.var_tecnico = ctk.StringVar(value=list(self.tecnicos_map.keys())[0] if self.tecnicos_map else "")
        combo_tecnico = ctk.CTkComboBox(top, values=list(self.tecnicos_map.keys()), 
                                       variable=self.var_tecnico, width=250, height=40,
                                       border_color=Theme.BORDER, button_color=Theme.PRIMARY)
        combo_tecnico.pack(side="left", padx=5)
        
        # Filtro por fecha
        ctk.CTkLabel(top, text="Desde:", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"), 
                    text_color=Theme.TEXT_PRIMARY).pack(side="left", padx=(20, 5))
        self.var_fecha_desde = ctk.StringVar(value="2026-01-01")
        entry_desde = ctk.CTkEntry(top, textvariable=self.var_fecha_desde, width=120, height=40,
                                   border_color=Theme.BORDER)
        entry_desde.pack(side="left", padx=5)
        
        ctk.CTkLabel(top, text="Hasta:", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"), 
                    text_color=Theme.TEXT_PRIMARY).pack(side="left", padx=(10, 5))
        self.var_fecha_hasta = ctk.StringVar(value="2026-12-31")
        entry_hasta = ctk.CTkEntry(top, textvariable=self.var_fecha_hasta, width=120, height=40,
                                   border_color=Theme.BORDER)
        entry_hasta.pack(side="left", padx=5)
        
        # Botón calcular
        ctk.CTkButton(top, text="📊 CALCULAR", command=self.load_commissions, width=140, height=40,
                     **Theme.get_button_style("success")).pack(side="left", padx=10)
        
        # Contenedor principal con scroll
        self.scroll_commissions = ctk.CTkScrollableFrame(self.tab_commissions, fg_color="transparent")
        self.scroll_commissions.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Cargar datos inicialmente
        self.load_commissions()
    
    def load_commissions(self):
        """Cargar y calcular comisiones del técnico seleccionado"""
        # Limpiar contenedor
        for w in self.scroll_commissions.winfo_children():
            w.destroy()
        
        if not self.var_tecnico.get() or self.var_tecnico.get() not in self.tecnicos_map:
            ctk.CTkLabel(self.scroll_commissions, text="⚠️ Seleccione un técnico", 
                        font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2), 
                        text_color=Theme.WARNING).pack(pady=50)
            return
        
        tecnico_id = self.tecnicos_map[self.var_tecnico.get()]
        fecha_desde = self.var_fecha_desde.get()
        fecha_hasta = self.var_fecha_hasta.get()
        
        # Consulta para obtener órdenes cerradas del técnico en el rango de fechas
        query = """
        SELECT 
            o.id,
            o.fecha_cierre,
            c.nombre AS cliente,
            o.equipo || ' ' || o.marca || ' ' || o.modelo AS equipo_completo,
            o.total_a_cobrar,
            o.costo_total_repuestos,
            o.costo_envio,
            o.descuento,
            o.comision_tecnico,
            o.utilidad_bruta,
            o.pago_efectivo,
            o.pago_transferencia,
            o.pago_debito,
            o.pago_credito
        FROM ordenes o
        LEFT JOIN clientes c ON o.cliente_id = c.id
        WHERE o.tecnico_id = ?
          AND o.estado = 'Entregado'
          AND o.fecha_cierre IS NOT NULL
          AND o.fecha_cierre >= ?
          AND o.fecha_cierre <= ?
        ORDER BY o.fecha_cierre DESC
        """
        
        ordenes = self.logic.bd.OBTENER_TODOS(query, (tecnico_id, fecha_desde, fecha_hasta))
        
        if not ordenes:
            ctk.CTkLabel(self.scroll_commissions, 
                        text="📭 No hay órdenes cerradas en el período seleccionado", 
                        font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2), 
                        text_color=Theme.TEXT_SECONDARY).pack(pady=50)
            return
        
        # ============= RESUMEN GENERAL =============
        resumen_frame = ctk.CTkFrame(self.scroll_commissions, **Theme.get_card_style())
        resumen_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(resumen_frame, text="💰 RESUMEN FINANCIERO", 
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H1, "bold"),
                    text_color=Theme.PRIMARY).pack(pady=15)
        
        # Calcular totales
        total_facturado = sum(o[4] or 0 for o in ordenes)
        total_costo_repuestos = sum(o[5] or 0 for o in ordenes)
        total_costo_envio = sum(o[6] or 0 for o in ordenes)
        total_descuentos = sum(o[7] or 0 for o in ordenes)
        total_comision_bruta = sum(o[8] or 0 for o in ordenes)
        total_utilidad_tienda = sum(o[9] or 0 for o in ordenes)
        
        # Calcular comisiones bancarias (suponer 2.5% para tarjetas)
        total_pago_efectivo = sum(o[10] or 0 for o in ordenes)
        total_pago_transferencia = sum(o[11] or 0 for o in ordenes)
        total_pago_debito = sum(o[12] or 0 for o in ordenes)
        total_pago_credito = sum(o[13] or 0 for o in ordenes)
        
        # Comisiones bancarias aproximadas
        comision_banco_debito = total_pago_debito * 0.015  # 1.5% débito
        comision_banco_credito = total_pago_credito * 0.025  # 2.5% crédito
        comision_banco_transferencia = total_pago_transferencia * 0.005  # 0.5% transferencia
        total_comision_banco = comision_banco_debito + comision_banco_credito + comision_banco_transferencia
        
        # IVA (ya incluido en total_facturado, pero mostramos cuánto es)
        iva_incluido = total_facturado - (total_facturado / 1.19)
        
        # Grid de métricas
        metrics_frame = ctk.CTkFrame(resumen_frame, fg_color=Theme.BACKGROUND_LIGHT, corner_radius=10)
        metrics_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        def add_metric(parent, label, valor, color=Theme.TEXT_PRIMARY, bold=False):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(row, text=label, anchor="w",
                        font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold" if bold else "normal"),
                        text_color=Theme.TEXT_SECONDARY).pack(side="left", fill="x", expand=True)
            
            ctk.CTkLabel(row, text=f"${int(valor):,}".replace(",", "."), anchor="e",
                        font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE if bold else Theme.FONT_SIZE_NORMAL, "bold"),
                        text_color=color).pack(side="right")
        
        add_metric(metrics_frame, "📦 Total Órdenes Completadas:", len(ordenes), Theme.PRIMARY, True)
        add_metric(metrics_frame, "💵 Total Facturado (con IVA):", total_facturado, Theme.SUCCESS, True)
        
        ctk.CTkFrame(metrics_frame, height=2, fg_color=Theme.DIVIDER).pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(metrics_frame, text="🔻 DEDUCCIONES Y COSTOS:", 
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
                    text_color=Theme.WARNING).pack(anchor="w", padx=10, pady=(5, 10))
        
        add_metric(metrics_frame, "  📦 Costo Repuestos:", -total_costo_repuestos, Theme.DANGER)
        add_metric(metrics_frame, "  🚚 Costo Envío:", -total_costo_envio, Theme.DANGER)
        add_metric(metrics_frame, "  💳 Comisiones Bancarias:", -total_comision_banco, Theme.DANGER)
        add_metric(metrics_frame, "  🏷️ IVA (19% incluido):", -iva_incluido, Theme.DANGER)
        add_metric(metrics_frame, "  🎁 Descuentos Aplicados:", -total_descuentos, Theme.DANGER)
        
        total_deducciones = total_costo_repuestos + total_costo_envio + total_comision_banco + iva_incluido + total_descuentos
        
        ctk.CTkFrame(metrics_frame, height=2, fg_color=Theme.DIVIDER).pack(fill="x", padx=10, pady=10)
        
        # Ingresos netos (después de deducciones)
        ingreso_neto = total_facturado - total_deducciones
        add_metric(metrics_frame, "💰 Ingreso Neto (después de costos):", ingreso_neto, Theme.SUCCESS, True)
        
        ctk.CTkFrame(metrics_frame, height=2, fg_color=Theme.DIVIDER).pack(fill="x", padx=10, pady=10)
        
        add_metric(metrics_frame, "👨‍🔧 Comisión Bruta Técnico:", total_comision_bruta, Theme.PRIMARY, True)
        
        # Comisión neta del técnico (descontando su parte proporcional de costos)
        # El técnico no paga repuestos ni envío, pero sí asume parte de comisiones bancarias
        proporcion_tecnico = total_comision_bruta / total_facturado if total_facturado > 0 else 0
        comision_banco_tecnico = total_comision_banco * proporcion_tecnico
        
        comision_neta_tecnico = total_comision_bruta - comision_banco_tecnico
        
        add_metric(metrics_frame, "  💳 (-) Comisiones Bancarias Técnico:", -comision_banco_tecnico, Theme.DANGER)
        
        ctk.CTkFrame(metrics_frame, height=3, fg_color=Theme.PRIMARY).pack(fill="x", padx=10, pady=10)
        
        add_metric(metrics_frame, "💵 GANANCIA NETA TÉCNICO:", comision_neta_tecnico, Theme.SUCCESS, True)
        add_metric(metrics_frame, "🏪 UTILIDAD NETA TIENDA:", total_utilidad_tienda, Theme.PRIMARY, True)
        
        # ============= DETALLE POR ORDEN =============
        detalle_frame = ctk.CTkFrame(self.scroll_commissions, **Theme.get_card_style())
        detalle_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(detalle_frame, text="📋 DETALLE POR ORDEN", 
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"),
                    text_color=Theme.PRIMARY).pack(pady=15)
        
        # Headers
        header_frame = ctk.CTkFrame(detalle_frame, fg_color=Theme.PRIMARY, corner_radius=8)
        header_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        headers = [
            ("ID", 50),
            ("FECHA", 100),
            ("CLIENTE", 150),
            ("EQUIPO", 200),
            ("TOTAL", 90),
            ("COSTOS", 80),
            ("COMISIÓN", 100),
            ("VER", 80)
        ]
        
        for h, w in headers:
            ctk.CTkLabel(header_frame, text=h, width=w, 
                        font=(Theme.FONT_FAMILY, 10, "bold"),
                        text_color=Theme.WHITE).pack(side="left", padx=2, pady=8)
        
        # Contenedor de órdenes
        ordenes_container = ctk.CTkScrollableFrame(detalle_frame, fg_color=Theme.BACKGROUND_LIGHT, 
                                                   height=400, corner_radius=8)
        ordenes_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        for orden in ordenes:
            orden_frame = ctk.CTkFrame(ordenes_container, fg_color=Theme.SURFACE, 
                                      corner_radius=8, border_width=1, border_color=Theme.BORDER)
            orden_frame.pack(fill="x", pady=3, padx=2)
            
            # ID
            ctk.CTkLabel(orden_frame, text=f"#{orden[0]}", width=50,
                        text_color=Theme.PRIMARY, font=(Theme.FONT_FAMILY, 10, "bold")).pack(side="left", padx=2)
            
            # FECHA
            fecha = orden[1][:10] if orden[1] else "-"
            ctk.CTkLabel(orden_frame, text=fecha, width=100,
                        text_color=Theme.TEXT_PRIMARY, font=(Theme.FONT_FAMILY, 10)).pack(side="left", padx=2)
            
            # CLIENTE
            cliente = (orden[2] or "---")[:20]
            ctk.CTkLabel(orden_frame, text=cliente, width=150,
                        text_color=Theme.TEXT_PRIMARY, font=(Theme.FONT_FAMILY, 10)).pack(side="left", padx=2)
            
            # EQUIPO
            equipo = (orden[3] or "---")[:25]
            ctk.CTkLabel(orden_frame, text=equipo, width=200,
                        text_color=Theme.TEXT_PRIMARY, font=(Theme.FONT_FAMILY, 10)).pack(side="left", padx=2)
            
            # TOTAL
            total = orden[4] or 0
            ctk.CTkLabel(orden_frame, text=f"${int(total):,}".replace(",", "."), width=90,
                        text_color=Theme.SUCCESS, font=(Theme.FONT_FAMILY, 10, "bold")).pack(side="left", padx=2)
            
            # COSTOS
            costos = (orden[5] or 0) + (orden[6] or 0)
            ctk.CTkLabel(orden_frame, text=f"-${int(costos):,}".replace(",", "."), width=80,
                        text_color=Theme.DANGER, font=(Theme.FONT_FAMILY, 10)).pack(side="left", padx=2)
            
            # COMISIÓN
            comision = orden[8] or 0
            ctk.CTkLabel(orden_frame, text=f"${int(comision):,}".replace(",", "."), width=100,
                        text_color=Theme.PRIMARY, font=(Theme.FONT_FAMILY, 10, "bold")).pack(side="left", padx=2)
            
            # Botón VER
            ctk.CTkButton(orden_frame, text="👁️", width=80, height=28,
                         **Theme.get_button_style("secondary"),
                         command=lambda oid=orden[0]: self.show_order_detail(oid)).pack(side="left", padx=2, pady=2)
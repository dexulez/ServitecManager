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
        
        self.setup_orders_tab()
        self.setup_sales_tab()

    def refresh(self):
        self.load_orders()
        self.load_sales()
    
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
        cols = [("ID", 90), ("FECHA", 110), ("CLIENTE", 170), ("EQUIPO", 170), ("TÉCNICO", 110), ("OBSERVACIONES", 390), ("ESTADO", 120), ("CONDICIÓN", 130), ("F.ENTREGA", 100), ("TOTAL", 80), ("VER", 80)]
        for c, w in cols: ctk.CTkLabel(h, text=c, width=w, font=(Theme.FONT_FAMILY, 12, "bold"), text_color=Theme.WHITE, anchor="center").pack(side="left", padx=1)
        
        self.scroll_orders = ctk.CTkScrollableFrame(self.tab_orders, fg_color=Theme.BACKGROUND_LIGHT, corner_radius=Theme.RADIUS_MEDIUM); self.scroll_orders.pack(fill="both", expand=True)
        self.load_orders()

    def load_orders(self, filter_txt=""):
        for w in self.scroll_orders.winfo_children(): w.destroy()
        data = self.logic.reports.get_full_history_orders()

        filter_txt = filter_txt.upper()
        ESTADOS = ['En proceso', 'Reparado', 'Sin Solución', 'Entregado']
        CONDICIONES = ['Solucionado', 'Sin Solución']
        for row in data:
            # 0:id, 1:fecha, 2:cliente, 3:equipo, 4:tecnico, 5:estado, 6:condicion, 7:observacion, 8:fecha_entrega, 9:total, 10:fecha_cierre
            oid = row[0]
            # Filtros
            if self.filtro_estado and row[5] != self.filtro_estado:
                continue
            if filter_txt and (filter_txt not in str(row[0]) and filter_txt not in str(row[2] or "") and filter_txt not in str(row[3])): continue

            f = ctk.CTkFrame(self.scroll_orders, **Theme.get_card_style()); f.pack(fill="x", pady=2)
            ctk.CTkLabel(f, text=f"#{row[0]}", width=90, text_color=Theme.PRIMARY, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"), anchor="center").pack(side="left", padx=1)
            ctk.CTkLabel(f, text=row[1][:10], width=110, text_color=Theme.TEXT_PRIMARY, anchor="center").pack(side="left", padx=1)
            ctk.CTkLabel(f, text=row[2] or "---", width=170, text_color=Theme.TEXT_PRIMARY, anchor="center").pack(side="left", padx=1)
            ctk.CTkLabel(f, text=row[3], width=170, text_color=Theme.TEXT_PRIMARY, anchor="center").pack(side="left", padx=1)
            ctk.CTkLabel(f, text=row[4] or "---", width=110, text_color=Theme.TEXT_SECONDARY, anchor="center").pack(side="left", padx=1)
            
            # Observaciones (truncadas y limpias)
            obs_raw = row[7] or "-"
            obs_clean = obs_raw.replace("FALLA: |", "").replace("FALLA:", "").replace("|", "").strip()
            obs_text = obs_clean[:60] + "..." if len(obs_clean) > 60 else obs_clean
            ctk.CTkLabel(f, text=obs_text, width=390, text_color=Theme.TEXT_PRIMARY, anchor="w").pack(side="left", padx=1)

            # Estado (ComboBox editable)
            estado_var = ctk.StringVar(value=row[5])
            estado_cb = ctk.CTkComboBox(f, values=ESTADOS, variable=estado_var, width=120)
            estado_cb.pack(side="left", padx=1, pady=4)

            # Condición (ComboBox dependiente)
            condicion_var = ctk.StringVar(value=row[6] or "")
            condicion_cb = ctk.CTkComboBox(f, values=CONDICIONES, variable=condicion_var, width=130)
            condicion_cb.pack(side="left", padx=1, pady=4)

            # Inicializar estado de condición
            def update_condicion_field(ev=None, oid=oid, estado_var=estado_var, condicion_var=condicion_var, condicion_cb=condicion_cb):
                if estado_var.get() == "Entregado":
                    condicion_cb.configure(state="normal")
                    # Regla de negocio
                    orden = self.logic.bd.OBTENER_UNO("SELECT estado FROM ordenes WHERE id = ?", (oid,))
                    prev_estado = orden[0] if orden else None
                    if prev_estado == "Reparado":
                        condicion_var.set("Solucionado")
                    elif prev_estado == "Sin Solución":
                        condicion_var.set("Sin Solución")
                else:
                    condicion_var.set("")
                    condicion_cb.configure(state="disabled")

            # Evento de cambio de estado
            def on_estado_change(choice, oid=oid, estado_var=estado_var, condicion_var=condicion_var):
                # Si pasa a Entregado, aplicar lógica de condición
                if choice == "Entregado":
                    orden = self.logic.bd.OBTENER_UNO("SELECT estado FROM ordenes WHERE id = ?", (oid,))
                    prev_estado = orden[0] if orden else None
                    if prev_estado == "Reparado":
                        condicion_var.set("Solucionado")
                    elif prev_estado == "Sin Solución":
                        condicion_var.set("Sin Solución")
                    condicion_cb.configure(state="normal")
                else:
                    condicion_var.set("")
                    condicion_cb.configure(state="disabled")
                # Guardar en base de datos
                self.logic.orders.ACTUALIZAR_ESTADO(oid, choice, condicion_var.get() if choice == "Entregado" else None)
                if self.app_ref:
                    self.app_ref.refresh_all_frames()

            estado_cb.configure(command=on_estado_change)
            # Evento de cambio de condición
            def on_condicion_change(choice, oid=oid, estado_var=estado_var, condicion_var=condicion_var):
                if estado_var.get() == "Entregado":
                    self.logic.orders.ACTUALIZAR_ESTADO(oid, estado_var.get(), choice)
                    if self.app_ref:
                        self.app_ref.refresh_all_frames()

            condicion_cb.configure(command=on_condicion_change)
            # Inicializar estado de campo condición
            update_condicion_field()
            
            # Fecha de entrega
            fecha_ent = row[8][:10] if row[8] else "-"
            ctk.CTkLabel(f, text=fecha_ent, width=100, text_color=Theme.TEXT_PRIMARY, anchor="center").pack(side="left", padx=1)

            total = f"${int(row[9]):,}".replace(",", ".") if row[9] else "$0"
            ctk.CTkLabel(f, text=total, width=80, text_color=Theme.TEXT_PRIMARY, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"), anchor="center").pack(side="left", padx=1)

            # Botón ver
            ctk.CTkButton(f, text="👁️", width=80, height=30, **Theme.get_button_style("secondary"), command=lambda oid=row[0]: self.show_order_detail(oid)).pack(side="left", padx=1)

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
                
            add_sec("CLIENTE", f"Nombre: {tdata[15]}\nRUT: {tdata[14]}\nTeléfono: {tdata[16]}\nEmail: {tdata[17]}")
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
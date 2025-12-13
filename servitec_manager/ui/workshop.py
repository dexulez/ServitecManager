import customtkinter as ctk
from tkinter import messagebox
from .theme import Theme

class WorkshopFrame(ctk.CTkFrame):
    def __init__(self, parent, logic, current_user, app_ref=None):
        super().__init__(parent, fg_color=Theme.BACKGROUND)
        self.logic = logic
        self.current_user = current_user
        self.app_ref = app_ref
        self.selected_order_id = None
        self.current_order_data = None 
        
        # Variables
        self.var_total = ctk.StringVar()
        self.var_abono = ctk.StringVar()
        self.var_pending_display = ctk.StringVar()
        
        self.var_cost_part = ctk.StringVar()
        self.var_cost_ship = ctk.StringVar()
        
        self.var_pay_cash = ctk.StringVar()
        self.var_pay_transf = ctk.StringVar()
        self.var_pay_card = ctk.StringVar()
        
        self.var_iva = ctk.BooleanVar()

        # Traces
        vars_to_trace = [self.var_total, self.var_abono, self.var_cost_part, self.var_cost_ship, 
                         self.var_pay_cash, self.var_pay_transf, self.var_pay_card]
        
        for v in vars_to_trace:
            v.trace("w", lambda *a, var=v: self.format_live(var))
            
        self.var_pay_card.trace("w", self.on_card_payment_change)

        self.setup_ui()
        self.load_orders()

    def refresh(self):
        self.load_orders()

    def focus_on_order(self, order_id):
        full_order = self.logic.orders.get_order_by_id(order_id)
        if full_order: self.show_details(full_order)
        else: messagebox.showerror("ERROR", "NO SE PUDO CARGAR LA ORDEN SOLICITADA.")

    def on_card_payment_change(self, *args):
        try:
            if self.clean_money(self.var_pay_card.get()) > 0:
                self.var_iva.set(True); self.chk_iva.configure(state="disabled")
            else: self.chk_iva.configure(state="normal")
        except: pass

    def auto_fill_payment(self, target, others):
        try:
            tot = self.clean_money(self.var_total.get())
            abo = self.clean_money(self.var_abono.get())
            pendiente_real = max(0, tot - abo)
            sum_others = sum([self.clean_money(v.get()) for v in others])
            target.set(int(max(0, pendiente_real - sum_others))) 
        except: pass

    def format_live(self, var):
        raw = var.get().replace(".", "")
        if not raw.isdigit():
            if raw: var.set(''.join(filter(str.isdigit, raw)))
            return
        try:
            val = int(raw)
            if var.get() != f"{val:,}".replace(",", "."): var.set(f"{val:,}".replace(",", "."))
        except: pass

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=0); self.grid_columnconfigure(1, weight=1); self.grid_rowconfigure(0, weight=1)

        left_panel = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color=Theme.SURFACE, border_width=2, border_color=Theme.BORDER)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        # Header
        header = ctk.CTkFrame(left_panel, fg_color="transparent")
        header.pack(fill="x", pady=(Theme.PADDING_LARGE, Theme.PADDING_MEDIUM), padx=Theme.PADDING_LARGE)
        ctk.CTkLabel(header, text="🔧 ÓRDENES DE SERVICIO", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"), text_color=Theme.TEXT_PRIMARY).pack()
        
        # Separator
        ctk.CTkFrame(left_panel, height=2, fg_color=Theme.DIVIDER).pack(fill="x", pady=(0, Theme.PADDING_MEDIUM))
        
        ctk.CTkButton(left_panel, text="🔄 ACTUALIZAR", command=self.load_orders, **Theme.get_button_style("secondary"), height=40).pack(pady=5, padx=20, fill="x")
        self.scrollable_frame = ctk.CTkScrollableFrame(left_panel, fg_color="transparent")
        self.scrollable_frame.pack(fill="both", expand=True, pady=10)

        self.right_panel = ctk.CTkFrame(self, fg_color=Theme.SURFACE, corner_radius=Theme.RADIUS_LARGE, border_width=2, border_color=Theme.BORDER)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # Header
        header_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        header_frame.pack(fill="x", pady=Theme.PADDING_LARGE, padx=Theme.PADDING_LARGE)
        self.lbl_title = ctk.CTkLabel(header_frame, text="⚙️ SELECCIONE ORDEN", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H1, "bold"), anchor="w", text_color=Theme.TEXT_PRIMARY)
        self.lbl_title.pack(fill="x")
        
        # Separator
        ctk.CTkFrame(self.right_panel, height=2, fg_color=Theme.DIVIDER).pack(fill="x", pady=(0, Theme.PADDING_MEDIUM))

        info_container = ctk.CTkFrame(self.right_panel, **Theme.get_card_style())
        info_container.pack(fill="x", pady=5, padx=Theme.PADDING_LARGE)
        ctk.CTkLabel(info_container, text="👤 CLIENTE:", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"), text_color="#000000").grid(row=0, column=0, sticky="w", padx=15, pady=(15,0))
        self.lbl_client = ctk.CTkLabel(info_container, text="---", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_MEDIUM), text_color=Theme.TEXT_PRIMARY)
        self.lbl_client.grid(row=1, column=0, sticky="w", padx=15, pady=(0,10))
        ctk.CTkLabel(info_container, text="📱 EQUIPO / SERIE:", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"), text_color="#000000").grid(row=0, column=1, sticky="w", padx=15, pady=(15,0))
        self.lbl_device = ctk.CTkLabel(info_container, text="---", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_MEDIUM), text_color=Theme.TEXT_PRIMARY)
        self.lbl_device.grid(row=1, column=1, sticky="w", padx=15, pady=(0,10))
        info_container.grid_columnconfigure(0, weight=1); info_container.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.right_panel, text="📋 REPORTE TÉCNICO:", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"), anchor="w", text_color="#000000").pack(fill="x", pady=(15, 5), padx=Theme.PADDING_LARGE)
        self.lbl_fault = ctk.CTkTextbox(self.right_panel, height=80, fg_color=Theme.BACKGROUND_LIGHT, text_color=Theme.TEXT_PRIMARY, corner_radius=Theme.RADIUS_MEDIUM, border_width=1, border_color=Theme.BORDER)
        self.lbl_fault.pack(fill="x", padx=Theme.PADDING_LARGE)

        status_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        status_frame.pack(fill="x", pady=15, padx=(10, 0))  # 10mm = ~28 pixeles de padding izquierdo
        ctk.CTkLabel(status_frame, text="ESTADO:", font=("Arial", 12, "bold"), text_color="#000000").pack(side="left")
        self.combo_status = ctk.CTkComboBox(status_frame, values=["PENDIENTE", "EN REPARACION", "ESPERA DE REPUESTO", "REPARADO", "SIN SOLUCION", "ENTREGADO"], width=180)
        self.combo_status.pack(side="left", padx=5)
        ctk.CTkLabel(status_frame, text="TÉCNICO:", font=("Arial", 12, "bold"), text_color="#000000").pack(side="left", padx=(20, 5))
        
        tech_data = self.logic.get_technicians()
        self.tech_map = {t[1]: t[0] for t in tech_data}
        self.tech_com_map = {t[0]: t[2] for t in tech_data}
        
        self.combo_tech = ctk.CTkComboBox(status_frame, values=list(self.tech_map.keys()), width=180)
        self.combo_tech.pack(side="left", padx=5)
        
        # Botones de acción
        btn_container = ctk.CTkFrame(status_frame, fg_color="transparent")
        btn_container.pack(side="left", padx=20)
        
        ctk.CTkButton(btn_container, text="💾 GUARDAR", command=self.update_order_info, width=140, **Theme.get_button_style("primary"), height=40).pack(side="left", padx=3)
        ctk.CTkButton(btn_container, text="💰 GUARDAR Y COBRAR", command=self.save_and_go_to_pos, width=160, fg_color="#FF6B35", hover_color="#E85A2A", height=40, text_color="white", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold")).pack(side="left", padx=3)

        finance_frame = ctk.CTkFrame(self.right_panel, **Theme.get_card_style())
        finance_frame.pack(fill="both", expand=True, pady=10, padx=Theme.PADDING_LARGE)
        ctk.CTkLabel(finance_frame, text="💰 CIERRE DE CAJA Y PAGOS", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"), text_color="#000000").pack(pady=15)
        fin_grid = ctk.CTkFrame(finance_frame, fg_color="transparent")
        fin_grid.pack(fill="x", padx=20)

        ctk.CTkLabel(fin_grid, text="TOTAL SERVICIO ($)", text_color="#000000", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, sticky="w")
        self.entry_total = ctk.CTkEntry(fin_grid, textvariable=self.var_total, font=("Arial", 16, "bold"), width=160)
        self.entry_total.grid(row=1, column=0, padx=10, pady=(0,10), sticky="w")

        ctk.CTkLabel(fin_grid, text="ABONO YA PAGADO ($)", text_color="#000000", font=("Arial", 12, "bold")).grid(row=0, column=1, padx=10, sticky="w")
        
        self.entry_abono = ctk.CTkEntry(
            fin_grid, 
            textvariable=self.var_abono, 
            font=("Arial", 16, "bold"), 
            state="disabled", 
            fg_color="gray25", 
            text_color="white", 
            width=160
        )
        self.entry_abono.grid(row=1, column=1, padx=10, pady=(0,10), sticky="w")

        self.lbl_pending_big = ctk.CTkLabel(fin_grid, textvariable=self.var_pending_display, font=("Arial", 24, "bold"), text_color="#FF5555", fg_color="gray20", corner_radius=8, height=50)
        self.lbl_pending_big.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=15)

        ctk.CTkLabel(fin_grid, text="COSTO REPUESTO ($)", text_color="#000000", font=("Arial", 12, "bold")).grid(row=3, column=0, padx=10, sticky="w")
        self.entry_cost_part = ctk.CTkEntry(fin_grid, textvariable=self.var_cost_part, font=("Arial", 12, "bold")).grid(row=4, column=0, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(fin_grid, text="COSTO ENVÍO ($)", text_color="#000000", font=("Arial", 12, "bold")).grid(row=5, column=0, padx=10, sticky="w")
        self.entry_cost_ship = ctk.CTkEntry(fin_grid, textvariable=self.var_cost_ship, font=("Arial", 12, "bold")).grid(row=6, column=0, padx=10, pady=5, sticky="ew")

        lbl_cash = ctk.CTkLabel(fin_grid, text="PAGO EFECTIVO ($) [Click Auto]", text_color="#000000", font=("Arial", 12, "bold"), cursor="hand2")
        lbl_cash.grid(row=3, column=1, padx=10, sticky="w")
        lbl_cash.bind("<Button-1>", lambda e: self.auto_fill_payment(self.var_pay_cash, [self.var_pay_transf, self.var_pay_card]))
        ctk.CTkEntry(fin_grid, textvariable=self.var_pay_cash, font=("Arial", 12, "bold")).grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        lbl_trf = ctk.CTkLabel(fin_grid, text="PAGO TRANSFERENCIA ($) [Click Auto]", text_color="#000000", font=("Arial", 12, "bold"), cursor="hand2")
        lbl_trf.grid(row=5, column=1, padx=10, sticky="w")
        lbl_trf.bind("<Button-1>", lambda e: self.auto_fill_payment(self.var_pay_transf, [self.var_pay_cash, self.var_pay_card]))
        ctk.CTkEntry(fin_grid, textvariable=self.var_pay_transf, font=("Arial", 12, "bold")).grid(row=6, column=1, padx=10, pady=5, sticky="ew")

        lbl_crd = ctk.CTkLabel(fin_grid, text="PAGO TARJETA ($) [Click Auto]", text_color="#000000", font=("Arial", 12, "bold"), cursor="hand2")
        lbl_crd.grid(row=7, column=1, padx=10, sticky="w")
        lbl_crd.bind("<Button-1>", lambda e: self.auto_fill_payment(self.var_pay_card, [self.var_pay_cash, self.var_pay_transf]))
        ctk.CTkEntry(fin_grid, textvariable=self.var_pay_card, font=("Arial", 12, "bold")).grid(row=8, column=1, padx=10, pady=5, sticky="ew")

        self.chk_iva = ctk.CTkCheckBox(fin_grid, text="EMITIR BOLETA/FACTURA (IVA 19%)", variable=self.var_iva, text_color="white")
        self.chk_iva.grid(row=9, column=0, columnspan=2, pady=15)
        fin_grid.grid_columnconfigure(0, weight=1); fin_grid.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(finance_frame, text="CALCULAR COMISIÓN (VISTA PREVIA)", command=self.preview_commission).pack(pady=5)
        self.lbl_preview = ctk.CTkLabel(finance_frame, text="", font=("Arial", 12, "bold"), text_color="gray")
        self.lbl_preview.pack(pady=5)

        self.btn_close = ctk.CTkButton(finance_frame, text="✅ CERRAR ORDEN Y GUARDAR", command=self.close_order, **Theme.get_button_style("success"), height=50)
        self.btn_close.pack(fill="x", padx=40, pady=(10, 20))

    def format_money(self, value):
        try: return f"{int(value):,}".replace(",", ".")
        except: return "0"
    def clean_money(self, text_val):
        if not text_val: return 0.0
        return float(str(text_val).replace(".", ""))

    def load_orders(self):
        for w in self.scrollable_frame.winfo_children(): w.destroy()
        orders = self.logic.orders.get_orders_by_tech(self.current_user)
        if not orders or len(orders) == 0:
            # Mostrar mensaje cuando no hay órdenes
            msg_frame = ctk.CTkFrame(self.scrollable_frame, **Theme.get_card_style())
            msg_frame.pack(fill="x", pady=10, padx=10)
            ctk.CTkLabel(msg_frame, text="📋 NO HAY ÓRDENES ACTIVAS", 
                        font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold"),
                        text_color=Theme.TEXT_SECONDARY).pack(pady=40)
            ctk.CTkLabel(msg_frame, text="Las órdenes pendientes y en proceso aparecerán aquí",
                        font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL),
                        text_color=Theme.TEXT_SECONDARY).pack(pady=(0,20))
            return
        for order in orders:
            oid = order[0]; cliente = order[14] if len(order)>14 and order[14] else "GENÉRICO"; modelo = f"{order[5]} {order[6]}"; estado = order[9]
            card = ctk.CTkFrame(self.scrollable_frame, **Theme.get_card_style())
            card.pack(fill="x", pady=5, padx=5)
            ctk.CTkLabel(card, text=f"🔧 ORDEN #{oid}", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"), text_color=Theme.PRIMARY).pack(anchor="w", padx=10, pady=(5,0))
            ctk.CTkLabel(card, text=f"{cliente.upper() if cliente else 'GENÉRICO'}", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL), text_color=Theme.TEXT_PRIMARY).pack(anchor="w", padx=10)
            ctk.CTkLabel(card, text=f"{modelo.upper()}", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL), text_color=Theme.TEXT_SECONDARY).pack(anchor="w", padx=10)
            col = Theme.get_status_color(estado)
            text_col = Theme.get_status_text_color(estado)
            ctk.CTkButton(card, text=f"👁️ VER DETALLE [{estado}]", command=lambda o=order: self.show_details(o), fg_color=col, text_color=text_col, height=30, corner_radius=Theme.RADIUS_SMALL, hover_color=Theme.PRIMARY_DARK).pack(fill="x", padx=5, pady=5)

    def clear_right_panel(self):
        self.selected_order_id = None
        self.lbl_title.configure(text="SELECCIONE ORDEN")
        self.lbl_client.configure(text="---")
        self.lbl_device.configure(text="---")
        self.lbl_fault.delete("0.0", "end")
        self.var_total.set("")
        self.var_abono.set("")
        self.var_pending_display.set("")
        self.var_cost_part.set("")
        self.var_cost_ship.set("")
        self.var_pay_cash.set("")
        self.var_pay_transf.set("")
        self.var_pay_card.set("")
        self.var_iva.set(False)
        self.lbl_preview.configure(text="")
        self.chk_iva.configure(state="normal")

    def show_details(self, order):
        self.current_order_data = order
        self.selected_order_id = order[0]
        cliente = order[14] if len(order)>14 else "DESCONOCIDO"; equipo = f"{order[4]} {order[5]} {order[6]}"; serie = order[7]; obs = order[8]; estado = order[9]; 
        presupuesto = order[12]; abono = order[13]; tech_id = order[2]

        self.lbl_title.configure(text=f"ORDEN #{self.selected_order_id}")
        self.lbl_client.configure(text=cliente.upper() if cliente else "GENÉRICO")
        self.lbl_device.configure(text=f"{equipo} | SN: {serie}".upper())
        self.lbl_fault.delete("0.0", "end"); self.lbl_fault.insert("0.0", obs.upper())
        
        tech_name = "DESCONOCIDO"
        for name, tid in self.tech_map.items():
            if tid == tech_id: tech_name = name; break
        self.combo_status.set(estado); self.combo_tech.set(tech_name)

        self.var_total.set(self.format_money(presupuesto))
        self.var_abono.set(self.format_money(abono)) 
        
        pendiente = max(0, presupuesto - abono)
        self.var_pending_display.set(f"RESTA POR PAGAR: ${self.format_money(pendiente)}")

        self.var_cost_part.set("0"); self.var_cost_ship.set("0")
        self.var_pay_cash.set("0"); self.var_pay_transf.set("0"); self.var_pay_card.set("0")
        self.var_iva.set(False); self.chk_iva.configure(state="normal")
        self.lbl_preview.configure(text="")

    def update_order_info(self):
        if not self.selected_order_id: 
            return
        
        # Obtener estado anterior y nuevo
        estado_anterior = self.current_order_data[9] if self.current_order_data else None
        estado_nuevo = self.combo_status.get()
        
        # Actualizar estado
        self.logic.orders.update_status(self.selected_order_id, estado_nuevo)
        
        # Actualizar técnico
        tech_name = self.combo_tech.get()
        new_tech_id = self.tech_map.get(tech_name)
        if new_tech_id: 
            self.logic.orders.update_order_tech(self.selected_order_id, new_tech_id)
        
        # Actualizar current_order_data con el nuevo estado
        if self.current_order_data:
            self.current_order_data = list(self.current_order_data)
            self.current_order_data[9] = estado_nuevo
            self.current_order_data = tuple(self.current_order_data)
        
        # Recargar órdenes para refrescar colores
        self.load_orders()
        
        # Refrescar detalles de la orden actual
        orden_actualizada = self.logic.orders.get_order_by_id(self.selected_order_id)
        if orden_actualizada:
            self.show_details(orden_actualizada)
        
        # Actualizar todas las vistas
        if self.app_ref:
            self.app_ref.refresh_all_frames()
        
        messagebox.showinfo("Info", "Datos actualizados")
        
        # Si cambió el estado, preguntar si desea notificar al cliente
        if estado_anterior and estado_anterior != estado_nuevo:
            if messagebox.askyesno("Notificar Cliente", 
                                  f"El estado cambió de '{estado_anterior}' a '{estado_nuevo}'.\n\n¿Desea notificar al cliente?"):
                self.mostrar_opciones_notificacion_cliente(estado_nuevo)

    def save_and_go_to_pos(self):
        """Guarda los cambios de la orden y abre el POS con el servicio en el carrito"""
        if not self.selected_order_id:
            messagebox.showerror("Error", "No hay orden seleccionada")
            return
        
        # Obtener valores financieros actuales del formulario
        try:
            total_servicio = self.clean_money(self.var_total.get())
            abono_pagado = self.clean_money(self.var_abono.get())
            costo_repuesto = self.clean_money(self.var_cost_part.get())
            costo_envio = self.clean_money(self.var_cost_ship.get())
            pago_efectivo = self.clean_money(self.var_pay_cash.get())
            pago_transferencia = self.clean_money(self.var_pay_transf.get())
            pago_tarjeta = self.clean_money(self.var_pay_card.get())
            con_iva = self.var_iva.get()
        except Exception as e:
            messagebox.showerror("Error", f"Error al leer valores: {e}")
            return
        
        # Primero actualizar la información de la orden
        estado_nuevo = self.combo_status.get()
        self.logic.orders.update_status(self.selected_order_id, estado_nuevo)
        
        tech_name = self.combo_tech.get()
        new_tech_id = self.tech_map.get(tech_name)
        if new_tech_id:
            self.logic.orders.update_order_tech(self.selected_order_id, new_tech_id)
        
        # Actualizar todas las vistas
        if self.app_ref:
            self.app_ref.refresh_all_frames()
        
        # Obtener datos de la orden actualizada
        orden = self.logic.orders.get_order_by_id(self.selected_order_id)
        if not orden:
            messagebox.showerror("Error", "No se pudo obtener la orden")
            return
        
        # Extraer información necesaria para el POS
        order_id = orden[0]
        cliente_nombre = orden[14] if len(orden) > 14 and orden[14] else "GENÉRICO"
        equipo = f"{orden[4]} {orden[5]} {orden[6]}"  # tipo + marca + modelo
        presupuesto = total_servicio if total_servicio > 0 else (orden[12] if len(orden) > 12 else 0)
        
        # Calcular monto pendiente (total - abono ya pagado)
        monto_pendiente = presupuesto - abono_pagado
        
        # Navegar al POS
        app = self.master.master  # Obtener referencia a la aplicación principal
        if hasattr(app, 'mostrar_frame') and hasattr(app, 'frames') and "POS" in app.frames:
            app.mostrar_frame("POS")
            
            # Agregar el servicio al carrito del POS
            pos_frame = app.frames["POS"]
            if hasattr(pos_frame, 'add_to_cart'):
                # Crear estructura de servicio con toda la información financiera
                service_data = (order_id, f"ORDEN #{order_id} - {equipo}", monto_pendiente)
                details = {
                    'cliente': cliente_nombre,
                    'equipo': equipo,
                    'estado': estado_nuevo,
                    'rep': costo_repuesto,
                    'env': costo_envio,
                    'iva': con_iva,
                    'card': pago_tarjeta > 0,
                    'total_original': presupuesto,
                    'abono': abono_pagado,
                    'efectivo_actual': pago_efectivo,
                    'transferencia_actual': pago_transferencia,
                    'tarjeta_actual': pago_tarjeta
                }
                pos_frame.add_to_cart(service_data, is_service=True, details=details)
                
                # Mensaje informativo
                msg = f"Orden #{order_id} agregada al carrito\n\n"
                msg += f"Total servicio: ${self.format_money(presupuesto)}\n"
                msg += f"Abono pagado: ${self.format_money(abono_pagado)}\n"
                msg += f"Pendiente de pago: ${self.format_money(monto_pendiente)}"
                messagebox.showinfo("Éxito", msg)
            else:
                messagebox.showwarning("Aviso", "No se pudo agregar al carrito automáticamente")
        else:
            messagebox.showerror("Error", "No se pudo acceder al módulo POS")

    def get_financial_values(self):
        try:
            tot = self.clean_money(self.var_total.get())
            rep = self.clean_money(self.var_cost_part.get())
            env = self.clean_money(self.var_cost_ship.get())
            efec = self.clean_money(self.var_pay_cash.get())
            transf = self.clean_money(self.var_pay_transf.get())
            tarj = self.clean_money(self.var_pay_card.get())
            return tot, rep, env, efec, transf, tarj
        except: return None

    def get_current_tech_percent(self):
        tech_name = self.combo_tech.get()
        tid = self.tech_map.get(tech_name)
        if tid and tid in self.tech_com_map: return self.tech_com_map[tid]
        return 0

    def preview_commission(self):
        vals = self.get_financial_values()
        if not vals: return
        tot, rep, env, _, _, tarj = vals
        banco = tarj * 0.0295
        utilidad_operativa = (tot - banco) - rep - env
        utilidad_comisionable = utilidad_operativa
        if self.var_iva.get(): utilidad_comisionable = utilidad_operativa * 0.81 
        pct = self.get_current_tech_percent()
        com = max(0, utilidad_comisionable * (pct/100))
        self.lbl_preview.configure(text=f"UTILIDAD: ${int(utilidad_comisionable):,} | COMISIÓN ({pct}%): ${int(com):,}".replace(",", "."))
    
    def mostrar_opciones_notificacion_cliente(self, estado):
        """Muestra ventana con opciones para notificar al cliente sobre cambio de estado"""
        if not self.selected_order_id or not self.current_order_data:
            return
        
        # Obtener datos del cliente y orden
        cliente_id = self.current_order_data[1]
        cliente_data = self.logic.bd.OBTENER_TODOS("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
        
        if not cliente_data or len(cliente_data) == 0:
            messagebox.showwarning("Sin Cliente", "No se encontró información del cliente")
            return
        
        cliente = cliente_data[0]
        nombre_cliente = cliente[2] if len(cliente) > 2 else "Cliente"
        telefono = cliente[3] if len(cliente) > 3 else ""
        email = cliente[4] if len(cliente) > 4 else ""
        
        # Datos de la orden
        tipo_dispositivo = self.current_order_data[4]
        marca = self.current_order_data[5]
        modelo = self.current_order_data[6]
        
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
            text=f"Orden #{self.selected_order_id}: {tipo_dispositivo} {marca} {modelo}",
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
                command=lambda: [win.destroy(), self.enviar_whatsapp_cambio_estado(cliente, estado, nota_text.get("1.0", "end").strip())],
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
                command=lambda: [win.destroy(), self.enviar_email_cambio_estado(cliente, estado, nota_text.get("1.0", "end").strip())],
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
    
    def enviar_whatsapp_cambio_estado(self, cliente, estado, nota_adicional=""):
        """Envía WhatsApp al cliente informando cambio de estado"""
        if not self.logic.mensajeria:
            messagebox.showerror("Error", "Módulo de mensajería no disponible")
            return
        
        from datetime import datetime
        
        nombre_cliente = cliente[2] if len(cliente) > 2 else "Cliente"
        telefono = cliente[3] if len(cliente) > 3 else ""
        
        # Datos de la orden
        tipo_dispositivo = self.current_order_data[4]
        marca = self.current_order_data[5]
        modelo = self.current_order_data[6]
        
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
        mensaje += f"📋 Orden #{self.selected_order_id}\n\n"
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
    
    def enviar_email_cambio_estado(self, cliente, estado, nota_adicional=""):
        """Envía Email al cliente informando cambio de estado"""
        if not self.logic.mensajeria:
            messagebox.showerror("Error", "Módulo de mensajería no disponible")
            return
        
        from datetime import datetime
        
        nombre_cliente = cliente[2] if len(cliente) > 2 else "Cliente"
        email = cliente[4] if len(cliente) > 4 else ""
        
        # Datos de la orden
        tipo_dispositivo = self.current_order_data[4]
        marca = self.current_order_data[5]
        modelo = self.current_order_data[6]
        
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
        
        asunto = f"Actualización Orden #{self.selected_order_id} - {estado}"
        
        mensaje = f"Estimado/a {nombre_cliente},\n\n"
        mensaje += f"Le informamos sobre su equipo:\n\n"
        mensaje += f"Equipo: {tipo_dispositivo} {marca} {modelo}\n"
        mensaje += f"Orden: #{self.selected_order_id}\n\n"
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

    def close_order(self):
        if not self.selected_order_id: return
        vals = self.get_financial_values()
        if not vals: messagebox.showerror("ERROR", "VERIFIQUE NÚMEROS"); return
        tot, rep, env, efec, transf, tarj = vals
        
        abono = self.clean_money(self.var_abono.get())
        pendiente = tot - abono
        pagado_ahora = efec + transf + tarj
        
        if pagado_ahora != pendiente:
            diff = pendiente - pagado_ahora
            messagebox.showwarning("ERROR CAJA", f"PAGO NO CUADRA.\nTOTAL SERV: ${self.format_money(tot)}\n- ABONO: ${self.format_money(abono)}\n= PENDIENTE: ${self.format_money(pendiente)}\n\nPAGADO AHORA: ${self.format_money(pagado_ahora)}\nDIFERENCIA: ${self.format_money(diff)}")
            return

        if messagebox.askyesno("CERRAR ORDEN", "Finalizar orden?"):
            self.update_order_info() 
            pct = self.get_current_tech_percent()
            self.logic.orders.close_order_finances(self.selected_order_id, tot, rep, env, efec, transf, tarj, self.var_iva.get(), pct)
            messagebox.showinfo("ÉXITO", "Cerrado")
            
            # LIMPIEZA AUTOMÁTICA DE PANTALLA
            self.load_orders() 
            self.clear_right_panel()
import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import datetime
from pdf_generator_v2 import PDFGeneratorV2
from .theme import Theme

class ReceptionFrame(ctk.CTkFrame):
    def __init__(self, parent, logic, current_user=None):
        super().__init__(parent, fg_color=Theme.BACKGROUND)
        self.logic = logic
        self.current_user = current_user
        self.selected_client_rut = None
        self.editing_order_id = None  # Para rastrear si estamos editando una orden
        
        # Mapas de precios
        self.services_map = {}
        self.parts_map = {}
        
        self.device_types = sorted(["CELULAR", "NOTEBOOK", "PC ESCRITORIO", "TABLET", "CONSOLA", "PARLANTE", "IMPRESORA", "SMARTWATCH"])
        self.device_types.append("OTRO")  # OTRO siempre al final
        # Cargar marcas base + marcas personalizadas de la BD
        self.base_brands = ["SAMSUNG", "APPLE", "XIAOMI", "HUAWEI", "MOTOROLA", "HONOR", "OPPO", "VIVO", "REALME", "GOOGLE", "ONEPLUS", "SONY", "LG", "NOKIA", "ASUS", "LENOVO", "HP", "DELL", "ACER", "JBL", "BOSE", "NINTENDO", "PLAYSTATION", "XBOX"]
        self.brands = self.load_all_brands()

        self.var_search = ctk.StringVar(); self.var_rut = ctk.StringVar(); self.var_name = ctk.StringVar()
        self.var_tel = ctk.StringVar(); self.var_email = ctk.StringVar(); self.var_model = ctk.StringVar()
        self.var_serial = ctk.StringVar(); self.var_fault = ctk.StringVar()
        self.var_price = ctk.StringVar(); self.var_discount = ctk.StringVar(); self.var_deposit = ctk.StringVar()
        self.var_part_search = ctk.StringVar()
        self.var_service = ctk.StringVar(); self.var_part = ctk.StringVar()
        self.var_delivery_date = None  # Se inicializará con DateEntry 

        self.setup_uppercase_trace()
        self.setup_money_trace() 
        self.setup_ui()
        
    def refresh(self):
        """Actualiza todos los datos cuando se cambia a esta pestaña"""
        self.load_services_combo()
        self.load_parts_combo()
        # Recargar marcas por si se agregaron nuevas
        self.brands = self.load_all_brands()
        self.combo_brand.configure(values=self.brands)
        # Recargar técnicos
        techs = self.logic.get_technicians()
        self.tech_map = {t[1]: t[0] for t in techs} if techs else {}
        self.combo_tech.configure(values=list(self.tech_map.keys()) or ["ADMIN"])
        # Si hay un cliente seleccionado, recargar su historial
        if self.selected_client_rut:
            cdata = self.logic.clients.get_client(self.selected_client_rut)
            if cdata:
                self.load_client_history(cdata[0])
    
    def load_all_brands(self):
        """Carga marcas base + marcas personalizadas de la BD"""
        custom_brands = self.logic.marcas.get_custom_brands()
        all_brands = self.base_brands.copy()
        all_brands.extend(custom_brands)
        all_brands = sorted(list(set(all_brands)))  # Eliminar duplicados y ordenar
        all_brands.append("OTRO")  # OTRO siempre al final
        return all_brands

    def setup_uppercase_trace(self):
        variables = [self.var_search, self.var_rut, self.var_name, self.var_tel, self.var_email, self.var_model, self.var_serial, self.var_fault, self.var_part_search]
        for var in variables: var.trace("w", lambda *args, v=var: self.force_uppercase(v))
        
        # Validación en tiempo real para habilitar campos de equipo
        self.var_rut.trace("w", self.check_client_fields)
        self.var_name.trace("w", self.check_client_fields)

    def setup_money_trace(self):
        self.var_price.trace("w", lambda *args: self.format_live_money(self.var_price))
        self.var_discount.trace("w", lambda *args: self.format_live_money(self.var_discount))
        self.var_deposit.trace("w", lambda *args: self.format_live_money(self.var_deposit))

    def force_uppercase(self, var):
        val = var.get()
        if val != val.upper():
            var.set(val.upper())

    def format_live_money(self, var):
        raw_val = var.get().replace(".", "") 
        if not raw_val.isdigit():
            if raw_val == "": return
            clean_val = ''.join(filter(str.isdigit, raw_val))
            var.set(clean_val)
            return
        try:
            val_int = int(raw_val)
            formatted = f"{val_int:,}".replace(",", ".")
            if var.get() != formatted: var.set(formatted)
        except: pass
        
    def format_live_int(self, var):
        val = var.get()
        if not val.isdigit(): 
            clean = ''.join(filter(str.isdigit, val))
            var.set(clean)

    def format_money_val(self, val):
        try: return f"{int(val):,}".replace(",", ".")
        except: return str(val)

    def format_rut_val(self, rut_str):
        raw = rut_str.replace(".", "").replace("-", "").upper()
        raw = ''.join(filter(lambda x: x.isalnum(), raw))
        if len(raw) < 2: return raw
        cuerpo = raw[:-1]; dv = raw[-1]
        try: return f"{int(cuerpo):,}".replace(",", ".") + "-" + dv
        except: return raw

    def on_rut_focus_out(self, event): self.var_rut.set(self.format_rut_val(self.var_rut.get()))
    def on_search_focus_out(self, event):
        cur = self.var_search.get()
        if any(char.isdigit() for char in cur): self.var_search.set(self.format_rut_val(cur))

    def setup_ui(self):
        # Configurar grid principal
        self.grid_columnconfigure(0, weight=1)  # Columna izquierda expandible (CLIENTE)
        self.grid_columnconfigure(1, weight=0)  # Columna derecha fija (EQUIPO)
        self.grid_rowconfigure(0, weight=1)
        
        left_panel = ctk.CTkFrame(
            self, 
            fg_color=Theme.SURFACE,
            corner_radius=Theme.RADIUS_LARGE,
            border_width=1,
            border_color=Theme.BORDER
        )
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(20,10), pady=20)

        # Header
        header = ctk.CTkFrame(left_panel, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20,10))
        
        ctk.CTkLabel(
            header,
            text="👤 CLIENTE",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold"),
            text_color=Theme.TEXT_PRIMARY
        ).pack(anchor="w")
        
        # Separador
        ctk.CTkFrame(left_panel, height=1, fg_color=Theme.DIVIDER).pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            left_panel,
            text="BUSCAR (RUT/NOMBRE):",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
            text_color=Theme.TEXT_SECONDARY
        ).pack(anchor="w", padx=20)
        
        entry_search = ctk.CTkEntry(
            left_panel,
            textvariable=self.var_search,
            height=40,
            corner_radius=Theme.RADIUS_MEDIUM,
            border_width=1,
            border_color=Theme.BORDER,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL)
        )
        entry_search.pack(pady=(0, 10), padx=20, fill="x")
        entry_search.bind("<FocusOut>", self.on_search_focus_out)
        entry_search.bind("<Return>", lambda e: self.search_client())
        
        btn_style = Theme.get_button_style("primary")
        ctk.CTkButton(
            left_panel,
            text="🔍 BUSCAR",
            command=self.search_client,
            **btn_style,
            height=40
        ).pack(pady=5, padx=20, fill="x")

        self.scroll_results = ctk.CTkScrollableFrame(
            left_panel,
            height=60,
            fg_color=Theme.BACKGROUND_LIGHT,
            corner_radius=Theme.RADIUS_MEDIUM
        )
        self.scroll_results.pack(pady=10, padx=20, fill="x")
        
        # Separador
        ctk.CTkFrame(left_panel, height=1, fg_color=Theme.DIVIDER).pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            left_panel,
            text="DATOS DEL CLIENTE",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_MEDIUM, "bold"),
            text_color=Theme.TEXT_PRIMARY
        ).pack(pady=(15,10), padx=20, anchor="w")
        ctk.CTkLabel(left_panel, text="RUT (*):", font=("Arial", 10, "bold")).pack(anchor="w", padx=10)
        self.rut_entry = ctk.CTkEntry(left_panel, textvariable=self.var_rut)
        self.rut_entry.pack(pady=(0,3), padx=10, fill="x")
        self.rut_entry.bind("<FocusOut>", self.on_rut_focus_out)

        ctk.CTkLabel(left_panel, text="NOMBRE COMPLETO (*):", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(3,0))
        self.entry_name = ctk.CTkEntry(left_panel, textvariable=self.var_name); self.entry_name.pack(pady=(0,3), padx=10, fill="x")
        ctk.CTkLabel(left_panel, text="TELÉFONO (*):", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(3,0))
        ctk.CTkEntry(left_panel, textvariable=self.var_tel).pack(pady=(0,3), padx=10, fill="x")
        ctk.CTkLabel(left_panel, text="EMAIL:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(3,0))
        ctk.CTkEntry(left_panel, textvariable=self.var_email).pack(pady=(0,3), padx=10, fill="x")
        
        self.btn_save_client = ctk.CTkButton(left_panel, text="GUARDAR CLIENTE", command=self.save_client_data)
        self.btn_save_client.pack(pady=5)
        
        ctk.CTkLabel(left_panel, text="ÚLTIMOS 10 SERVICIOS", font=("Arial", 12, "bold"), text_color="black").pack(pady=(8,3))
        self.history_scroll = ctk.CTkScrollableFrame(left_panel, height=62, fg_color="white")
        self.history_scroll.pack(padx=10, fill="both", expand=True)
        ctk.CTkLabel(self.history_scroll, text="SELECCIONE UN CLIENTE...", text_color="gray").pack(pady=10)
        
        ctk.CTkButton(left_panel, text="LIMPIAR FORMULARIO", command=self.clear_client_form, fg_color="gray", height=25).pack(pady=5)

        right_panel = ctk.CTkFrame(
            self,
            width=750,
            fg_color=Theme.SURFACE,
            corner_radius=Theme.RADIUS_LARGE,
            border_width=1,
            border_color=Theme.BORDER
        )
        right_panel.grid(row=0, column=1, sticky="ns", padx=(10,20), pady=20)
        right_panel.grid_propagate(False)  # Forzar ancho fijo
        
        # Header
        header_right = ctk.CTkFrame(right_panel, fg_color="transparent")
        header_right.pack(fill="x", padx=20, pady=(20,10))
        
        ctk.CTkLabel(
            header_right,
            text="⚙️ INGRESO DE EQUIPO",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold"),
            text_color=Theme.TEXT_PRIMARY
        ).pack(anchor="w")
        
        # Separador
        ctk.CTkFrame(right_panel, height=1, fg_color=Theme.DIVIDER).pack(fill="x", padx=20, pady=10)
        
        form_grid = ctk.CTkFrame(right_panel, fg_color="transparent"); form_grid.pack(fill="x", padx=10)
        ctk.CTkLabel(form_grid, text="TIPO DE DISPOSITIVO (*):", font=("Arial", 11, "bold")).grid(row=0, column=0, padx=5, sticky="w")
        self.combo_type = ctk.CTkComboBox(form_grid, values=self.device_types, command=self.on_type_select); self.combo_type.set("CELULAR"); self.combo_type.grid(row=1, column=0, padx=5, pady=(0,10), sticky="ew")
        ctk.CTkLabel(form_grid, text="MARCA (*):", font=("Arial", 11, "bold")).grid(row=0, column=1, padx=5, sticky="w")
        self.combo_brand = ctk.CTkComboBox(form_grid, values=self.brands, command=self.on_brand_select); self.combo_brand.set("SAMSUNG"); self.combo_brand.grid(row=1, column=1, padx=5, pady=(0,10), sticky="ew")
        ctk.CTkLabel(form_grid, text="MODELO (*):", font=("Arial", 11, "bold")).grid(row=2, column=0, padx=5, sticky="w")
        self.combo_model = ctk.CTkComboBox(form_grid, variable=self.var_model); self.combo_model.set(""); self.combo_model.grid(row=3, column=0, padx=5, pady=(0,10), sticky="ew")
        ctk.CTkLabel(form_grid, text="SERIE / IMEI:", font=("Arial", 11, "bold")).grid(row=2, column=1, padx=5, sticky="w")
        ctk.CTkEntry(form_grid, textvariable=self.var_serial).grid(row=3, column=1, padx=5, pady=(0,10), sticky="ew")

        service_frame = ctk.CTkFrame(right_panel, fg_color="#E0E0E0", corner_radius=8)
        service_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(service_frame, text="CONFIGURACIÓN DE SERVICIO (*)", font=("Arial", 12, "bold")).pack(pady=5)
        
        srv_grid = ctk.CTkFrame(service_frame, fg_color="transparent"); srv_grid.pack(fill="x", padx=5)
        ctk.CTkLabel(srv_grid, text="SERVICIO (MANO OBRA):", font=("Arial", 11, "bold")).pack(anchor="w")
        self.entry_service = ctk.CTkEntry(srv_grid, textvariable=self.var_service, state="readonly", placeholder_text="USAR BUSCADOR →")
        self.entry_service.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(srv_grid, text="🔍 BUSCAR", width=80, command=lambda: self.open_search_modal("SERVICE"), fg_color="#5DADE2").pack(side="left", padx=5)

        part_grid = ctk.CTkFrame(service_frame, fg_color="transparent"); part_grid.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(part_grid, text="REPUESTO (OPCIONAL):", font=("Arial", 11, "bold")).pack(anchor="w")
        self.entry_part = ctk.CTkEntry(part_grid, textvariable=self.var_part, state="readonly", placeholder_text="USAR BUSCADOR →")
        self.var_part.set("SIN REPUESTO")
        self.entry_part.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(part_grid, text="🔍 BUSCAR", width=80, command=lambda: self.open_search_modal("PART", initial_search=self.var_model.get()), fg_color="#F5B041").pack(side="left", padx=5)

        # Campo de proveedor para el repuesto
        prov_grid = ctk.CTkFrame(service_frame, fg_color="transparent"); prov_grid.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(prov_grid, text="PROVEEDOR:", font=("Arial", 11, "bold")).pack(anchor="w")
        proveedores = self.logic.providers.get_all_providers()
        proveedores_nombres = ["CUALQUIERA"] + [p[1] for p in proveedores]
        self.combo_provider = ctk.CTkComboBox(prov_grid, values=proveedores_nombres)
        self.combo_provider.set("CUALQUIERA")
        self.combo_provider.pack(fill="x")

        ctk.CTkLabel(right_panel, text="ASIGNAR TÉCNICO:", font=("Arial", 11, "bold")).pack(anchor="w", padx=15)
        techs = self.logic.get_technicians()
        self.tech_map = {t[1]: t[0] for t in techs} if techs else {}
        self.combo_tech = ctk.CTkComboBox(right_panel, values=list(self.tech_map.keys()) or ["ADMIN"]); self.combo_tech.pack(fill="x", padx=15, pady=(0,10))

        form_grid.grid_columnconfigure(0, weight=1); form_grid.grid_columnconfigure(1, weight=1)

        # Campo de fecha de entrega comprometida
        delivery_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        delivery_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(delivery_frame, text="FECHA COMPROMISO ENTREGA:", font=("Arial", 11, "bold")).pack(anchor="w")
        self.date_delivery = DateEntry(delivery_frame, width=20, background='darkblue',
                                      foreground='white', borderwidth=2, 
                                      date_pattern='dd/mm/yyyy', locale='es_ES')
        self.date_delivery.pack(anchor="w", pady=5)

        ctk.CTkLabel(right_panel, text="OBSERVACIONES ADICIONALES:", font=("Arial", 11, "bold")).pack(anchor="w", padx=15)
        self.text_obs = ctk.CTkTextbox(right_panel, height=50)
        self.text_obs.pack(fill="x", padx=15, pady=(0, 10))
        self.text_obs.bind("<KeyRelease>", self.uppercase_textbox)

        acc_frame = ctk.CTkFrame(right_panel, fg_color="transparent"); acc_frame.pack(fill="x", padx=15, pady=5)
        self.var_sim = ctk.BooleanVar(); self.var_simcard = ctk.BooleanVar(); self.var_sd = ctk.BooleanVar(); self.var_charger = ctk.BooleanVar(); self.var_wet = ctk.BooleanVar(); self.var_risky = ctk.BooleanVar()
        ctk.CTkCheckBox(acc_frame, text="BANDEJA SIM", variable=self.var_sim).pack(side="left", padx=5)
        ctk.CTkCheckBox(acc_frame, text="SIM CARD", variable=self.var_simcard).pack(side="left", padx=5)
        ctk.CTkCheckBox(acc_frame, text="MICRO SD", variable=self.var_sd).pack(side="left", padx=5)
        ctk.CTkCheckBox(acc_frame, text="CARGADOR", variable=self.var_charger).pack(side="left", padx=5)
        ctk.CTkCheckBox(acc_frame, text="MOJADO", variable=self.var_wet, fg_color="#cc0000", hover_color="#990000").pack(side="left", padx=5)
        ctk.CTkSwitch(acc_frame, text="RIESGOSO", variable=self.var_risky, progress_color="red").pack(side="right", padx=5)

        money_frame = ctk.CTkFrame(right_panel, fg_color="gray20"); money_frame.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(money_frame, text="PRESUPUESTO ($) *:", text_color="white", font=("Arial", 14, "bold")).pack(side="left", padx=10, pady=10)
        self.entry_price = ctk.CTkEntry(money_frame, textvariable=self.var_price, width=120, font=("Arial", 14, "bold")); self.entry_price.pack(side="left", padx=5, pady=10)
        ctk.CTkLabel(money_frame, text="DESCUENTO ($):", text_color="white", font=("Arial", 14, "bold")).pack(side="left", padx=10, pady=10)
        self.entry_discount = ctk.CTkEntry(money_frame, textvariable=self.var_discount, width=120, font=("Arial", 14, "bold")); self.entry_discount.pack(side="left", padx=5, pady=10)
        ctk.CTkLabel(money_frame, text="ABONO ($):", text_color="white", font=("Arial", 14, "bold")).pack(side="left", padx=10, pady=10)
        self.entry_deposit = ctk.CTkEntry(money_frame, textvariable=self.var_deposit, width=120, font=("Arial", 14, "bold")); self.entry_deposit.pack(side="left", padx=5, pady=10)

        buttons_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=15)
        
        self.btn_generate_order = ctk.CTkButton(
            buttons_frame,
            text="✅ GENERAR ORDEN (PENDIENTE)",
            command=self.save_order,
            height=50,
            **Theme.get_button_style("success")
        )
        self.btn_generate_order.pack(fill="x", pady=(0, 5))
        
        # Botón para enviar mensajes al cliente
        btn_msg_frame = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        btn_msg_frame.pack(fill="x", pady=(5, 0))
        
        ctk.CTkButton(
            btn_msg_frame,
            text="📱 WhatsApp Cliente",
            command=self.enviar_whatsapp_cliente,
            height=40,
            **Theme.get_button_style("secondary"),
            width=150
        ).pack(side="left", padx=(0, 5), expand=True, fill="x")
        
        ctk.CTkButton(
            btn_msg_frame,
            text="📧 Email Cliente",
            command=self.enviar_email_cliente,
            height=40,
            **Theme.get_button_style("secondary"),
            width=150
        ).pack(side="right", padx=(5, 0), expand=True, fill="x")
        
        self.on_brand_change("SAMSUNG")
        self.load_services_combo()
        self.load_parts_combo()
        
        # Deshabilitar campos de equipo inicialmente
        self.toggle_equipment_fields(False)

    # --- FUNCIONES ---
    def check_client_fields(self, *args):
        """Habilita campos de equipo si RUT y NOMBRE tienen contenido"""
        rut = self.var_rut.get().strip()
        nombre = self.var_name.get().strip()
        
        # Habilitar si ambos campos tienen datos
        should_enable = bool(rut and nombre)
        self.toggle_equipment_fields(should_enable)
        
        # Lógica del botón Guardar/Editar
        # Si el RUT cambió y ya no coincide con el cliente seleccionado, volver a "GUARDAR"
        if self.selected_client_rut and rut != self.selected_client_rut:
            self.btn_save_client.configure(text="GUARDAR CLIENTE")
            # Opcional: Resetear selected_client_rut si queremos forzar que sea un "nuevo" cliente
            # self.selected_client_rut = None 

    def toggle_equipment_fields(self, enabled):
        """Habilita o deshabilita todos los campos de ingreso de equipo"""
        state = "normal" if enabled else "disabled"
        
        # Campos básicos
        self.combo_type.configure(state=state)
        self.combo_brand.configure(state=state)
        self.combo_model.configure(state=state)
        
        # Servicios y repuestos
        self.entry_service.configure(state="readonly")
        self.entry_part.configure(state="readonly")
        self.combo_tech.configure(state=state)
        
        # Text fields
        if enabled:
            self.text_obs.configure(state="normal")
            self.entry_price.configure(state="normal")
            self.entry_deposit.configure(state="normal")
        else:
            self.text_obs.configure(state="disabled")
            self.entry_price.configure(state="disabled")
            self.entry_deposit.configure(state="disabled")
        
        # Checkboxes y switches - CustomTkinter no soporta state=disabled en checkboxes fácilmente, 
        # pero podemos dejarlos funcionales o bloquear la lógica de guardado si no hay cliente.
        # Por ahora solo deshabilitamos el botón de generar.
        
        # Botón de generar orden
        self.btn_generate_order.configure(state=state)

    def load_services_combo(self):
        services = self.logic.services.get_all_services()
        self.services_map = {s[1]: s[2] for s in services}
        # Ya no se usa combo, los servicios se seleccionan por buscador

    def load_parts_combo(self):
        # Ya no se usa combo, los repuestos se seleccionan por buscador
        self.parts_map = {}

    def open_search_modal(self, context, initial_search=""):
        win = ctk.CTkToplevel(self); win.title(f"BUSCAR {context}"); win.geometry("700x550"); win.attributes("-topmost", True)
        # Centrar ventana
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (700 // 2)
        y = (win.winfo_screenheight() // 2) - (550 // 2)
        win.geometry(f"700x550+{x}+{y}")
        head = ctk.CTkFrame(win); head.pack(fill="x", padx=10, pady=10)
        v_search = ctk.StringVar(value=initial_search)
        
        ctk.CTkEntry(head, textvariable=v_search, placeholder_text="ESCRIBE PARA FILTRAR...").pack(side="left", fill="x", expand=True, padx=5)
        btn_txt = "+ NUEVO SERVICIO" if context == "SERVICE" else "+ NUEVO REPUESTO"
        cmd = self.open_service_manager if context == "SERVICE" else self.open_add_part_window
        ctk.CTkButton(head, text=btn_txt, width=120, command=lambda: [cmd(), win.destroy()]).pack(side="right", padx=5)
        
        scroll = ctk.CTkScrollableFrame(win); scroll.pack(fill="both", expand=True, padx=10, pady=5)
        v_search.trace("w", lambda *a: self.filter_list(v_search.get(), context, scroll, win))

        if context == "SERVICE": 
            items = self.logic.services.get_all_services()
        else: 
            # Obtener repuestos con proveedor_id directo y nombre del proveedor
            query = """
                SELECT r.id, r.nombre, r.categoria, r.costo, r.precio_sugerido, r.stock,
                       r.proveedor_id,
                       COALESCE(p.nombre, 'SIN PROVEEDOR') as proveedor_nombre
                FROM repuestos r
                LEFT JOIN proveedores p ON r.proveedor_id = p.id
                ORDER BY r.nombre ASC
            """
            items = self.logic.bd.OBTENER_TODOS(query)
        win.all_items = items
        self.render_search_list(scroll, items, context, win)
        
        # Si hay búsqueda inicial, ejecutar filtro
        if initial_search:
            self.filter_list(initial_search, context, scroll, win)

    def render_search_list(self, scroll, items, context, win):
        for w in scroll.winfo_children(): w.destroy()
        if not items: ctk.CTkLabel(scroll, text="SIN RESULTADOS").pack(pady=10); return
        for i in items:
            nombre = i[1]; precio = i[3] if context == "SERVICE" else i[4]
            
            # Para repuestos, obtener información del proveedor (índice 7 = proveedor_nombre)
            proveedor_info = ""
            if context == "PART" and len(i) > 7 and i[7] and i[7] != "SIN PROVEEDOR":
                proveedor_info = f" [{i[7]}]"
            
            card = ctk.CTkFrame(scroll, fg_color="#E0E0E0"); card.pack(fill="x", pady=2)
            
            # Nombre del repuesto/servicio con proveedor
            nombre_completo = nombre + proveedor_info
            ctk.CTkLabel(card, text=nombre_completo, width=320, anchor="w", font=("Arial", 10, "bold")).pack(side="left", padx=5)
            
            ctk.CTkLabel(card, text=f"${int(precio):,}".replace(",", "."), width=80, text_color="green").pack(side="left")
            ctk.CTkButton(card, text="ELEGIR", width=60, height=25, command=lambda n=nombre, p=precio, item=i: self.select_item_from_modal(context, n, p, win, item)).pack(side="right", padx=5, pady=5)
            # Botón EDITAR solo para repuestos (PART)
            if context == "PART":
                ctk.CTkButton(card, text="✏️ EDITAR", width=70, height=25, fg_color="#F39C12", hover_color="#E67E22", 
                             command=lambda item=i, scr=scroll, ctx=context, w=win: self.open_edit_part_dialog(item, scr, ctx, w)).pack(side="right", padx=2, pady=5)

    def filter_list(self, query, context, scroll_frame, win):
        query = query.upper()
        if hasattr(win, 'all_items'):
            filtered = [i for i in win.all_items if query in i[1].upper()]
            self.render_search_list(scroll_frame, filtered, context, win)

    def open_edit_part_dialog(self, item, scroll, context, parent_win):
        """Abre un diálogo para editar precio, costo, stock y proveedor de un repuesto"""
        # Extraer datos del item (id, nombre, categoria, costo, precio_sugerido, stock, proveedor_id, proveedor_nombre)
        part_id = item[0]
        nombre = item[1]
        categoria = item[2]
        costo_actual = item[3]
        precio_actual = item[4]
        stock_actual = item[5]
        proveedor_id_actual = item[6] if len(item) > 6 else 0
        proveedor_nombre_actual = item[7] if len(item) > 7 else "SIN PROVEEDOR"
        
        # Crear ventana de edición
        edit_win = ctk.CTkToplevel(self)
        edit_win.title(f"EDITAR REPUESTO: {nombre}")
        edit_win.geometry("550x750")
        edit_win.attributes("-topmost", True)
        edit_win.transient(parent_win)
        edit_win.grab_set()
        
        # Centrar ventana
        edit_win.update_idletasks()
        x = (edit_win.winfo_screenwidth() // 2) - (550 // 2)
        y = (edit_win.winfo_screenheight() // 2) - (750 // 2)
        edit_win.geometry(f"550x750+{x}+{y}")
        
        # Header
        ctk.CTkLabel(edit_win, text="EDITAR PRECIOS Y STOCK", 
                    font=("Arial", 16, "bold")).pack(pady=15)
        
        # Información del repuesto
        info_frame = ctk.CTkFrame(edit_win, fg_color="gray20")
        info_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(info_frame, text=f"REPUESTO: {nombre}", 
                    font=("Arial", 12, "bold"), anchor="w").pack(padx=10, pady=5, fill="x")
        ctk.CTkLabel(info_frame, text=f"PROVEEDOR ACTUAL: {proveedor_nombre_actual}", 
                    font=("Arial", 11), anchor="w", text_color="#66BB6A").pack(padx=10, pady=5, fill="x")
        
        # Variables para los campos
        v_categoria = ctk.StringVar(value=categoria)
        v_costo = ctk.StringVar(value=f"{int(costo_actual):,}".replace(",", "."))
        v_precio = ctk.StringVar(value=f"{int(precio_actual):,}".replace(",", "."))
        v_stock = ctk.StringVar(value=str(stock_actual))
        
        # Obtener lista de proveedores
        proveedores_list = self.logic.providers.get_all_providers()
        proveedores_nombres = [p[1] for p in proveedores_list]  # p[1] es el nombre
        proveedores_map = {p[1]: p[0] for p in proveedores_list}  # nombre -> id
        
        # Aplicar formato automático
        v_costo.trace("w", lambda *a: self.format_live_money(v_costo))
        v_precio.trace("w", lambda *a: self.format_live_money(v_precio))
        v_stock.trace("w", lambda *a: self.format_live_int(v_stock))
        
        # Formulario de edición
        form_frame = ctk.CTkFrame(edit_win, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Categoría
        ctk.CTkLabel(form_frame, text="🏷️ CATEGORÍA:", 
                    font=("Arial", 12, "bold"), anchor="w").pack(pady=(10,5), fill="x")
        cats = self.logic.bd.OBTENER_TODOS("SELECT nombre FROM categorias WHERE tipo = 'REPUESTO' ORDER BY nombre", ())
        cat_list = [c[0] for c in cats] if cats else ["PANTALLAS", "BATERIAS", "PINES CARGA", "FLEX", "OTROS"]
        
        cat_frame_inner = ctk.CTkFrame(form_frame, fg_color="transparent")
        cat_frame_inner.pack(pady=(0,15), fill="x")
        combo_categoria = ctk.CTkComboBox(cat_frame_inner, values=cat_list, variable=v_categoria, height=35, 
                                         font=("Arial", 12))
        combo_categoria.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        def crear_categoria_edit():
            nueva_cat = ctk.CTkInputDialog(text="Ingrese nombre de la nueva categoría:", title="Nueva Categoría").get_input()
            if nueva_cat:
                nueva_cat = nueva_cat.strip().upper()
                if nueva_cat:
                    try:
                        self.logic.bd.EJECUTAR_CONSULTA("INSERT INTO categorias (nombre, tipo) VALUES (?, 'REPUESTO')", (nueva_cat,))
                        cats = self.logic.bd.OBTENER_TODOS("SELECT nombre FROM categorias WHERE tipo = 'REPUESTO' ORDER BY nombre", ())
                        cat_list = [c[0] for c in cats]
                        combo_categoria.configure(values=cat_list)
                        v_categoria.set(nueva_cat)
                        messagebox.showinfo("Éxito", f"Categoría '{nueva_cat}' creada", parent=edit_win)
                    except:
                        messagebox.showerror("Error", "La categoría ya existe", parent=edit_win)
        
        ctk.CTkButton(cat_frame_inner, text="➕", width=40, command=crear_categoria_edit, 
                     fg_color="#2196F3", height=35).pack(side="left")
        
        # Proveedor
        ctk.CTkLabel(form_frame, text="🏭 PROVEEDOR:", 
                    font=("Arial", 12, "bold"), anchor="w").pack(pady=(10,5), fill="x")
        
        prov_frame_inner = ctk.CTkFrame(form_frame, fg_color="transparent")
        prov_frame_inner.pack(pady=(0,15), fill="x")
        combo_proveedor = ctk.CTkComboBox(prov_frame_inner, values=proveedores_nombres, height=35, 
                                          font=("Arial", 12))
        combo_proveedor.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        def crear_proveedor_edit():
            dialog_win = ctk.CTkToplevel(edit_win)
            dialog_win.title("NUEVO PROVEEDOR")
            dialog_win.geometry("400x400")
            dialog_win.transient(edit_win)
            dialog_win.grab_set()
            dialog_win.attributes("-topmost", True)
            dialog_win.update_idletasks()
            x = (dialog_win.winfo_screenwidth() // 2) - 200
            y = (dialog_win.winfo_screenheight() // 2) - 200
            dialog_win.geometry(f"400x400+{x}+{y}")
            
            ctk.CTkLabel(dialog_win, text="CREAR PROVEEDOR", font=("Arial", 14, "bold")).pack(pady=15)
            
            v_nombre = ctk.StringVar()
            v_telefono = ctk.StringVar()
            v_email = ctk.StringVar()
            v_direccion = ctk.StringVar()
            
            ctk.CTkLabel(dialog_win, text="NOMBRE:", anchor="w").pack(padx=20, pady=(10,5), fill="x")
            ctk.CTkEntry(dialog_win, textvariable=v_nombre).pack(padx=20, fill="x")
            
            ctk.CTkLabel(dialog_win, text="TELÉFONO:", anchor="w").pack(padx=20, pady=(10,5), fill="x")
            ctk.CTkEntry(dialog_win, textvariable=v_telefono).pack(padx=20, fill="x")
            
            ctk.CTkLabel(dialog_win, text="EMAIL:", anchor="w").pack(padx=20, pady=(10,5), fill="x")
            ctk.CTkEntry(dialog_win, textvariable=v_email).pack(padx=20, fill="x")
            
            ctk.CTkLabel(dialog_win, text="DIRECCIÓN:", anchor="w").pack(padx=20, pady=(10,5), fill="x")
            ctk.CTkEntry(dialog_win, textvariable=v_direccion).pack(padx=20, fill="x")
            
            def guardar_proveedor():
                nombre = v_nombre.get().strip()
                telefono = v_telefono.get().strip()
                email = v_email.get().strip()
                direccion = v_direccion.get().strip()
                
                if not nombre:
                    messagebox.showerror("Error", "Ingrese el nombre del proveedor", parent=dialog_win)
                    return
                
                resultado = self.logic.providers.add_provider(nombre, telefono, email, direccion)
                if resultado:
                    messagebox.showinfo("Éxito", f"Proveedor '{nombre}' creado correctamente", parent=dialog_win)
                    # Actualizar lista de proveedores
                    proveedores_list = self.logic.providers.get_all_providers()
                    nuevos_nombres = [p[1] for p in proveedores_list]
                    combo_proveedor.configure(values=nuevos_nombres)
                    combo_proveedor.set(nombre.upper())
                    dialog_win.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo crear el proveedor", parent=dialog_win)
            
            ctk.CTkButton(dialog_win, text="GUARDAR", command=guardar_proveedor, 
                         fg_color="green", height=40).pack(pady=20)
        
        ctk.CTkButton(prov_frame_inner, text="➕", width=40, command=crear_proveedor_edit, 
                     fg_color="#2196F3", height=35).pack(side="left")
        
        # Seleccionar el proveedor actual
        if proveedor_nombre_actual and proveedor_nombre_actual != "SIN PROVEEDOR":
            combo_proveedor.set(proveedor_nombre_actual)
        elif proveedores_nombres:
            combo_proveedor.set(proveedores_nombres[0])
        
        # Costo
        ctk.CTkLabel(form_frame, text="COSTO DE COMPRA ($):", 
                    font=("Arial", 12, "bold"), anchor="w").pack(pady=(10,5), fill="x")
        ctk.CTkEntry(form_frame, textvariable=v_costo, height=35, 
                    font=("Arial", 12)).pack(pady=(0,15), fill="x")
        
        # Precio de venta
        ctk.CTkLabel(form_frame, text="PRECIO DE VENTA ($):", 
                    font=("Arial", 12, "bold"), anchor="w").pack(pady=(10,5), fill="x")
        ctk.CTkEntry(form_frame, textvariable=v_precio, height=35, 
                    font=("Arial", 12)).pack(pady=(0,15), fill="x")
        
        # Stock
        ctk.CTkLabel(form_frame, text="STOCK DISPONIBLE:", 
                    font=("Arial", 12, "bold"), anchor="w").pack(pady=(10,5), fill="x")
        ctk.CTkEntry(form_frame, textvariable=v_stock, height=35, 
                    font=("Arial", 12)).pack(pady=(0,15), fill="x")
        
        # Función para guardar cambios
        processing = [False]  # Flag para prevenir múltiples ejecuciones
        def save_changes():
            # Prevenir múltiples clics
            if processing[0]:
                return
            processing[0] = True
            
            try:
                # Obtener proveedor seleccionado
                proveedor_nombre = combo_proveedor.get()
                print(f"DEBUG EDIT: Proveedor seleccionado: '{proveedor_nombre}'")
                print(f"DEBUG EDIT: Proveedores map: {proveedores_map}")
                
                # Si hay proveedor seleccionado, obtener su ID
                if proveedor_nombre and proveedor_nombre in proveedores_map:
                    proveedor_id = proveedores_map[proveedor_nombre]
                elif proveedor_nombre and proveedores_map:
                    # Si el proveedor no está en el mapa pero hay proveedores, es error
                    messagebox.showerror("Error", "Debe seleccionar un proveedor válido", parent=edit_win)
                    processing[0] = False
                    return
                else:
                    # Sin proveedor o sin proveedores en la lista
                    proveedor_id = proveedor_id_actual if proveedor_id_actual else 0
                
                print(f"DEBUG EDIT: Proveedor ID: {proveedor_id}")
                
                # Limpiar y convertir valores
                print(f"DEBUG EDIT: v_costo.get() = '{v_costo.get()}'")
                print(f"DEBUG EDIT: v_precio.get() = '{v_precio.get()}'")
                print(f"DEBUG EDIT: v_stock.get() = '{v_stock.get()}'")
                
                # Limpiar valores eliminando puntos y convirtiendo
                try:
                    nuevo_costo = self.clean_money(v_costo.get())
                except Exception as e:
                    messagebox.showerror("Error", f"Costo inválido: {v_costo.get()}", parent=edit_win)
                    processing[0] = False
                    return
                
                try:
                    nuevo_precio = self.clean_money(v_precio.get())
                except Exception as e:
                    messagebox.showerror("Error", f"Precio inválido: {v_precio.get()}", parent=edit_win)
                    processing[0] = False
                    return
                
                try:
                    # Limpiar el stock también eliminando puntos
                    stock_str = str(v_stock.get()).replace(".", "").strip()
                    nuevo_stock = int(stock_str) if stock_str else 0
                except Exception as e:
                    messagebox.showerror("Error", f"Stock inválido: {v_stock.get()}", parent=edit_win)
                    processing[0] = False
                    return
                
                print(f"DEBUG EDIT: nuevo_costo = {nuevo_costo}, nuevo_precio = {nuevo_precio}, nuevo_stock = {nuevo_stock}")
                
                # Validaciones
                if nuevo_precio <= 0:
                    messagebox.showerror("Error", "El precio debe ser mayor a 0", parent=edit_win)
                    processing[0] = False
                    return
                
                if nuevo_costo < 0:
                    messagebox.showerror("Error", "El costo no puede ser negativo", parent=edit_win)
                    processing[0] = False
                    return
                
                if nuevo_stock < 0:
                    messagebox.showerror("Error", "El stock no puede ser negativo", parent=edit_win)
                    processing[0] = False
                    return
                
                # Obtener categoría editada
                nueva_categoria = v_categoria.get().strip() or categoria
                
                # Actualizar en la base de datos (con proveedor y categoría)
                success = self.logic.parts.ACTUALIZAR_REPUESTO(part_id, nombre, nueva_categoria, nuevo_costo, nuevo_precio, nuevo_stock, proveedor_id)
                
                if success:
                    # Agregar el repuesto al campo de repuesto automáticamente
                    disp = f"{nombre} ($" + f"{int(nuevo_precio):,}".replace(",", ".") + ")"
                    self.var_part.set(disp)
                    self.parts_map[disp] = nuevo_precio
                    self.update_observaciones_repuesto()
                    
                    # Si tiene proveedor, seleccionarlo en el dropdown
                    if hasattr(self, 'combo_provider'):
                        try:
                            self.combo_provider.set(proveedor_nombre)
                        except:
                            pass
                    
                    self.update_total_budget()
                    
                    # Cerrar todas las ventanas emergentes (edit_win y parent_win)
                    try:
                        edit_win.destroy()
                    except:
                        pass
                    
                    try:
                        parent_win.destroy()
                    except:
                        pass
                else:
                    messagebox.showerror("Error", "No se pudo actualizar el repuesto", parent=edit_win)
                    processing[0] = False
                    
            except ValueError as ve:
                processing[0] = False
                print(f"DEBUG EDIT: ValueError: {ve}")
                import traceback
                traceback.print_exc()
                messagebox.showerror("Error", "Por favor ingrese valores numéricos válidos", parent=edit_win)
            except Exception as e:
                processing[0] = False
                print(f"DEBUG EDIT: Exception: {e}")
                import traceback
                traceback.print_exc()
                messagebox.showerror("Error", f"Error al guardar: {str(e)}", parent=edit_win)
        
        # Función para guardar y vender
        def save_and_sell():
            # Prevenir múltiples clics
            if processing[0]:
                return
            processing[0] = True
            
            try:
                # Obtener proveedor seleccionado
                proveedor_nombre = combo_proveedor.get()
                
                # Si hay proveedor seleccionado, obtener su ID
                if proveedor_nombre and proveedor_nombre in proveedores_map:
                    proveedor_id = proveedores_map[proveedor_nombre]
                elif proveedor_nombre and proveedores_map:
                    messagebox.showerror("Error", "Debe seleccionar un proveedor válido", parent=edit_win)
                    processing[0] = False
                    return
                else:
                    proveedor_id = proveedor_id_actual if proveedor_id_actual else 0
                
                # Limpiar y convertir valores
                try:
                    nuevo_costo = self.clean_money(v_costo.get())
                except Exception as e:
                    messagebox.showerror("Error", f"Costo inválido: {v_costo.get()}", parent=edit_win)
                    processing[0] = False
                    return
                
                try:
                    nuevo_precio = self.clean_money(v_precio.get())
                except Exception as e:
                    messagebox.showerror("Error", f"Precio inválido: {v_precio.get()}", parent=edit_win)
                    processing[0] = False
                    return
                
                try:
                    stock_str = str(v_stock.get()).replace(".", "").strip()
                    nuevo_stock = int(stock_str) if stock_str else 0
                except Exception as e:
                    messagebox.showerror("Error", f"Stock inválido: {v_stock.get()}", parent=edit_win)
                    processing[0] = False
                    return
                
                # Obtener categoría editada
                nueva_categoria = v_categoria.get().strip() or categoria
                
                # Actualizar en la base de datos
                success = self.logic.parts.ACTUALIZAR_REPUESTO(part_id, nombre, nueva_categoria, nuevo_costo, nuevo_precio, nuevo_stock, proveedor_id)
                
                if success:
                    edit_win.destroy()
                    
                    # Navegar al POS y agregar el producto
                    app = self.master.master  # Obtener referencia a la aplicación principal
                    if hasattr(app, 'mostrar_frame') and hasattr(app, 'frames') and "POS" in app.frames:
                        # Cambiar al frame POS
                        app.mostrar_frame("POS")
                        
                        # Agregar el producto al carrito del POS
                        pos_frame = app.frames["POS"]
                        if hasattr(pos_frame, 'add_to_cart'):
                            # El método add_to_cart espera: (id, nombre, categoria, costo, precio, stock, proveedor_id) para productos
                            item_data = (part_id, nombre, nueva_categoria, nuevo_costo, nuevo_precio, nuevo_stock, proveedor_id)
                            pos_frame.add_to_cart(item_data, is_service=False, details=None)
                            messagebox.showinfo("Éxito", f"Repuesto '{nombre}' agregado al carrito del POS", parent=self)
                    else:
                        messagebox.showinfo("Guardado", "Repuesto actualizado correctamente", parent=self)
                else:
                    messagebox.showerror("Error", "No se pudo actualizar el repuesto", parent=edit_win)
                    processing[0] = False
            except Exception as e:
                processing[0] = False
                messagebox.showerror("Error", f"Error al guardar: {str(e)}", parent=edit_win)
        
        # Botones
        btn_frame = ctk.CTkFrame(edit_win, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(btn_frame, text="💾 GUARDAR", 
                     command=save_changes, 
                     fg_color="#28a745", hover_color="#218838",
                     height=40, font=("Arial", 11, "bold")).pack(side="left", expand=True, padx=3)
        
        ctk.CTkButton(btn_frame, text="💰 GUARDAR Y VENDER", 
                     command=save_and_sell, 
                     fg_color="#FF6B35", hover_color="#E85A2A",
                     height=40, font=("Arial", 11, "bold")).pack(side="left", expand=True, padx=3)
        
        ctk.CTkButton(btn_frame, text="❌ CANCELAR", 
                     command=edit_win.destroy,
                     fg_color="gray", hover_color="darkgray",
                     height=40, font=("Arial", 11, "bold")).pack(side="left", expand=True, padx=3)

    def select_item_from_modal(self, context, name, price, win, item=None):
        if context == "SERVICE":
            self.var_service.set(name)
            self.services_map[name] = price
            self.update_observaciones_servicio()
        else:
            disp = f"{name} ($" + f"{int(price):,}".replace(",", ".") + ")"
            self.var_part.set(disp)
            self.parts_map[disp] = price
            self.update_observaciones_repuesto()
            
            # Si el repuesto tiene proveedor asignado, seleccionarlo automáticamente
            if hasattr(self, 'combo_provider'):
                try:
                    if item and len(item) > 7 and item[7] and item[7] != "SIN PROVEEDOR":
                        # Tiene proveedor: usar el proveedor del repuesto
                        proveedor_nombre = item[7]
                        self.combo_provider.set(proveedor_nombre)
                    else:
                        # No tiene proveedor: usar "CUALQUIERA"
                        self.combo_provider.set("CUALQUIERA")
                except:
                    pass  # Si no existe el dropdown o el proveedor, continuar normalmente
        
        self.update_total_budget()
        try:
            win.destroy()
        except:
            pass

    def on_service_select(self, choice): 
        self.update_observaciones_servicio()
        self.update_total_budget()
    
    def on_part_select(self, choice): 
        self.update_observaciones_repuesto()
        self.update_total_budget()
    
    def update_observaciones_servicio(self):
        """Agregar servicio seleccionado a observaciones"""
        srv = self.var_service.get()
        if srv and srv != "SELECCIONE":
            obs_actual = self.text_obs.get("0.0", "end-1c").strip()
            
            # Si hay contenido, agregar con " + ", sino solo el servicio
            if obs_actual:
                obs_nueva = f"{obs_actual} + {srv}"
            else:
                obs_nueva = srv
            
            self.text_obs.delete("0.0", "end")
            self.text_obs.insert("0.0", obs_nueva.upper())
    
    def update_observaciones_repuesto(self):
        """Agregar repuesto seleccionado a observaciones"""
        rep = self.var_part.get()
        if rep and rep != "SIN REPUESTO":
            # Extraer nombre del repuesto sin el precio
            rep_nombre = rep.split('($')[0].strip() if '($' in rep else rep
            obs_actual = self.text_obs.get("0.0", "end-1c").strip()
            
            # Si hay contenido, agregar con " + ", sino solo el repuesto
            if obs_actual:
                obs_nueva = f"{obs_actual} + {rep_nombre}"
            else:
                obs_nueva = rep_nombre
            
            self.text_obs.delete("0.0", "end")
            self.text_obs.insert("0.0", obs_nueva.upper())
    
    def update_total_budget(self):
        s = self.var_service.get()
        p = self.var_part.get()
        mo = self.services_map.get(s, 0) if s and s != "SELECCIONE" else 0
        pa = self.parts_map.get(p, 0) if p and p != "SIN REPUESTO" else 0
        total = float(mo) + float(pa)
        
        # Establecer el precio total
        try:
            self.var_price.set(str(int(total)))
        except:
            self.var_price.set("0")

    def open_add_part_window(self):
        win = ctk.CTkToplevel(self); win.title("CREAR NUEVO REPUESTO"); win.geometry("450x720"); win.attributes("-topmost", True)
        # Centrar ventana
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (450 // 2)
        y = (win.winfo_screenheight() // 2) - (360)
        win.geometry(f"450x720+{x}+{y}")
        ctk.CTkLabel(win, text="REGISTRO RÁPIDO DE REPUESTO", font=("Arial", 14, "bold")).pack(pady=15)
        v_n = ctk.StringVar(); v_n.trace("w", lambda *a: self.force_uppercase(v_n))
        v_cat = ctk.StringVar()
        v_c = ctk.StringVar(); v_c.trace("w", lambda *a: self.format_live_money(v_c))
        v_p = ctk.StringVar(); v_p.trace("w", lambda *a: self.format_live_money(v_p))
        v_s = ctk.StringVar(); v_s.trace("w", lambda *a: self.format_live_int(v_s))
        v_prov = ctk.StringVar(value="CUALQUIERA")
        
        ctk.CTkLabel(win, text="NOMBRE DEL REPUESTO:").pack(anchor="w", padx=20); ctk.CTkEntry(win, textvariable=v_n).pack(pady=5, padx=20, fill="x")
        
        # Categorías dinámicas
        ctk.CTkLabel(win, text="CATEGORÍA:").pack(anchor="w", padx=20, pady=(10,0))
        cats = self.logic.bd.OBTENER_TODOS("SELECT nombre FROM categorias WHERE tipo = 'REPUESTO' ORDER BY nombre", ())
        cat_list = [c[0] for c in cats] if cats else ["PANTALLAS", "BATERIAS", "PINES CARGA", "FLEX", "OTROS"]
        cat_frame = ctk.CTkFrame(win, fg_color="transparent")
        cat_frame.pack(pady=5, padx=20, fill="x")
        combo_cat = ctk.CTkComboBox(cat_frame, values=cat_list, variable=v_cat)
        combo_cat.pack(side="left", fill="x", expand=True, padx=(0, 5))
        if cat_list:
            v_cat.set(cat_list[0])
        
        def crear_categoria_rapida():
            nueva_cat = ctk.CTkInputDialog(text="Ingrese nombre de la nueva categoría:", title="Nueva Categoría").get_input()
            if nueva_cat:
                nueva_cat = nueva_cat.strip().upper()
                if nueva_cat:
                    try:
                        self.logic.bd.EJECUTAR_CONSULTA("INSERT INTO categorias (nombre, tipo) VALUES (?, 'REPUESTO')", (nueva_cat,))
                        cats = self.logic.bd.OBTENER_TODOS("SELECT nombre FROM categorias WHERE tipo = 'REPUESTO' ORDER BY nombre", ())
                        cat_list = [c[0] for c in cats]
                        combo_cat.configure(values=cat_list)
                        v_cat.set(nueva_cat)
                        messagebox.showinfo("Éxito", f"Categoría '{nueva_cat}' creada", parent=win)
                    except:
                        messagebox.showerror("Error", "La categoría ya existe", parent=win)
        
        ctk.CTkButton(cat_frame, text="➕", width=40, command=crear_categoria_rapida, fg_color="#2196F3").pack(side="left")
        
        ctk.CTkLabel(win, text="COSTO DE COMPRA ($):").pack(anchor="w", padx=20); ctk.CTkEntry(win, textvariable=v_c).pack(pady=5, padx=20, fill="x")
        ctk.CTkLabel(win, text="PRECIO DE VENTA AL PÚBLICO ($):").pack(anchor="w", padx=20); ctk.CTkEntry(win, textvariable=v_p).pack(pady=5, padx=20, fill="x")
        ctk.CTkLabel(win, text="STOCK INICIAL:").pack(anchor="w", padx=20); ctk.CTkEntry(win, textvariable=v_s).pack(pady=5, padx=20, fill="x")
        
        # ComboBox de proveedores
        ctk.CTkLabel(win, text="PROVEEDOR:").pack(anchor="w", padx=20, pady=(10,0))
        provs = self.logic.providers.get_all_providers()
        prov_list = ["CUALQUIERA"] + [f"{p[0]} - {p[1]}" for p in provs]
        
        prov_frame_rapida = ctk.CTkFrame(win, fg_color="transparent")
        prov_frame_rapida.pack(pady=5, padx=20, fill="x")
        combo_prov = ctk.CTkComboBox(prov_frame_rapida, values=prov_list, variable=v_prov, state="readonly")
        combo_prov.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        def crear_proveedor_rapido():
            dialog_win = ctk.CTkToplevel(win)
            dialog_win.title("NUEVO PROVEEDOR")
            dialog_win.geometry("400x400")
            dialog_win.transient(win)
            dialog_win.grab_set()
            dialog_win.attributes("-topmost", True)
            dialog_win.update_idletasks()
            x = (dialog_win.winfo_screenwidth() // 2) - 200
            y = (dialog_win.winfo_screenheight() // 2) - 200
            dialog_win.geometry(f"400x400+{x}+{y}")
            
            ctk.CTkLabel(dialog_win, text="CREAR PROVEEDOR", font=("Arial", 14, "bold")).pack(pady=15)
            
            v_nombre = ctk.StringVar()
            v_telefono = ctk.StringVar()
            v_email = ctk.StringVar()
            v_direccion = ctk.StringVar()
            
            ctk.CTkLabel(dialog_win, text="NOMBRE:", anchor="w").pack(padx=20, pady=(10,5), fill="x")
            ctk.CTkEntry(dialog_win, textvariable=v_nombre).pack(padx=20, fill="x")
            
            ctk.CTkLabel(dialog_win, text="TELÉFONO:", anchor="w").pack(padx=20, pady=(10,5), fill="x")
            ctk.CTkEntry(dialog_win, textvariable=v_telefono).pack(padx=20, fill="x")
            
            ctk.CTkLabel(dialog_win, text="EMAIL:", anchor="w").pack(padx=20, pady=(10,5), fill="x")
            ctk.CTkEntry(dialog_win, textvariable=v_email).pack(padx=20, fill="x")
            
            ctk.CTkLabel(dialog_win, text="DIRECCIÓN:", anchor="w").pack(padx=20, pady=(10,5), fill="x")
            ctk.CTkEntry(dialog_win, textvariable=v_direccion).pack(padx=20, fill="x")
            
            def guardar_proveedor():
                nombre = v_nombre.get().strip()
                telefono = v_telefono.get().strip()
                email = v_email.get().strip()
                direccion = v_direccion.get().strip()
                
                if not nombre:
                    messagebox.showerror("Error", "Ingrese el nombre del proveedor", parent=dialog_win)
                    return
                
                resultado = self.logic.providers.add_provider(nombre, telefono, email, direccion)
                if resultado:
                    messagebox.showinfo("Éxito", f"Proveedor '{nombre}' creado correctamente", parent=dialog_win)
                    # Actualizar lista de proveedores
                    provs_nuevos = self.logic.providers.get_all_providers()
                    prov_list_nuevo = ["CUALQUIERA"] + [f"{p[0]} - {p[1]}" for p in provs_nuevos]
                    combo_prov.configure(values=prov_list_nuevo)
                    # Seleccionar el nuevo proveedor
                    nuevo_id = self.logic.bd.OBTENER_UNO("SELECT id FROM proveedores WHERE nombre = ?", (nombre.upper(),))
                    if nuevo_id:
                        combo_prov.set(f"{nuevo_id[0]} - {nombre.upper()}")
                    dialog_win.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo crear el proveedor", parent=dialog_win)
            
            ctk.CTkButton(dialog_win, text="GUARDAR", command=guardar_proveedor, 
                         fg_color="green", height=40).pack(pady=20)
        
        ctk.CTkButton(prov_frame_rapida, text="➕", width=40, command=crear_proveedor_rapido, 
                     fg_color="#2196F3").pack(side="left")
        
        def save_part():
            try:
                nombre_repuesto = v_n.get().strip()
                
                if not nombre_repuesto: 
                    messagebox.showerror("Error", "Ingrese nombre", parent=win)
                    return
                
                # Validar y limpiar valores numéricos
                c_str = v_c.get().strip()
                p_str = v_p.get().strip()
                s_str = v_s.get().strip()
                
                if not c_str or not p_str:
                    messagebox.showerror("Error", "Debe ingresar costo y precio", parent=win)
                    return
                
                c_val = self.clean_money(c_str)
                p_val = self.clean_money(p_str)
                s_val = int(s_str) if s_str else 1
                
                # Obtener proveedor_id
                prov_seleccionado = v_prov.get()
                if prov_seleccionado == "CUALQUIERA":
                    proveedor_id = 0  # 0 significa sin proveedor específico
                else:
                    proveedor_id = int(prov_seleccionado.split(" - ")[0])
                
                # Obtener categoría seleccionada
                categoria = v_cat.get().strip() or "GENERAL"
                    
                result = self.logic.parts.add_part(nombre_repuesto, c_val, p_val, s_val, categoria, proveedor_id)
                if result:
                    messagebox.showinfo("OK", "Repuesto Creado", parent=win)
                    
                    # Formato con precio
                    disp = f"{nombre_repuesto} ($" + f"{int(p_val):,}".replace(",", ".") + ")"
                    self.parts_map[disp] = p_val
                    
                    # Seleccionar automáticamente el repuesto recién creado
                    self.var_part.set(disp)
                    
                    # Actualizar observaciones
                    self.update_observaciones_repuesto()
                    
                    # Actualizar presupuesto total
                    self.update_total_budget()
                    
                    win.destroy()
                else:
                    # El error ya fue mostrado por AGREGAR_REPUESTO
                    pass
            except Exception as e: 
                messagebox.showerror("Error", f"Error al crear repuesto: {e}", parent=win)
        ctk.CTkButton(win, text="GUARDAR", command=save_part, fg_color="green").pack(pady=20)

    def open_service_manager(self):
        win = ctk.CTkToplevel(self); win.title("CATÁLOGO DE SERVICIOS"); win.geometry("500x400"); win.attributes("-topmost", True)
        # Centrar ventana
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (500 // 2)
        y = (win.winfo_screenheight() // 2) - (400 // 2)
        win.geometry(f"500x400+{x}+{y}")
        ctk.CTkLabel(win, text="NUEVO SERVICIO (MANO DE OBRA)", font=("Arial", 14, "bold")).pack(pady=10)
        v_nom = ctk.StringVar(); v_nom.trace("w", lambda *a: self.force_uppercase(v_nom))
        v_cos = ctk.StringVar(); v_cos.trace("w", lambda *a: self.format_live_money(v_cos))
        
        ctk.CTkLabel(win, text="NOMBRE DEL SERVICIO:").pack(anchor="w", padx=20); ctk.CTkEntry(win, textvariable=v_nom).pack(pady=5, padx=20, fill="x")
        ctk.CTkLabel(win, text="COSTO MANO DE OBRA ($):").pack(anchor="w", padx=20); ctk.CTkEntry(win, textvariable=v_cos).pack(pady=5, padx=20, fill="x")
        
        def save():
            try:
                val_cos = self.clean_money(v_cos.get())
                nombre_servicio = v_nom.get().strip()
                if not nombre_servicio:
                    messagebox.showerror("Error", "Ingrese un nombre para el servicio", parent=win)
                    return
                    
                if self.logic.services.add_service(nombre_servicio, val_cos):
                    messagebox.showinfo("OK", "Servicio Agregado", parent=win)
                    
                    # Cargar el servicio recién creado
                    self.load_services_combo()
                    
                    # Seleccionar automáticamente el servicio recién creado
                    self.var_service.set(nombre_servicio)
                    self.services_map[nombre_servicio] = val_cos
                    
                    # Actualizar observaciones
                    self.update_observaciones_servicio()
                    
                    # Actualizar presupuesto total
                    self.update_total_budget()
                    
                    win.destroy()
                else: 
                    messagebox.showerror("Error", "Ya existe", parent=win)
            except Exception as e: 
                messagebox.showerror("Error", f"Datos inválidos: {e}", parent=win)
        ctk.CTkButton(win, text="GUARDAR", command=save, fg_color="green").pack(pady=20)

    def on_brand_select(self, brand_name):
        """Maneja la selección de marca, incluyendo OTRO"""
        if brand_name == "OTRO":
            self.add_custom_brand()
        else:
            self.on_brand_change(brand_name)
    
    def add_custom_brand(self):
        """Permite agregar una marca personalizada"""
        win = ctk.CTkToplevel(self)
        win.title("AGREGAR NUEVA MARCA")
        win.geometry("500x300")
        win.attributes("-topmost", True)
        win.grab_set()
        # Centrar ventana
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (500 // 2)
        y = (win.winfo_screenheight() // 2) - (300 // 2)
        win.geometry(f"500x300+{x}+{y}")
        
        ctk.CTkLabel(win, text="NUEVA MARCA", font=("Arial", 16, "bold")).pack(pady=20)
        
        var_new_brand = ctk.StringVar()
        var_new_brand.trace("w", lambda *args: var_new_brand.set(var_new_brand.get().upper()))
        
        ctk.CTkLabel(win, text="NOMBRE DE LA MARCA:", font=("Arial", 12)).pack(pady=5)
        entry_brand = ctk.CTkEntry(win, textvariable=var_new_brand, width=350, height=35, font=("Arial", 12))
        entry_brand.pack(pady=10)
        entry_brand.focus()
        
        def save_brand():
            new_brand = var_new_brand.get().strip()
            if not new_brand:
                messagebox.showwarning("CAMPO VACÍO", "Debe ingresar un nombre de marca.", parent=win)
                return
            
            if new_brand in self.brands:
                messagebox.showwarning("YA EXISTE", f"La marca '{new_brand}' ya existe en la lista.", parent=win)
                return
            
            # Guardar en la base de datos
            if self.logic.marcas.add_brand(new_brand):
                # Recargar lista de marcas
                self.brands = self.load_all_brands()
                self.combo_brand.configure(values=self.brands)
                self.combo_brand.set(new_brand)
                
                # Actualizar modelos
                self.on_brand_change(new_brand)
                
                messagebox.showinfo("MARCA AGREGADA", f"La marca '{new_brand}' ha sido guardada exitosamente.", parent=win)
                win.destroy()
            else:
                messagebox.showerror("ERROR", "No se pudo guardar la marca.", parent=win)
        
        def cancel():
            # Volver a la marca anterior o Samsung
            self.combo_brand.set("SAMSUNG")
            self.on_brand_change("SAMSUNG")
            win.destroy()
        
        btn_frame = ctk.CTkFrame(win, fg_color="transparent")
        btn_frame.pack(pady=20)
        ctk.CTkButton(btn_frame, text="GUARDAR", command=save_brand, fg_color="green", 
                     width=150, height=40, font=("Arial", 12, "bold")).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="CANCELAR", command=cancel, fg_color="gray", 
                     width=150, height=40, font=("Arial", 12, "bold")).pack(side="left", padx=10)
        
        entry_brand.bind("<Return>", lambda e: save_brand())
        win.protocol("WM_DELETE_WINDOW", cancel)

    def on_brand_change(self, brand_name):
        tipo = self.combo_type.get()
        modelos = self.logic.models.get_models_by_brand(brand_name, tipo)
        # Ordenar modelos alfabéticamente
        modelos_ordenados = sorted(modelos) if modelos else []
        self.combo_model.configure(values=modelos_ordenados)
        self.combo_model.set("")

    def on_type_select(self, type_name):
        """Maneja la selección de tipo de dispositivo, incluyendo OTRO"""
        if type_name == "OTRO":
            self.add_custom_device_type()
        else:
            self.on_type_change(type_name)
    
    def add_custom_device_type(self):
        """Permite agregar un tipo de dispositivo personalizado"""
        win = ctk.CTkToplevel(self)
        win.title("AGREGAR NUEVO TIPO DE DISPOSITIVO")
        win.geometry("500x300")
        win.attributes("-topmost", True)
        win.grab_set()
        # Centrar ventana
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (500 // 2)
        y = (win.winfo_screenheight() // 2) - (300 // 2)
        win.geometry(f"500x300+{x}+{y}")
        
        ctk.CTkLabel(win, text="NUEVO TIPO DE DISPOSITIVO", font=("Arial", 16, "bold")).pack(pady=20)
        
        var_new_type = ctk.StringVar()
        var_new_type.trace("w", lambda *args: var_new_type.set(var_new_type.get().upper()))
        
        ctk.CTkLabel(win, text="NOMBRE DEL TIPO:", font=("Arial", 12)).pack(pady=5)
        entry_type = ctk.CTkEntry(win, textvariable=var_new_type, width=350, height=35, font=("Arial", 12))
        entry_type.pack(pady=10)
        entry_type.focus()
        
        def save_type():
            new_type = var_new_type.get().strip()
            if not new_type:
                messagebox.showwarning("CAMPO VACÍO", "Debe ingresar un nombre de tipo.", parent=win)
                return
            
            if new_type in self.device_types:
                messagebox.showwarning("YA EXISTE", f"El tipo '{new_type}' ya existe en la lista.", parent=win)
                return
            
            # Agregar a la lista (antes de OTRO)
            self.device_types.insert(-1, new_type)  # Insertar antes de OTRO
            self.device_types = sorted(self.device_types[:-1]) + ["OTRO"]  # Re-ordenar alfabéticamente
            self.combo_type.configure(values=self.device_types)
            self.combo_type.set(new_type)
            
            # Actualizar modelos
            self.on_type_change(new_type)
            
            messagebox.showinfo("TIPO AGREGADO", f"El tipo '{new_type}' ha sido guardado exitosamente.", parent=win)
            win.destroy()
        
        def cancel():
            # Volver al tipo anterior o CELULAR
            self.combo_type.set("CELULAR")
            self.on_type_change("CELULAR")
            win.destroy()
        
        btn_frame = ctk.CTkFrame(win, fg_color="transparent")
        btn_frame.pack(pady=20)
        ctk.CTkButton(btn_frame, text="GUARDAR", command=save_type, fg_color="green", 
                     width=150, height=40, font=("Arial", 12, "bold")).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="CANCELAR", command=cancel, fg_color="gray", 
                     width=150, height=40, font=("Arial", 12, "bold")).pack(side="left", padx=10)
        
        entry_type.bind("<Return>", lambda e: save_type())
        win.protocol("WM_DELETE_WINDOW", cancel)

    def on_type_change(self, type_name):
        # Cuando cambia el tipo, actualizamos los modelos si hay una marca seleccionada
        brand = self.combo_brand.get()
        if brand:
            self.on_brand_change(brand)
    def uppercase_textbox(self, event):
        try:
            c = self.text_obs.get("0.0", "end-1c")
            if c != c.upper():
                cursor_pos = self.text_obs.index("insert")
                self.text_obs.delete("0.0", "end")
                self.text_obs.insert("0.0", c.upper())
                # Intentar restaurar posición del cursor
                try:
                    self.text_obs.mark_set("insert", cursor_pos)
                except:
                    pass
        except:
            pass
    def clean_money(self, text_val): return float(str(text_val).replace(".", "")) if text_val else 0.0
    
    def search_client(self):
        self.on_search_focus_out(None); q = self.var_search.get(); 
        for w in self.scroll_results.winfo_children(): w.destroy()
        results = self.logic.clients.search_clients(q)
        if not results:
            messagebox.showinfo("CLIENTE NO ENCONTRADO", "El RUT ingresado no existe.\nPor favor, complete los datos para registrarlo.")
            self.var_rut.set(q); self.var_name.set(""); self.var_tel.set(""); self.var_email.set(""); self.entry_name.focus()
            self.btn_save_client.configure(text="GUARDAR CLIENTE") # Asegurar que diga GUARDAR
            self.selected_client_rut = None
            return
        for c in results:
            display_text = f"{c[2]}\n{c[1]}\n{'-'*30}\n"
            btn = ctk.CTkButton(self.scroll_results, text=display_text, command=lambda data=c: self.fill_client_form(data), fg_color="gray30", hover_color="gray40", anchor="w")
            btn.pack(fill="x", pady=2)

    def fill_client_form(self, d): 
        self.var_rut.set(d[1])
        self.var_name.set(d[2])
        self.var_tel.set(d[3])
        self.var_email.set(d[4])
        self.selected_client_rut = d[1]
        self.btn_save_client.configure(text="EDITAR")
        
        # Limpiar observaciones para nuevo servicio
        self.text_obs.delete("0.0", "end")
        self.var_service.set("")
        self.var_part.set("SIN REPUESTO")
        self.var_price.set("")
        self.var_deposit.set("")
        
        self.load_client_history(d[0])
        # La validación automática (trace) se encargará de habilitar los campos, 
        # pero forzamos la verificación aquí por si acaso
        self.check_client_fields()

    def load_client_history(self, client_id):
        orders = self.logic.orders.get_client_history(client_id)
        for w in self.history_scroll.winfo_children(): w.destroy()
        if not orders: 
            ctk.CTkLabel(self.history_scroll, text="SIN SERVICIOS PREVIOS", text_color="gray").pack(pady=10)
        else:
            for o in orders:
                # Extraer información completa
                order_id = o[0]
                equipo = o[4].upper() if o[4] else "N/A"  # Tipo de dispositivo
                marca = o[5].upper() if o[5] else "N/A"   # Marca
                modelo = o[6].upper() if o[6] else "N/A"  # Modelo
                serie = o[7].upper() if o[7] else "S/N"   # Serial
                estado = o[10] if o[10] else "PENDIENTE"  # Estado
                
                # Extraer solo la falla sin el prefijo "FALLA:"
                falla_completa = o[8] if o[8] else "SIN DESCRIPCIÓN"
                if "|" in falla_completa:
                    falla = falla_completa.split("|")[0].replace("FALLA:", "").strip().upper()
                else:
                    falla = falla_completa.replace("FALLA:", "").strip().upper()
                
                # Truncar falla si es muy larga
                if len(falla) > 40:
                    falla = falla[:37] + "..."
                
                precio = self.format_money_val(o[12]) if o[12] else "0"
                
                # Determinar si está activo o entregado
                estado_display = "ENTREGADO" if estado == "ENTREGADO" else "ACTIVO"
                estado_color = "#28a745" if estado == "ENTREGADO" else "#007bff"  # Verde si entregado, azul si activo
                
                # Card container - tamaño reducido
                card = ctk.CTkFrame(self.history_scroll, fg_color="#E8E8E8", corner_radius=5)
                card.pack(fill="x", pady=1, padx=3)
                
                # Info frame 
                info_frame = ctk.CTkFrame(card, fg_color="transparent")
                info_frame.pack(side="left", fill="both", expand=True, padx=3, pady=2)
                
                # Línea 1: ID, Equipo, Marca, Modelo - fuente 14+4=18
                ctk.CTkLabel(info_frame, text=f"#{order_id} - {equipo} {marca} {modelo}", 
                            font=("Arial", 18, "bold"), text_color="#333333", 
                            anchor="w").pack(fill="x", pady=(0,0))
                
                # Línea 2: Serial - fuente 11+4=15
                ctk.CTkLabel(info_frame, text=f"S/N: {serie}", 
                            font=("Arial", 15), text_color="#666666", 
                            anchor="w").pack(fill="x", pady=(0,0))
                
                # Línea 3: Falla - fuente 12+4=16
                ctk.CTkLabel(info_frame, text=f"Falla: {falla}", 
                            font=("Arial", 16), text_color="#555555", 
                            anchor="w").pack(fill="x", pady=(0,0))
                
                # Línea 4: Precio y Estado - fuente 14+4=18 y 11+4=15
                footer_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
                footer_frame.pack(fill="x", pady=(1,0))
                
                ctk.CTkLabel(footer_frame, text=f"${precio}", 
                            font=("Arial", 18, "bold"), text_color="green", 
                            anchor="w").pack(side="left")
                
                ctk.CTkLabel(footer_frame, text=f"[{estado_display}]", 
                            font=("Arial", 15, "bold"), text_color=estado_color, 
                            anchor="e").pack(side="right")
                
                # Botones: Verificar si se puede editar
                can_edit = self.logic.orders.can_edit_order(order_id)
                
                if can_edit:
                    # Botón Editar - tamaño reducido, fuente 11+4=15
                    ctk.CTkButton(card, text="EDITAR", width=40, height=25,
                                 fg_color="#F39C12", hover_color="#E67E22",
                                 font=("Arial", 15, "bold"),
                                 command=lambda oid=order_id: self.load_order_for_edit(oid)).pack(side="right", padx=2, pady=2)
                
                # Botón Ver Detalle - tamaño reducido, fuente 11+4=15
                ctk.CTkButton(card, text="VER", width=35, height=25,
                             fg_color="#5D6D7E", hover_color="#34495E",
                             font=("Arial", 15, "bold"),
                             command=lambda oid=order_id: self.view_ticket_modal(oid)).pack(side="right", padx=2, pady=2)

    def view_ticket_modal(self, order_id):
        data = self.logic.orders.get_ticket_data(order_id); 
        if not data: return
        win = ctk.CTkToplevel(self); win.title(f"ORDEN #{order_id}"); win.geometry("500x600"); win.attributes("-topmost", True)
        # Centrar ventana
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (500 // 2)
        y = (win.winfo_screenheight() // 2) - (600 // 2)
        win.geometry(f"500x600+{x}+{y}")
        ctk.CTkLabel(win, text=f"DETALLE DE ORDEN #{order_id}", font=("Arial", 16, "bold")).pack(pady=20)
        info = f"FECHA: {data[3]}\n\nEQUIPO: {data[4]} {data[5]} {data[6]}\n\nCLIENTE: {data[16]}\n\nFALLA:\n{data[8]}\n\nTOTAL: {self.format_money_val(data[12])}"
        txt = ctk.CTkTextbox(win, height=250); txt.pack(fill="both", padx=20, pady=10); txt.insert("0.0", info)
        def print_ticket(): pdf = PDFGeneratorV2(self.logic); filepath = pdf.generar_orden_ingreso(data); pdf.abrir_pdf(filepath); win.destroy()
        ctk.CTkButton(win, text="🖨️ RE-IMPRIMIR TICKET", command=print_ticket, height=50, font=("Arial", 14, "bold")).pack(pady=20, padx=20, fill="x")

    def load_order_for_edit(self, order_id):
        """Carga los datos de una orden existente para editarla"""
        # Verificar que se puede editar
        if not self.logic.orders.can_edit_order(order_id):
            messagebox.showerror("NO EDITABLE", "Esta orden ya fue cobrada o entregada y no puede ser editada.")
            return
        
        # Obtener datos completos de la orden
        order_data = self.logic.orders.get_ticket_data(order_id)
        if not order_data:
            messagebox.showerror("ERROR", "No se pudo cargar la información de la orden.")
            return
        
        # Configurar modo edición
        self.editing_order_id = order_id
        self.btn_generate_order.configure(text=f"ACTUALIZAR ORDEN #{order_id}")
        
        # Cargar datos del cliente (índices del query: o.*, c.rut, c.nombre, c.telefono, c.email)
        # ordenes tiene 15 columnas (0-14), entonces: [15]=rut, [16]=nombre, [17]=telefono, [18]=email
        self.var_rut.set(order_data[15])
        self.var_name.set(order_data[16])
        self.var_tel.set(order_data[17] if order_data[17] else "")
        self.var_email.set(order_data[18] if order_data[18] else "")
        self.selected_client_rut = order_data[15]
        
        # Cargar datos del equipo
        # [4]=equipo, [5]=marca, [6]=modelo, [7]=serie, [8]=observacion, [10]=accesorios, [11]=riesgoso, [12]=presupuesto, [13]=abono
        self.combo_type.set(order_data[4])
        self.on_brand_change(order_data[5])  # Cargar modelos de la marca
        self.combo_brand.set(order_data[5])
        self.combo_model.set(order_data[6])
        self.var_model.set(order_data[6])
        self.var_serial.set(order_data[7])
        
        # Extraer falla de la observación
        obs_completa = order_data[8]
        if "|" in obs_completa:
            partes = obs_completa.split("|", 1)
            falla = partes[0].replace("FALLA:", "").strip()
            obs_adicional = partes[1].strip()
        else:
            falla = obs_completa.replace("FALLA:", "").strip()
            obs_adicional = ""
        
        self.var_fault.set(falla)
        self.text_obs.delete("0.0", "end")
        self.text_obs.insert("0.0", obs_adicional)
        
        # Accesorios
        accesorios = order_data[10] if order_data[10] else ""
        self.var_sim.set("BANDEJA SIM" in accesorios)
        self.var_simcard.set("SIM CARD" in accesorios)
        self.var_sd.set("MICRO SD" in accesorios)
        self.var_charger.set("CARGADOR" in accesorios)
        self.var_wet.set("MOJADO" in accesorios)
        
        # Riesgoso
        self.var_risky.set(bool(order_data[11]))
        
        # Presupuesto y Abono
        self.var_price.set(str(int(order_data[12])))
        self.var_deposit.set(str(int(order_data[13])) if order_data[13] else "0")
        
        # Cargar técnico asignado
        tech_id = order_data[2]
        for tech_name, tid in self.tech_map.items():
            if tid == tech_id:
                self.combo_tech.set(tech_name)
                break
        
        # Cargar servicios y repuestos desde la base de datos
        # Esto es necesario para poder buscar en los mapas
        services = self.logic.services.get_all_services()
        self.services_map = {s[1]: s[2] for s in services}
        
        parts = self.logic.parts.get_all_parts()
        self.parts_map = {}
        for p in parts:
            nombre = p[1]
            precio = p[4]
            disp = f"{nombre} (${int(precio):,})".replace(",", ".")
            self.parts_map[disp] = precio
        
        # Ya no es necesario actualizar los combos porque ahora son Entry readonly
        
        # Buscar servicio y repuesto en las observaciones adicionales
        # Cuando se selecciona un servicio, se agrega a las observaciones
        # El formato es: "SERVICIO + REPUESTO" o solo "SERVICIO" o solo "REPUESTO"
        
        servicio_encontrado = None
        repuesto_encontrado = None
        
        if obs_adicional:
            obs_texto = obs_adicional.strip()
            
            # Buscar servicio en observaciones
            servicios_coincidentes = []
            for servicio_nombre in self.services_map.keys():
                # Comparación insensible a mayúsculas
                if servicio_nombre.upper() in obs_texto.upper():
                    servicios_coincidentes.append(servicio_nombre)
            
            if servicios_coincidentes:
                # Elegir el servicio más largo (más específico)
                servicio_encontrado = max(servicios_coincidentes, key=len)
                self.var_service.set(servicio_encontrado)
                print(f"DEBUG: Servicio encontrado: '{servicio_encontrado}' en observaciones: '{obs_texto}'")
            else:
                self.var_service.set("")
                print(f"DEBUG: No se encontró servicio en observaciones: '{obs_texto}'")
                print(f"DEBUG: Servicios disponibles: {list(self.services_map.keys())}")
            
            # Buscar repuesto en observaciones
            repuestos_coincidentes = []
            for repuesto_display in self.parts_map.keys():
                # Extraer el nombre sin el precio
                repuesto_nombre = repuesto_display.split('($')[0].strip().upper()
                if repuesto_nombre in obs_texto.upper():
                    repuestos_coincidentes.append(repuesto_display)
            
            if repuestos_coincidentes:
                # Elegir el repuesto más largo (más específico)
                repuesto_encontrado = max(repuestos_coincidentes, key=len)
                self.var_part.set(repuesto_encontrado)
            else:
                self.var_part.set("SIN REPUESTO")
        else:
            # No hay observaciones adicionales
            self.var_service.set("")
            self.var_part.set("SIN REPUESTO")
        
        # Scroll al área de edición
        messagebox.showinfo("MODO EDICIÓN", f"Orden #{order_id} cargada para edición.\n\nRealice los cambios necesarios y presione 'ACTUALIZAR ORDEN'.")

    def clear_client_form(self):
        """Limpiar completamente todos los campos del formulario de cliente e ingreso de equipo"""
        # Resetear modo edición
        self.editing_order_id = None
        self.btn_generate_order.configure(text="GENERAR ORDEN (PENDIENTE)")
        
        # Limpiar datos del cliente
        self.var_rut.set("")
        self.var_name.set("")
        self.var_tel.set("")
        self.var_email.set("")
        self.var_search.set("")
        self.selected_client_rut = None
        self.btn_save_client.configure(text="GUARDAR CLIENTE")
        for w in self.history_scroll.winfo_children(): w.destroy()
        ctk.CTkLabel(self.history_scroll, text="SELECCIONE UN CLIENTE...", text_color="gray").pack(pady=20)
        
        # Limpiar datos del equipo
        self.combo_type.set("CELULAR")  # Resetear tipo de dispositivo
        self.combo_brand.set("SAMSUNG")  # Resetear marca
        self.var_model.set("")
        self.var_serial.set("")
        self.var_fault.set("")  # Limpiar falla interna
        self.text_obs.delete("0.0", "end")  # Limpiar observaciones
        self.var_price.set("")
        self.var_discount.set("")  # Limpiar descuento
        self.var_deposit.set("")
        self.var_service.set("")  # Limpiar servicio seleccionado
        self.var_part.set("SIN REPUESTO")  # Resetear repuesto
        
        # Reset checkboxes y switches
        self.var_sim.set(False)
        self.var_simcard.set(False)
        self.var_sd.set(False)
        self.var_charger.set(False)
        self.var_wet.set(False)
        self.var_risky.set(False)
        
        # Reset servicios y repuestos
        self.var_service.set("")
        self.var_part.set("SIN REPUESTO")
        
        # Deshabilitar campos de equipo
        self.toggle_equipment_fields(False)

    def save_client_data(self):
        self.on_rut_focus_out(None); r = self.var_rut.get().strip(); n = self.var_name.get().strip(); t = self.var_tel.get().strip()
        if not r or not n or not t: messagebox.showwarning("FALTAN DATOS", "RUT, NOMBRE y TELÉFONO obligatorios"); return
        if self.logic.clients.get_client(r): self.logic.clients.update_client(r, n, t, self.var_email.get()); messagebox.showinfo("OK", "Actualizado"); self.search_client()
        else: self.logic.clients.add_client(r, n, t, self.var_email.get()); messagebox.showinfo("OK", "Registrado"); self.var_search.set(r); self.search_client()

    def select_payment_method(self, amount):
        dialog = ctk.CTkToplevel(self)
        dialog.title("SELECCIONAR MÉTODO DE PAGO")
        dialog.geometry("500x450")
        dialog.attributes("-topmost", True)
        dialog.transient(self)
        dialog.grab_set()
        # Centrar ventana
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (450 // 2)
        dialog.geometry(f"500x450+{x}+{y}")

        ctk.CTkLabel(dialog, text=f"ABONO: ${amount:,.0f}".replace(",", "."), font=("Arial", 16, "bold")).pack(pady=15)
        
        payment_method = ctk.StringVar(value="EFECTIVO")
        
        ctk.CTkLabel(dialog, text="MÉTODO DE PAGO PRINCIPAL:").pack(anchor="w", padx=20)
        methods = ["EFECTIVO", "TRANSFERENCIA", "DÉBITO", "CRÉDITO", "PAGO MIXTO"]
        for method in methods:
            ctk.CTkRadioButton(dialog, text=method, variable=payment_method, value=method).pack(anchor="w", padx=40, pady=2)

        def on_confirm():
            dialog.result = payment_method.get()
            dialog.destroy()

        def on_cancel():
            dialog.result = None
            dialog.destroy()

        ctk.CTkButton(dialog, text="CONFIRMAR PAGO", command=on_confirm, fg_color="green").pack(pady=20)
        dialog.protocol("WM_DELETE_WINDOW", on_cancel)
        
        self.wait_window(dialog)
        return getattr(dialog, 'result', None)

    def save_order(self):
        rut = self.var_rut.get(); cdata = self.logic.clients.get_client(rut)
        if not cdata:
            if messagebox.askyesno("CLIENTE NO EXISTE", "Guardar primero?"): self.save_client_data(); cdata = self.logic.clients.get_client(rut); 
            else: return
        if not cdata: return

        brand = self.combo_brand.get(); model = self.var_model.get(); fail = self.var_fault.get()
        try: pre = self.clean_money(self.var_price.get())
        except: pre = 0
        try: desc = self.clean_money(self.var_discount.get())
        except: desc = 0
        if not brand or not model: messagebox.showwarning("FALTAN DATOS", "Falta Marca/Modelo"); return
        # Campo de falla eliminado - ahora es opcional
        if pre <= 0: messagebox.showwarning("FALTAN DATOS", "El PRESUPUESTO TOTAL no puede ser cero."); return
        
        # Validar abono y método de pago
        abo = self.clean_money(self.var_deposit.get())
        metodo_pago = None
        if abo > 0:
            metodo_pago = self.select_payment_method(abo)
            if not metodo_pago:
                messagebox.showwarning("ABONO SIN MÉTODO", "Debe seleccionar un método de pago para el abono.")
                return
        
        tid = self.tech_map.get(self.combo_tech.get()) or 1
        acc = []
        if self.var_sim.get(): acc.append("BANDEJA SIM")
        if self.var_simcard.get(): acc.append("SIM CARD")
        if self.var_sd.get(): acc.append("MICRO SD")
        if self.var_charger.get(): acc.append("CARGADOR")
        if self.var_wet.get(): acc.append("MOJADO")
        self.logic.models.learn_model(brand, model, self.combo_type.get())
        
        # Obtener fecha de entrega
        delivery_date = self.date_delivery.get_date().strftime('%Y-%m-%d')
        
        try:
            # Verificar si estamos editando una orden existente
            if self.editing_order_id:
                # Actualizar orden existente
                success = self.logic.orders.update_order(
                    self.editing_order_id, tid, self.combo_type.get(), brand, model, 
                    self.var_serial.get(), fail, self.text_obs.get("0.0", "end").strip(), 
                    acc, self.var_risky.get(), pre, desc, abo, delivery_date
                )
                if success:
                    # Crear pedido automáticamente si hay repuesto seleccionado
                    repuesto_seleccionado = self.var_part.get()
                    print(f"DEBUG (UPDATE): Repuesto seleccionado: '{repuesto_seleccionado}'")
                    
                    if repuesto_seleccionado and repuesto_seleccionado != "SIN REPUESTO":
                        try:
                            # Obtener proveedor seleccionado
                            proveedor_nombre = self.combo_provider.get() if hasattr(self, 'combo_provider') else None
                            print(f"DEBUG (UPDATE): Proveedor nombre: '{proveedor_nombre}'")
                            
                            if proveedor_nombre and proveedor_nombre != "CUALQUIERA":
                                # Buscar el ID del proveedor
                                proveedores = self.logic.providers.get_all_providers()
                                proveedor_id = None
                                for prov in proveedores:
                                    if prov[1] == proveedor_nombre:
                                        proveedor_id = prov[0]
                                        break
                                
                                print(f"DEBUG (UPDATE): Proveedor ID: {proveedor_id}")
                                
                                # Buscar el repuesto por nombre
                                nombre_repuesto = repuesto_seleccionado.split(" ($")[0] if " ($" in repuesto_seleccionado else repuesto_seleccionado
                                print(f"DEBUG (UPDATE): Nombre repuesto a buscar: '{nombre_repuesto}'")
                                
                                repuestos = self.logic.parts.OBTENER_TODOS_REPUESTOS()
                                repuesto_id = None
                                for rep in repuestos:
                                    if rep[1] == nombre_repuesto:
                                        repuesto_id = rep[0]
                                        break
                                
                                print(f"DEBUG (UPDATE): Repuesto ID: {repuesto_id}")
                                
                                # Crear el pedido si tenemos proveedor y repuesto
                                if proveedor_id and repuesto_id:
                                    print(f"DEBUG (UPDATE): Creando pedido - Proveedor: {proveedor_id}, Repuesto: {repuesto_id}, Orden: {self.editing_order_id}")
                                    pedido_id = self.logic.pedidos.CREAR_PEDIDO(
                                        proveedor_id=proveedor_id,
                                        cantidad=1,
                                        tipo_item='REPUESTO',
                                        item_id=repuesto_id,
                                        orden_id=self.editing_order_id,
                                        notas=f"Pedido automático - Orden #{self.editing_order_id} (actualizada)",
                                        usuario=self.logic.current_user[1] if hasattr(self.logic, 'current_user') else "SISTEMA"
                                    )
                                    if pedido_id:
                                        print(f"✓ Pedido #{pedido_id} creado automáticamente para orden #{self.editing_order_id}")
                                    else:
                                        print(f"✗ No se pudo crear el pedido para orden #{self.editing_order_id}")
                                else:
                                    print(f"DEBUG (UPDATE): No se pudo crear pedido - Proveedor ID: {proveedor_id}, Repuesto ID: {repuesto_id}")
                            else:
                                print(f"DEBUG (UPDATE): Proveedor no válido o es CUALQUIERA")
                        except Exception as e:
                            print(f"Error al crear pedido automático (UPDATE): {e}")
                            import traceback
                            traceback.print_exc()
                    else:
                        print(f"DEBUG (UPDATE): No se creará pedido - repuesto no seleccionado o es SIN REPUESTO")
                    
                    messagebox.showinfo("ORDEN ACTUALIZADA", f"ORDEN #{self.editing_order_id} ACTUALIZADA EXITOSAMENTE.")
                    self.editing_order_id = None
                    self.btn_generate_order.configure(text="GENERAR ORDEN (PENDIENTE)")
                    self.clear_client_form()
                    for w in self.scroll_results.winfo_children(): w.destroy()
                else:
                    messagebox.showerror("ERROR", "No se pudo actualizar la orden. Puede que ya haya sido cobrada o entregada.")
            else:
                # Crear nueva orden
                oid = self.logic.orders.create_order(cdata[0], tid, self.combo_type.get(), brand, model, self.var_serial.get(), fail, self.text_obs.get("0.0", "end").strip(), acc, self.var_risky.get(), pre, desc, abo, delivery_date)
                if oid:
                    # Crear pedido automáticamente si hay repuesto seleccionado
                    repuesto_seleccionado = self.var_part.get()
                    print(f"DEBUG: Repuesto seleccionado: '{repuesto_seleccionado}'")
                    
                    if repuesto_seleccionado and repuesto_seleccionado != "SIN REPUESTO":
                        try:
                            # Obtener proveedor seleccionado
                            proveedor_nombre = self.combo_provider.get() if hasattr(self, 'combo_provider') else None
                            print(f"DEBUG: Proveedor nombre: '{proveedor_nombre}'")
                            
                            if proveedor_nombre and proveedor_nombre != "CUALQUIERA":
                                # Buscar el ID del proveedor
                                proveedores = self.logic.providers.get_all_providers()
                                proveedor_id = None
                                for prov in proveedores:
                                    if prov[1] == proveedor_nombre:
                                        proveedor_id = prov[0]
                                        break
                                
                                print(f"DEBUG: Proveedor ID: {proveedor_id}")
                                
                                # Buscar el repuesto por nombre
                                nombre_repuesto = repuesto_seleccionado.split(" ($")[0] if " ($" in repuesto_seleccionado else repuesto_seleccionado
                                print(f"DEBUG: Nombre repuesto a buscar: '{nombre_repuesto}'")
                                
                                repuestos = self.logic.parts.OBTENER_TODOS_REPUESTOS()
                                repuesto_id = None
                                for rep in repuestos:
                                    if rep[1] == nombre_repuesto:  # rep[1] es el nombre
                                        repuesto_id = rep[0]  # rep[0] es el id
                                        break
                                
                                print(f"DEBUG: Repuesto ID: {repuesto_id}")
                                
                                # Crear el pedido si tenemos proveedor y repuesto
                                if proveedor_id and repuesto_id:
                                    print(f"DEBUG: Creando pedido - Proveedor: {proveedor_id}, Repuesto: {repuesto_id}, Orden: {oid}")
                                    # Usar el formato correcto: proveedor_id, cantidad, tipo_item, item_id, orden_id, notas, usuario
                                    pedido_id = self.logic.pedidos.CREAR_PEDIDO(
                                        proveedor_id=proveedor_id,
                                        cantidad=1,
                                        tipo_item='REPUESTO',
                                        item_id=repuesto_id,
                                        orden_id=oid,
                                        notas=f"Pedido automático - Orden #{oid}",
                                        usuario=self.logic.current_user[1] if hasattr(self.logic, 'current_user') else "SISTEMA"
                                    )
                                    if pedido_id:
                                        print(f"✓ Pedido #{pedido_id} creado automáticamente para orden #{oid}")
                                    else:
                                        print(f"✗ No se pudo crear el pedido para orden #{oid}")
                                else:
                                    print(f"DEBUG: No se pudo crear pedido - Proveedor ID: {proveedor_id}, Repuesto ID: {repuesto_id}")
                            else:
                                print(f"DEBUG: Proveedor no válido o es CUALQUIERA")
                        except Exception as e:
                            print(f"Error al crear pedido automático: {e}")
                            import traceback
                            traceback.print_exc()
                    else:
                        print(f"DEBUG: No se creará pedido - repuesto no seleccionado o es SIN REPUESTO")
                    
                    # TODO: Registrar el abono en caja cuando la funcionalidad esté implementada
                    # if abo > 0 and metodo_pago:
                    #     exito, mensaje = self.logic.caja.REGISTRAR_INGRESO(abo, metodo_pago, f"ABONO ORDEN #{oid}", orden_id=oid)
                    #     if not exito:
                    #         messagebox.showerror("ERROR DE CAJA", f"No se pudo registrar el abono en caja.\n\n{mensaje}\n\nLa orden #{oid} fue creada, pero deberá registrar el abono manualmente en el módulo de Caja.")
                    
                    if messagebox.askyesno("ORDEN GUARDADA", f"ORDEN #{oid} GENERADA EXITOSAMENTE.\n\n¿DESEA IMPRIMIR EL TICKET AHORA?"):
                        full_data = self.logic.orders.get_ticket_data(oid)
                        if full_data: 
                            pdf = PDFGeneratorV2(self.logic)
                            filepath = pdf.generar_orden_ingreso(full_data)
                            pdf.abrir_pdf(filepath)
                    
                    self.clear_client_form()
                    for w in self.scroll_results.winfo_children(): w.destroy()
        except Exception as e: messagebox.showerror("Error al Guardar Orden", f"Ha ocurrido un error:\n{e}")

    def on_rut_focus_out(self, event):
        self.var_rut.set(self.format_rut_val(self.var_rut.get()))
    
    def enviar_whatsapp_cliente(self):
        """Envía mensaje de WhatsApp al cliente seleccionado"""
        if not self.logic.mensajeria:
            messagebox.showerror("Error", "Módulo de mensajería no disponible")
            return
        
        # Verificar que haya un cliente seleccionado
        rut = self.var_rut.get().strip()
        if not rut:
            messagebox.showwarning("Sin Cliente", "Debe seleccionar o ingresar un cliente primero")
            return
        
        # Obtener datos del cliente
        cliente = self.logic.clients.get_client(rut)
        if not cliente:
            messagebox.showwarning("Cliente No Encontrado", "No se encontró el cliente en la base de datos")
            return
        
        telefono = cliente[3] if len(cliente) > 3 else ""
        if not telefono:
            messagebox.showwarning("Sin Teléfono", "El cliente no tiene número de teléfono registrado")
            return
        
        nombre_cliente = cliente[1] if len(cliente) > 1 else "Cliente"
        
        # Obtener datos del equipo y servicio
        tipo_dispositivo = self.combo_type.get()
        marca = self.combo_brand.get()
        modelo = self.var_model.get()
        falla = self.var_fault.get()
        servicio = self.var_service.get()
        observaciones = self.text_obs.get("0.0", "end").strip()
        
        # Obtener fechas
        fecha_recepcion = datetime.now().strftime('%d/%m/%Y')
        try:
            fecha_entrega = self.date_delivery.get_date().strftime('%d/%m/%Y')
        except:
            fecha_entrega = "Por definir"
        
        # Generar mensaje automático
        mensaje_base = f"Estimado/a {nombre_cliente},\n\n"
        mensaje_base += f"Le informamos que hemos recibido su equipo:\n\n"
        mensaje_base += f"📱 Equipo: {tipo_dispositivo} {marca} {modelo}\n"
        mensaje_base += f"📅 Fecha de recepción: {fecha_recepcion}\n\n"
        
        if falla:
            mensaje_base += f"🔧 Problema reportado: {falla}\n\n"
        
        if servicio:
            mensaje_base += f"⚙️ Servicio a realizar: {servicio}\n\n"
        
        if observaciones:
            mensaje_base += f"📋 Trabajos a realizar: {observaciones}\n\n"
        
        mensaje_base += f"📆 Fecha estimada de entrega: {fecha_entrega}\n\n"
        mensaje_base += f"Le mantendremos informado del progreso de la reparación.\n\n"
        mensaje_base += f"Saludos cordiales,\nServitec Manager"
        
        # Ventana para editar mensaje
        win = ctk.CTkToplevel(self)
        win.title("📱 Enviar WhatsApp")
        win.geometry("650x700")
        win.attributes("-topmost", True)
        win.configure(fg_color=Theme.BACKGROUND)
        win.grab_set()
        
        # Centrar ventana
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (650 // 2)
        y = (win.winfo_screenheight() // 2) - (700 // 2)
        win.geometry(f"650x700+{x}+{y}")
        
        header = ctk.CTkFrame(win, fg_color=Theme.SUCCESS, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(
            header,
            text=f"📱 ENVIAR WHATSAPP A {nombre_cliente}",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"),
            text_color=Theme.WHITE
        ).pack(pady=20)
        
        content = ctk.CTkFrame(win, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            content,
            text=f"Teléfono: {telefono}",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold")
        ).pack(pady=(0, 10))
        
        ctk.CTkLabel(
            content,
            text="Mensaje (puede editarlo antes de enviar):",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
            anchor="w"
        ).pack(fill="x")
        
        mensaje_text = ctk.CTkTextbox(content, height=400, font=(Theme.FONT_FAMILY, 12))
        mensaje_text.pack(fill="both", expand=True, pady=(5, 15))
        mensaje_text.insert("1.0", mensaje_base)
        
        def enviar():
            mensaje = mensaje_text.get("1.0", "end").strip()
            if not mensaje:
                messagebox.showwarning("Mensaje Vacío", "Debe escribir un mensaje")
                return
            
            try:
                exito = self.logic.mensajeria.ENVIAR_WHATSAPP_WEB(telefono, mensaje)
                if exito:
                    messagebox.showinfo("✓ Enviado", "WhatsApp enviado correctamente")
                    win.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo enviar el mensaje")
            except Exception as e:
                messagebox.showerror("Error", f"Error al enviar: {str(e)}")
        
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x")
        
        ctk.CTkButton(
            btn_frame,
            text="📤 ENVIAR",
            command=enviar,
            **Theme.get_button_style("success"),
            height=45
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ctk.CTkButton(
            btn_frame,
            text="CANCELAR",
            command=win.destroy,
            **Theme.get_button_style("error"),
            height=45
        ).pack(side="right", fill="x", expand=True, padx=(5, 0))
    
    def enviar_email_cliente(self):
        """Envía email al cliente seleccionado"""
        if not self.logic.mensajeria:
            messagebox.showerror("Error", "Módulo de mensajería no disponible")
            return
        
        # Verificar que haya un cliente seleccionado
        rut = self.var_rut.get().strip()
        if not rut:
            messagebox.showwarning("Sin Cliente", "Debe seleccionar o ingresar un cliente primero")
            return
        
        # Obtener datos del cliente
        cliente = self.logic.clients.get_client(rut)
        if not cliente:
            messagebox.showwarning("Cliente No Encontrado", "No se encontró el cliente en la base de datos")
            return
        
        email = cliente[4] if len(cliente) > 4 else ""
        if not email:
            messagebox.showwarning("Sin Email", "El cliente no tiene email registrado")
            return
        
        nombre_cliente = cliente[1] if len(cliente) > 1 else "Cliente"
        
        # Obtener datos del equipo y servicio
        tipo_dispositivo = self.combo_type.get()
        marca = self.combo_brand.get()
        modelo = self.var_model.get()
        falla = self.var_fault.get()
        servicio = self.var_service.get()
        observaciones = self.text_obs.get("0.0", "end").strip()
        
        # Obtener fechas
        fecha_recepcion = datetime.now().strftime('%d/%m/%Y')
        try:
            fecha_entrega = self.date_delivery.get_date().strftime('%d/%m/%Y')
        except:
            fecha_entrega = "Por definir"
        
        # Generar mensaje automático
        mensaje_base = f"Estimado/a {nombre_cliente},\n\n"
        mensaje_base += f"Le informamos que hemos recibido su equipo:\n\n"
        mensaje_base += f"Equipo: {tipo_dispositivo} {marca} {modelo}\n"
        mensaje_base += f"Fecha de recepción: {fecha_recepcion}\n\n"
        
        if falla:
            mensaje_base += f"Problema reportado: {falla}\n\n"
        
        if servicio:
            mensaje_base += f"Servicio a realizar: {servicio}\n\n"
        
        if observaciones:
            mensaje_base += f"Trabajos a realizar:\n{observaciones}\n\n"
        
        mensaje_base += f"Fecha estimada de entrega: {fecha_entrega}\n\n"
        mensaje_base += f"Le mantendremos informado del progreso de la reparación.\n\n"
        mensaje_base += f"Saludos cordiales,\nServitec Manager"
        
        # Ventana para escribir email
        win = ctk.CTkToplevel(self)
        win.title("📧 Enviar Email")
        win.geometry("700x750")
        win.attributes("-topmost", True)
        win.configure(fg_color=Theme.BACKGROUND)
        win.grab_set()
        
        # Centrar ventana
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (700 // 2)
        y = (win.winfo_screenheight() // 2) - (750 // 2)
        win.geometry(f"700x750+{x}+{y}")
        
        header = ctk.CTkFrame(win, fg_color=Theme.PRIMARY, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(
            header,
            text=f"📧 ENVIAR EMAIL A {nombre_cliente}",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"),
            text_color=Theme.WHITE
        ).pack(pady=20)
        
        content = ctk.CTkFrame(win, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            content,
            text=f"Para: {email}",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold")
        ).pack(pady=(0, 10))
        
        ctk.CTkLabel(
            content,
            text="Asunto:",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
            anchor="w"
        ).pack(fill="x")
        
        asunto_var = ctk.StringVar(value=f"Recepción de su {tipo_dispositivo} {marca} {modelo}")
        ctk.CTkEntry(content, textvariable=asunto_var, font=(Theme.FONT_FAMILY, 12)).pack(fill="x", pady=(5, 15))
        
        ctk.CTkLabel(
            content,
            text="Mensaje (puede editarlo antes de enviar):",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
            anchor="w"
        ).pack(fill="x")
        
        mensaje_text = ctk.CTkTextbox(content, height=400, font=(Theme.FONT_FAMILY, 12))
        mensaje_text.pack(fill="both", expand=True, pady=(5, 15))
        mensaje_text.insert("1.0", mensaje_base)
        
        def enviar():
            asunto = asunto_var.get().strip()
            mensaje = mensaje_text.get("1.0", "end").strip()
            
            if not asunto:
                messagebox.showwarning("Asunto Vacío", "Debe ingresar un asunto")
                return
            if not mensaje:
                messagebox.showwarning("Mensaje Vacío", "Debe escribir un mensaje")
                return
            
            try:
                mensaje_html = f"<html><body><pre style='font-family: Arial; font-size: 14px;'>{mensaje}</pre></body></html>"
                exito = self.logic.mensajeria.ENVIAR_EMAIL([email], asunto, mensaje_html)
                if exito:
                    messagebox.showinfo("✓ Enviado", "Email enviado correctamente")
                    win.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo enviar el email")
            except Exception as e:
                messagebox.showerror("Error", f"Error al enviar: {str(e)}")
        
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x")
        
        ctk.CTkButton(
            btn_frame,
            text="📤 ENVIAR",
            command=enviar,
            **Theme.get_button_style("primary"),
            height=45
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ctk.CTkButton(
            btn_frame,
            text="CANCELAR",
            command=win.destroy,
            **Theme.get_button_style("error"),
            height=45
        ).pack(side="right", fill="x", expand=True, padx=(5, 0))
        mensaje_text.pack(fill="both", expand=True, pady=(5, 15))
        mensaje_text.insert("1.0", f"Estimado/a {cliente[1]},\n\n")
        
        def enviar():
            asunto = asunto_var.get().strip()
            mensaje = mensaje_text.get("1.0", "end").strip()
            
            if not asunto:
                messagebox.showwarning("Asunto Vacío", "Debe ingresar un asunto")
                return
            if not mensaje:
                messagebox.showwarning("Mensaje Vacío", "Debe escribir un mensaje")
                return
            
            try:
                mensaje_html = f"<html><body><p>{mensaje.replace(chr(10), '<br>')}</p></body></html>"
                exito = self.logic.mensajeria.ENVIAR_EMAIL([email], asunto, mensaje_html)
                if exito:
                    messagebox.showinfo("✓ Enviado", "Email enviado correctamente")
                    win.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo enviar el email")
            except Exception as e:
                messagebox.showerror("Error", f"Error al enviar: {str(e)}")
        
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x")
        
        ctk.CTkButton(
            btn_frame,
            text="📤 ENVIAR",
            command=enviar,
            **Theme.get_button_style("primary"),
            height=45
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ctk.CTkButton(
            btn_frame,
            text="CANCELAR",
            command=win.destroy,
            **Theme.get_button_style("error"),
            height=45
        ).pack(side="right", fill="x", expand=True, padx=(5, 0))
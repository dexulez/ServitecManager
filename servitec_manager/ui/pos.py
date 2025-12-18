import customtkinter as ctk
from tkinter import messagebox
from .theme import Theme

class POSFrame(ctk.CTkFrame):
    def __init__(self, parent, logic, current_user):
        super().__init__(parent, fg_color=Theme.BACKGROUND)
        self.logic = logic
        self.current_user = current_user
        
        self.cart = [] 
        self.all_products = []
        
        # Variables de Pago
        self.var_cash = ctk.StringVar()
        self.var_transf = ctk.StringVar()
        self.var_debit = ctk.StringVar()
        self.var_credit = ctk.StringVar()
        self.var_discount = ctk.StringVar()
        self.var_search = ctk.StringVar()
        
        # Traces
        self.var_search.trace("w", lambda *a: self.force_uppercase(self.var_search))
        for v in [self.var_cash, self.var_transf, self.var_debit, self.var_credit, self.var_discount]:
            v.trace("w", lambda *a, var=v: self.format_live(var))
            
        self.var_discount.trace("w", self.update_total_label)

        self.setup_ui()
        self.load_products()

    def refresh(self):
        self.load_products()

    def force_uppercase(self, var):
        val = var.get()
        if val != val.upper():
            var.set(val.upper())

    def format_live(self, var):
        raw = var.get().replace(".", "")
        if not raw.isdigit():
            if raw: var.set(''.join(filter(str.isdigit, raw)))
            return
        try:
            val = int(raw)
            if var.get() != f"{val:,}".replace(",", "."): var.set(f"{val:,}".replace(",", "."))
        except: pass

    def clean_money(self, text):
        if not text: return 0.0
        return float(str(text).replace(".", ""))

    def format_money(self, val):
        try: return f"{int(val):,}".replace(",", ".")
        except: return "0"

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1); self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # IZQUIERDA: PRODUCTOS
        left_panel = ctk.CTkFrame(self, **Theme.get_card_style())
        left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Header
        header = ctk.CTkFrame(left_panel, fg_color="transparent")
        header.pack(fill="x", pady=Theme.PADDING_LARGE, padx=Theme.PADDING_LARGE)
        ctk.CTkLabel(header, text="📚 CATÁLOGO (VENTA DIRECTA)", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"), text_color=Theme.TEXT_PRIMARY).pack()
        
        # Separator
        ctk.CTkFrame(left_panel, height=2, fg_color=Theme.DIVIDER).pack(fill="x", pady=(0, Theme.PADDING_MEDIUM))
        
        self.entry_search = ctk.CTkEntry(left_panel, textvariable=self.var_search, placeholder_text="🔍 BUSCAR ARTÍCULO...", height=40, corner_radius=Theme.RADIUS_MEDIUM, border_color=Theme.BORDER)
        self.entry_search.pack(fill="x", padx=10, pady=5)
        self.entry_search.bind("<KeyRelease>", self.filter_products)
        
        self.scroll_products = ctk.CTkScrollableFrame(left_panel, fg_color=Theme.BACKGROUND_LIGHT, corner_radius=Theme.RADIUS_MEDIUM)
        self.scroll_products.pack(fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkButton(left_panel, text="➕ NUEVO ARTÍCULO (TIENDA)", command=self.open_add_product_window, **Theme.get_button_style("accent"), height=45).pack(pady=10, fill="x", padx=10)

        # DERECHA: CARRITO Y PAGO
        right_panel = ctk.CTkFrame(self, **Theme.get_card_style())
        right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Header
        header_right = ctk.CTkFrame(right_panel, fg_color="transparent")
        header_right.pack(fill="x", pady=Theme.PADDING_LARGE, padx=Theme.PADDING_LARGE)
        ctk.CTkLabel(header_right, text="🛒 CARRITO DE COMPRAS", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"), text_color=Theme.TEXT_PRIMARY).pack()
        
        # Separator
        ctk.CTkFrame(right_panel, height=2, fg_color=Theme.DIVIDER).pack(fill="x", pady=(0, Theme.PADDING_MEDIUM))
        
        ctk.CTkButton(right_panel, text="🔧 IMPORTAR ORDEN TALLER", command=self.open_service_picker, **Theme.get_button_style("primary"), height=40).pack(fill="x", padx=10, pady=5)

        self.scroll_cart = ctk.CTkScrollableFrame(right_panel, fg_color=Theme.BACKGROUND_LIGHT, height=200, corner_radius=Theme.RADIUS_MEDIUM)
        self.scroll_cart.pack(fill="both", expand=True, padx=5, pady=5)
        
        # TOTALES
        self.lbl_total = ctk.CTkLabel(right_panel, text="TOTAL: $0", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H1, "bold"), text_color=Theme.SUCCESS)
        self.lbl_total.pack(pady=10)

        # PAGOS
        pay_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        pay_frame.pack(fill="x", padx=10)
        
        def make_pay_row(parent, txt, target_var, other_vars):
            f = ctk.CTkFrame(parent, fg_color="transparent"); f.pack(fill="x", pady=2)
            
            ctk.CTkLabel(f, text=txt, width=140, anchor="w", text_color="#333333", font=("Arial", 12, "bold")).pack(side="left")
            
            entry = ctk.CTkEntry(f, textvariable=target_var, width=120, justify="right", font=("Arial", 12, "bold"))
            entry.pack(side="right")
            
            entry.bind("<FocusIn>", lambda e: self.auto_fill_payment(target_var, other_vars))
            entry.bind("<Return>", lambda e: self.auto_fill_payment(target_var, other_vars))

        all_vars = [self.var_cash, self.var_transf, self.var_debit, self.var_credit]

        make_pay_row(pay_frame, "EFECTIVO:", self.var_cash, [v for v in all_vars if v != self.var_cash])
        make_pay_row(pay_frame, "TRANSFERENCIA:", self.var_transf, [v for v in all_vars if v != self.var_transf])
        make_pay_row(pay_frame, "T. DÉBITO:", self.var_debit, [v for v in all_vars if v != self.var_debit])
        make_pay_row(pay_frame, "T. CRÉDITO:", self.var_credit, [v for v in all_vars if v != self.var_credit])
        
        ctk.CTkLabel(pay_frame, text="------------------", text_color="gray").pack()
        
        f_desc = ctk.CTkFrame(pay_frame, fg_color="transparent"); f_desc.pack(fill="x", pady=2)
        ctk.CTkLabel(f_desc, text="DESCUENTO ($):", width=140, anchor="w", text_color="#C0392B", font=("Arial", 12, "bold")).pack(side="left")
        entry_desc = ctk.CTkEntry(f_desc, textvariable=self.var_discount, width=120, justify="right", text_color="#C0392B", font=("Arial", 12, "bold"))
        entry_desc.pack(side="right")
        entry_desc.bind("<Return>", lambda e: self.update_total_label())

        ctk.CTkButton(right_panel, text="💵 COBRAR", command=self.checkout, **Theme.get_button_style("success"), height=55).pack(pady=20, fill="x", padx=20)

    def get_subtotal(self):
        return sum([item[2] * item[3] for item in self.cart])

    def get_final_total(self):
        sub = self.get_subtotal()
        desc = self.clean_money(self.var_discount.get())
        return max(0, sub - desc)
    
    def get_abonos_total(self):
        """Calcula el total de abonos ya pagados de órdenes en el carrito"""
        abonos = 0
        for item in self.cart:
            _, _, _, _, is_srv, details = item
            if is_srv and details:
                abono = details.get('abono', 0)
                abonos += abono
        return abonos
    
    def get_total_to_pay(self):
        """Calcula el monto pendiente de pago (Total - Abonos - Descuentos)"""
        total = self.get_final_total()
        abonos = self.get_abonos_total()
        return max(0, total - abonos)

    def update_total_label(self, *args):
        total = self.get_final_total()
        abonos = self.get_abonos_total()
        
        if abonos > 0:
            pendiente = self.get_total_to_pay()
            self.lbl_total.configure(text=f"TOTAL: ${self.format_money(total)} | PENDIENTE: ${self.format_money(pendiente)}")
        else:
            self.lbl_total.configure(text=f"TOTAL: ${self.format_money(total)}")

    def auto_fill_payment(self, target_var, other_vars):
        try:
            total_to_pay = self.get_total_to_pay()
            paid_so_far = sum([self.clean_money(v.get()) for v in other_vars])
            target_var.set(int(max(0, total_to_pay - paid_so_far)))
            self.update() 
        except: pass

    def load_products(self):
        # CARGA DESDE LA TABLA 'INVENTARIO' (SOLO VENTAS)
        self.all_products = self.logic.inventory.get_products()
        print(f"DEBUG POS: Productos cargados: {len(self.all_products)}")
        if self.all_products:
            for p in self.all_products[:3]:  # Mostrar los primeros 3
                print(f"DEBUG POS: Producto: ID={p[0]}, Nombre={p[1]}, Precio={p[4] if len(p) > 4 else 'N/A'}")
        self.display_products(self.all_products)

    def filter_products(self, event):
        query = self.entry_search.get().upper()
        # Filtramos usando el índice 1 (nombre) independientemente del tamaño de la tupla
        filtered = [p for p in self.all_products if query in p[1].upper()]
        self.display_products(filtered)

    def display_products(self, products):
        for w in self.scroll_products.winfo_children(): w.destroy()
        for p in products:
            # Extracción segura de datos usando índices negativos
            # Estructura esperada: (id, nombre, categoria, costo, precio, stock, proveedor_id)
            pid = p[0]
            name = p[1]
            price = p[4]  # CORREGIDO: precio está en índice 4
            stock = p[5]  # CORREGIDO: stock está en índice 5
            
            card = ctk.CTkFrame(self.scroll_products, **Theme.get_card_style())
            card.pack(fill="x", pady=2, padx=2)
            
            ctk.CTkLabel(card, text=name.upper(), font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"), width=150, anchor="w", text_color=Theme.TEXT_PRIMARY).pack(side="left", padx=5)
            ctk.CTkLabel(card, text=f"${self.format_money(price)}", width=80, text_color=Theme.SUCCESS, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold")).pack(side="left")
            
            color_stock = Theme.TEXT_PRIMARY if stock > 5 else Theme.ERROR
            ctk.CTkLabel(card, text=f"S:{stock}", width=50, text_color=color_stock, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold")).pack(side="left")
            
            # CORRECCIÓN DEL ERROR "unknown option -state":
            # Creamos el botón sin el estado y lo configuramos después si es necesario
            btn = ctk.CTkButton(card, text="➕", width=40, **Theme.get_button_style("primary"), command=lambda x=p: self.add_to_cart(x, False))
            btn.pack(side="right", padx=5)
            
            if stock <= 0:
                btn.configure(state="disabled")

    def add_to_cart(self, item_data, is_service, details=None):
        if is_service:
            pid, name, price = item_data
            for i in self.cart:
                if i[0] == pid and i[4]: return 
            self.cart.append((pid, name, 1, price, True, details))
        else:
            # Extracción segura - CORREGIDO
            pid = item_data[0]
            name = item_data[1]
            price = item_data[4]  # CORREGIDO: precio está en índice 4
            
            found = False
            for i, it in enumerate(self.cart):
                if it[0] == pid and not it[4]:
                    self.cart[i] = (pid, name, it[2]+1, price, False, None)
                    found = True; break
            if not found: self.cart.append((pid, name, 1, price, False, None))
        self.update_cart_ui()

    def update_cart_ui(self):
        for w in self.scroll_cart.winfo_children(): w.destroy()
        total = 0
        abonos_total = 0
        
        for i, item in enumerate(self.cart):
            pid, name, qty, price, is_srv, details = item
            sub = qty * price
            total += sub
            
            row = ctk.CTkFrame(self.scroll_cart, fg_color="white")
            row.pack(fill="x", pady=2)
            
            txt = f"[SERV] {name.upper()}" if is_srv else f"{name.upper()} x{qty}"
            ctk.CTkLabel(row, text=txt, width=250, anchor="w", font=("Arial", 11), text_color="#333333").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=f"${self.format_money(sub)}", width=80, text_color="green", font=("Arial", 11, "bold")).pack(side="left")
            ctk.CTkButton(row, text="X", width=30, fg_color="red", command=lambda idx=i: self.remove_from_cart(idx)).pack(side="right", padx=5)
            
            # Si es un servicio con abono pagado, mostrar detalles del abono
            if is_srv and details:
                abono = details.get('abono', 0)
                if abono > 0:
                    abonos_total += abono
                    # Row adicional para mostrar el abono
                    row_abono = ctk.CTkFrame(self.scroll_cart, fg_color="#f0f0f0")
                    row_abono.pack(fill="x", pady=(0, 2), padx=(10, 0))
                    ctk.CTkLabel(row_abono, text="   ↳ Abono pagado:", font=("Arial", 10), text_color="#666666").pack(side="left", padx=5)
                    ctk.CTkLabel(row_abono, text=f"-${self.format_money(abono)}", font=("Arial", 10, "bold"), text_color="#ff6b6b").pack(side="left")
        
        self.update_total_label()
        
        # Mostrar resumen de abonos si existen
        if abonos_total > 0:
            row_resumen = ctk.CTkFrame(self.scroll_cart, fg_color="#e8f5e9")
            row_resumen.pack(fill="x", pady=(10, 2))
            ctk.CTkLabel(row_resumen, text=f"💰 TOTAL ABONOS: ${self.format_money(abonos_total)}", font=("Arial", 11, "bold"), text_color="#2e7d32").pack(padx=10, pady=5)

    def remove_from_cart(self, index):
        del self.cart[index]; self.update_cart_ui()

    def open_service_picker(self):
        top = ctk.CTkToplevel(self); top.title("SELECCIONAR ORDEN TALLER"); top.geometry("700x600"); top.attributes("-topmost", True)
        # Centrar ventana
        top.update_idletasks()
        x = (top.winfo_screenwidth() // 2) - (700 // 2)
        y = (top.winfo_screenheight() // 2) - (600 // 2)
        top.geometry(f"700x600+{x}+{y}")
        
        ctk.CTkLabel(top, text="ÓRDENES ACTIVAS (NO ENTREGADAS)", font=("Arial", 14, "bold")).pack(pady=10)
        
        orders = self.logic.orders.get_dashboard_orders()
        
        scroll = ctk.CTkScrollableFrame(top); scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        if not orders:
            ctk.CTkLabel(scroll, text="NO HAY ÓRDENES ACTIVAS").pack(pady=20)
            return
        
        for o in orders:
            # Manejar tanto dict como tupla
            if isinstance(o, dict):
                oid = o.get('id')
                eq = o.get('equipo', 'N/A')
                mod = o.get('modelo', 'N/A')
                st = o.get('estado', 'N/A')
                tec = o.get('tecnico', 'SIN ASIGNAR')
                cli = o.get('cliente', 'SIN CLIENTE')
            else:
                # Tupla
                oid = o[0] if len(o) > 0 else None
                eq = o[1] if len(o) > 1 else 'N/A'
                mod = o[2] if len(o) > 2 else 'N/A'
                st = o[3] if len(o) > 3 else 'N/A'
                tec = o[4] if len(o) > 4 else 'SIN ASIGNAR'
                cli = o[5] if len(o) > 5 else 'SIN CLIENTE'
            
            if not oid:
                continue
            
            full_order = self.logic.orders.get_order_by_id(oid) 
            if not full_order: 
                continue
            
            cliente = full_order[14] if len(full_order) > 14 else cli
            presupuesto = full_order[12] if len(full_order) > 12 else 0
            abono = full_order[13] if len(full_order) > 13 else 0
            deuda = presupuesto - abono
            
            obs_raw = full_order[8] if len(full_order) > 8 else ""
            try:
                if "|" in obs_raw:
                    falla_detalle = obs_raw.split("|")[0].replace("FALLA:", "").strip()
                else:
                    falla_detalle = obs_raw.replace("FALLA:", "").strip() if obs_raw else "REPARACIÓN"
                if not falla_detalle:
                    falla_detalle = "REPARACIÓN"
            except:
                falla_detalle = "REPARACIÓN"

            cart_name = f"SERV: {falla_detalle} ({eq} {mod})".upper()
            
            card = ctk.CTkFrame(scroll, fg_color="#E0E0E0")
            card.pack(fill="x", pady=4, padx=5)
            
            # DATOS EN MAYÚSCULAS
            info_text = f"#{oid} | {cliente.upper() if cliente else 'N/A'}\n{eq.upper()} {mod.upper()} | Estado: {st.upper()}"
            ctk.CTkLabel(card, text=info_text, width=250, anchor="w", font=("Arial", 11, "bold"), text_color="#333333").pack(side="left", padx=10)
            
            # Mostrar presupuesto y deuda
            if deuda > 0:
                price_text = f"DEUDA: ${self.format_money(deuda)}"
                price_color = "#C0392B"
            elif deuda == 0 and presupuesto > 0:
                price_text = f"PAGADO: ${self.format_money(presupuesto)}"
                price_color = "#27AE60"
            else:
                price_text = f"TOTAL: ${self.format_money(presupuesto)}"
                price_color = "#555555"
                
            ctk.CTkLabel(card, text=price_text, text_color=price_color, font=("Arial", 11, "bold")).pack(side="left", padx=10)
            
            # Usar deuda si existe, sino usar presupuesto total
            precio_cobrar = deuda if deuda > 0 else presupuesto
            
            ctk.CTkButton(card, text="AGREGAR", width=80, fg_color="#77DD77", text_color="black",
                          command=lambda i=oid, n=cart_name, p=precio_cobrar: self.ask_service_details(i, n, p, top)).pack(side="right", padx=10)

    def ask_service_details(self, order_id, name, price, top_parent):
        win = ctk.CTkToplevel(self); win.title("CONFIRMAR DATOS SERVICIO"); win.geometry("500x500")
        win.transient(top_parent)  # Hacer que sea hijo de la ventana de selección
        win.grab_set()  # Hacer modal
        win.attributes("-topmost", True)  # Siempre al frente
        # Centrar ventana
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (500 // 2)
        y = (win.winfo_screenheight() // 2) - (500 // 2)
        win.geometry(f"500x500+{x}+{y}")
        ctk.CTkLabel(win, text=name, font=("Arial", 12, "bold")).pack(pady=10)
        v_rep = ctk.StringVar(); v_env = ctk.StringVar(); v_iva = ctk.BooleanVar(); v_card = ctk.BooleanVar()
        
        # Cargar automáticamente los costos de repuestos y envío de la orden
        costo_rep = 0
        costo_env = 0
        try:
            # Query para obtener costos detallados de detalles_orden
            query = """
            SELECT tipo_item, SUM(costo) as total_costo
            FROM detalles_orden 
            WHERE orden_id = ? 
            GROUP BY tipo_item
            """
            resultados = self.logic.bd.OBTENER_TODOS(query, (order_id,))
            
            if resultados:
                for row in resultados:
                    tipo = row[0] if isinstance(row, tuple) else row.get('tipo_item', '')
                    costo = row[1] if isinstance(row, tuple) else row.get('total_costo', 0)
                    
                    if 'REPUESTO' in str(tipo).upper():
                        costo_rep = int(costo) if costo else 0
                    elif 'ENVIO' in str(tipo).upper():
                        costo_env = int(costo) if costo else 0
                
                print(f"DEBUG POS: Costos cargados - Repuestos: ${costo_rep}, Envío: ${costo_env}")
            
            # Formatear con miles
            if costo_rep > 0:
                v_rep.set(f"{costo_rep:,}".replace(",", "."))
            if costo_env > 0:
                v_env.set(f"{costo_env:,}".replace(",", "."))
                
        except Exception as e:
            print(f"Error cargando costos de detalles_orden: {e}")
            import traceback
            traceback.print_exc()
        
        # Traces para formato de miles
        v_rep.trace("w", lambda *a: self.format_live(v_rep))
        v_env.trace("w", lambda *a: self.format_live(v_env))
        
        ctk.CTkLabel(win, text="COSTO REPUESTO ($):").pack()
        entry_rep = ctk.CTkEntry(win, textvariable=v_rep)
        entry_rep.pack(pady=5)
        
        ctk.CTkLabel(win, text="COSTO ENVÍO ($):").pack()
        entry_env = ctk.CTkEntry(win, textvariable=v_env)
        entry_env.pack(pady=5)
        
        ctk.CTkCheckBox(win, text="APLICA IVA (BOLETA/FACTURA)", variable=v_iva).pack(pady=10)
        ctk.CTkCheckBox(win, text="PAGO CON TARJETA (COMISIÓN BANCO)", variable=v_card).pack(pady=5)
        
        def confirm():
            details = {
                'rep': self.clean_money(v_rep.get()),
                'env': self.clean_money(v_env.get()),
                'iva': v_iva.get(),
                'card': v_card.get()
            }
            self.add_to_cart((order_id, name, price), True, details)
            
            # Cerrar ambas ventanas
            win.destroy()
            top_parent.destroy()
            
            # Rellenar automáticamente los campos en el formulario de pago
            total = self.get_final_total()
            self.var_cash.set(f"{int(total):,}".replace(",", "."))
            
        ctk.CTkButton(win, text="CONFIRMAR Y AGREGAR", command=confirm, fg_color="green").pack(pady=20)

    def reset_pos_ui(self):
        """Limpiar completamente todos los campos del carrito de compras"""
        self.cart = []
        self.update_cart_ui()
        # Limpiar todos los campos de pago
        self.var_cash.set("")
        self.var_transf.set("")
        self.var_debit.set("")
        self.var_credit.set("")
        self.var_discount.set("")
        self.var_search.set("")
        # Recargar productos
        self.load_products()
        self.update_total_label()

    def checkout(self):
        if not self.cart: return
        
        # 1️⃣ VALIDAR QUE CAJA/TURNO ESTÉ ABIERTO
        user_id = self.current_user['id'] if isinstance(self.current_user, dict) else self.current_user[0]
        sesion_activa = self.logic.cash.get_active_session(user_id)
        if not sesion_activa:
            messagebox.showerror("❌ CAJA CERRADA", "Debe abrir un turno antes de realizar cobros.\n\nVaya al módulo de CAJA y abra el turno.")
            return
        
        # 2️⃣ CALCULAR TOTAL CONSIDERANDO ABONOSY DESCUENTOS
        total_final = self.get_final_total()
        desc = self.clean_money(self.var_discount.get())
        
        # Verificar si hay servicios (órdenes) en el carrito con abonos ya pagados
        monto_abonos_pagados = 0
        detalles_carrito = []
        
        for item in self.cart:
            pid, name, qty, price, is_srv, details = item
            if is_srv and details:
                # Si es un servicio con detalles de orden
                abono_pagado = details.get('abono', 0)
                monto_abonos_pagados += abono_pagado
                detalles_carrito.append({
                    'order_id': pid,
                    'name': name,
                    'price': price,
                    'abono': abono_pagado
                })
        
        # El total a cobrar es: Total - Abonosy - Descuentos
        monto_a_cobrar = max(0, total_final - monto_abonos_pagados)
        
        # 3️⃣ VALIDAR PAGOS
        efec = self.clean_money(self.var_cash.get())
        trf = self.clean_money(self.var_transf.get())
        deb = self.clean_money(self.var_debit.get())
        cred = self.clean_money(self.var_credit.get())
        
        pagado = efec + trf + deb + cred
        
        if pagado != monto_a_cobrar:
            messagebox.showwarning(
                "ERROR", 
                f"PAGOS NO CUADRAN.\n\n" +
                f"Subtotal: ${self.format_money(total_final)}\n" +
                f"Abonosy previos: ${self.format_money(monto_abonos_pagados)}\n" +
                f"Descuentos: ${self.format_money(desc)}\n\n" +
                f"💰 PENDIENTE DE PAGO: ${self.format_money(monto_a_cobrar)}\n" +
                f"💵 PAGADO: ${self.format_money(pagado)}\n\n" +
                f"Diferencia: ${self.format_money(abs(monto_a_cobrar - pagado))}"
            )
            return
        
        # 4️⃣ MOSTRAR RESUMEN ANTES DE PROCESAR
        resumen = f"📋 RESUMEN DE COBRO:\n\n"
        resumen += f"Subtotal: ${self.format_money(total_final)}\n"
        if monto_abonos_pagados > 0:
            resumen += f"(-) Abonosy pagados: ${self.format_money(monto_abonos_pagados)}\n"
        if desc > 0:
            resumen += f"(-) Descuentos: ${self.format_money(desc)}\n"
        resumen += f"\n{'='*40}\n"
        resumen += f"Total a pagar: ${self.format_money(monto_a_cobrar)}\n\n"
        
        resumen += "Formas de pago:\n"
        if efec > 0:
            resumen += f"  💵 Efectivo: ${self.format_money(efec)}\n"
        if trf > 0:
            resumen += f"  🏦 Transferencia: ${self.format_money(trf)}\n"
        if deb > 0:
            resumen += f"  💳 Débito: ${self.format_money(deb)}\n"
        if cred > 0:
            resumen += f"  💳 Crédito: ${self.format_money(cred)}\n"
            
        if messagebox.askyesno("CONFIRMAR COBRO", resumen):
            pays = {'efectivo': efec, 'transferencia': trf, 'debito': deb, 'credito': cred}
            
            # 5️⃣ PROCESAR VENTA
            if self.logic.inventory.process_sale(user_id, self.cart, pays, total_final, desc):
                messagebox.showinfo("✅ ÉXITO", "VENTA REGISTRADA CORRECTAMENTE.\n\nTurno actualizado.")
                self.reset_pos_ui()
            else: 
                messagebox.showerror("❌ ERROR", "FALLO AL GUARDAR EN BASE DE DATOS")

    def open_add_product_window(self):
        # Obtener proveedores
        proveedores = self.logic.proveedores.OBTENER_TODOS_PROVEEDORES()
        if not proveedores:
            messagebox.showerror("Error", "Debe registrar al menos un proveedor antes de crear productos")
            return
        
        top = ctk.CTkToplevel(self); top.title("NUEVO ARTÍCULO (TIENDA)"); top.geometry("400x550"); top.attributes("-topmost", True)
        # Centrar ventana
        top.update_idletasks()
        x = (top.winfo_screenwidth() // 2) - (400 // 2)
        y = (top.winfo_screenheight() // 2) - (275)
        top.geometry(f"400x550+{x}+{y}")
        
        v_name = ctk.StringVar(); v_name.trace("w", lambda *a: self.force_uppercase(v_name))
        v_cost = ctk.StringVar(); v_cost.trace("w", lambda *a: self.format_live(v_cost))
        v_price = ctk.StringVar(); v_price.trace("w", lambda *a: self.format_live(v_price))
        
        ctk.CTkLabel(top, text="REGISTRAR ARTÍCULO (VENTA)", font=("Arial", 14, "bold")).pack(pady=10)
        
        ctk.CTkLabel(top, text="NOMBRE:").pack(); ctk.CTkEntry(top, textvariable=v_name, placeholder_text="EJ: FUNDA IPHONE").pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(top, text="COSTO ($):").pack(); ctk.CTkEntry(top, textvariable=v_cost, placeholder_text="0").pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(top, text="PRECIO ($):").pack(); ctk.CTkEntry(top, textvariable=v_price, placeholder_text="0").pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(top, text="STOCK:").pack(); e_stock = ctk.CTkEntry(top, placeholder_text="1"); e_stock.pack(pady=5, padx=10, fill="x")
        
        # Proveedor
        ctk.CTkLabel(top, text="PROVEEDOR (OBLIGATORIO):").pack(pady=(10,5))
        proveedor_nombres = {str(p['id']): p['nombre'] for p in proveedores}
        proveedor_ids = list(proveedor_nombres.keys())
        proveedor_values = [proveedor_nombres[pid] for pid in proveedor_ids]
        v_proveedor = ctk.StringVar(value=proveedor_values[0] if proveedor_values else "")
        combo_prov = ctk.CTkComboBox(top, values=proveedor_values, variable=v_proveedor, state="readonly")
        combo_prov.pack(pady=5, padx=10, fill="x")
        
        def save():
            try:
                nombre = v_name.get().strip()
                if not nombre:
                    messagebox.showerror("ERROR", "El nombre es obligatorio", parent=top)
                    return
                
                # Obtener ID del proveedor seleccionado
                proveedor_nombre = v_proveedor.get()
                proveedor_id = None
                for pid, pname in proveedor_nombres.items():
                    if pname == proveedor_nombre:
                        proveedor_id = int(pid)
                        break
                
                if not proveedor_id:
                    messagebox.showerror("ERROR", "Debe seleccionar un proveedor", parent=top)
                    return
                
                costo = self.clean_money(v_cost.get())
                precio = self.clean_money(v_price.get())
                stock = int(e_stock.get() or 1)
                
                print(f"DEBUG POS: Guardando producto: {nombre}, costo={costo}, precio={precio}, stock={stock}, proveedor_id={proveedor_id}")
                
                if self.logic.inventory.add_product(nombre, costo, precio, stock, "GENERAL", proveedor_id):
                    messagebox.showinfo("ÉXITO", "ARTÍCULO AGREGADO", parent=top)
                    top.destroy()
                    self.load_products()
                else: 
                    messagebox.showerror("ERROR", "EL ARTÍCULO YA EXISTE O NO SE PUDO GUARDAR", parent=top)
            except Exception as e:
                print(f"DEBUG POS ERROR: {e}")
                messagebox.showerror("ERROR", f"VERIFIQUE NÚMEROS: {e}", parent=top)
            
        ctk.CTkButton(top, text="GUARDAR", command=save, fg_color="green", height=40).pack(pady=20, padx=10, fill="x")
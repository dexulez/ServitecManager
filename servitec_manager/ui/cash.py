import customtkinter as ctk
from tkinter import messagebox, simpledialog
from .theme import Theme

class CashFrame(ctk.CTkFrame):
    def __init__(self, parent, logic, current_user):
        super().__init__(parent, fg_color=Theme.BACKGROUND)
        self.logic = logic
        self.current_user = current_user
        self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(0, weight=1)
        self.main_container = ctk.CTkFrame(self, fg_color="transparent"); self.main_container.pack(expand=True, fill="both", padx=20, pady=20)
        self.refresh_state()

    def refresh(self):
        self.refresh_state()

    def refresh_state(self):
        for w in self.main_container.winfo_children(): w.destroy()
        user_id = self.current_user['id'] if isinstance(self.current_user, dict) else self.current_user[0]
        session = self.logic.cash.get_active_session(user_id)
        if session: self.show_close_ui(session)
        else: self.show_open_ui()

    def show_open_ui(self):
        # Frame principal con tema
        main_card = ctk.CTkFrame(self.main_container, **Theme.get_card_style())
        main_card.pack(expand=True, pady=50, padx=50)
        
        ctk.CTkLabel(main_card, text="🔒 CAJA CERRADA", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_XXLARGE, "bold"), text_color=Theme.ERROR).pack(pady=30)
        ctk.CTkLabel(main_card, text="MONTO INICIAL DE APERTURA ($):", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"), text_color=Theme.TEXT_PRIMARY).pack(pady=10)
        self.entry_start = ctk.CTkEntry(main_card, placeholder_text="0", width=250, height=45, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold"), border_color=Theme.BORDER, corner_radius=Theme.RADIUS_MEDIUM)
        self.entry_start.pack(pady=15)
        ctk.CTkButton(main_card, text="🔓 ABRIR TURNO", command=self.open_shift, **Theme.get_button_style("success"), height=55).pack(pady=30, padx=40, fill="x")

    def open_shift(self):
        try:
            monto = float(self.entry_start.get())
            user_id = self.current_user['id'] if isinstance(self.current_user, dict) else self.current_user[0]
            self.logic.cash.open_shift(user_id, monto)
            messagebox.showinfo("ÉXITO", "TURNO ABIERTO CORRECTAMENTE"); self.refresh_state()
        except: messagebox.showerror("ERROR", "INGRESE UN MONTO VÁLIDO")

    def show_close_ui(self, session):
        monto_inicial = session[4]
        user_id = self.current_user['id'] if isinstance(self.current_user, dict) else self.current_user[0]
        sales = self.logic.cash.get_current_shift_sales(user_id)
        # sales: (Efec, Trf, Deb, Cred)
        
        # Limpiar completamente y crear layout simple y efectivo
        for w in self.main_container.winfo_children(): w.destroy()
        
        # Panel derecho (gastos) - ancho fijo 300px
        right = ctk.CTkFrame(self.main_container, **Theme.get_card_style())
        right.pack(side="right", fill="y", padx=(10,0))
        right.configure(width=300)
        right.pack_propagate(False)
        
        # Panel izquierdo (turno) - ocupa TODO el espacio restante
        left = ctk.CTkFrame(self.main_container, **Theme.get_card_style())
        left.pack(fill="both", expand=True, padx=(0,10))

        # El resto del código debe usar 'left' y 'right' como antes
        
        # Header
        header = ctk.CTkFrame(left, fg_color="transparent")
        header.pack(fill="x", padx=Theme.PADDING_LARGE, pady=Theme.PADDING_LARGE)
        ctk.CTkLabel(header, text="💰 TURNO EN CURSO", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H1, "bold"), text_color=Theme.SUCCESS).pack()
        
        ctk.CTkFrame(left, height=2, fg_color=Theme.DIVIDER).pack(fill="x", pady=(0, Theme.PADDING_MEDIUM))
        
        info = ctk.CTkFrame(left, fg_color="transparent"); info.pack(pady=10, fill="x", padx=Theme.PADDING_LARGE)
        
        def info_row(label, value, color=Theme.TEXT_PRIMARY, size=Theme.FONT_SIZE_NORMAL):
            row = ctk.CTkFrame(info, fg_color=Theme.BACKGROUND_LIGHT, corner_radius=Theme.RADIUS_SMALL)
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=label, font=(Theme.FONT_FAMILY, size, "bold"), text_color=Theme.TEXT_SECONDARY, anchor="w").pack(side="left", padx=10, pady=8)
            ctk.CTkLabel(row, text=value, font=(Theme.FONT_FAMILY, size, "bold"), text_color=color, anchor="e").pack(side="right", padx=10, pady=8)
        
        info_row("FONDO INICIAL:", f"${int(monto_inicial):,}".replace(",", "."), Theme.PRIMARY, Theme.FONT_SIZE_LARGE)
        info_row("VENTAS EFECTIVO:", f"${int(sales[0]):,}".replace(",", "."), Theme.SUCCESS, Theme.FONT_SIZE_LARGE)
        info_row("VENTAS TRANSFERENCIA:", f"${int(sales[1]):,}".replace(",", "."))
        info_row("VENTAS DÉBITO:", f"${int(sales[2]):,}".replace(",", "."))
        info_row("VENTAS CRÉDITO:", f"${int(sales[3]):,}".replace(",", "."))
        
        ctk.CTkButton(left, text="🔒 REALIZAR ARQUEO Y CERRAR", command=self.prompt_close, **Theme.get_button_style("danger"), height=55).pack(pady=Theme.PADDING_LARGE, padx=Theme.PADDING_LARGE, fill="x")
        
        # Separador
        ctk.CTkFrame(left, height=2, fg_color=Theme.DIVIDER).pack(fill="x", pady=Theme.PADDING_MEDIUM)
        
        # Lista de ventas y servicios del día
        ctk.CTkLabel(left, text="📋 VENTAS Y SERVICIOS DEL DÍA", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"), text_color=Theme.TEXT_PRIMARY).pack(pady=Theme.PADDING_SMALL)
        
        # Scroll para la lista
        sales_scroll = ctk.CTkScrollableFrame(left, fg_color=Theme.BACKGROUND_LIGHT, corner_radius=Theme.RADIUS_MEDIUM, height=200)
        sales_scroll.pack(fill="both", expand=True, padx=Theme.PADDING_LARGE, pady=Theme.PADDING_SMALL)
        
        # Obtener ventas del POS del día actual
        try:
            ventas_query = """SELECT 
                v.id, v.fecha, v.total_final, 
                COALESCE(t.monto_efectivo, 0), 
                COALESCE(t.monto_transferencia, 0), 
                COALESCE(t.monto_debito, 0), 
                COALESCE(t.monto_credito, 0)
                FROM ventas v
                LEFT JOIN transacciones t ON v.transaccion_id = t.id
                WHERE v.usuario_id = ? AND v.fecha >= ? 
                ORDER BY v.id DESC"""
            user_id = self.current_user['id'] if isinstance(self.current_user, dict) else self.current_user[0]
            ventas_pos = self.logic.bd.OBTENER_TODOS(ventas_query, (user_id, session[2]))
        except Exception as e:
            pass
            ventas_pos = []
        
        # Obtener servicios cobrados (órdenes cerradas) del día
        try:
            servicios_query = """SELECT o.id, o.equipo, o.modelo, o.presupuesto_inicial, o.fecha_entrada, c.nombre
                                 FROM ordenes o
                                 JOIN clientes c ON o.cliente_id = c.id
                                 WHERE o.estado = 'Entregado' AND o.fecha_entrada >= ? 
                                 ORDER BY o.fecha_entrada DESC"""
            servicios = self.logic.bd.OBTENER_TODOS(servicios_query, (session[2],))
        except:
            servicios = []
        
        # Mostrar ventas POS
        if ventas_pos:
            ctk.CTkLabel(sales_scroll, text="💰 VENTAS POS:", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"), text_color=Theme.SUCCESS, anchor="w").pack(fill="x", padx=5, pady=(5,2))
            for venta in ventas_pos:
                # Manejar tanto tuplas como DictRow
                if isinstance(venta, dict):
                    vid = venta.get('id', venta[0] if len(venta) > 0 else 0)
                    fecha = venta.get('fecha', venta[1] if len(venta) > 1 else '')
                    total = venta.get('total', venta[2] if len(venta) > 2 else 0)
                    efec = venta.get('pago_efectivo', venta[3] if len(venta) > 3 else 0)
                    transf = venta.get('pago_transferencia', venta[4] if len(venta) > 4 else 0)
                    deb = venta.get('pago_debito', venta[5] if len(venta) > 5 else 0)
                    cred = venta.get('pago_credito', venta[6] if len(venta) > 6 else 0)
                else:
                    vid, fecha, total, efec, transf, deb, cred = venta
                # Convertir a números para evitar errores de comparación
                efec = float(efec) if efec else 0
                transf = float(transf) if transf else 0
                deb = float(deb) if deb else 0
                cred = float(cred) if cred else 0
                total = float(total) if total else 0
                metodos = []
                if efec > 0: metodos.append(f"Ef:${int(efec):,}".replace(",", "."))
                if transf > 0: metodos.append(f"Tr:${int(transf):,}".replace(",", "."))
                if deb > 0: metodos.append(f"Db:${int(deb):,}".replace(",", "."))
                if cred > 0: metodos.append(f"Cr:${int(cred):,}".replace(",", "."))
                metodo_texto = " | ".join(metodos) if metodos else "Sin pago"
                
                venta_frame = ctk.CTkFrame(sales_scroll, fg_color=Theme.SURFACE, corner_radius=Theme.RADIUS_SMALL)
                venta_frame.pack(fill="x", pady=2, padx=2)
                ctk.CTkLabel(venta_frame, text=f"Venta #{vid} - {fecha[11:16]}", text_color=Theme.TEXT_SECONDARY, anchor="w", font=(Theme.FONT_FAMILY, 9)).pack(side="left", padx=5, pady=3)
                ctk.CTkLabel(venta_frame, text=metodo_texto, text_color=Theme.TEXT_PRIMARY, anchor="center", font=(Theme.FONT_FAMILY, 9)).pack(side="left", padx=5, expand=True)
                ctk.CTkLabel(venta_frame, text=f"${int(total):,}".replace(",", "."), text_color=Theme.SUCCESS, font=(Theme.FONT_FAMILY, 10, "bold"), width=80).pack(side="right", padx=5, pady=3)
        
        # Mostrar servicios cobrados
        if servicios:
            ctk.CTkLabel(sales_scroll, text="🔧 SERVICIOS COBRADOS:", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"), text_color=Theme.PRIMARY, anchor="w").pack(fill="x", padx=5, pady=(10,2))
            for servicio in servicios:
                # Manejar tanto tuplas como DictRow
                if isinstance(servicio, dict):
                    oid = servicio.get('id', servicio[0] if len(servicio) > 0 else 0)
                    equipo = servicio.get('equipo', servicio[1] if len(servicio) > 1 else '')
                    modelo = servicio.get('modelo', servicio[2] if len(servicio) > 2 else '')
                    total = servicio.get('presupuesto', servicio[3] if len(servicio) > 3 else 0)
                    fecha = servicio.get('fecha', servicio[4] if len(servicio) > 4 else '')
                    cliente = servicio.get('nombre', servicio[5] if len(servicio) > 5 else 'CLIENTE')
                else:
                    oid, equipo, modelo, total, fecha, cliente = servicio
                servicio_frame = ctk.CTkFrame(sales_scroll, fg_color=Theme.SURFACE, corner_radius=Theme.RADIUS_SMALL)
                servicio_frame.pack(fill="x", pady=2, padx=2)
                ctk.CTkLabel(servicio_frame, text=f"#{oid} - {cliente[:15]}", text_color=Theme.TEXT_SECONDARY, anchor="w", font=(Theme.FONT_FAMILY, 9)).pack(side="left", padx=5, pady=3)
                ctk.CTkLabel(servicio_frame, text=f"{equipo} {modelo}"[:20], text_color=Theme.TEXT_PRIMARY, anchor="center", font=(Theme.FONT_FAMILY, 9)).pack(side="left", padx=5, expand=True)
                ctk.CTkLabel(servicio_frame, text=f"${int(total):,}".replace(",", "."), text_color=Theme.PRIMARY, font=(Theme.FONT_FAMILY, 10, "bold"), width=80).pack(side="right", padx=5, pady=3)
        
        if not ventas_pos and not servicios:
            ctk.CTkLabel(sales_scroll, text="No hay ventas ni servicios registrados en este turno", text_color=Theme.TEXT_SECONDARY).pack(pady=20)

        # --- RIGHT: GASTOS DEL TURNO ---
        # Header
        header_right = ctk.CTkFrame(right, fg_color="transparent")
        header_right.pack(fill="x", padx=Theme.PADDING_LARGE, pady=Theme.PADDING_LARGE)
        ctk.CTkLabel(header_right, text="📝 GASTOS DEL TURNO", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"), text_color=Theme.TEXT_PRIMARY).pack()
        
        ctk.CTkFrame(right, height=2, fg_color=Theme.DIVIDER).pack(fill="x", pady=(0, Theme.PADDING_MEDIUM))
        
        # Formulario Gasto
        gf = ctk.CTkFrame(right, fg_color=Theme.BACKGROUND_LIGHT, corner_radius=Theme.RADIUS_MEDIUM); gf.pack(fill="x", padx=Theme.PADDING_MEDIUM, pady=Theme.PADDING_SMALL)
        self.entry_gasto_desc = ctk.CTkEntry(gf, placeholder_text="Descripción Gasto", width=200, border_color=Theme.BORDER, corner_radius=Theme.RADIUS_SMALL)
        self.entry_gasto_desc.pack(side="left", padx=5, pady=8)
        self.entry_gasto_monto = ctk.CTkEntry(gf, placeholder_text="Monto", width=100, border_color=Theme.BORDER, corner_radius=Theme.RADIUS_SMALL)
        self.entry_gasto_monto.pack(side="left", padx=5, pady=8)
        ctk.CTkButton(gf, text="➕", width=50, **Theme.get_button_style("accent"), command=self.add_expense).pack(side="left", padx=5)
        
        # Lista Gastos
        self.scroll_gastos = ctk.CTkScrollableFrame(right, fg_color="transparent", corner_radius=0); self.scroll_gastos.pack(fill="both", expand=True, padx=Theme.PADDING_MEDIUM, pady=Theme.PADDING_SMALL)
        self.load_expenses()

    def load_expenses(self):
        for w in self.scroll_gastos.winfo_children(): w.destroy()
        user_id = self.current_user['id'] if isinstance(self.current_user, dict) else self.current_user[0]
        gastos = self.logic.cash.get_session_expenses(user_id)
        total_g = 0
        for g in gastos:
            # 0:id, 1:sid, 2:desc, 3:monto, 4:fecha
            f = ctk.CTkFrame(self.scroll_gastos, fg_color=Theme.SURFACE, corner_radius=Theme.RADIUS_SMALL)
            f.pack(fill="x", pady=3, padx=2)
            ctk.CTkLabel(f, text=g[2], text_color=Theme.TEXT_PRIMARY, anchor="w", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL)).pack(side="left", padx=10, pady=8, expand=True, fill="x")
            ctk.CTkLabel(f, text=f"${int(g[3]):,}".replace(",", "."), text_color=Theme.ERROR, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"), width=100).pack(side="right", padx=10, pady=8)
            total_g += g[3]
        
        # Total con estilo destacado
        total_frame = ctk.CTkFrame(self.scroll_gastos, fg_color="#ffcccb", corner_radius=Theme.RADIUS_MEDIUM)
        total_frame.pack(pady=15, fill="x", padx=5)
        ctk.CTkLabel(total_frame, text=f"TOTAL GASTOS: ${int(total_g):,}".replace(",", "."), font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold"), text_color=Theme.ERROR).pack(pady=12)

    def add_expense(self):
        d = self.entry_gasto_desc.get()
        m = self.entry_gasto_monto.get()
        if not d or not m: return
        try:
            val = float(m)
            user_id = self.current_user['id'] if isinstance(self.current_user, dict) else self.current_user[0]
            self.logic.cash.add_expense(user_id, d, val)
            self.entry_gasto_desc.delete(0, "end"); self.entry_gasto_monto.delete(0, "end")
            self.load_expenses()
        except: messagebox.showerror("Error", "Monto inválido")

    def prompt_close(self):
        # Dialogo personalizado para cierre con tema
        win = ctk.CTkToplevel(self)
        win.title("Cierre de Caja - Arqueo")
        win.geometry("550x700")
        win.grab_set()
        win.configure(fg_color=Theme.BACKGROUND)
        # Centrar ventana
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (550 // 2)
        y = (win.winfo_screenheight() // 2) - (700 // 2)
        win.geometry(f"550x700+{x}+{y}")
        
        # Header
        header = ctk.CTkFrame(win, fg_color=Theme.PRIMARY, corner_radius=0)
        header.pack(fill="x", pady=(0, Theme.PADDING_LARGE))
        ctk.CTkLabel(header, text="🔒 CIERRE DE CAJA - ARQUEO", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H1, "bold"), text_color="white").pack(pady=20)
        
        # Contenedor principal
        container = ctk.CTkFrame(win, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=Theme.PADDING_LARGE)
        
        ctk.CTkLabel(container, text="INGRESE MONTOS REALES CONTADOS:", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"), text_color=Theme.TEXT_PRIMARY).pack(pady=(0, 15))
        
        def mk_entry(lbl, icon="💵"):
            frame = ctk.CTkFrame(container, fg_color=Theme.SURFACE, corner_radius=Theme.RADIUS_MEDIUM)
            frame.pack(fill="x", pady=8)
            ctk.CTkLabel(frame, text=f"{icon} {lbl}", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL), text_color=Theme.TEXT_SECONDARY, anchor="w").pack(padx=15, pady=(10, 5), fill="x")
            e = ctk.CTkEntry(frame, placeholder_text="0", height=40, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"), border_color=Theme.BORDER, corner_radius=Theme.RADIUS_SMALL)
            e.pack(padx=15, pady=(0, 10), fill="x")
            return e
            
        e_efec = mk_entry("Efectivo en Caja (Billetes/Monedas):", "💵")
        e_trf = mk_entry("Total Transferencias (Revisar Banco):", "🏦")
        e_deb = mk_entry("Total Débito (Voucher Transbank):", "💳")
        e_cred = mk_entry("Total Crédito (Voucher Transbank):", "💳")
        
        def confirm():
            try:
                v_efec = float(e_efec.get() or 0)
                v_trf = float(e_trf.get() or 0)
                v_deb = float(e_deb.get() or 0)
                v_cred = float(e_cred.get() or 0)
                
                if messagebox.askyesno("Confirmar", "¿Cerrar turno con estos montos?"):
                    # 1. Cerrar Turno
                    user_id = self.current_user['id'] if isinstance(self.current_user, dict) else self.current_user[0]
                    self.logic.cash.close_shift(user_id, v_efec, v_trf, v_deb, v_cred)
                    win.destroy()
                    messagebox.showinfo("Cierre Exitoso", "Turno cerrado correctamente.")
                    
                    # 2. Generar Reporte
                    if messagebox.askyesno("Reporte", "¿Desea generar el informe de cierre de caja?"):
                        try:
                            # Obtener datos actualizados de la sesión cerrada
                            user_id = self.current_user['id'] if isinstance(self.current_user, dict) else self.current_user[0]
                            last_session = self.logic.bd.OBTENER_UNO("SELECT * FROM caja_sesiones WHERE usuario_id = ? ORDER BY id DESC LIMIT 1", (user_id,))
                            if last_session:
                                expenses = self.logic.bd.OBTENER_TODOS("SELECT * FROM gastos WHERE sesion_id = ?", (last_session['id'] if isinstance(last_session, dict) else last_session[0],))
                                f_inicio = last_session['fecha_apertura'] if isinstance(last_session, dict) else last_session[2]
                                f_fin = last_session['fecha_cierre'] if isinstance(last_session, dict) else last_session[3]
                                
                                # Finanzas (Ordenes consolidadas) - calcular desde pagos mixtos
                                res_t = self.logic.bd.OBTENER_UNO("SELECT SUM(COALESCE(pago_efectivo,0)), SUM(COALESCE(pago_transferencia,0)), SUM(COALESCE(pago_debito,0)), SUM(COALESCE(pago_credito,0)) FROM ordenes WHERE estado = 'Entregado' AND fecha >= ? AND fecha <= ?", (f_inicio, f_fin))
                                # Ventas (POS)
                                res_p = self.logic.bd.OBTENER_UNO("SELECT SUM(pago_efectivo), SUM(pago_transferencia), SUM(pago_debito), SUM(pago_credito) FROM ventas WHERE fecha >= ? AND fecha <= ?", (f_inicio, f_fin))
                                
                                # Acceso compatible con DictRow y tuplas
                                def get_val(row, idx_or_key):
                                    if row is None:
                                        return 0
                                    if isinstance(row, dict):
                                        keys = list(row.keys())
                                        return row.get(keys[idx_or_key] if isinstance(idx_or_key, int) else idx_or_key, 0) or 0
                                    return row[idx_or_key] or 0
                                
                                sales_data = (
                                    get_val(res_t, 0) + get_val(res_p, 0),
                                    get_val(res_t, 1) + get_val(res_p, 1),
                                    get_val(res_t, 2) + get_val(res_p, 2),
                                    get_val(res_t, 3) + get_val(res_p, 3)
                                )
                                
                                from pdf_generator import GENERADOR_PDF
                                session_id = last_session['id'] if isinstance(last_session, dict) else last_session[0]
                                pdf = GENERADOR_PDF(f"cierre_caja_{session_id}.pdf")
                                pdf.GENERAR_REPORTE_CIERRE_CAJA(pdf.filename, last_session, expenses, sales_data)
                        except Exception as e:
                            messagebox.showerror("Error Reporte", f"No se pudo generar el reporte: {e}")

                    self.refresh_state()
            except ValueError: messagebox.showerror("Error", "Ingrese valores numéricos válidos")
        
        # Botón de confirmación
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(pady=25, fill="x")
        ctk.CTkButton(btn_frame, text="🔒 CERRAR CAJA Y GENERAR REPORTE", command=confirm, **Theme.get_button_style("danger"), height=55).pack(fill="x")

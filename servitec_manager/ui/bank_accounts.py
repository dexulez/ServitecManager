import customtkinter as ctk
from tkinter import messagebox
from .theme import Theme

class BankAccountsFrame(ctk.CTkFrame):
    """Módulo para gestión de cuentas bancarias"""
    def __init__(self, parent, logic, current_user):
        super().__init__(parent, fg_color=Theme.BACKGROUND)
        self.logic = logic
        self.current_user = current_user
        
        # Grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Panel izquierdo - Lista
        left_panel = ctk.CTkFrame(self, **Theme.get_card_style())
        left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Header
        header = ctk.CTkFrame(left_panel, fg_color="transparent")
        header.pack(fill="x", pady=Theme.PADDING_LARGE, padx=Theme.PADDING_LARGE)
        ctk.CTkLabel(
            header, 
            text="🏦 CUENTAS BANCARIAS", 
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"), 
            text_color=Theme.TEXT_PRIMARY
        ).pack()
        
        ctk.CTkFrame(left_panel, height=2, fg_color=Theme.DIVIDER).pack(fill="x", pady=(0, Theme.PADDING_MEDIUM))
        
        ctk.CTkButton(
            left_panel, 
            text="🔄 ACTUALIZAR", 
            command=self.load_accounts, 
            **Theme.get_button_style("primary"), 
            height=40
        ).pack(pady=5, padx=Theme.PADDING_LARGE, fill="x")
        
        self.scroll_accounts = ctk.CTkScrollableFrame(left_panel, fg_color=Theme.BACKGROUND_LIGHT)
        self.scroll_accounts.pack(fill="both", expand=True, pady=10, padx=Theme.PADDING_MEDIUM)
        
        # Panel derecho - Formulario
        right_panel = ctk.CTkFrame(self, **Theme.get_card_style())
        right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Header derecho
        header_right = ctk.CTkFrame(right_panel, fg_color="transparent")
        header_right.pack(fill="x", pady=Theme.PADDING_LARGE, padx=Theme.PADDING_LARGE)
        ctk.CTkLabel(
            header_right, 
            text="➕ NUEVA CUENTA", 
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"), 
            text_color=Theme.TEXT_PRIMARY
        ).pack()
        
        ctk.CTkFrame(right_panel, height=2, fg_color=Theme.DIVIDER).pack(fill="x", pady=(0, Theme.PADDING_LARGE))
        
        # Formulario
        form_scroll = ctk.CTkScrollableFrame(right_panel, fg_color="transparent")
        form_scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Banco
        ctk.CTkLabel(form_scroll, text="🏦 BANCO", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold")).pack(anchor="w", pady=(10, 0))
        self.var_banco = ctk.StringVar()
        self.entry_banco = ctk.CTkComboBox(
            form_scroll,
            values=["Banco de Chile", "BCI", "Santander", "Itaú", "Scotiabank", "Estado", "BBVA", "Falabella", "Ripley", "Otro"],
            variable=self.var_banco,
            height=40,
            corner_radius=Theme.RADIUS_MEDIUM
        )
        self.entry_banco.pack(fill="x", pady=(5, 15))
        
        # Número de cuenta
        ctk.CTkLabel(form_scroll, text="🔢 NÚMERO DE CUENTA", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold")).pack(anchor="w", pady=(10, 0))
        self.var_numero = ctk.StringVar()
        ctk.CTkEntry(
            form_scroll,
            textvariable=self.var_numero,
            placeholder_text="Ej: 12345678901234",
            height=40,
            corner_radius=Theme.RADIUS_MEDIUM
        ).pack(fill="x", pady=(5, 15))
        
        # Tipo de cuenta
        ctk.CTkLabel(form_scroll, text="📋 TIPO DE CUENTA", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold")).pack(anchor="w", pady=(10, 0))
        self.var_tipo = ctk.StringVar()
        self.combo_tipo = ctk.CTkComboBox(
            form_scroll,
            values=["Corriente", "Ahorro", "Chequera", "Cuenta Vista"],
            variable=self.var_tipo,
            height=40,
            corner_radius=Theme.RADIUS_MEDIUM
        )
        self.combo_tipo.pack(fill="x", pady=(5, 15))
        
        # Titular
        ctk.CTkLabel(form_scroll, text="👤 TITULAR DE CUENTA", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold")).pack(anchor="w", pady=(10, 0))
        self.var_titular = ctk.StringVar()
        ctk.CTkEntry(
            form_scroll,
            textvariable=self.var_titular,
            placeholder_text="Nombre del titular",
            height=40,
            corner_radius=Theme.RADIUS_MEDIUM
        ).pack(fill="x", pady=(5, 15))
        
        # RUT
        ctk.CTkLabel(form_scroll, text="🆔 RUT DEL TITULAR", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold")).pack(anchor="w", pady=(10, 0))
        self.var_rut = ctk.StringVar()
        ctk.CTkEntry(
            form_scroll,
            textvariable=self.var_rut,
            placeholder_text="Ej: 12345678-9",
            height=40,
            corner_radius=Theme.RADIUS_MEDIUM
        ).pack(fill="x", pady=(5, 15))
        
        # Notas
        ctk.CTkLabel(form_scroll, text="📝 NOTAS", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold")).pack(anchor="w", pady=(10, 0))
        self.var_notas = ctk.CTkTextbox(form_scroll, height=80, corner_radius=Theme.RADIUS_MEDIUM)
        self.var_notas.pack(fill="x", pady=(5, 15))
        
        # Botones
        btn_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        
        ctk.CTkButton(
            btn_frame,
            text="✅ GUARDAR CUENTA",
            command=self.save_account,
            **Theme.get_button_style("success"),
            height=40
        ).pack(side="left", padx=5, fill="x", expand=True)
        
        ctk.CTkButton(
            btn_frame,
            text="🗑️ LIMPIAR",
            command=self.clear_form,
            **Theme.get_button_style("secondary"),
            height=40
        ).pack(side="left", padx=5, fill="x", expand=True)
        
        # Cargar datos
        self.load_accounts()
    
    def load_accounts(self):
        """Carga las cuentas bancarias"""
        for widget in self.scroll_accounts.winfo_children():
            widget.destroy()
        
        try:
            query = "SELECT id, banco, numero_cuenta, tipo_cuenta, titular, rut_titular, notas, activa FROM cuentas_bancarias ORDER BY banco, numero_cuenta"
            cuentas = self.logic.bd.OBTENER_TODOS(query)
            
            if not cuentas:
                ctk.CTkLabel(
                    self.scroll_accounts,
                    text="✅ No hay cuentas registradas",
                    text_color=Theme.TEXT_SECONDARY
                ).pack(pady=50)
                return
            
            for cuenta in cuentas:
                id_c, banco, numero, tipo, titular, rut, notas, activa = cuenta
                self.render_account_row(id_c, banco, numero, tipo, titular, rut, notas, activa)
        
        except Exception as e:
            print(f"Error cargando cuentas: {e}")
            ctk.CTkLabel(
                self.scroll_accounts,
                text=f"❌ Error: {e}",
                text_color=Theme.ERROR
            ).pack(pady=50)
    
    def render_account_row(self, id_c, banco, numero, tipo, titular, rut, notas, activa):
        """Renderiza una fila de cuenta"""
        row = ctk.CTkFrame(
            self.scroll_accounts,
            fg_color=Theme.SURFACE,
            corner_radius=Theme.RADIUS_MEDIUM,
            border_width=1,
            border_color=Theme.BORDER
        )
        row.pack(fill="x", pady=5)
        
        # Info
        info_frame = ctk.CTkFrame(row, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text=f"🏦 {banco} - {tipo}",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold"),
            text_color=Theme.PRIMARY
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            info_frame,
            text=f"Cuenta: {numero} | Titular: {titular}",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
            text_color=Theme.TEXT_SECONDARY
        ).pack(anchor="w", pady=(2, 0))
        
        if rut:
            ctk.CTkLabel(
                info_frame,
                text=f"RUT: {rut}",
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL),
                text_color=Theme.TEXT_SECONDARY
            ).pack(anchor="w")
        
        if notas:
            ctk.CTkLabel(
                info_frame,
                text=f"Notas: {notas}",
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL),
                text_color=Theme.TEXT_SECONDARY
            ).pack(anchor="w", pady=(2, 0))
        
        # Status
        status_text = "✅ ACTIVA" if activa else "❌ INACTIVA"
        status_color = Theme.SUCCESS if activa else Theme.ERROR
        
        ctk.CTkLabel(
            info_frame,
            text=status_text,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
            text_color=status_color
        ).pack(anchor="w", pady=(5, 0))
        
        # Botones
        btn_frame = ctk.CTkFrame(row, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkButton(
            btn_frame,
            text="📝 EDITAR",
            command=lambda: self.edit_account(id_c, banco, numero, tipo, titular, rut, notas, activa),
            **Theme.get_button_style("primary"),
            height=32,
            width=100
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            btn_frame,
            text="🗑️ ELIMINAR",
            command=lambda: self.delete_account(id_c),
            **Theme.get_button_style("error"),
            height=32,
            width=100
        ).pack(side="left", padx=2)
        
        # Toggle activa/inactiva
        btn_state_text = "DESACTIVAR" if activa else "ACTIVAR"
        btn_state_style = "secondary" if activa else "success"
        
        ctk.CTkButton(
            btn_frame,
            text=btn_state_text,
            command=lambda: self.toggle_account_status(id_c, activa),
            **Theme.get_button_style(btn_state_style),
            height=32,
            width=100
        ).pack(side="left", padx=2)
    
    def save_account(self):
        """Guarda una nueva cuenta"""
        banco = self.var_banco.get().strip()
        numero = self.var_numero.get().strip()
        tipo = self.var_tipo.get().strip()
        titular = self.var_titular.get().strip()
        rut = self.var_rut.get().strip()
        notas = self.var_notas.get("0.0", "end").strip()
        
        if not banco or not numero or not tipo or not titular:
            messagebox.showwarning("FALTAN DATOS", "Debe completar: Banco, Número, Tipo y Titular")
            return
        
        try:
            query = """
                INSERT INTO cuentas_bancarias (banco, numero_cuenta, tipo_cuenta, titular, rut_titular, notas, activa)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """
            self.logic.bd.EJECUTAR(query, (banco, numero, tipo, titular, rut, notas))
            messagebox.showinfo("ÉXITO", "✅ Cuenta bancaria guardada exitosamente")
            self.clear_form()
            self.load_accounts()
        except Exception as e:
            messagebox.showerror("ERROR", f"❌ Error al guardar: {e}")
    
    def edit_account(self, id_c, banco, numero, tipo, titular, rut, notas, activa):
        """Carga datos en el formulario para editar"""
        self.var_banco.set(banco)
        self.var_numero.set(numero)
        self.var_tipo.set(tipo)
        self.var_titular.set(titular)
        self.var_rut.set(rut)
        self.var_notas.delete("0.0", "end")
        self.var_notas.insert("0.0", notas or "")
        
        # Cambiar botón a actualizar
        messagebox.showinfo("EDITAR", f"Modifica los datos y haz clic en GUARDAR para actualizar")
    
    def delete_account(self, id_c):
        """Elimina una cuenta"""
        if messagebox.askyesno("CONFIRMAR", "¿Eliminar esta cuenta bancaria?"):
            try:
                self.logic.bd.EJECUTAR("DELETE FROM cuentas_bancarias WHERE id = ?", (id_c,))
                messagebox.showinfo("ÉXITO", "✅ Cuenta eliminada")
                self.load_accounts()
            except Exception as e:
                messagebox.showerror("ERROR", f"❌ Error: {e}")
    
    def toggle_account_status(self, id_c, activa):
        """Activa o desactiva una cuenta"""
        nuevo_estado = 0 if activa else 1
        try:
            self.logic.bd.EJECUTAR(
                "UPDATE cuentas_bancarias SET activa = ? WHERE id = ?",
                (nuevo_estado, id_c)
            )
            self.load_accounts()
        except Exception as e:
            messagebox.showerror("ERROR", f"❌ Error: {e}")
    
    def clear_form(self):
        """Limpia el formulario"""
        self.var_banco.set("")
        self.var_numero.set("")
        self.var_tipo.set("")
        self.var_titular.set("")
        self.var_rut.set("")
        self.var_notas.delete("0.0", "end")

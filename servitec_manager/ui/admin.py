import customtkinter as ctk
from tkinter import messagebox
from .theme import Theme

class AdminFrame(ctk.CTkFrame):
    def __init__(self, parent, logic, current_user, app=None):
        super().__init__(parent, fg_color=Theme.BACKGROUND)
        self.logic = logic
        self.app = app
        
        # GRID LAYOUT
        self.grid_columnconfigure(0, weight=1) # Lista
        self.grid_columnconfigure(1, weight=1) # Formulario
        self.grid_rowconfigure(0, weight=1)

        # --- LISTA DE USUARIOS ---
        left_panel = ctk.CTkFrame(self, **Theme.get_card_style())
        left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Header
        header = ctk.CTkFrame(left_panel, fg_color="transparent")
        header.pack(fill="x", pady=Theme.PADDING_LARGE, padx=Theme.PADDING_LARGE)
        ctk.CTkLabel(header, text="👥 LISTA DE PERSONAL", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"), text_color=Theme.TEXT_PRIMARY).pack()
        
        # Separator
        ctk.CTkFrame(left_panel, height=2, fg_color=Theme.DIVIDER).pack(fill="x", pady=(0, Theme.PADDING_MEDIUM))
        
        ctk.CTkButton(left_panel, text="🔄 ACTUALIZAR", command=self.load_users, **Theme.get_button_style("primary"), height=40).pack(pady=5, padx=Theme.PADDING_LARGE, fill="x")
        
        self.scroll_users = ctk.CTkScrollableFrame(left_panel, fg_color=Theme.BACKGROUND_LIGHT, corner_radius=Theme.RADIUS_MEDIUM)
        self.scroll_users.pack(fill="both", expand=True, pady=10, padx=Theme.PADDING_MEDIUM)

        # --- FORMULARIO NUEVO ---
        right_panel = ctk.CTkFrame(self, **Theme.get_card_style())
        right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Header
        header_right = ctk.CTkFrame(right_panel, fg_color="transparent")
        header_right.pack(fill="x", pady=Theme.PADDING_LARGE, padx=Theme.PADDING_LARGE)
        ctk.CTkLabel(header_right, text="➕ CREAR NUEVO USUARIO", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"), text_color=Theme.TEXT_PRIMARY).pack()
        
        # Separator
        ctk.CTkFrame(right_panel, height=2, fg_color=Theme.DIVIDER).pack(fill="x", pady=(0, Theme.PADDING_LARGE))
        
        self.var_user = ctk.StringVar()
        self.var_user.trace("w", lambda *a: self.force_upper(self.var_user))
        
        ctk.CTkEntry(right_panel, textvariable=self.var_user, placeholder_text="👤 NOMBRE USUARIO", height=45, corner_radius=Theme.RADIUS_MEDIUM, border_color=Theme.BORDER).pack(pady=10, fill="x", padx=20)
        self.entry_pass = ctk.CTkEntry(right_panel, placeholder_text="🔒 CONTRASEÑA", show="*", height=45, corner_radius=Theme.RADIUS_MEDIUM, border_color=Theme.BORDER)
        self.entry_pass.pack(pady=10, fill="x", padx=20)
        
        ctk.CTkLabel(right_panel, text="🎭 ROL ASIGNADO:", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"), text_color=Theme.TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(10,5))
        self.combo_rol = ctk.CTkComboBox(right_panel, values=["TECNICO", "RECEPCIONISTA", "ADMINISTRADOR", "GERENTE"], height=40, corner_radius=Theme.RADIUS_MEDIUM, border_color=Theme.BORDER)
        self.combo_rol.pack(pady=5, fill="x", padx=20)
        
        ctk.CTkLabel(right_panel, text="💰 COMISIÓN TÉCNICA (%):", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"), text_color=Theme.TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(10,5))
        self.entry_comision = ctk.CTkEntry(right_panel, placeholder_text="EJ: 50", height=40, corner_radius=Theme.RADIUS_MEDIUM, border_color=Theme.BORDER)
        self.entry_comision.pack(pady=5, fill="x", padx=20)
        self.entry_comision.insert(0, "0")

        ctk.CTkButton(right_panel, text="✅ GUARDAR USUARIO", command=self.save_user, **Theme.get_button_style("success"), height=50).pack(pady=30, fill="x", padx=20)

        self.load_users()

    def refresh(self):
        self.load_users()

    def force_upper(self, var):
        var.set(var.get().upper())

    def load_users(self):
        for w in self.scroll_users.winfo_children(): w.destroy()
        users = self.logic.get_all_users()
        
        for u in users:
            uid, name, _, rol, com = u
            card = ctk.CTkFrame(self.scroll_users, **Theme.get_card_style())
            card.pack(fill="x", pady=5, padx=5)
            
            ctk.CTkLabel(card, text=f"👤 {name} [{rol}]", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"), text_color=Theme.TEXT_PRIMARY).pack(side="left", padx=10)
            if rol == "TECNICO":
                ctk.CTkLabel(card, text=f"{com}%", text_color=Theme.ACCENT, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold")).pack(side="left", padx=5)
            
            if name != "ADMIN": # No dejar borrar al admin principal
                ctk.CTkButton(card, text="❌", width=40, **Theme.get_button_style("error"), command=lambda x=uid: self.delete_user(x)).pack(side="right", padx=5, pady=5)

    def save_user(self):
        try:
            name = self.var_user.get()
            pwd = self.entry_pass.get()
            rol = self.combo_rol.get()
            com = float(self.entry_comision.get())
            
            if not name or not pwd:
                messagebox.showerror("ERROR", "FALTAN DATOS")
                return

            if self.logic.create_user(name, pwd, rol, com):
                messagebox.showinfo("ÉXITO", "USUARIO CREADO")
                self.load_users()
                self.var_user.set("")
                self.entry_pass.delete(0, "end")
                # Refrescar lista de técnicos en recepción
                if self.app and hasattr(self.app, 'frames') and 'Reception' in self.app.frames:
                    self.app.frames['Reception'].refresh()
            else:
                messagebox.showerror("ERROR", "EL USUARIO YA EXISTE")
        except ValueError:
            messagebox.showerror("ERROR", "COMISIÓN DEBE SER NÚMERO")

    def delete_user(self, uid):
        if messagebox.askyesno("CONFIRMAR", "¿ELIMINAR ESTE USUARIO?"):
            self.logic.delete_user(uid)
            self.load_users()
            # Refrescar lista de técnicos en recepción
            if self.app and hasattr(self.app, 'frames') and 'Reception' in self.app.frames:
                self.app.frames['Reception'].refresh()
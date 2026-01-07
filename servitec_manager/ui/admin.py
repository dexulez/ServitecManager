import customtkinter as ctk
from tkinter import messagebox
from .theme import Theme
from .bank_accounts import BankAccountsFrame

class AdminFrame(ctk.CTkFrame):
    def __init__(self, parent, logic, current_user, app=None):
        super().__init__(parent, fg_color=Theme.BACKGROUND)
        self.logic = logic
        self.app = app
        
        # Crear TabView para Usuarios y Cuentas Bancarias
        self.tabview = ctk.CTkTabview(
            self,
            fg_color=Theme.SURFACE,
            segmented_button_fg_color=Theme.BACKGROUND_LIGHT,
            segmented_button_selected_color=Theme.PRIMARY,
            text_color=Theme.TEXT_PRIMARY
        )
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tab de Usuarios
        self.tab_usuarios = self.tabview.add("👥 USUARIOS")
        self.setup_usuarios_tab()
        
        # Tab de Cuentas Bancarias
        self.tab_banco = self.tabview.add("🏦 CUENTAS BANCARIAS")
        self.banco_frame = BankAccountsFrame(self.tab_banco, logic, current_user)
        self.banco_frame.pack(fill="both", expand=True)

    def setup_usuarios_tab(self):
        """Configura el tab de usuarios"""
        # GRID LAYOUT
        self.tab_usuarios.grid_columnconfigure(0, weight=1) # Lista
        self.tab_usuarios.grid_columnconfigure(1, weight=1) # Formulario
        self.tab_usuarios.grid_rowconfigure(0, weight=1)

        # --- LISTA DE USUARIOS ---
        left_panel = ctk.CTkFrame(self.tab_usuarios, **Theme.get_card_style())
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
        right_panel = ctk.CTkFrame(self.tab_usuarios, **Theme.get_card_style())
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

        # Separador
        ctk.CTkFrame(right_panel, height=2, fg_color=Theme.DIVIDER).pack(fill="x", pady=20, padx=20)
        
        # Sección de gestión de base de datos
        ctk.CTkLabel(right_panel, text="💾 GESTIÓN DE BASE DE DATOS", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"), text_color=Theme.PRIMARY).pack(anchor="w", padx=20, pady=(10,5))
        ctk.CTkButton(right_panel, text="💾 RESPALDAR BASE DE DATOS", command=self.respaldar_base_datos, fg_color="#2196F3", hover_color="#1976D2", text_color="white", height=50).pack(pady=10, fill="x", padx=20)
        
        # Zona peligrosa
        ctk.CTkLabel(right_panel, text="⚠️ ZONA PELIGROSA", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"), text_color="#FF0000").pack(anchor="w", padx=20, pady=(20,5))
        ctk.CTkButton(right_panel, text="🗑️ LIMPIAR BASE DE DATOS", command=self.limpiar_base_datos, fg_color="#FF4444", hover_color="#CC0000", text_color="white", height=50).pack(pady=10, fill="x", padx=20)

        self.load_users()

    def refresh(self):
        self.load_users()

    def force_upper(self, var):
        var.set(var.get().upper())

    def load_users(self):
        for w in self.scroll_users.winfo_children(): w.destroy()
        users = self.logic.get_all_users()
        
        for u in users:
            # Usuarios: (id, nombre, password, rol, porcentaje_comision, activo, fecha_creacion)
            uid = u[0]
            name = u[1]
            rol = u[3]
            com = u[4] if len(u) > 4 else 50
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
    
    def respaldar_base_datos(self):
        """Crea un respaldo manual de la base de datos"""
        try:
            import os
            import shutil
            from datetime import datetime
            from tkinter import filedialog
            
            db_path = 'SERVITEC.DB'
            
            if not os.path.exists(db_path):
                messagebox.showerror("Error", "No se encuentra la base de datos SERVITEC.DB")
                return
            
            # Crear directorio de backups si no existe
            backup_dir = 'backups'
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # Generar nombre del backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f'SERVITEC_BACKUP_{timestamp}.DB'
            backup_path = os.path.join(backup_dir, backup_name)
            
            # Preguntar si desea elegir ubicación personalizada
            respuesta = messagebox.askyesnocancel(
                "💾 RESPALDO DE BASE DE DATOS",
                f"Se creará un respaldo de la base de datos.\n\n"
                f"¿Desea elegir la ubicación del respaldo?\n\n"
                f"• SÍ: Elegir ubicación personalizada\n"
                f"• NO: Guardar en carpeta 'backups' predeterminada\n"
                f"• Cancelar: Cancelar operación"
            )
            
            if respuesta is None:  # Cancelar
                return
            
            if respuesta:  # Sí - elegir ubicación
                custom_path = filedialog.asksaveasfilename(
                    title="Guardar respaldo como",
                    initialfile=backup_name,
                    defaultextension=".DB",
                    filetypes=[("Base de datos", "*.DB"), ("Todos los archivos", "*.*")]
                )
                
                if not custom_path:  # Usuario canceló el diálogo
                    return
                
                backup_path = custom_path
            
            # Crear el respaldo
            shutil.copy2(db_path, backup_path)
            
            # Obtener estadísticas de la base de datos
            import sqlite3
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            
            ordenes = c.execute('SELECT COUNT(*) FROM ordenes').fetchone()[0]
            clientes = c.execute('SELECT COUNT(*) FROM clientes').fetchone()[0]
            usuarios = c.execute('SELECT COUNT(*) FROM usuarios').fetchone()[0]
            ventas = c.execute('SELECT COUNT(*) FROM ventas').fetchone()[0]
            
            conn.close()
            
            # Obtener tamaño del archivo
            file_size = os.path.getsize(backup_path)
            size_mb = file_size / (1024 * 1024)
            
            messagebox.showinfo(
                "✅ RESPALDO COMPLETADO",
                f"Base de datos respaldada exitosamente.\n\n"
                f"📁 Ubicación:\n{backup_path}\n\n"
                f"📊 Contenido respaldado:\n"
                f"• Órdenes: {ordenes}\n"
                f"• Clientes: {clientes}\n"
                f"• Usuarios: {usuarios}\n"
                f"• Ventas: {ventas}\n\n"
                f"💾 Tamaño: {size_mb:.2f} MB\n\n"
                f"🕐 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
        except Exception as e:
            messagebox.showerror(
                "❌ ERROR",
                f"No se pudo crear el respaldo:\n\n{str(e)}"
            )
    
    def limpiar_base_datos(self):
        """Limpia todos los datos de la base de datos manteniendo usuarios"""
        # Primera confirmación
        respuesta1 = messagebox.askquestion(
            "⚠️ ADVERTENCIA - ACCIÓN IRREVERSIBLE",
            "Esta acción eliminará:\n\n"
            "• Todas las órdenes de servicio\n"
            "• Todos los clientes\n"
            "• Todas las ventas\n"
            "• Todo el inventario\n"
            "• Todas las transacciones\n\n"
            "Se mantendrán:\n"
            "✓ Usuarios y contraseñas\n"
            "✓ Configuración del sistema\n\n"
            "¿Está SEGURO que desea continuar?",
            icon='warning'
        )
        
        if respuesta1 != 'yes':
            return
        
        # Segunda confirmación
        respuesta2 = messagebox.askquestion(
            "⚠️ ÚLTIMA CONFIRMACIÓN",
            "Esta es su última oportunidad para cancelar.\n\n"
            "Se creará un backup automático antes de limpiar.\n\n"
            "¿Confirma que desea LIMPIAR LA BASE DE DATOS?",
            icon='warning'
        )
        
        if respuesta2 != 'yes':
            messagebox.showinfo("Operación cancelada", "No se realizaron cambios en la base de datos.")
            return
        
        try:
            import sqlite3
            import os
            from datetime import datetime
            
            db_path = 'SERVITEC.DB'
            
            # Crear backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = 'backups'
            
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            backup_path = os.path.join(backup_dir, f'SERVITEC_BACKUP_{timestamp}.DB')
            
            import shutil
            shutil.copy2(db_path, backup_path)
            
            # Limpiar base de datos
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            
            # Eliminar datos de tablas principales
            tablas = ['ordenes', 'clientes', 'ventas', 'detalle_ventas', 'inventario', 
                     'finanzas', 'proveedores', 'pedidos', 'caja']
            
            for tabla in tablas:
                try:
                    c.execute(f'DELETE FROM {tabla}')
                except:
                    pass
            
            # Limpiar servicios y repuestos excepto el primero
            try:
                c.execute('DELETE FROM servicios WHERE id > 1')
                c.execute('DELETE FROM repuestos WHERE id > 1')
            except:
                pass
            
            # Reiniciar secuencias
            try:
                c.execute('UPDATE sqlite_sequence SET seq = 0 WHERE name IN ("ordenes", "clientes", "ventas", "inventario", "finanzas", "proveedores", "pedidos", "caja")')
            except:
                pass
            
            conn.commit()
            
            # Verificar resultado
            ordenes = c.execute('SELECT COUNT(*) FROM ordenes').fetchone()[0]
            clientes = c.execute('SELECT COUNT(*) FROM clientes').fetchone()[0]
            
            conn.close()
            
            # Refrescar todas las vistas
            if self.app:
                self.app.refresh_all_frames()
            
            messagebox.showinfo(
                "✅ BASE DE DATOS LIMPIADA",
                f"Operación completada exitosamente.\n\n"
                f"📊 Estado actual:\n"
                f"• Órdenes: {ordenes}\n"
                f"• Clientes: {clientes}\n\n"
                f"💾 Backup guardado en:\n{backup_path}\n\n"
                f"La aplicación está lista para usarse."
            )
            
        except Exception as e:
            messagebox.showerror(
                "❌ ERROR",
                f"No se pudo limpiar la base de datos:\n\n{str(e)}\n\n"
                f"Por favor, cierre ServitecManager y ejecute:\n"
                f"python limpiar_db.py"
            )
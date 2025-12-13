import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import os
import shutil
from .theme import Theme

class CompanySettingsFrame(ctk.CTkFrame):
    def __init__(self, parent, logic, current_user):
        super().__init__(parent, fg_color=Theme.BACKGROUND)
        self.logic = logic
        self.current_user = current_user
        self.logo_path = None
        
        # Título Principal
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=Theme.PADDING_LARGE, padx=Theme.PADDING_LARGE)
        ctk.CTkLabel(header, text="🏢 CONFIGURACIÓN DE EMPRESA", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H1, "bold"), text_color=Theme.TEXT_PRIMARY).pack()
        
        ctk.CTkFrame(self, height=2, fg_color=Theme.DIVIDER).pack(fill="x", pady=(0, Theme.PADDING_MEDIUM))
        
        # Contenedor principal con scroll
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=Theme.PADDING_LARGE, pady=Theme.PADDING_MEDIUM)
        
        # ========== SECCIÓN LOGO ==========
        logo_card = ctk.CTkFrame(scroll, **Theme.get_card_style())
        logo_card.pack(fill="x", pady=Theme.PADDING_MEDIUM)
        
        # Header de sección
        logo_header = ctk.CTkFrame(logo_card, fg_color=Theme.PRIMARY, corner_radius=Theme.RADIUS_LARGE)
        logo_header.pack(fill="x")
        ctk.CTkLabel(logo_header, text="🎨 LOGO DE LA EMPRESA", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"), text_color=Theme.WHITE).pack(pady=15)
        
        # Contenido
        logo_content = ctk.CTkFrame(logo_card, fg_color="transparent")
        logo_content.pack(fill="both", expand=True, padx=Theme.PADDING_LARGE, pady=Theme.PADDING_LARGE)
        
        # Visor de logo
        self.logo_frame = ctk.CTkFrame(logo_content, fg_color=Theme.SURFACE, width=300, height=300, corner_radius=Theme.RADIUS_LARGE, border_width=3, border_color=Theme.BORDER)
        self.logo_frame.pack(pady=15)
        self.logo_frame.pack_propagate(False)
        
        self.logo_label = ctk.CTkLabel(self.logo_frame, text="📷\n\nSIN LOGO\n\nHaga clic en 'Cargar Logo'\npara agregar una imagen", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL), text_color=Theme.TEXT_SECONDARY)
        self.logo_label.pack(expand=True)
        
        # Botones de logo
        logo_buttons = ctk.CTkFrame(logo_content, fg_color="transparent")
        logo_buttons.pack(pady=10)
        
        ctk.CTkButton(logo_buttons, text="📁 CARGAR LOGO", command=self.load_logo, **Theme.get_button_style("primary"), width=180, height=45).pack(side="left", padx=5)
        ctk.CTkButton(logo_buttons, text="🗑️ ELIMINAR LOGO", command=self.remove_logo, **Theme.get_button_style("danger"), width=180, height=45).pack(side="left", padx=5)
        
        ctk.CTkLabel(logo_content, text="💡 Formatos: PNG, JPG, JPEG | Tamaño recomendado: 500x500 px", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL), text_color=Theme.TEXT_SECONDARY).pack(pady=5)
        
        # ========== SECCIÓN DATOS DE LA EMPRESA ==========
        info_card = ctk.CTkFrame(scroll, **Theme.get_card_style())
        info_card.pack(fill="x", pady=Theme.PADDING_MEDIUM)
        
        # Header de sección
        info_header = ctk.CTkFrame(info_card, fg_color=Theme.SUCCESS, corner_radius=Theme.RADIUS_LARGE)
        info_header.pack(fill="x")
        ctk.CTkLabel(info_header, text="📋 INFORMACIÓN DE LA EMPRESA", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"), text_color=Theme.WHITE).pack(pady=15)
        
        # Contenido
        info_content = ctk.CTkFrame(info_card, fg_color="transparent")
        info_content.pack(fill="both", expand=True, padx=Theme.PADDING_LARGE, pady=Theme.PADDING_LARGE)
        
        # Grid para formulario
        info_content.grid_columnconfigure(1, weight=1)
        
        def create_field(parent, row, label, icon, var_name, placeholder=""):
            field_frame = ctk.CTkFrame(parent, fg_color=Theme.SURFACE, corner_radius=Theme.RADIUS_MEDIUM)
            field_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=8, padx=5)
            
            ctk.CTkLabel(field_frame, text=f"{icon} {label}:", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"), text_color=Theme.TEXT_PRIMARY, anchor="w").pack(fill="x", padx=15, pady=(10, 5))
            
            var = ctk.StringVar()
            setattr(self, var_name, var)
            entry = ctk.CTkEntry(field_frame, textvariable=var, placeholder_text=placeholder, height=40, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL), border_color=Theme.BORDER, corner_radius=Theme.RADIUS_SMALL)
            entry.pack(fill="x", padx=15, pady=(0, 10))
            
            return var
        
        row = 0
        create_field(info_content, row, "NOMBRE DE LA EMPRESA", "🏢", "var_nombre", "Ej: SERVITEC CHILE LTDA"); row += 1
        create_field(info_content, row, "RUT / IDENTIFICACIÓN FISCAL", "🆔", "var_rut", "Ej: 76.XXX.XXX-X"); row += 1
        create_field(info_content, row, "RAZÓN SOCIAL", "📝", "var_razon", "Ej: SERVITEC SERVICIOS TECNOLÓGICOS LTDA"); row += 1
        create_field(info_content, row, "GIRO COMERCIAL", "💼", "var_giro", "Ej: REPARACIÓN DE EQUIPOS ELECTRÓNICOS"); row += 1
        create_field(info_content, row, "DIRECCIÓN", "📍", "var_direccion", "Ej: Av. Principal #123, Santiago"); row += 1
        create_field(info_content, row, "COMUNA / CIUDAD", "🏙️", "var_comuna", "Ej: Santiago Centro"); row += 1
        create_field(info_content, row, "REGIÓN / ESTADO", "🗺️", "var_region", "Ej: Región Metropolitana"); row += 1
        create_field(info_content, row, "TELÉFONO", "📞", "var_telefono", "Ej: +56 9 XXXX XXXX"); row += 1
        create_field(info_content, row, "EMAIL", "📧", "var_email", "Ej: contacto@servitec.cl"); row += 1
        create_field(info_content, row, "SITIO WEB", "🌐", "var_web", "Ej: www.servitec.cl"); row += 1
        
        # ========== BOTONES DE ACCIÓN ==========
        actions_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        actions_frame.pack(fill="x", pady=Theme.PADDING_LARGE)
        
        ctk.CTkButton(actions_frame, text="💾 GUARDAR CONFIGURACIÓN", command=self.save_settings, **Theme.get_button_style("success"), height=55).pack(pady=5, fill="x", padx=100)
        ctk.CTkButton(actions_frame, text="🔄 CARGAR CONFIGURACIÓN ACTUAL", command=self.load_settings, **Theme.get_button_style("secondary"), height=45).pack(pady=5, fill="x", padx=100)
        
        # Cargar configuración existente
        self.load_settings()
    
    def refresh(self):
        """Método para compatibilidad con app.py"""
        self.load_settings()
    
    def load_logo(self):
        """Cargar logo desde archivo"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar Logo",
            filetypes=[
                ("Imágenes", "*.png *.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("Todos", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Crear carpeta assets si no existe
                assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
                if not os.path.exists(assets_dir):
                    os.makedirs(assets_dir)
                
                # Copiar archivo con nombre estándar
                ext = os.path.splitext(file_path)[1]
                logo_dest = os.path.join(assets_dir, f"company_logo{ext}")
                shutil.copy2(file_path, logo_dest)
                
                self.logo_path = logo_dest
                self.display_logo(logo_dest)
                messagebox.showinfo("Éxito", "Logo cargado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el logo: {str(e)}")
    
    def display_logo(self, path):
        """Mostrar logo en el visor"""
        try:
            # Cargar y redimensionar imagen
            img = Image.open(path)
            img.thumbnail((280, 280), Image.Resampling.LANCZOS)
            
            # Convertir a PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # Actualizar label
            self.logo_label.configure(image=photo, text="")
            self.logo_label.image = photo  # Mantener referencia
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo mostrar el logo: {str(e)}")
    
    def remove_logo(self):
        """Eliminar logo"""
        if messagebox.askyesno("Confirmar", "¿Desea eliminar el logo de la empresa?"):
            try:
                assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
                # Buscar y eliminar archivos de logo
                for ext in ['.png', '.jpg', '.jpeg']:
                    logo_file = os.path.join(assets_dir, f"company_logo{ext}")
                    if os.path.exists(logo_file):
                        os.remove(logo_file)
                
                self.logo_path = None
                self.logo_label.configure(image="", text="📷\n\nSIN LOGO\n\nHaga clic en 'Cargar Logo'\npara agregar una imagen")
                self.logo_label.image = None
                
                messagebox.showinfo("Éxito", "Logo eliminado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el logo: {str(e)}")
    
    def save_settings(self):
        """Guardar configuración en base de datos"""
        try:
            datos = {
                'nombre': self.var_nombre.get(),
                'rut': self.var_rut.get(),
                'razon_social': self.var_razon.get(),
                'giro': self.var_giro.get(),
                'direccion': self.var_direccion.get(),
                'comuna': self.var_comuna.get(),
                'region': self.var_region.get(),
                'telefono': self.var_telefono.get(),
                'email': self.var_email.get(),
                'web': self.var_web.get(),
                'logo_path': self.logo_path or ''
            }
            
            # Crear tabla si no existe
            self.logic.bd.EJECUTAR_CONSULTA("""
                CREATE TABLE IF NOT EXISTS empresa_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT,
                    rut TEXT,
                    razon_social TEXT,
                    giro TEXT,
                    direccion TEXT,
                    comuna TEXT,
                    region TEXT,
                    telefono TEXT,
                    email TEXT,
                    web TEXT,
                    logo_path TEXT
                )
            """, ())
            
            # Verificar si existe registro
            existing = self.logic.bd.OBTENER_UNO("SELECT id FROM empresa_config LIMIT 1", ())
            
            if existing:
                # Actualizar
                self.logic.bd.EJECUTAR_CONSULTA("""
                    UPDATE empresa_config SET
                        nombre = ?,
                        rut = ?,
                        razon_social = ?,
                        giro = ?,
                        direccion = ?,
                        comuna = ?,
                        region = ?,
                        telefono = ?,
                        email = ?,
                        web = ?,
                        logo_path = ?
                    WHERE id = ?
                """, (datos['nombre'], datos['rut'], datos['razon_social'], datos['giro'],
                      datos['direccion'], datos['comuna'], datos['region'], datos['telefono'],
                      datos['email'], datos['web'], datos['logo_path'], existing[0]))
            else:
                # Insertar
                self.logic.bd.EJECUTAR_CONSULTA("""
                    INSERT INTO empresa_config (nombre, rut, razon_social, giro, direccion, comuna, region, telefono, email, web, logo_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (datos['nombre'], datos['rut'], datos['razon_social'], datos['giro'],
                      datos['direccion'], datos['comuna'], datos['region'], datos['telefono'],
                      datos['email'], datos['web'], datos['logo_path']))
            
            messagebox.showinfo("✅ Éxito", "Configuración guardada correctamente.\n\nLos cambios se aplicarán en los documentos generados.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la configuración: {str(e)}")
    
    def load_settings(self):
        """Cargar configuración desde base de datos"""
        try:
            # Crear tabla si no existe
            self.logic.bd.EJECUTAR_CONSULTA("""
                CREATE TABLE IF NOT EXISTS empresa_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT,
                    rut TEXT,
                    razon_social TEXT,
                    giro TEXT,
                    direccion TEXT,
                    comuna TEXT,
                    region TEXT,
                    telefono TEXT,
                    email TEXT,
                    web TEXT,
                    logo_path TEXT
                )
            """, ())
            
            config = self.logic.bd.OBTENER_UNO("SELECT * FROM empresa_config LIMIT 1", ())
            
            if config:
                # config: 0:id, 1:nombre, 2:rut, 3:razon, 4:giro, 5:dir, 6:comuna, 7:region, 8:tel, 9:email, 10:web, 11:logo
                self.var_nombre.set(config[1] or "")
                self.var_rut.set(config[2] or "")
                self.var_razon.set(config[3] or "")
                self.var_giro.set(config[4] or "")
                self.var_direccion.set(config[5] or "")
                self.var_comuna.set(config[6] or "")
                self.var_region.set(config[7] or "")
                self.var_telefono.set(config[8] or "")
                self.var_email.set(config[9] or "")
                self.var_web.set(config[10] or "")
                
                # Cargar logo si existe
                logo_path = config[11]
                if logo_path and os.path.exists(logo_path):
                    self.logo_path = logo_path
                    self.display_logo(logo_path)
                else:
                    # Buscar logo en carpeta assets
                    assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
                    for ext in ['.png', '.jpg', '.jpeg']:
                        logo_file = os.path.join(assets_dir, f"company_logo{ext}")
                        if os.path.exists(logo_file):
                            self.logo_path = logo_file
                            self.display_logo(logo_file)
                            break
        except Exception as e:
            print(f"Error al cargar configuración: {str(e)}")

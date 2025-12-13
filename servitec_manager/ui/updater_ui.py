"""
Interfaz gráfica para el sistema de actualizaciones
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
from .theme import Theme
from updater import GestorActualizaciones

class UpdaterFrame(ctk.CTkFrame):
    def __init__(self, parent, logic, current_user):
        super().__init__(parent, fg_color=Theme.BACKGROUND)
        self.logic = logic
        self.current_user = current_user
        self.updater = GestorActualizaciones()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.setup_ui()
        self.cargar_info_version()
    
    def setup_ui(self):
        # Contenedor principal
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Header
        header = ctk.CTkFrame(main, **Theme.get_card_style())
        header.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            header,
            text="🔄 SISTEMA DE ACTUALIZACIONES",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H1, "bold"),
            text_color=Theme.PRIMARY
        ).pack(pady=20)
        
        # Información de versión actual
        version_frame = ctk.CTkFrame(main, **Theme.get_card_style())
        version_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            version_frame,
            text="ℹ️ INFORMACIÓN DEL SISTEMA",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"),
            text_color=Theme.TEXT_PRIMARY
        ).pack(pady=(15, 10), padx=20, anchor="w")
        
        info_container = ctk.CTkFrame(version_frame, fg_color=Theme.BACKGROUND_LIGHT, corner_radius=Theme.RADIUS_MEDIUM)
        info_container.pack(fill="x", padx=20, pady=(0, 15))
        
        self.lbl_version = ctk.CTkLabel(
            info_container,
            text="",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold"),
            text_color=Theme.SUCCESS,
            anchor="w"
        )
        self.lbl_version.pack(padx=15, pady=10, anchor="w")
        
        self.lbl_ultima_actualizacion = ctk.CTkLabel(
            info_container,
            text="",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
            text_color=Theme.TEXT_SECONDARY,
            anchor="w"
        )
        self.lbl_ultima_actualizacion.pack(padx=15, pady=(0, 10), anchor="w")
        
        # Panel de acciones
        acciones_frame = ctk.CTkFrame(main, **Theme.get_card_style())
        acciones_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            acciones_frame,
            text="📦 CARGAR ACTUALIZACIÓN",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"),
            text_color=Theme.TEXT_PRIMARY
        ).pack(pady=(15, 10), padx=20, anchor="w")
        
        btn_container = ctk.CTkFrame(acciones_frame, fg_color="transparent")
        btn_container.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkButton(
            btn_container,
            text="📂 SELECCIONAR PAQUETE DE ACTUALIZACIÓN (.zip)",
            command=self.seleccionar_paquete,
            **Theme.get_button_style("primary"),
            height=50
        ).pack(fill="x", pady=5)
        
        ctk.CTkButton(
            btn_container,
            text="🔙 VER BACKUPS Y RESTAURAR",
            command=self.mostrar_backups,
            **Theme.get_button_style("secondary"),
            height=45
        ).pack(fill="x", pady=5)
        
        # Barra de progreso
        self.progress_frame = ctk.CTkFrame(main, **Theme.get_card_style())
        self.progress_frame.pack(fill="x", pady=(0, 20))
        self.progress_frame.pack_forget()  # Ocultar inicialmente
        
        ctk.CTkLabel(
            self.progress_frame,
            text="⏳ APLICANDO ACTUALIZACIÓN",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"),
            text_color=Theme.WARNING
        ).pack(pady=(15, 5), padx=20, anchor="w")
        
        self.lbl_progreso = ctk.CTkLabel(
            self.progress_frame,
            text="Iniciando...",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
            text_color=Theme.TEXT_SECONDARY
        )
        self.lbl_progreso.pack(padx=20, pady=5, anchor="w")
        
        self.progressbar = ctk.CTkProgressBar(
            self.progress_frame,
            height=20,
            corner_radius=10
        )
        self.progressbar.pack(fill="x", padx=20, pady=(5, 15))
        self.progressbar.set(0)
        
        # Historial de actualizaciones
        historial_frame = ctk.CTkFrame(main, **Theme.get_card_style())
        historial_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            historial_frame,
            text="📜 HISTORIAL DE ACTUALIZACIONES",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"),
            text_color=Theme.TEXT_PRIMARY
        ).pack(pady=(15, 10), padx=20, anchor="w")
        
        self.scroll_historial = ctk.CTkScrollableFrame(
            historial_frame,
            fg_color=Theme.BACKGROUND_LIGHT,
            corner_radius=Theme.RADIUS_MEDIUM
        )
        self.scroll_historial.pack(fill="both", expand=True, padx=20, pady=(0, 15))
    
    def cargar_info_version(self):
        """Carga la información de la versión actual"""
        version = self.updater.version_actual
        self.lbl_version.configure(text=f"Versión Actual: {version}")
        
        try:
            import os
            version_file = os.path.join(self.updater.ruta_base, "version.json")
            if os.path.exists(version_file):
                import json
                with open(version_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    fecha = data.get('fecha_actualizacion', 'Desconocida')
                    self.lbl_ultima_actualizacion.configure(text=f"Última actualización: {fecha}")
            else:
                self.lbl_ultima_actualizacion.configure(text="Última actualización: Instalación inicial")
        except:
            self.lbl_ultima_actualizacion.configure(text="Última actualización: Desconocida")
        
        # Cargar historial
        self.cargar_historial()
    
    def cargar_historial(self):
        """Carga el historial de actualizaciones"""
        for widget in self.scroll_historial.winfo_children():
            widget.destroy()
        
        historial = self.updater.obtener_historial_actualizaciones()
        
        if not historial:
            ctk.CTkLabel(
                self.scroll_historial,
                text="No hay actualizaciones registradas",
                text_color=Theme.TEXT_SECONDARY
            ).pack(pady=20)
            return
        
        for item in historial:
            card = ctk.CTkFrame(
                self.scroll_historial,
                fg_color=Theme.SURFACE if item['tipo'] == 'actual' else Theme.BACKGROUND,
                corner_radius=Theme.RADIUS_SMALL,
                border_width=2 if item['tipo'] == 'actual' else 0,
                border_color=Theme.SUCCESS if item['tipo'] == 'actual' else "transparent"
            )
            card.pack(fill="x", pady=5, padx=5)
            
            # Header del item
            header_item = ctk.CTkFrame(card, fg_color="transparent")
            header_item.pack(fill="x", padx=10, pady=8)
            
            icono = "✅" if item['tipo'] == 'actual' else "📦"
            ctk.CTkLabel(
                header_item,
                text=f"{icono} Versión {item['version']}",
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
                text_color=Theme.SUCCESS if item['tipo'] == 'actual' else Theme.TEXT_PRIMARY
            ).pack(side="left")
            
            if item['tipo'] == 'actual':
                ctk.CTkLabel(
                    header_item,
                    text="ACTUAL",
                    font=(Theme.FONT_FAMILY, 9, "bold"),
                    text_color="white",
                    fg_color=Theme.SUCCESS,
                    corner_radius=5,
                    padx=10,
                    pady=2
                ).pack(side="right")
            
            ctk.CTkLabel(
                card,
                text=f"Fecha: {item['fecha']}",
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL),
                text_color=Theme.TEXT_SECONDARY,
                anchor="w"
            ).pack(padx=10, pady=(0, 5), anchor="w")
            
            if item.get('cambios'):
                cambios_text = item['cambios'][:100] + "..." if len(item['cambios']) > 100 else item['cambios']
                ctk.CTkLabel(
                    card,
                    text=f"Cambios: {cambios_text}",
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL),
                    text_color=Theme.TEXT_SECONDARY,
                    anchor="w",
                    wraplength=500
                ).pack(padx=10, pady=(0, 8), anchor="w")
    
    def seleccionar_paquete(self):
        """Abre diálogo para seleccionar paquete de actualización"""
        archivo = filedialog.askopenfilename(
            title="Seleccionar paquete de actualización",
            filetypes=[("Paquetes de actualización", "*.zip"), ("Todos los archivos", "*.*")]
        )
        
        if not archivo:
            return
        
        # Validar paquete
        valido, mensaje, update_info = self.updater.validar_paquete_actualizacion(archivo)
        
        if not valido:
            messagebox.showerror("Paquete Inválido", mensaje)
            return
        
        # Mostrar información y confirmar
        confirmacion = messagebox.askyesno(
            "Confirmar Actualización",
            f"PAQUETE VÁLIDO\n\n"
            f"Versión: {update_info['version']}\n"
            f"Versión actual: {self.updater.version_actual}\n\n"
            f"Descripción:\n{update_info['descripcion']}\n\n"
            f"Archivos a actualizar: {len(update_info['archivos'])}\n\n"
            f"IMPORTANTE:\n"
            f"- Se creará un backup automático\n"
            f"- Se recomienda cerrar el programa después\n"
            f"- No apagar el equipo durante la actualización\n\n"
            f"¿Desea continuar con la actualización?"
        )
        
        if not confirmacion:
            return
        
        # Aplicar actualización en segundo plano
        self.aplicar_actualizacion_async(archivo)
    
    def aplicar_actualizacion_async(self, ruta_paquete):
        """Aplica la actualización en un hilo separado"""
        self.progress_frame.pack(fill="x", pady=(0, 20))
        self.progressbar.set(0)
        self.lbl_progreso.configure(text="Iniciando actualización...")
        
        def callback_progreso(mensaje, porcentaje):
            self.lbl_progreso.configure(text=mensaje)
            self.progressbar.set(porcentaje / 100)
            self.update_idletasks()
        
        def ejecutar_actualizacion():
            exito, mensaje = self.updater.aplicar_actualizacion(ruta_paquete, callback_progreso)
            
            # Actualizar UI en hilo principal
            self.after(100, lambda: self.finalizar_actualizacion(exito, mensaje))
        
        thread = threading.Thread(target=ejecutar_actualizacion, daemon=True)
        thread.start()
    
    def finalizar_actualizacion(self, exito, mensaje):
        """Finaliza el proceso de actualización y muestra resultado"""
        self.progress_frame.pack_forget()
        
        if exito:
            messagebox.showinfo("Actualización Exitosa", mensaje)
            self.cargar_info_version()
            
            # Preguntar si desea reiniciar
            if messagebox.askyesno("Reiniciar Aplicación", "¿Desea cerrar la aplicación ahora para aplicar los cambios?\n\nSe recomienda reiniciar."):
                self.quit()
        else:
            messagebox.showerror("Error en Actualización", mensaje)
    
    def mostrar_backups(self):
        """Muestra ventana con lista de backups disponibles"""
        win = ctk.CTkToplevel(self)
        win.title("Backups Disponibles")
        win.geometry("600x500")
        win.transient(self)
        win.grab_set()
        
        # Centrar ventana
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (600 // 2)
        y = (win.winfo_screenheight() // 2) - (500 // 2)
        win.geometry(f"600x500+{x}+{y}")
        
        ctk.CTkLabel(
            win,
            text="🔙 BACKUPS DISPONIBLES",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H1, "bold")
        ).pack(pady=20)
        
        scroll = ctk.CTkScrollableFrame(win, fg_color=Theme.BACKGROUND_LIGHT)
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        backups = self.updater.listar_backups()
        
        if not backups:
            ctk.CTkLabel(
                scroll,
                text="No hay backups disponibles",
                text_color=Theme.TEXT_SECONDARY
            ).pack(pady=50)
        else:
            for backup in backups:
                card = ctk.CTkFrame(scroll, fg_color=Theme.SURFACE, corner_radius=Theme.RADIUS_SMALL)
                card.pack(fill="x", pady=5)
                
                info_frame = ctk.CTkFrame(card, fg_color="transparent")
                info_frame.pack(side="left", fill="x", expand=True, padx=15, pady=10)
                
                ctk.CTkLabel(
                    info_frame,
                    text=f"📦 Versión {backup['version']}",
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
                    anchor="w"
                ).pack(anchor="w")
                
                ctk.CTkLabel(
                    info_frame,
                    text=f"Fecha: {backup['fecha']}",
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL),
                    text_color=Theme.TEXT_SECONDARY,
                    anchor="w"
                ).pack(anchor="w")
                
                ctk.CTkButton(
                    card,
                    text="Restaurar",
                    width=100,
                    command=lambda b=backup: self.restaurar_backup_confirmacion(b, win),
                    **Theme.get_button_style("warning")
                ).pack(side="right", padx=10)
        
        ctk.CTkButton(
            win,
            text="Cerrar",
            command=win.destroy,
            **Theme.get_button_style("secondary")
        ).pack(pady=(0, 20))
    
    def restaurar_backup_confirmacion(self, backup, ventana_padre):
        """Confirma y restaura un backup"""
        if messagebox.askyesno(
            "Confirmar Restauración",
            f"¿Está seguro de restaurar el backup?\n\n"
            f"Versión: {backup['version']}\n"
            f"Fecha: {backup['fecha']}\n\n"
            f"ADVERTENCIA:\n"
            f"- Se perderán todos los cambios desde esta fecha\n"
            f"- La aplicación se cerrará automáticamente\n",
            parent=ventana_padre
        ):
            ruta_backup = backup['ruta']
            exito, mensaje = self.updater.restaurar_backup(ruta_backup)
            
            if exito:
                messagebox.showinfo("Restauración Exitosa", f"{mensaje}\n\nLa aplicación se cerrará ahora.", parent=ventana_padre)
                ventana_padre.destroy()
                self.quit()
            else:
                messagebox.showerror("Error", mensaje, parent=ventana_padre)
    
    def refresh(self):
        """Refresca la información cuando se cambia a esta pestaña"""
        self.cargar_info_version()

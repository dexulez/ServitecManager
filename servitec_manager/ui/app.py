import customtkinter as ctk
from .login import LoginFrame
from .reception import ReceptionFrame
from .workshop import WorkshopFrame
from .dashboard import DashboardFrame
from .admin import AdminFrame
from .history import HistoryFrame
from .reports import ReportsFrame
from .cash import CashFrame
from .pos import POSFrame
from .inventory import InventoryFrame
from .providers_ui import ProvidersUI
from .pedidos_ui import PedidosFrame  # 🆕 Sistema de pedidos
from .company_settings import CompanySettingsFrame
from .updater_ui import UpdaterFrame
from .theme import Theme

class APLICACION(ctk.CTk):
    def __init__(self, gestor_lógica):
        super().__init__()
        self.gestor_lógica = gestor_lógica
        self.title("SERVITEC MANAGER PRO")
        self.geometry("1400x850")
        self.after(0, lambda: self.state("zoomed"))
        
        # Aplicar tema de color general
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=Theme.BACKGROUND)
        
        self.usuario_actual = None
        self.frames = {}

        self.grid_columnconfigure(0, weight=0, minsize=350)  # Sidebar con ancho fijo de 350px
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.mostrar_login()

    def mostrar_login(self):
        for widget in self.winfo_children(): widget.destroy()
        login_frame = LoginFrame(self, self.gestor_lógica, self.en_inicio_sesión_exitoso)
        login_frame.place(relx=0.5, rely=0.5, anchor="center")

    def en_inicio_sesión_exitoso(self, datos_usuario):
        self.usuario_actual = datos_usuario
        self.crear_disposición_principal()

    def crear_disposición_principal(self):
        for widget in self.winfo_children(): widget.destroy()
        
        # Sidebar moderno - Ancho aumentado para textos largos
        self.sidebar = ctk.CTkFrame(
            self, 
            width=350, 
            corner_radius=0, 
            fg_color=Theme.SIDEBAR_BG,
            border_width=1,
            border_color=Theme.BORDER
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # Logo/Título con icono
        header_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header_frame.pack(pady=30, padx=20)
        
        ctk.CTkLabel(
            header_frame, 
            text="⚙️ SERVITEC", 
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_XXLARGE, "bold"), 
            text_color=Theme.PRIMARY
        ).pack()
        
        ctk.CTkLabel(
            header_frame,
            text="MANAGER PRO",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL),
            text_color=Theme.TEXT_SECONDARY
        ).pack()
        
        # Separador
        ctk.CTkFrame(self.sidebar, height=1, fg_color=Theme.DIVIDER).pack(fill="x", padx=20, pady=10)
        
        rol = str(self.usuario_actual['rol']).upper() if isinstance(self.usuario_actual, dict) else str(self.usuario_actual[3]).upper()
        
        # Scroll frame para menú
        menu_scroll = ctk.CTkScrollableFrame(
            self.sidebar,
            fg_color="transparent",
            scrollbar_button_color=Theme.PRIMARY,
            scrollbar_button_hover_color=Theme.PRIMARY_DARK
        )
        menu_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Variables para submenús colapsables
        self.menu_states = {}
        
        def crear_botón_menu(parent, icono, txt, cmd, is_submenu=False):
            """Crea un botón de menú con estilo consistente"""
            btn = ctk.CTkButton(
                parent,
                text=f"{icono}  {txt}",
                command=cmd,
                fg_color="transparent" if is_submenu else Theme.SURFACE,
                hover_color=Theme.SIDEBAR_ACTIVE if is_submenu else Theme.PRIMARY,
                text_color=Theme.TEXT_SECONDARY if is_submenu else Theme.TEXT_PRIMARY,
                corner_radius=Theme.RADIUS_MEDIUM,
                border_width=0 if is_submenu else 1,
                border_color=Theme.BORDER,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE if is_submenu else Theme.FONT_SIZE_LARGE, "normal" if is_submenu else "bold"),
                anchor="w",
                height=45 if is_submenu else 50
            )
            if is_submenu:
                btn.pack(pady=3, padx=(30, 10), fill="x")
            else:
                btn.pack(pady=6, padx=10, fill="x")
            return btn
        
        def crear_seccion_colapsable(icono, titulo, items):
            """Crea una sección con submenús colapsables"""
            section_id = titulo.replace(" ", "_")
            self.menu_states[section_id] = {"expanded": False, "frame": None, "items": items, "btn": None}
            
            def toggle_section():
                state = self.menu_states[section_id]
                was_expanded = state["expanded"]
                
                # Cerrar todas las demás secciones
                for other_id, other_state in self.menu_states.items():
                    if other_id != section_id and other_state["expanded"]:
                        other_state["expanded"] = False
                        if other_state["frame"]:
                            other_state["frame"].pack_forget()
                        if other_state["btn"]:
                            # Obtener icono y título del botón
                            btn_text = other_state["btn"].cget("text")
                            if btn_text.startswith("▼"):
                                other_state["btn"].configure(text=btn_text.replace("▼", "▶"))
                
                # Toggle estado actual
                state["expanded"] = not was_expanded
                
                if state["expanded"]:
                    # Mostrar items
                    if state["frame"] is None:
                        state["frame"] = ctk.CTkFrame(menu_scroll, fg_color="transparent")
                        state["frame"].pack(fill="x", pady=(0, 5))
                        for item_icono, item_txt, item_cmd in items:
                            crear_botón_menu(state["frame"], item_icono, item_txt, item_cmd, is_submenu=True)
                    else:
                        state["frame"].pack(fill="x", pady=(0, 5))
                    section_btn.configure(text=f"▼ {icono}  {titulo}")
                else:
                    # Ocultar items
                    if state["frame"]:
                        state["frame"].pack_forget()
                    section_btn.configure(text=f"▶ {icono}  {titulo}")
            
            section_btn = ctk.CTkButton(
                menu_scroll,
                text=f"▶ {icono}  {titulo}",
                command=toggle_section,
                fg_color=Theme.BACKGROUND_LIGHT,
                hover_color=Theme.SIDEBAR_HOVER,
                text_color=Theme.TEXT_PRIMARY,
                corner_radius=Theme.RADIUS_MEDIUM,
                border_width=0,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold"),
                anchor="w",
                height=70
            )
            section_btn.pack(pady=4, padx=10, fill="x")
            
            # Guardar referencia al botón
            self.menu_states[section_id]["btn"] = section_btn
            
            return section_btn
        
        # === MENÚ PRINCIPAL POR ROL ===
        
        # === 0. TURNOS ===
        if rol in ['RECEPCIONISTA', 'ADMINISTRADOR', 'GERENTE']:
            turnos_items = [
                ("💰", "Caja", lambda: self.mostrar_frame("Cash")),
                ("📊", "Reportes", lambda: self.mostrar_frame("Reports"))
            ]
            crear_seccion_colapsable("💵", "Turnos", turnos_items)
        
        # === 1. POS / VENTAS ===
        if rol in ['RECEPCIONISTA', 'ADMINISTRADOR', 'GERENTE']:
            crear_botón_menu(menu_scroll, "🛒", "POS / Ventas", lambda: self.mostrar_frame("POS"))
        
        # === 2. ÓRDENES ===
        if rol in ['RECEPCIONISTA', 'ADMINISTRADOR', 'GERENTE', 'TECNICO']:
            ordenes_items = []
            
            if rol in ['TECNICO', 'ADMINISTRADOR', 'GERENTE']:
                ordenes_items.append(("🔧", "Taller", lambda: self.mostrar_frame("Workshop")))
            
            if rol in ['RECEPCIONISTA', 'ADMINISTRADOR', 'GERENTE']:
                ordenes_items.append(("📝", "Recepción", lambda: self.mostrar_frame("Reception")))
            
            if ordenes_items:
                crear_seccion_colapsable("📋", "Órdenes", ordenes_items)
        
        # === 3. HISTORIAL ===
        if rol in ['ADMINISTRADOR', 'GERENTE', 'TECNICO', 'RECEPCIONISTA']:
            crear_botón_menu(menu_scroll, "📜", "Historial", lambda: self.mostrar_frame("History"))
        
        # === 4. INVENTARIOS Y COMPRAS ===
        if rol in ['ADMINISTRADOR', 'GERENTE']:
            inventario_items = [
                ("📦", "Productos", lambda: self.mostrar_frame("Inventory")),
                ("🔧", "Repuestos (Taller)", lambda: self.mostrar_frame("Inventory")),
                ("💼", "Servicios (Mano de obra)", lambda: self.mostrar_frame("Inventory")),
                ("🏢", "Proveedores", lambda: self.mostrar_frame("Providers")),
                ("📋", "Pedidos", lambda: self.mostrar_frame("Pedidos"))
            ]
            crear_seccion_colapsable("📦", "Inventarios\ny Compras", inventario_items)
        
        # === 5. ADMINISTRACIÓN ===
        if rol in ['GERENTE', 'ADMINISTRADOR']:
            admin_items = [
                ("👥", "Usuarios", lambda: self.mostrar_frame("Admin")),
                ("⚙️", "Configuración", lambda: self.mostrar_frame("CompanySettings")),
                ("🔄", "Actualizaciones", lambda: self.mostrar_frame("Updater"))
            ]
            crear_seccion_colapsable("⚙️", "Administración", admin_items)
        
        # Espaciador
        ctk.CTkFrame(menu_scroll, fg_color="transparent", height=20).pack()
        
        # Separador inferior
        ctk.CTkFrame(self.sidebar, height=1, fg_color=Theme.DIVIDER).pack(fill="x", padx=20, pady=10)
        
        # Botón logout con estilo especial
        logout_btn = ctk.CTkButton(
            self.sidebar,
            text="🚪  Cerrar Sesión",
            command=self.cerrar_sesión,
            fg_color=Theme.SURFACE,
            hover_color=Theme.ERROR,
            text_color=Theme.ERROR_DARK,
            corner_radius=Theme.RADIUS_LARGE,
            border_width=2,
            border_color=Theme.ERROR,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
            anchor="w",
            height=45
        )
        logout_btn.pack(pady=8, padx=15, fill="x")

        # Área principal
        self.main_frame = ctk.CTkFrame(self, fg_color=Theme.BACKGROUND, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        
        self.frames["Dashboard"] = DashboardFrame(self.main_frame, self.gestor_lógica, self.usuario_actual)
        self.frames["Reception"] = ReceptionFrame(self.main_frame, self.gestor_lógica, self.usuario_actual)
        self.frames["Workshop"] = WorkshopFrame(self.main_frame, self.gestor_lógica, self.usuario_actual, self)
        self.frames["Admin"] = AdminFrame(self.main_frame, self.gestor_lógica, self.usuario_actual)
        self.frames["History"] = HistoryFrame(self.main_frame, self.gestor_lógica, self.usuario_actual, self)
        self.frames["Reports"] = ReportsFrame(self.main_frame, self.gestor_lógica, self.usuario_actual)
        self.frames["Cash"] = CashFrame(self.main_frame, self.gestor_lógica, self.usuario_actual)
        self.frames["POS"] = POSFrame(self.main_frame, self.gestor_lógica, self.usuario_actual)
        self.frames["Inventory"] = InventoryFrame(self.main_frame, self.gestor_lógica, self.usuario_actual)
        self.frames["Providers"] = ProvidersUI(self.main_frame, self.gestor_lógica)
        self.frames["Pedidos"] = PedidosFrame(self.main_frame, self.gestor_lógica, self.usuario_actual)  # 🆕 Sistema de pedidos
        self.frames["CompanySettings"] = CompanySettingsFrame(self.main_frame, self.gestor_lógica, self.usuario_actual)
        self.frames["Updater"] = UpdaterFrame(self.main_frame, self.gestor_lógica, self.usuario_actual)
        
        inicio = "Reception"
        if rol == 'TECNICO': inicio = "Workshop"
        elif rol == 'GERENTE': inicio = "Dashboard"
        self.mostrar_frame(inicio)

    def mostrar_frame(self, nombre, datos=None, filtro=None):
        for frame in self.frames.values(): frame.pack_forget()
        if nombre in self.frames:
            f = self.frames[nombre]
            
            # Si hay filtro y el frame lo soporta, aplicarlo antes de cargar
            if filtro is not None and hasattr(f, "set_filtro"):
                try:
                    f.set_filtro(filtro)
                except:
                    pass
            
            for método in ["load_orders", "refresh_chart", "load_users", "load_data", "refresh_state", "load_products", "load_parts", "load_services", "load_providers", "refresh"]:
                if hasattr(f, método): 
                    try:
                        getattr(f, método)()
                    except:
                        pass
            
            if hasattr(f, "refresh"):
                try:
                    f.refresh()
                except:
                    pass
            
            if datos is not None and hasattr(f, "focus_on_order"):
                try:
                    f.focus_on_order(datos)
                except:
                    pass
            f.pack(fill="both", expand=True)
    
    def refresh_all_frames(self):
        """Actualizar todos los frames con datos frescos de la base de datos"""
        for frame_name, frame in self.frames.items():
            # Ejecutar métodos de actualización en cada frame
            for método in ["load_orders", "refresh_chart", "load_users", "load_data", "refresh_state", "load_products", "load_parts", "load_services", "load_providers", "refresh"]:
                if hasattr(frame, método):
                    try:
                        getattr(frame, método)()
                    except Exception as e:
                        # Silenciar errores para no interrumpir otras actualizaciones
                        pass

    def cerrar_sesión(self):
        self.usuario_actual = None
        self.mostrar_login()
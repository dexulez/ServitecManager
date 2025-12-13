"""
Sistema de temas visuales para ServitecManager
Inspirado en Apple Human Interface y Material Design 3
Paleta pastel profesional con sombras suaves
"""

class Theme:
    """Tema visual moderno tipo Apple/Google"""
    
    # Colores principales - Paleta Pastel Profesional
    PRIMARY = "#6B9BD1"  # Azul cielo suave
    PRIMARY_LIGHT = "#A8C9E8"  # Azul muy claro
    PRIMARY_DARK = "#4A7BA7"  # Azul profundo suave
    
    SECONDARY = "#C492B1"  # Lila/Rosa polvo
    SECONDARY_LIGHT = "#E5D0DD"
    
    ACCENT = "#E8B384"  # Melocotón suave
    ACCENT_LIGHT = "#F5D9BF"
    
    SUCCESS = "#90C695"  # Verde menta
    SUCCESS_DARK = "#6FA876"
    
    WARNING = "#F5D586"  # Amarillo mantequilla
    WARNING_DARK = "#E5B84D"
    
    ERROR = "#E59999"  # Coral suave
    ERROR_DARK = "#D16B6B"
    
    INFO = "#A6C1CC"  # Azul grisáceo
    
    # Neutrales - Escala de grises profesional
    WHITE = "#FFFFFF"
    BACKGROUND = "#F5F7FA"  # Gris claro principal (fondo app)
    BACKGROUND_LIGHT = "#FAFBFC"  # Casi blanco
    SURFACE = "#FFFFFF"  # Blanco puro para cards
    
    SIDEBAR_BG = "#FFFFFF"  # Sidebar blanco limpio
    SIDEBAR_HOVER = "#F0F4F8"  # Hover muy sutil
    SIDEBAR_ACTIVE = "#E8F0F7"  # Activo azul pastel muy tenue
    
    TEXT_PRIMARY = "#1A202C"  # Texto principal casi negro
    TEXT_SECONDARY = "#718096"  # Gris medio
    TEXT_LIGHT = "#A0AEC0"  # Gris claro
    TEXT_WHITE = "#FFFFFF"
    
    BORDER = "#E2E8F0"  # Bordes ultra suaves
    DIVIDER = "#EDF2F7"  # Divisores sutiles
    
    # Sombras ultra suaves (Soft Shadows)
    SHADOW_LIGHT = "0 1px 3px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.06)"
    SHADOW_MEDIUM = "0 4px 6px rgba(0, 0, 0, 0.05), 0 2px 4px rgba(0, 0, 0, 0.06)"
    SHADOW_HEAVY = "0 10px 15px rgba(0, 0, 0, 0.08), 0 4px 6px rgba(0, 0, 0, 0.05)"
    SHADOW_FLOAT = "0 20px 25px rgba(0, 0, 0, 0.08), 0 10px 10px rgba(0, 0, 0, 0.04)"  # Efecto flotante
    
    # Estados
    HOVER = "#F7FAFC"
    ACTIVE = "#EDF2F7"
    DISABLED = "#E2E8F0"
    
    # Específicos por módulo - Fondos ultra sutiles
    DASHBOARD_CARD_1 = "#EBF4FB"  # Azul glaciar
    DASHBOARD_CARD_2 = "#F9EFF5"  # Rosa polvo
    DASHBOARD_CARD_3 = "#FFF8F0"  # Melocotón claro
    DASHBOARD_CARD_4 = "#F0F9F4"  # Menta claro
    
    # Estados de órdenes - Colores pastel suaves
    STATUS_PENDING = "#FFD700"  # Amarillo dorado (fondo)
    STATUS_PENDING_TEXT = "#000000"  # Negro (texto)
    
    STATUS_IN_PROGRESS = "#4A90E2"  # Azul intenso (fondo)
    STATUS_IN_PROGRESS_TEXT = "#FFFFFF"  # Blanco (texto)
    
    STATUS_WAITING = "#FF8C00"  # Naranja oscuro (fondo)
    STATUS_WAITING_TEXT = "#FFFFFF"  # Blanco (texto)
    
    STATUS_REPAIRED = "#2ECC71"  # Verde intenso (fondo)
    STATUS_REPAIRED_TEXT = "#FFFFFF"  # Blanco (texto)
    
    STATUS_DELIVERED = "#5DADE2"  # Azul cielo intenso (fondo)
    STATUS_DELIVERED_TEXT = "#000000"  # Negro (texto)
    
    STATUS_NO_SOLUTION = "#E74C3C"  # Rojo intenso (fondo)
    STATUS_NO_SOLUTION_TEXT = "#FFFFFF"  # Blanco (texto)
    
    # Tipografía
    FONT_FAMILY = "Segoe UI"  # Fuente principal moderna
    FONT_SIZE_SMALL = 10
    FONT_SIZE_NORMAL = 12
    FONT_SIZE_MEDIUM = 14
    FONT_SIZE_LARGE = 16
    FONT_SIZE_XLARGE = 20
    FONT_SIZE_XXLARGE = 24
    FONT_SIZE_H1 = 24  # Títulos grandes
    FONT_SIZE_H2 = 18  # Subtítulos
    
    # Espaciado aumentado (más "aire")
    PADDING_SMALL = 12
    PADDING_MEDIUM = 20
    PADDING_LARGE = 28
    PADDING_XLARGE = 36
    
    # Bordes redondeados amplios (estilo moderno)
    RADIUS_SMALL = 8
    RADIUS_MEDIUM = 12
    RADIUS_LARGE = 16
    RADIUS_XLARGE = 20
    RADIUS_PILL = 24  # Para badges tipo píldora
    
    # Botones según función
    BTN_PRIMARY = PRIMARY
    BTN_PRIMARY_HOVER = PRIMARY_DARK
    BTN_SECONDARY = SECONDARY
    BTN_SUCCESS = SUCCESS_DARK
    BTN_WARNING = WARNING_DARK
    BTN_ERROR = ERROR_DARK
    BTN_INFO = INFO
    
    # Sidebar buttons - Tonos muy sutiles
    SIDEBAR_BTN_ACTIVE_BG = "#E8F0F7"  # Azul pastel ultra tenue
    SIDEBAR_BTN_HOVER_BG = "#F0F4F8"  # Gris muy claro
    
    @classmethod
    def get_status_color(cls, status):
        """Retorna el color de fondo según el estado de la orden (para badges)"""
        status_map = {
            "PENDIENTE": cls.STATUS_PENDING,
            "EN REPARACION": cls.STATUS_IN_PROGRESS,
            "ESPERA DE REPUESTO": cls.STATUS_WAITING,
            "REPARADO": cls.STATUS_REPAIRED,
            "ENTREGADO": cls.STATUS_DELIVERED,
        }
        return status_map.get(status, cls.INFO)
    
    @classmethod
    def get_status_text_color(cls, status):
        """Retorna el color de texto según el estado de la orden (para badges)"""
        if not status:
            return cls.WHITE
        status_map = {
            "PENDIENTE": cls.STATUS_PENDING_TEXT,
            "EN REPARACION": cls.STATUS_IN_PROGRESS_TEXT,
            "ESPERA DE REPUESTO": cls.STATUS_WAITING_TEXT,
            "REPARADO": cls.STATUS_REPAIRED_TEXT,
            "ENTREGADO": cls.STATUS_DELIVERED_TEXT,
        }
        return status_map.get(status.upper(), cls.WHITE)
    
    @classmethod
    def get_button_style(cls, style_type="primary"):
        """Retorna configuración de estilo para botones"""
        styles = {
            "primary": {
                "fg_color": cls.BTN_PRIMARY,
                "hover_color": cls.BTN_PRIMARY_HOVER,
                "text_color": cls.TEXT_WHITE,
                "corner_radius": cls.RADIUS_MEDIUM,
                "border_width": 0,
                "font": (cls.FONT_FAMILY, cls.FONT_SIZE_NORMAL, "bold")
            },
            "secondary": {
                "fg_color": cls.BTN_SECONDARY,
                "hover_color": cls.SECONDARY,
                "text_color": cls.TEXT_WHITE,
                "corner_radius": cls.RADIUS_MEDIUM,
                "border_width": 0,
                "font": (cls.FONT_FAMILY, cls.FONT_SIZE_NORMAL, "bold")
            },
            "success": {
                "fg_color": cls.BTN_SUCCESS,
                "hover_color": cls.SUCCESS_DARK,
                "text_color": cls.WHITE,
                "corner_radius": cls.RADIUS_MEDIUM,
                "border_width": 0,
                "font": (cls.FONT_FAMILY, cls.FONT_SIZE_NORMAL, "bold")
            },
            "warning": {
                "fg_color": cls.BTN_WARNING,
                "hover_color": cls.WARNING_DARK,
                "text_color": cls.TEXT_PRIMARY,
                "corner_radius": cls.RADIUS_MEDIUM,
                "border_width": 0,
                "font": (cls.FONT_FAMILY, cls.FONT_SIZE_NORMAL, "bold")
            },
            "error": {
                "fg_color": cls.BTN_ERROR,
                "hover_color": cls.ERROR_DARK,
                "text_color": cls.TEXT_WHITE,
                "corner_radius": cls.RADIUS_MEDIUM,
                "border_width": 0,
                "font": (cls.FONT_FAMILY, cls.FONT_SIZE_NORMAL, "bold")
            },
            "ghost": {
                "fg_color": "transparent",
                "hover_color": cls.HOVER,
                "text_color": cls.TEXT_PRIMARY,
                "corner_radius": cls.RADIUS_MEDIUM,
                "border_width": 1,
                "border_color": cls.BORDER,
                "font": (cls.FONT_FAMILY, cls.FONT_SIZE_NORMAL)
            }
        }
        return styles.get(style_type, styles["primary"])
    
    @classmethod
    def get_card_style(cls):
        """Retorna configuración de estilo para tarjetas con sombras suaves"""
        return {
            "fg_color": cls.SURFACE,
            "corner_radius": cls.RADIUS_LARGE,
            "border_width": 0,  # Sin bordes, solo sombra
            "border_color": cls.BORDER
        }
    
    @classmethod
    def get_sidebar_button_style(cls, is_active=False):
        """Retorna configuración minimalista para botones del sidebar
        
        Args:
            is_active: Si el botón representa la página activa
        """
        if is_active:
            return {
                "fg_color": cls.SIDEBAR_BTN_ACTIVE_BG,
                "hover_color": cls.SIDEBAR_BTN_ACTIVE_BG,
                "text_color": cls.PRIMARY_DARK,
                "corner_radius": cls.RADIUS_MEDIUM,
                "border_width": 0,
                "font": (cls.FONT_FAMILY, cls.FONT_SIZE_NORMAL, "bold"),
                "anchor": "w"
            }
        else:
            return {
                "fg_color": "transparent",
                "hover_color": cls.SIDEBAR_BTN_HOVER_BG,
                "text_color": cls.TEXT_SECONDARY,
                "corner_radius": cls.RADIUS_MEDIUM,
                "border_width": 0,
                "font": (cls.FONT_FAMILY, cls.FONT_SIZE_NORMAL),
                "anchor": "w"
            }
    
    @classmethod
    def get_badge_style(cls, status):
        """Retorna configuración de estilo para badges tipo píldora
        
        Args:
            status: Estado de la orden (PENDIENTE, EN REPARACION, etc.)
        
        Returns:
            dict: Configuración de fg_color y text_color para el badge
        """
        return {
            "fg_color": cls.get_status_color(status),
            "text_color": cls.get_status_text_color(status),
            "corner_radius": cls.RADIUS_PILL,
            "font": (cls.FONT_FAMILY, cls.FONT_SIZE_SMALL, "bold")
        }

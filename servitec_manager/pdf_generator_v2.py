from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5, landscape
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from PIL import Image
import os
import textwrap
from datetime import datetime

class PDFGeneratorV2:
    """
    Generador de PDF profesional para Servitec Manager
    Diseño basado en la orden de ingreso moderna con separación de datos configurables
    Formato: A5 Horizontal (210mm x 148mm)
    """
    
    def __init__(self, logic):
        self.logic = logic
        self.reports_dir = "ordenes"
        
        # Colores corporativos (un poco más vivos)
        self.COLOR_PRIMARIO = HexColor('#0055cc')  # Azul Servitec más vivo
        self.COLOR_SECUNDARIO = HexColor('#e8f4ff')  # Azul muy claro para fondos
        self.COLOR_TEXTO = HexColor('#1a1a1a')  # Texto principal más intenso
        self.COLOR_TEXTO_CLARO = HexColor('#666666')  # Texto secundario más definido
        
        # Dimensiones página A5 Horizontal
        self.width = 210 * mm  # A5 horizontal
        self.height = 148 * mm
        self.margin = 10 * mm
        
        self._asegurar_directorio()
        self._cargar_config_empresa()
    
    def _asegurar_directorio(self):
        """Crear directorio de reportes si no existe"""
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)
    
    def _cargar_config_empresa(self):
        """Cargar configuración de empresa desde base de datos"""
        try:
            config = self.logic.bd.OBTENER_UNO("SELECT * FROM empresa_config LIMIT 1", ())
            
            if config:
                # config: 0:id, 1:nombre, 2:rut, 3:razon, 4:giro, 5:dir, 6:comuna, 7:region, 8:tel, 9:email, 10:web, 11:logo
                self.empresa_nombre = config[1] or "SERVITEC"
                self.empresa_rut = config[2] or ""
                self.empresa_razon_social = config[3] or ""
                self.empresa_giro = config[4] or ""
                self.empresa_direccion = config[5] or "Ignacio Riquelme 281, Mejillones, Antofagasta"
                self.empresa_comuna = config[6] or ""
                self.empresa_region = config[7] or ""
                self.empresa_telefono = config[8] or "+56 9 5100 7877"
                self.empresa_email = config[9] or ""
                self.empresa_web = config[10] or ""
                self.empresa_logo = config[11] or None
            else:
                # Valores por defecto
                self._configuracion_por_defecto()
        except Exception as e:
            print(f"Error al cargar configuración de empresa: {e}")
            self._configuracion_por_defecto()
    
    def _configuracion_por_defecto(self):
        """Configuración por defecto si no existe en BD"""
        self.empresa_nombre = "SERVITEC"
        self.empresa_rut = ""
        self.empresa_razon_social = ""
        self.empresa_giro = ""
        self.empresa_direccion = "Ignacio Riquelme 281, Mejillones, Antofagasta"
        self.empresa_comuna = ""
        self.empresa_region = ""
        self.empresa_telefono = "+56 9 5100 7877"
        self.empresa_email = ""
        self.empresa_web = ""
        self.empresa_logo = None
    
    def _formatear_dinero(self, valor):
        """Formatear valores monetarios"""
        try:
            return f"${int(valor):,}".replace(",", ".")
        except:
            return "$0"
    
    def _dibujar_caja_con_titulo(self, c, x, y, width, height, titulo):
        """Dibujar caja con título en barra azul y borde"""
        # Barra de título azul
        c.setFillColor(self.COLOR_PRIMARIO)
        c.roundRect(x, y, width, 8*mm, 4, fill=1, stroke=0)
        
        # Texto del título
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x + 5*mm, y + 2.5*mm, titulo)
        
        # Caja principal gris claro con borde
        c.setFillColor(self.COLOR_SECUNDARIO)
        c.setStrokeColor(self.COLOR_PRIMARIO)
        c.setLineWidth(0.5)
        c.roundRect(x, y - height + 8*mm, width, height - 8*mm, 4, fill=1, stroke=1)
        
        c.setFillColor(black)
        return y - 10*mm  # Retornar Y para empezar contenido
    
    def generar_orden_ingreso(self, orden_data):
        """
        Generar PDF de orden de ingreso profesional en formato A5 Horizontal
        
        orden_data: Tupla con datos de la orden
        0:id, 3:fecha, 4:tipo, 5:marca, 6:modelo, 7:serie, 8:obs, 10:accesorios, 
        11:riesgoso, 12:presupuesto, 13:abono, 14:rut_cli, 15:nom_cli, 16:tel_cli
        """
        
        # Nombre del archivo
        filename = f"orden_ingreso_{orden_data[0]}.pdf"
        filepath = os.path.join(self.reports_dir, filename)
        
        c = canvas.Canvas(filepath, pagesize=(self.width, self.height))
        
        # ==================== SECCIÓN 1: ENCABEZADO ====================
        y = self.height - self.margin
        
        # Logo (izquierda superior)
        logo_x = self.margin
        logo_y = y - 17*mm  # Bajado 4mm (era -13mm, ahora -17mm)
        logo_width = 35*mm
        logo_height = 20*mm
        
        # Intentar cargar logo
        logo_cargado = False
        if self.empresa_logo and os.path.exists(self.empresa_logo):
            try:
                c.drawImage(self.empresa_logo, logo_x, logo_y, width=logo_width, height=logo_height, 
                           preserveAspectRatio=True, mask='auto')
                logo_cargado = True
            except:
                pass
        
        if not logo_cargado:
            logo_default = os.path.join("assets", "servitec_logo.png")
            if os.path.exists(logo_default):
                try:
                    c.drawImage(logo_default, logo_x, logo_y, width=logo_width, height=logo_height,
                               preserveAspectRatio=True, mask='auto')
                    logo_cargado = True
                except:
                    pass
        
        # NOMBRE DE EMPRESA GRANDE Y EN NEGRITAS debajo del logo
        nombre_y = logo_y - 5*mm
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(self.COLOR_PRIMARIO)
        c.drawString(logo_x, nombre_y, self.empresa_nombre)
        
        # Teléfono debajo del nombre
        info_y = nombre_y - 4*mm
        c.setFont("Helvetica", 8)
        c.setFillColor(self.COLOR_TEXTO_CLARO)
        c.drawString(logo_x, info_y, f"TEL: {self.empresa_telefono}")
        
        # Dirección debajo del teléfono
        info_y -= 3.5*mm
        c.drawString(logo_x, info_y, self.empresa_direccion.upper())
        
        # ==================== SELLO EN LA PARTE SUPERIOR CENTRAL ====================
        sello_width = 41*mm  # 35mm + 6mm (3mm por cada lado)
        sello_height = 25*mm
        # Calcular posición central entre logo y título
        sello_x = (self.width - sello_width) / 2
        sello_y = y - 23*mm  # Bajado 4mm adicionales (era -19mm, ahora -23mm)
        
        # Dibujar borde del cuadro de sello
        c.setStrokeColor(HexColor('#CCCCCC'))
        c.setLineWidth(1)
        c.rect(sello_x, sello_y, sello_width, sello_height, fill=0, stroke=1)
        
        # Texto "SELLO" en marca de agua (diagonal)
        c.saveState()
        c.translate(sello_x + sello_width/2, sello_y + sello_height/2)
        c.rotate(45)
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(HexColor('#E0E0E0'))
        c.drawCentredString(0, 0, "SELLO")
        c.restoreState()
        
        # Título ORDEN DE INGRESO (derecha superior)
        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(self.COLOR_TEXTO)
        titulo_y = y - 9*mm  # Bajado 4mm (era -5mm, ahora -9mm)
        c.drawRightString(self.width - self.margin, titulo_y, "ORDEN DE INGRESO")
        
        c.setFont("Helvetica-Bold", 14)
        titulo_y -= 7*mm
        c.drawRightString(self.width - self.margin, titulo_y, f"N° {orden_data[0]}")
        
        # Fecha de recepción (etiqueta y valor en la misma línea)
        c.setFont("Helvetica", 8)
        c.setFillColor(self.COLOR_TEXTO_CLARO)
        titulo_y -= 4.5*mm
        fecha_recepcion = orden_data[3][:16] if len(orden_data[3]) > 16 else orden_data[3]
        c.drawRightString(self.width - self.margin, titulo_y, f"FECHA RECEPCIÓN: {fecha_recepcion}")
        
        # Fecha de entrega (etiqueta y valor en la misma línea)
        titulo_y -= 3.5*mm
        fecha_entrega_header = str(orden_data[14] or "Sin definir")[:10] if len(orden_data) > 14 and orden_data[14] else "Sin definir"
        c.drawRightString(self.width - self.margin, titulo_y, f"FECHA ENTREGA: {fecha_entrega_header}")
        
        # ==================== SECCIÓN 2: GRID DE INFORMACIÓN (2 COLUMNAS) ====================
        y = self.height - 49*mm  # Bajado 4mm (era -45mm, ahora -49mm)
        
        col_width = (self.width - 2*self.margin - 5*mm) / 2
        box_height = 25*mm
        
        # COLUMNA IZQUIERDA: DATOS DEL CLIENTE
        cliente_x = self.margin
        y_titulo_cliente = self._dibujar_caja_con_titulo(c, cliente_x, y, col_width, box_height, "DATOS DEL CLIENTE")
        
        # Empezar desde la parte superior de la caja de contenido (bajado 7mm total)
        y_contenido = y - 5.5*mm
        
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(self.COLOR_TEXTO)
        c.drawString(cliente_x + 3*mm, y_contenido, "CLIENTE:")
        c.setFont("Helvetica", 10)
        cliente_nombre = str(orden_data[17] or "").upper()[:30]
        c.drawString(cliente_x + 25*mm, y_contenido, cliente_nombre)
        
        y_contenido -= 3.35*mm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(cliente_x + 3*mm, y_contenido, "RUT:")
        c.setFont("Helvetica", 10)
        cliente_rut = str(orden_data[16] or "")
        c.drawString(cliente_x + 25*mm, y_contenido, cliente_rut)
        
        y_contenido -= 3.35*mm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(cliente_x + 3*mm, y_contenido, "TELÉFONO:")
        c.setFont("Helvetica", 10)
        cliente_tel = str(orden_data[18] or "")
        c.drawString(cliente_x + 25*mm, y_contenido, cliente_tel)
        
        # COLUMNA DERECHA: INFORMACIÓN DEL EQUIPO
        equipo_x = self.margin + col_width + 5*mm
        y_titulo_equipo = self._dibujar_caja_con_titulo(c, equipo_x, y, col_width, box_height, "INFORMACIÓN DEL EQUIPO")
        
        # Empezar desde la parte superior de la caja de contenido (bajado 7mm total)
        y_contenido = y - 5.5*mm
        
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(self.COLOR_TEXTO)
        c.drawString(equipo_x + 3*mm, y_contenido, "EQUIPO:")
        c.setFont("Helvetica", 10)
        equipo_tipo = str(orden_data[4] or "")
        equipo_marca = str(orden_data[5] or "")
        equipo_modelo = str(orden_data[6] or "")
        equipo_nombre = f"{equipo_tipo} {equipo_marca} {equipo_modelo}".upper()[:30]
        c.drawString(equipo_x + 25*mm, y_contenido, equipo_nombre)
        
        y_contenido -= 3.35*mm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(equipo_x + 3*mm, y_contenido, "SERIE/IMEI:")
        c.setFont("Helvetica", 10)
        equipo_serie = str(orden_data[7] or "")[:27]
        c.drawString(equipo_x + 25*mm, y_contenido, equipo_serie)
        
        y_contenido -= 3.35*mm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(equipo_x + 3*mm, y_contenido, "FECHA ENTREGA:")
        c.setFont("Helvetica", 10)
        # La fecha de entrega está después de descuento y abono (índice 15)
        fecha_entrega = str(orden_data[15] or "")[:10] if len(orden_data) > 15 and orden_data[15] else "Sin definir"
        c.drawString(equipo_x + 35*mm, y_contenido, fecha_entrega)
        
        # ==================== SECCIÓN 3: ESTADO Y ACCESORIOS ====================
        y -= 26*mm  # Subido 3mm (era -29mm, ahora -26mm)
        
        acc_height = 16*mm
        y_acc_titulo = self._dibujar_caja_con_titulo(c, self.margin, y, self.width - 2*self.margin, acc_height, "ESTADO Y ACCESORIOS")
        
        # Parsear accesorios (detectar variantes de texto)
        accesorios_str = str(orden_data[10] or "").upper()
        
        accesorios_check = {
            'BANDEJA SIM': 'BANDEJA' in accesorios_str and 'SIM' in accesorios_str,
            'SIM CARD': 'SIM CARD' in accesorios_str or 'SIMCARD' in accesorios_str,
            'CARGADOR': 'CARGADOR' in accesorios_str,
            'MICRO SD': 'MICRO SD' in accesorios_str or 'MICROSD' in accesorios_str,
            'MOJADO': 'MOJADO' in accesorios_str
        }
        
        # Dibujar checkboxes centrados verticalmente en una sola fila
        checkbox_y = y - 4.5*mm  # Centrado vertical ajustado para nueva altura
        checkbox_x = self.margin + 3*mm
        checkbox_spacing = 37*mm
        
        for idx, (label, checked) in enumerate(accesorios_check.items()):
            x_pos = checkbox_x + idx * checkbox_spacing
            
            # Dibujar checkbox
            c.setFillColor(white)
            c.setStrokeColor(self.COLOR_TEXTO)
            c.setLineWidth(1)
            c.rect(x_pos, checkbox_y, 3*mm, 3*mm, fill=1, stroke=1)
            
            # Si está marcado, dibujar checkmark
            if checked:
                c.setStrokeColor(self.COLOR_PRIMARIO)
                c.setLineWidth(1.5)
                c.line(x_pos + 0.5*mm, checkbox_y + 1.5*mm, x_pos + 1*mm, checkbox_y + 0.5*mm)
                c.line(x_pos + 1*mm, checkbox_y + 0.5*mm, x_pos + 2.5*mm, checkbox_y + 2.5*mm)
            
            # Label
            c.setFillColor(self.COLOR_TEXTO)
            c.setFont("Helvetica", 7)
            c.drawString(x_pos + 4*mm, checkbox_y + 0.8*mm, label)
        
        # ==================== SECCIÓN 4: FALLA REPORTADA ====================
        y -= 17*mm  # Subido 8mm (era -25mm, ahora -17mm)
        
        # Ancho de la caja de falla (resta el espacio del bloque financiero)
        falla_width = self.width - 2*self.margin - 50*mm
        falla_height = 24*mm
        y_falla_titulo = self._dibujar_caja_con_titulo(c, self.margin, y, falla_width, falla_height, "FALLA REPORTADA / SERVICIO")
        
        # Texto de falla (aumentar fuente de 8 a 9)
        c.setFont("Helvetica", 9)
        c.setFillColor(self.COLOR_TEXTO)
        falla_texto = str(orden_data[8] or "").upper()
        
        # Eliminar el prefijo "FALLA:" si existe
        if falla_texto.startswith("FALLA:"):
            falla_texto = falla_texto[6:].strip()
        
        # Envolver texto ajustado al ancho del cuadro
        max_width = 70  # Reducido para ajustarse al ancho real del cuadro
        lineas = textwrap.wrap(falla_texto, width=max_width) if falla_texto else []
        
        y_texto = y - 4*mm
        for linea in lineas[:4]:
            c.drawString(self.margin + 3*mm, y_texto, linea)
            y_texto -= 3.5*mm
        
        # ==================== SECCIÓN 5: BLOQUE FINANCIERO (CON BORDE) ====================
        financiero_x = self.width - self.margin - 48*mm
        financiero_y = y + 7*mm  # Bajado 2mm (era +9mm, ahora +7mm)
        financiero_width = 48*mm
        financiero_height = 32*mm
        
        # Dibujar BORDE de toda la caja financiera (incluye título)
        c.setStrokeColor(self.COLOR_TEXTO_CLARO)
        c.setLineWidth(1.5)
        c.rect(financiero_x, financiero_y - financiero_height + 8*mm, financiero_width, financiero_height - 8*mm, fill=0, stroke=1)
        
        # Calcular valores financieros
        total = orden_data[12]
        descuento = orden_data[13] if len(orden_data) > 13 else 0
        abono = orden_data[14] if len(orden_data) > 14 else 0
        
        # Calcular IVA (19%) y subtotal
        subtotal = total / 1.19  # Asumiendo que el total incluye IVA
        iva = total - subtotal
        saldo = total - abono
        
        # Dibujar valores DENTRO del borde (bajar texto 8mm total)
        y_fin = financiero_y - 4*mm
        
        # Subtotal
        c.setFont("Helvetica", 10)
        c.setFillColor(self.COLOR_TEXTO)
        c.drawString(financiero_x + 3*mm, y_fin, "SUBTOTAL:")
        c.drawRightString(financiero_x + financiero_width - 3*mm, y_fin, self._formatear_dinero(subtotal))
        
        # Descuento
        y_fin -= 3.3*mm
        c.drawString(financiero_x + 3*mm, y_fin, "DESCUENTO:")
        c.drawRightString(financiero_x + financiero_width - 3*mm, y_fin, self._formatear_dinero(descuento))
        
        # IVA
        y_fin -= 3.3*mm
        c.drawString(financiero_x + 3*mm, y_fin, "IVA (19%):")
        c.drawRightString(financiero_x + financiero_width - 3*mm, y_fin, self._formatear_dinero(iva))
        
        # Total
        y_fin -= 3.8*mm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(financiero_x + 3*mm, y_fin, "TOTAL:")
        c.drawRightString(financiero_x + financiero_width - 3*mm, y_fin, self._formatear_dinero(total))
        
        # Abono
        y_fin -= 3.3*mm
        c.setFont("Helvetica", 10)
        c.drawString(financiero_x + 3*mm, y_fin, "ABONO:")
        c.setFillColor(HexColor('#0066cc'))
        c.drawRightString(financiero_x + financiero_width - 3*mm, y_fin, self._formatear_dinero(abono))
        
        # Saldo (destacado en rojo si > 0, negro si está pagado)
        y_fin -= 3.8*mm
        c.setFont("Helvetica-Bold", 12)
        saldo_color = HexColor('#cc0000') if saldo > 0 else black
        c.setFillColor(saldo_color)
        c.drawString(financiero_x + 3*mm, y_fin, "SALDO:")
        c.drawRightString(financiero_x + financiero_width - 3*mm, y_fin, self._formatear_dinero(saldo))
        
        # ==================== ÁREA DE FIRMAS ====================
        y_firma = 17*mm
        
        # Línea firma cliente
        firma_width = 60*mm
        firma1_x = self.margin + 20*mm
        c.setLineWidth(1)
        c.setStrokeColor(black)
        c.setFillColor(black)
        c.line(firma1_x, y_firma, firma1_x + firma_width, y_firma)
        
        c.setFont("Helvetica", 8)
        c.drawCentredString(firma1_x + firma_width/2, y_firma - 4*mm, "FIRMA CLIENTE")
        
        # Línea firma Servitec
        firma2_x = self.width - self.margin - 12*mm - firma_width
        c.line(firma2_x, y_firma, firma2_x + firma_width, y_firma)
        c.drawCentredString(firma2_x + firma_width/2, y_firma - 4*mm, "FIRMA SERVITEC")
        
        # ==================== NOTA AL FINAL (DEBAJO DE FIRMAS) ====================
        y_nota = 8*mm
        
        c.setFont("Helvetica", 7)
        c.setFillColor(self.COLOR_TEXTO_CLARO)
        nota_texto = "Nota: Para firmar debe leer las condiciones que están al reverso del documento."
        c.drawCentredString(self.width / 2, y_nota, nota_texto)
        
        # Guardar PDF
        c.save()
        
        return filepath
    
    def abrir_pdf(self, filepath):
        """Abrir PDF generado con el visor predeterminado"""
        try:
            import platform
            import subprocess
            
            if platform.system() == 'Windows':
                os.startfile(filepath)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', filepath])
            else:  # Linux
                subprocess.run(['xdg-open', filepath])
        except Exception as e:
            print(f"No se pudo abrir el PDF automáticamente: {e}")

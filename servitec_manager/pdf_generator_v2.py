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
        
        orden_data: Tupla con datos de la orden desde query:
        SELECT o.*, c.cedula, c.nombre, c.telefono, c.email
        
        Índices de tabla ordenes (0-15):
        0:id, 1:cliente_id, 2:tecnico_id, 3:fecha, 4:equipo, 5:marca, 6:modelo, 
        7:serie, 8:observacion, 9:estado, 10:accesorios, 11:riesgoso, 
        12:presupuesto, 13:descuento, 14:abono, 15:fecha_entrega
        
        Índices de join con clientes (16-19):
        16:cedula, 17:nombre, 18:telefono, 19:email
        """
        
        try:
            # Nombre del archivo
            filename = f"orden_ingreso_{orden_data[0]}.pdf"
            filepath = os.path.join(self.reports_dir, filename)
            
            print(f"\n{'='*80}")
            print(f"[PDF GENERATOR] Generando PDF para orden #{orden_data[0]}")
            print(f"[PDF GENERATOR] Ruta: {filepath}")
            print(f"[PDF GENERATOR] Datos recibidos (longitud): {len(orden_data)}")
            print(f"[PDF GENERATOR] Índices 0-16 (ordenes - incluye condicion en [10]):")
            for i in range(min(17, len(orden_data))):
                print(f"  [{i}]: {orden_data[i]}")
            if len(orden_data) > 30:
                print(f"[PDF GENERATOR] Índices 30-33 (cliente desde JOIN):")
                for i in range(30, min(34, len(orden_data))):
                    print(f"  [{i}]: {orden_data[i]}")
            print(f"{'='*80}\n")
            
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
        
            # ==================== SECCIÓN 2: GRID DE INFORMACIÓN (2 COLUMNAS) ====================
            y = self.height - 49*mm  # Bajado 4mm (era -45mm, ahora -49mm)
        
            col_width = (self.width - 2*self.margin - 5*mm) / 2
            box_height = 25*mm
        
            # COLUMNA IZQUIERDA: DATOS DEL CLIENTE
            cliente_x = self.margin
            y_titulo_cliente = self._dibujar_caja_con_titulo(c, cliente_x, y, col_width, box_height, "DATOS DEL CLIENTE")
        
            # Empezar desde la parte superior de la caja de contenido (bajado 7mm total)
            y_contenido = y - 5.5*mm
        
            # Extraer datos del cliente (índices correctos del esquema de 34 columnas)
            cliente_cedula = str(orden_data[30] or "")  # cedula en [30]
            cliente_nombre = str(orden_data[31] or "").upper()[:30]  # nombre en [31]
            cliente_tel = str(orden_data[32] or "")  # telefono en [32]
            
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(self.COLOR_TEXTO)
            c.drawString(cliente_x + 3*mm, y_contenido, "CLIENTE:")
            c.setFont("Helvetica", 10)
            c.drawString(cliente_x + 25*mm, y_contenido, cliente_nombre)
        
            y_contenido -= 3.35*mm
            c.setFont("Helvetica-Bold", 10)
            c.drawString(cliente_x + 3*mm, y_contenido, "RUT:")
            c.setFont("Helvetica", 10)
            c.drawString(cliente_x + 25*mm, y_contenido, cliente_cedula)
        
            y_contenido -= 3.35*mm
            c.setFont("Helvetica-Bold", 10)
            c.drawString(cliente_x + 3*mm, y_contenido, "TELÉFONO:")
            c.setFont("Helvetica", 10)
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
            equipo_tipo = str(orden_data[5] or "")  # [5] = equipo
            equipo_marca = str(orden_data[6] or "")  # [6] = marca
            equipo_modelo = str(orden_data[7] or "")  # [7] = modelo
            equipo_nombre = f"{equipo_tipo} {equipo_marca} {equipo_modelo}".upper()[:45]
            c.drawString(equipo_x + 25*mm, y_contenido, equipo_nombre)
        
            y_contenido -= 3.35*mm
            c.setFont("Helvetica-Bold", 10)
            c.drawString(equipo_x + 3*mm, y_contenido, "SERIE/IMEI:")
            c.setFont("Helvetica", 10)
            equipo_serie = str(orden_data[8] or "")[:27]  # [8] = serie
            c.drawString(equipo_x + 25*mm, y_contenido, equipo_serie)
        
            y_contenido -= 3.35*mm
            c.setFont("Helvetica-Bold", 10)
            c.drawString(equipo_x + 3*mm, y_contenido, "FECHA ENTREGA:")
            c.setFont("Helvetica", 10)
            # La fecha de entrega está en índice 4
            fecha_entrega_str = str(orden_data[4] or "") if orden_data[4] else "Sin definir"
            # Si es fecha SQL (YYYY-MM-DD), formatear; si es timestamp, mostrar solo fecha
            if fecha_entrega_str and fecha_entrega_str != "Sin definir":
                fecha_entrega = fecha_entrega_str[:10]
            else:
                fecha_entrega = "Sin definir"
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
            falla_texto = str(orden_data[9] or "").upper()  # [9] = observacion
            
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
            
            # Calcular valores financieros - conversión segura con índices correctos del esquema
            def to_float_safe(value):
                try:
                    return float(value or 0)
                except (ValueError, TypeError):
                    return 0
            
            # Índices correctos según esquema de 34 columnas:
            # [14]=presupuesto_inicial, [18]=descuento, [19]=total_a_cobrar, [20]=abono
            presupuesto_inicial = to_float_safe(orden_data[14])
            descuento = to_float_safe(orden_data[18])
            total_a_cobrar = to_float_safe(orden_data[19])
            abono = to_float_safe(orden_data[20])
            
            # Si total_a_cobrar es 0, calcularlo a partir del presupuesto
            if total_a_cobrar == 0:
                total_a_cobrar = presupuesto_inicial - descuento
            
            # Calcular subtotal e IVA
            subtotal = total_a_cobrar / 1.19  # Sin IVA
            iva = total_a_cobrar - subtotal
            saldo = abs(total_a_cobrar - abono)  # Valor absoluto para evitar negativos
            print(f"  TOTAL A COBRAR: ${total_a_cobrar:,.2f}")
            print(f"  SALDO: ${saldo:,.2f}")
        
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
            c.drawRightString(financiero_x + financiero_width - 3*mm, y_fin, self._formatear_dinero(total_a_cobrar))
        
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
            
            print(f"[PDF GENERATOR] ✅ PDF generado exitosamente: {filepath}")
            print(f"{'='*80}\n")
            
            return filepath
            
        except Exception as e:
            print(f"\n[PDF GENERATOR] ❌ ERROR al generar PDF:")
            print(f"[PDF GENERATOR] Error: {e}")
            import traceback
            traceback.print_exc()
            print(f"{'='*80}\n")
            return None
    
    def abrir_pdf(self, filepath):
        """Abrir PDF generado con el visor predeterminado"""
        try:
            import platform
            import subprocess
            
            print(f"\n[PDF VIEWER] Intentando abrir PDF...")
            print(f"[PDF VIEWER] Ruta: {filepath}")
            
            # Verificar que el archivo existe
            if not os.path.exists(filepath):
                print(f"[PDF VIEWER] ❌ ERROR: El archivo no existe")
                return False
            
            # Obtener ruta absoluta
            filepath = os.path.abspath(filepath)
            file_size = os.path.getsize(filepath)
            print(f"[PDF VIEWER] Archivo encontrado, tamaño: {file_size} bytes")
            print(f"[PDF VIEWER] Sistema operativo: {platform.system()}")
            
            if platform.system() == 'Windows':
                print(f"[PDF VIEWER] Ejecutando: os.startfile()")
                os.startfile(filepath)
            elif platform.system() == 'Darwin':  # macOS
                print(f"[PDF VIEWER] Ejecutando: open")
                subprocess.run(['open', filepath])
            else:  # Linux
                print(f"[PDF VIEWER] Ejecutando: xdg-open")
                subprocess.run(['xdg-open', filepath])
            
            print(f"[PDF VIEWER] ✅ PDF abierto exitosamente\n")
            return True
        except Exception as e:
            print(f"[PDF VIEWER] ❌ ERROR al abrir el PDF:")
            print(f"[PDF VIEWER] Error: {e}")
            import traceback
            traceback.print_exc()
            print()
            return False

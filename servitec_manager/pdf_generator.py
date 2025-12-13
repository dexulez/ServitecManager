from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import os
import platform
import subprocess
import textwrap

class GENERADOR_PDF:
    def __init__(self, filename="ticket_temp.pdf"):
        self.filename = filename
        # TAMAÑO MEDIA CARTA (Statement): 140mm x 216mm
        self.width = 140 * mm
        self.height = 216 * mm
        self.logo_path = "logo.png" # Asegúrate que este archivo esté en la carpeta
        self.reports_dir = "reports"
        self.ASEGURAR_DIRECTORIO_REPORTES()

    def ASEGURAR_DIRECTORIO_REPORTES(self):
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)

    def OBTENER_RUTA_REPORTE_DIARIO(self, filename):
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        daily_dir = os.path.join(self.reports_dir, today)
        if not os.path.exists(daily_dir):
            os.makedirs(daily_dir)
        return os.path.join(daily_dir, filename)

    def FORMATEAR_DINERO(self, val):
        try: return f"${int(val):,}".replace(",", ".")
        except: return "$0"

    def DIBUJAR_TEXTO(self, c, x, y, text, size=8, font="Helvetica", bold=False, align="left"):
        if bold: font = "Helvetica-Bold"
        c.setFont(font, size)
        text = str(text).upper()
        if align == "right":
            c.drawRightString(x, y, text)
        elif align == "center":
            c.drawCentredString(x, y, text)
        else:
            c.drawString(x, y, text)

    def DIBUJAR_CHECKBOX(self, c, x, y, label, checked=False):
        # Dibuja un cuadrito y si está marcado pone una X
        c.rect(x, y, 3*mm, 3*mm, fill=0)
        if checked:
            c.line(x, y, x+3*mm, y+3*mm)
            c.line(x, y+3*mm, x+3*mm, y)
        self.DIBUJAR_TEXTO(c, x + 5*mm, y, label, size=7)
    
    def _draw_section_box(self, c, x, y, width, title):
        """Dibuja caja de sección con encabezado gris (estilo HTML)"""
        # Encabezado gris
        c.setFillColorRGB(0.933, 0.933, 0.933)
        c.rect(x, y - 7*mm, width, 7*mm, fill=1, stroke=0)
        
        # Borde de la sección
        c.setStrokeColorRGB(0.2, 0.2, 0.2)
        c.setLineWidth(0.5)
        c.rect(x, y - 7*mm, width, 7*mm, fill=0, stroke=1)
        
        # Título
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(x + 3*mm, y - 4.5*mm, title.upper())
    
    def _draw_data_row(self, c, x, y, width, label, value, bold=False):
        """Dibuja una fila de datos (estilo HTML)"""
        c.setFillColorRGB(1, 1, 1)  # Fondo blanco por defecto
        
        font = "Helvetica-Bold" if bold else "Helvetica"
        c.setFont(font, 9)
        
        # Etiqueta (izquierda)
        c.drawString(x + 3*mm, y - 4*mm, label)
        
        # Valor (derecha)
        c.drawRightString(x + width - 3*mm, y - 4*mm, str(value))
        
        # Línea separadora suave
        c.setStrokeColorRGB(0.867, 0.867, 0.867)
        c.setLineWidth(0.3)
        c.line(x, y - 7*mm, x + width, y - 7*mm)
        
        return y - 7*mm

    def GENERAR_TICKET_INGRESO(self, data):
        """
        Data esperada (Tupla de BD):
        0:id, 3:fecha, 4:tipo, 5:marca, 6:modelo, 7:serie, 8:obs, 10:accesorios, 11:riesgoso, 12:presupuesto, 13:abono
        14:rut_cli, 15:nom_cli, 16:tel_cli, 17:mail_cli
        """
        # Usar nombre de archivo basado en ID si es ticket_temp
        if self.filename == "ticket_temp.pdf":
            self.filename = f"ticket_orden_{data[0]}.pdf"
            
        full_path = self.OBTENER_RUTA_REPORTE_DIARIO(self.filename)
        c = canvas.Canvas(full_path, pagesize=(self.width, self.height))
        margin = 8 * mm
        
        # --- 1. ENCABEZADO (LOGO Y DATOS EMPRESA) ---
        y = self.height - 10*mm
        
        # Intentar dibujar Logo
        if os.path.exists(self.logo_path):
            try:
                # Ajustamos logo a 30mm de ancho aprox
                c.drawImage(self.logo_path, margin, y - 15*mm, width=35*mm, height=15*mm, mask='auto', preserveAspectRatio=True)
            except: pass
        else:
            # Si no hay logo, ponemos texto
            self.DIBUJAR_TEXTO(c, margin, y - 5*mm, "SERVITEC", size=18, bold=True)

        # Datos de la Empresa (Derecha) - Extraídos del PDF de Samii
        c.setFillColorRGB(0.2, 0.2, 0.2) # Gris oscuro
        self.DIBUJAR_TEXTO(c, self.width - margin, y, "IGNACIO RIQUELME 281", size=7, align="right")
        y -= 3.5*mm
        self.DIBUJAR_TEXTO(c, self.width - margin, y, "MEJILLONES, ANTOFAGASTA", size=7, align="right")
        y -= 3.5*mm
        self.DIBUJAR_TEXTO(c, self.width - margin, y, "TEL: +56 9 5100 7877", size=7, align="right")
        c.setFillColorRGB(0, 0, 0) # Volver a negro

        # Título del Documento
        y -= 10*mm
        c.setLineWidth(1)
        c.line(margin, y, self.width - margin, y)
        y -= 5*mm
        self.DIBUJAR_TEXTO(c, margin, y, "ORDEN DE INGRESO", size=12, bold=True)
        self.DIBUJAR_TEXTO(c, self.width - margin, y, f"N° {data[0]}", size=12, bold=True, align="right")
        y -= 4*mm
        self.DIBUJAR_TEXTO(c, self.width - margin, y, f"FECHA: {data[3][:16]}", size=8, align="right")

        # --- 2. DATOS DEL CLIENTE ---
        y -= 8*mm
        # Fondo gris suave para título
        c.setFillColorRGB(0.9, 0.9, 0.9)
        c.rect(margin, y-1*mm, self.width-(2*margin), 5*mm, fill=1, stroke=0)
        c.setFillColorRGB(0, 0, 0)
        self.DIBUJAR_TEXTO(c, margin + 2*mm, y, "DATOS DEL CLIENTE", size=9, bold=True)
        
        y -= 5*mm
        self.DIBUJAR_TEXTO(c, margin, y, f"CLIENTE: {data[15]}", bold=True)
        y -= 4.5*mm
        self.DIBUJAR_TEXTO(c, margin, y, f"RUT: {data[14]}")
        self.DIBUJAR_TEXTO(c, margin + 60*mm, y, f"TELÉFONO: {data[16]}")
        
        # --- 3. DATOS DEL EQUIPO ---
        y -= 8*mm
        c.setFillColorRGB(0.9, 0.9, 0.9)
        c.rect(margin, y-1*mm, self.width-(2*margin), 5*mm, fill=1, stroke=0)
        c.setFillColorRGB(0, 0, 0)
        self.DIBUJAR_TEXTO(c, margin + 2*mm, y, "INFORMACIÓN DEL EQUIPO", size=9, bold=True)
        
        y -= 5*mm
        self.DIBUJAR_TEXTO(c, margin, y, f"EQUIPO: {data[4]} {data[5]} {data[6]}", size=10, bold=True)
        y -= 4.5*mm
        self.DIBUJAR_TEXTO(c, margin, y, f"SERIE / IMEI: {data[7]}")
        
        # CHECKBOXES (Estado visual)
        y -= 8*mm
        acc_str = data[10] if data[10] else ""
        
        # Fila 1
        self.DIBUJAR_CHECKBOX(c, margin, y, "BANDEJA SIM", checked="BANDEJA SIM" in acc_str)
        self.DIBUJAR_CHECKBOX(c, margin + 35*mm, y, "SIM CARD", checked="SIM CARD" in acc_str)
        self.DIBUJAR_CHECKBOX(c, margin + 70*mm, y, "MICRO SD", checked="MICRO SD" in acc_str)
        
        # Fila 2
        y -= 5*mm
        self.DIBUJAR_CHECKBOX(c, margin, y, "CARGADOR", checked="CARGADOR" in acc_str)
        self.DIBUJAR_CHECKBOX(c, margin + 35*mm, y, "MOJADO", checked="MOJADO" in acc_str)
        
        # Riesgoso (Destacado)
        if data[11] == 1:
            c.setFont("Helvetica-Bold", 9)
            c.drawString(margin + 70*mm, y, "!!! EQUIPO RIESGOSO !!!")

        # --- 4. SERVICIO Y FALLA ---
        y -= 10*mm  # Aumentado de 8mm a 10mm para más espacio
        c.line(margin, y+2*mm, self.width-margin, y+2*mm)
        y -= 1.5*mm  # Espacio adicional entre la línea y el texto
        self.DIBUJAR_TEXTO(c, margin, y, "FALLA REPORTADA / SERVICIO:", bold=True)
        y -= 4*mm
        
        # Texto envuelto
        obs = data[8]
        text_obj = c.beginText(margin, y)
        text_obj.setFont("Helvetica", 8)
        lines = textwrap.wrap(obs.upper(), width=75)
        for line in lines:
            text_obj.textLine(line)
            y -= 3.5*mm
        c.drawText(text_obj)

        # --- 5. TOTALES (Cuadro estilo factura) ---
        y -= 5*mm # Espacio extra
        
        # Caja de fondo para totales
        box_height = 18*mm
        c.setLineWidth(1)
        c.rect(self.width - margin - 50*mm, y - box_height, 50*mm, box_height)
        
        # Textos dentro de la caja
        c.setFont("Helvetica", 9)
        
        total = data[12]
        abono = data[13]
        pendiente = total - abono
        
        yt = y - 5*mm
        c.drawString(self.width - margin - 48*mm, yt, "TOTAL:")
        c.drawRightString(self.width - margin - 2*mm, yt, self.FORMATEAR_DINERO(total))
        
        yt -= 5*mm
        c.drawString(self.width - margin - 48*mm, yt, "ABONO:")
        c.drawRightString(self.width - margin - 2*mm, yt, self.FORMATEAR_DINERO(abono))
        
        yt -= 6*mm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(self.width - margin - 48*mm, yt, "SALDO:")
        c.drawRightString(self.width - margin - 2*mm, yt, self.FORMATEAR_DINERO(pendiente))

        # --- 6. CONDICIONES (Letra chica legal) ---
        # Fijamos la posición Y para que siempre esté abajo, antes de las firmas
        y_legal = 55*mm 
        
        c.setFont("Helvetica", 5)
        condiciones = [
            "CONDICIONES DE SERVICIO (RESUMEN):",
            "1. EL CLIENTE ASUME LA PROPIEDAD DEL EQUIPO Y EXIME DE RESPONSABILIDAD LEGAL A SERVITEC.",
            "2. SERVITEC NO SE RESPONSABILIZA POR PÉRDIDA DE DATOS. SE SUGIERE RESPALDO.",
            "3. EQUIPOS MOJADOS, RIESGOSOS O CON PANTALLA APAGADA PUEDEN SUFRIR DAÑO TOTAL EN REVISIÓN.",
            "4. PANTALLAS Y TÁCTILES NO TIENEN GARANTÍA POR FRACTURAS POSTERIORES.",
            "5. RETIRO DE EQUIPOS: MÁXIMO 60 DÍAS. LUEGO SE CONSIDERA ABANDONO LEGAL (LEY 19.496).",
            "6. AL FIRMAR, EL CLIENTE ACEPTA ESTAS CONDICIONES Y EL PRESUPUESTO INDICADO."
        ]
        
        for cond in condiciones:
            c.drawString(margin, y_legal, cond)
            y_legal -= 2.2*mm

        # --- 7. FIRMAS ---
        y_firma = 15*mm
        
        # Línea Cliente
        c.line(margin + 5*mm, y_firma, margin + 50*mm, y_firma)
        self.DIBUJAR_TEXTO(c, margin + 27.5*mm, y_firma - 3*mm, "FIRMA CLIENTE", size=7, align="center")
        
        # Línea Servitec
        c.line(self.width - margin - 50*mm, y_firma, self.width - margin - 5*mm, y_firma)
        self.DIBUJAR_TEXTO(c, self.width - margin - 27.5*mm, y_firma - 3*mm, "FIRMA SERVITEC", size=7, align="center")

        c.save()
        self.ABRIR_PDF()

    def GENERAR_REPORTE_COMISIONES(self, filename, tech_name, date_range, data):
        # A5 Horizontal: 210mm ancho x 148mm alto
        width, height = 210 * mm, 148 * mm
        full_path = self.OBTENER_RUTA_REPORTE_DIARIO(filename)
        c = canvas.Canvas(full_path, pagesize=(width, height))
        margin = 10 * mm
        
        # --- ENCABEZADO ---
        y = height - 15 * mm
        if os.path.exists(self.logo_path):
            try: c.drawImage(self.logo_path, margin, y - 5*mm, width=30*mm, height=12*mm, mask='auto', preserveAspectRatio=True)
            except: pass
        else:
            self.DIBUJAR_TEXTO(c, margin, y, "SERVITEC", size=14, bold=True)
            
        self.DIBUJAR_TEXTO(c, width - margin, y, "REPORTE DE COMISIONES", size=12, bold=True, align="right")
        y -= 5 * mm
        self.DIBUJAR_TEXTO(c, width - margin, y, f"TÉCNICO: {tech_name}", size=9, align="right")
        y -= 4 * mm
        self.DIBUJAR_TEXTO(c, width - margin, y, f"PERIODO: {date_range}", size=9, align="right")
        
        # --- TABLA ---
        y -= 10 * mm
        headers = ["FECHA", "EQUIPO", "TOTAL", "REP/ENV", "C.BANCO", "IVA", "COMISIÓN"]
        x_positions = [margin, margin+25*mm, margin+80*mm, margin+105*mm, margin+130*mm, margin+155*mm, margin+175*mm]
        
        # Dibujar Encabezados
        c.setFillColorRGB(0.9, 0.9, 0.9)
        c.rect(margin, y-1*mm, width-2*margin, 5*mm, fill=1, stroke=0)
        c.setFillColorRGB(0, 0, 0)
        
        for i, h in enumerate(headers):
            self.DIBUJAR_TEXTO(c, x_positions[i], y, h, size=7, bold=True)
            
        y -= 5 * mm
        
        # Calcular totales para mostrar en PDF
        sum_total = 0; sum_costos = 0; sum_banco = 0; sum_iva = 0; sum_comision = 0

        for row in data:
            if y < 15 * mm: # Nueva página si se acaba el espacio
                c.showPage()
                y = height - 15 * mm
            
            # Datos
            fecha = row[3].split(" ")[0]
            equipo = f"{row[1]} {row[2]}"[:25] # Truncar nombre largo
            total = row[4]
            costos = row[5] + row[10]
            comision = row[6]
            
            m_tarjeta = (row[7] or 0) + (row[8] or 0)
            com_banco = m_tarjeta * 0.0295
            util_op = (total - com_banco - costos)
            m_iva = util_op * 0.19 if row[9] else 0
            
            sum_total += total
            sum_costos += costos
            sum_banco += com_banco
            sum_iva += m_iva
            sum_comision += comision
            
            vals = [
                fecha,
                equipo,
                self.FORMATEAR_DINERO(total),
                self.FORMATEAR_DINERO(costos),
                self.FORMATEAR_DINERO(com_banco),
                self.FORMATEAR_DINERO(m_iva),
                self.FORMATEAR_DINERO(comision)
            ]
            
            for i, v in enumerate(vals):
                self.DIBUJAR_TEXTO(c, x_positions[i], y, v, size=7)
                
            y -= 4 * mm
            
        # --- TOTAL FINAL ---
        y -= 5 * mm
        c.line(margin, y+2*mm, width-margin, y+2*mm)
        
        self.DIBUJAR_TEXTO(c, margin+25*mm, y, "TOTALES:", size=8, bold=True, align="right")
        self.DIBUJAR_TEXTO(c, margin+80*mm, y, self.FORMATEAR_DINERO(sum_total), size=7, bold=True)
        self.DIBUJAR_TEXTO(c, margin+105*mm, y, self.FORMATEAR_DINERO(sum_costos), size=7, bold=True)
        self.DIBUJAR_TEXTO(c, margin+130*mm, y, self.FORMATEAR_DINERO(sum_banco), size=7, bold=True)
        self.DIBUJAR_TEXTO(c, margin+155*mm, y, self.FORMATEAR_DINERO(sum_iva), size=7, bold=True)
        self.DIBUJAR_TEXTO(c, margin+175*mm, y, self.FORMATEAR_DINERO(sum_comision), size=7, bold=True)

        y -= 5 * mm
        self.DIBUJAR_TEXTO(c, width - margin, y, f"TOTAL A PAGAR: {self.FORMATEAR_DINERO(sum_comision)}", size=10, bold=True, align="right")
        
        c.save()
        self.filename = full_path # Actualizar filename para ABRIR_PDF
        self.ABRIR_PDF()

    def GENERAR_REPORTE_CIERRE_CAJA(self, filename, session_data, expenses, sales_data):
        """
        Genera reporte de cierre de caja con diseño mejorado estilo HTML
        """
        # A4 Vertical
        width, height = A4
        full_path = self.OBTENER_RUTA_REPORTE_DIARIO(filename)
        c = canvas.Canvas(full_path, pagesize=A4)
        margin = 15 * mm
        
        # Extraer datos de session_data (compatible con DictRow y tupla)
        def get_val(data, key_or_idx, default=0):
            if isinstance(data, dict):
                return data.get(key_or_idx, default) or default
            return data[key_or_idx] if isinstance(key_or_idx, int) else default
        
        session_id = get_val(session_data, 'id' if isinstance(session_data, dict) else 0)
        fecha_cierre = get_val(session_data, 'fecha_cierre' if isinstance(session_data, dict) else 3, '')
        monto_inicial = get_val(session_data, 'monto_inicial' if isinstance(session_data, dict) else 4, 0)
        total_gastos = get_val(session_data, 'total_gastos' if isinstance(session_data, dict) else 11, 0)
        r_efec = get_val(session_data, 'real_efectivo' if isinstance(session_data, dict) else 7, 0)
        r_trf = get_val(session_data, 'real_transferencia' if isinstance(session_data, dict) else 8, 0)
        r_deb = get_val(session_data, 'real_debito' if isinstance(session_data, dict) else 9, 0)
        r_cred = get_val(session_data, 'real_credito' if isinstance(session_data, dict) else 10, 0)
        real_total = get_val(session_data, 'monto_final_real' if isinstance(session_data, dict) else 6, 0)
        diferencia = get_val(session_data, 'diferencia' if isinstance(session_data, dict) else 12, 0)
        
        # Ventas Sistema (sales_data)
        v_efec, v_trf, v_deb, v_cred = sales_data
        total_ventas = v_efec + v_trf + v_deb + v_cred
        sys_total = monto_inicial + total_ventas - total_gastos
        
        # --- CABECERA (Estilo Orden de Ingreso) ---
        y = height - 25 * mm
        
        # Logo y datos empresa (izquierda)
        c.setFillColorRGB(0, 0.337, 0.702)  # Azul Servitec
        c.setFont("Helvetica-Bold", 16)
        c.drawString(margin, y, "SERVITEC SPA")
        
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica", 8)
        c.drawString(margin, y - 5*mm, "RIQUELME 281")
        c.drawString(margin, y - 8*mm, "TEL: +56 9 5100 7877")
        
        # Recuadro derecho (documento)
        box_x = width - margin - 70*mm
        box_y = y - 10*mm
        c.setLineWidth(1.5)
        c.rect(box_x, box_y, 70*mm, 20*mm, stroke=1, fill=0)
        
        # Título documento
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(box_x + 35*mm, box_y + 15*mm, "CIERRE DE CAJA")
        
        # Número turno (destacado)
        c.setFillColorRGB(0.851, 0.325, 0.310)  # Rojo
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(box_x + 35*mm, box_y + 9*mm, f"TURNO ID: {session_id}")
        
        # Fecha
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica", 8)
        c.drawCentredString(box_x + 35*mm, box_y + 3*mm, f"FECHA: {fecha_cierre[:16]}")
        
        y -= 35 * mm
        
        # --- SECCIÓN 1: RESUMEN GENERAL (SISTEMA) ---
        self._draw_section_box(c, margin, y, width - 2*margin, "RESUMEN GENERAL (SISTEMA)")
        y -= 8 * mm
        
        y = self._draw_data_row(c, margin, y, width - 2*margin, "FONDO INICIAL:", self.FORMATEAR_DINERO(monto_inicial))
        y = self._draw_data_row(c, margin, y, width - 2*margin, "TOTAL VENTAS (Todas las vías):", self.FORMATEAR_DINERO(total_ventas))
        y = self._draw_data_row(c, margin, y, width - 2*margin, "TOTAL GASTOS:", f"-{self.FORMATEAR_DINERO(total_gastos)}")
        
        # Total esperado (destacado)
        c.setFillColorRGB(0.976, 0.976, 0.976)
        c.rect(margin, y - 7*mm, width - 2*margin, 7*mm, fill=1, stroke=0)
        y = self._draw_data_row(c, margin, y, width - 2*margin, "TOTAL ESPERADO:", self.FORMATEAR_DINERO(sys_total), bold=True)
        
        y -= 12 * mm
        
        # --- SECCIÓN 2: ARQUEO REAL (DECLARADO) ---
        self._draw_section_box(c, margin, y, width - 2*margin, "ARQUEO REAL (DECLARADO)")
        y -= 8 * mm
        
        y = self._draw_data_row(c, margin, y, width - 2*margin, "EFECTIVO EN CAJA:", self.FORMATEAR_DINERO(r_efec))
        y = self._draw_data_row(c, margin, y, width - 2*margin, "TRANSFERENCIAS:", self.FORMATEAR_DINERO(r_trf))
        
        transbank_total = r_deb + r_cred
        y = self._draw_data_row(c, margin, y, width - 2*margin, "TRANSBANK (DÉBITO + CRÉDITO):", self.FORMATEAR_DINERO(transbank_total))
        
        # Total real (destacado)
        c.setFillColorRGB(0.976, 0.976, 0.976)
        c.rect(margin, y - 7*mm, width - 2*margin, 7*mm, fill=1, stroke=0)
        y = self._draw_data_row(c, margin, y, width - 2*margin, "TOTAL REAL CONTADO:", self.FORMATEAR_DINERO(real_total), bold=True)
        
        y -= 15 * mm
        
        # --- TABLA DE TOTALES FINALES ---
        # Total Esperado
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(width - margin - 50*mm, y, "TOTAL ESPERADO:")
        c.setLineWidth(0.5)
        c.rect(width - margin - 48*mm, y - 5*mm, 48*mm, 7*mm, stroke=1, fill=0)
        c.drawRightString(width - margin - 2*mm, y, self.FORMATEAR_DINERO(sys_total))
        
        y -= 10 * mm
        
        # Total Real
        c.drawRightString(width - margin - 50*mm, y, "TOTAL REAL:")
        c.rect(width - margin - 48*mm, y - 5*mm, 48*mm, 7*mm, stroke=1, fill=0)
        c.drawRightString(width - margin - 2*mm, y, self.FORMATEAR_DINERO(real_total))
        
        y -= 10 * mm
        
        # Diferencia (destacado)
        c.setFillColorRGB(0.933, 0.933, 0.933)
        c.rect(width - margin - 48*mm, y - 5*mm, 48*mm, 9*mm, fill=1, stroke=1)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 11)
        c.drawRightString(width - margin - 50*mm, y + 1*mm, "DIFERENCIA:")
        
        diff_str = self.FORMATEAR_DINERO(abs(diferencia))
        if diferencia < 0:
            diff_str = f"-{diff_str}"
        elif diferencia > 0:
            diff_str = f"+{diff_str}"
        c.drawRightString(width - margin - 2*mm, y + 1*mm, diff_str)
        
        y -= 25 * mm
        
        # --- FIRMAS ---
        if y > 40*mm:
            # Líneas de firma
            sig_y = 35 * mm
            sig_width = 60 * mm
            
            # Firma izquierda
            c.setLineWidth(0.5)
            c.line(margin + 10*mm, sig_y, margin + 10*mm + sig_width, sig_y)
            c.setFont("Helvetica-Bold", 8)
            c.drawCentredString(margin + 10*mm + sig_width/2, sig_y - 4*mm, "FIRMA RESPONSABLE")
            
            # Firma derecha
            c.line(width - margin - 10*mm - sig_width, sig_y, width - margin - 10*mm, sig_y)
            c.drawCentredString(width - margin - 10*mm - sig_width/2, sig_y - 4*mm, "FIRMA SUPERVISOR / SERVITEC")
        
        # --- DETALLE GASTOS (si hay) ---
        if expenses:
            y -= 10 * mm
            self.DIBUJAR_TEXTO(c, margin, y, "DETALLE DE GASTOS:", bold=True)
            y -= 4 * mm
            for g in expenses:
                # g: id, sesion_id, desc, monto, fecha
                if y < 15 * mm:
                    c.showPage()
                    y = height - 15 * mm
                self.DIBUJAR_TEXTO(c, margin, y, f"- {g[2]}", size=7)
                self.DIBUJAR_TEXTO(c, width-margin, y, self.FORMATEAR_DINERO(g[3]), size=7, align="right")
                y -= 3.5 * mm

        c.save()
        self.filename = full_path # Actualizar filename para ABRIR_PDF
        self.ABRIR_PDF()

    def ABRIR_PDF(self):
        try:
            # Si self.filename ya es ruta absoluta, usarla. Si no, buscar en daily path
            if os.path.isabs(self.filename):
                path_to_open = self.filename
            else:
                # Fallback por si acaso, aunque ya deberíamos tener la ruta completa
                path_to_open = self.OBTENER_RUTA_REPORTE_DIARIO(os.path.basename(self.filename))
                
            if platform.system() == "Windows": os.startfile(path_to_open)
            elif platform.system() == "Darwin": subprocess.call(["open", path_to_open])
            else: subprocess.call(["xdg-open", path_to_open])
        except Exception as e:
            print(f"Error al abrir PDF: {e}")
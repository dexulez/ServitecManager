"""
Módulo de mensajería para WhatsApp y Email
Integra envío de mensajes, PDFs y notificaciones
"""
import os
from datetime import datetime
try:
    import pywhatkit as kit
except ImportError:
    kit = None
try:
    from twilio.rest import Client
except ImportError:
    Client = None
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class GESTOR_MENSAJERIA:
    """Gestiona envío de mensajes por WhatsApp y Email"""
    
    def __init__(self, gestor_bd):
        self.bd = gestor_bd
        
        # Configuración de Twilio (WhatsApp API)
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID', '')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN', '')
        self.twilio_whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')
        
        # Configuración de Email
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_user = os.getenv('EMAIL_USER', '')
        self.email_password = os.getenv('EMAIL_PASSWORD', '')
        
        # Inicializar cliente Twilio si está configurado
        self.twilio_client = None
        if Client and self.twilio_account_sid and self.twilio_auth_token:
            try:
                self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
            except Exception as e:
                print(f"Error inicializando Twilio: {e}")
    
    def ENVIAR_WHATSAPP_WEB(self, telefono, mensaje, hora=None, minuto=None):
        """
        Envía mensaje por WhatsApp Web usando pywhatkit.
        Abre WhatsApp Web y programa el mensaje.
        
        Args:
            telefono: Número con código de país (ej: +56912345678)
            mensaje: Texto del mensaje
            hora: Hora para enviar (24h), None para envío inmediato
            minuto: Minuto para enviar, None para envío inmediato
        """
        if not kit:
            return False
        
        try:
            # Limpiar número (solo dígitos y +)
            telefono_limpio = ''.join(filter(lambda x: x.isdigit() or x == '+', telefono))
            
            if hora is not None and minuto is not None:
                # Programar envío
                kit.sendwhatmsg(telefono_limpio, mensaje, hora, minuto)
            else:
                # Envío inmediato
                now = datetime.now()
                kit.sendwhatmsg(telefono_limpio, mensaje, now.hour, now.minute + 2)
            
            return True
        except Exception as e:
            print(f"Error enviando WhatsApp Web: {e}")
            return False
    
    def ENVIAR_WHATSAPP_API(self, telefono, mensaje):
        """
        Envía mensaje por WhatsApp Business API usando Twilio.
        Requiere configuración de Twilio.
        
        Args:
            telefono: Número con código de país (ej: +56912345678)
            mensaje: Texto del mensaje
        """
        if not self.twilio_client:
            return False, "Twilio no configurado"
        
        try:
            # Limpiar número
            telefono_limpio = ''.join(filter(lambda x: x.isdigit() or x == '+', telefono))
            
            message = self.twilio_client.messages.create(
                body=mensaje,
                from_=self.twilio_whatsapp_number,
                to=f'whatsapp:{telefono_limpio}'
            )
            
            return True, message.sid
        except Exception as e:
            return False, str(e)
    
    def ENVIAR_EMAIL(self, destinatarios, asunto, cuerpo_html, adjuntos=None):
        """
        Envía email con soporte para HTML y adjuntos.
        
        Args:
            destinatarios: Email o lista de emails de destinatarios
            asunto: Asunto del email
            cuerpo_html: Cuerpo en formato HTML
            adjuntos: Lista de rutas de archivos a adjuntar
        """
        if not self.email_user or not self.email_password:
            return False
        
        try:
            # Asegurar que destinatarios es una lista
            if isinstance(destinatarios, str):
                destinatarios = [destinatarios]
            
            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_user
            msg['To'] = ', '.join(destinatarios)
            msg['Subject'] = asunto
            
            # Agregar cuerpo HTML
            html_part = MIMEText(cuerpo_html, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Agregar adjuntos
            if adjuntos:
                for archivo in adjuntos:
                    if os.path.exists(archivo):
                        with open(archivo, 'rb') as f:
                            adjunto = MIMEApplication(f.read(), _subtype="pdf")
                            adjunto.add_header('Content-Disposition', 'attachment', 
                                             filename=os.path.basename(archivo))
                            msg.attach(adjunto)
            
            # Conectar y enviar
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Error enviando email: {e}")
            return False
    
    def ENVIAR_ORDEN_COMPRA_WHATSAPP(self, proveedor_id, pdf_path):
        """Envía orden de compra por WhatsApp al proveedor"""
        proveedor = self.bd.OBTENER_UNO("SELECT * FROM proveedores WHERE id = ?", (proveedor_id,))
        if not proveedor:
            return False, "Proveedor no encontrado"
        
        telefono = proveedor.get('telefono', '')
        if not telefono:
            return False, "Proveedor sin teléfono"
        
        mensaje = f"""
🏭 *SERVITEC MANAGER*
📦 Orden de Compra

Estimado/a {proveedor['nombre']},

Adjuntamos orden de compra generada.

Por favor, confirmar recepción.

Saludos cordiales,
SERVITEC Team
        """.strip()
        
        # Intentar con API, si falla usar Web
        if self.twilio_client:
            exito, resultado = self.ENVIAR_WHATSAPP_API(telefono, mensaje)
            if exito:
                return True, "WhatsApp API enviado"
        
        return self.ENVIAR_WHATSAPP_WEB(telefono, mensaje), "WhatsApp Web programado"
    
    def ENVIAR_ORDEN_COMPRA_EMAIL(self, proveedor_id, pdf_path):
        """Envía orden de compra por email al proveedor"""
        proveedor = self.bd.OBTENER_UNO("SELECT * FROM proveedores WHERE id = ?", (proveedor_id,))
        if not proveedor:
            return False, "Proveedor no encontrado"
        
        email = proveedor.get('correo', '')
        if not email:
            return False, "Proveedor sin email"
        
        asunto = f"Orden de Compra - {datetime.now().strftime('%d/%m/%Y')}"
        
        cuerpo_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #0055cc; border-bottom: 3px solid #0055cc; padding-bottom: 10px;">
                    🏭 SERVITEC MANAGER
                </h2>
                
                <h3 style="color: #666;">📦 Orden de Compra</h3>
                
                <p>Estimado/a <strong>{proveedor['nombre']}</strong>,</p>
                
                <p>Adjuntamos la orden de compra generada en formato PDF.</p>
                
                <p>Por favor, confirmar recepción de este correo y disponibilidad de los items solicitados.</p>
                
                <div style="background-color: #f0f4f8; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>Fecha:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                    <p style="margin: 5px 0 0 0;"><strong>Documento adjunto:</strong> Orden de Compra (PDF)</p>
                </div>
                
                <p>Saludos cordiales,<br>
                <strong>SERVITEC Team</strong></p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                
                <p style="font-size: 12px; color: #999; text-align: center;">
                    Este es un correo automático generado por SERVITEC MANAGER<br>
                    Por favor, no responder a este correo
                </p>
            </div>
        </body>
        </html>
        """
        
        return self.ENVIAR_EMAIL(email, asunto, cuerpo_html, adjuntos=[pdf_path])
    
    def NOTIFICAR_RECEPCION_CLIENTE(self, orden_id, por_whatsapp=True, por_email=False):
        """Notifica al cliente que su equipo está listo para retiro"""
        orden = self.bd.OBTENER_UNO("""
            SELECT o.*, c.nombre as cliente_nombre, c.telefono, c.email
            FROM ordenes o
            LEFT JOIN clientes c ON o.cliente_id = c.id
            WHERE o.id = ?
        """, (orden_id,))
        
        if not orden:
            return False, "Orden no encontrada"
        
        mensaje = f"""
🔧 *SERVITEC - Equipo Listo*

Estimado/a {orden['cliente_nombre']},

Su equipo *{orden.get('equipo', 'N/A')}* ya está reparado y listo para retiro.

📍 Puede pasar a recogerlo en nuestro local.

Gracias por su confianza.

SERVITEC Team
        """.strip()
        
        resultados = []
        
        if por_whatsapp and orden.get('telefono'):
            exito = self.ENVIAR_WHATSAPP_WEB(orden['telefono'], mensaje)
            resultados.append(("WhatsApp", exito))
        
        if por_email and orden.get('email'):
            asunto = f"Equipo Listo - Orden #{orden_id}"
            html = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: #0055cc;">🔧 SERVITEC - Equipo Listo</h2>
                <p>Estimado/a <strong>{orden['cliente_nombre']}</strong>,</p>
                <p>Su equipo <strong>{orden.get('equipo', 'N/A')}</strong> ya está reparado y listo para retiro.</p>
                <p>📍 Puede pasar a recogerlo en nuestro local.</p>
                <p>Gracias por su confianza.</p>
                <p>SERVITEC Team</p>
            </body>
            </html>
            """
            exito, _ = self.ENVIAR_EMAIL(orden['email'], asunto, html)
            resultados.append(("Email", exito))
        
        return True, resultados
    
    def ESTA_CONFIGURADO_WHATSAPP(self):
        """Verifica si WhatsApp API está configurada"""
        return self.twilio_client is not None
    
    def ESTA_CONFIGURADO_EMAIL(self):
        """Verifica si Email está configurado"""
        return bool(self.email_user and self.email_password)

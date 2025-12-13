# 📱 Sistema de Mensajería - SERVITEC MANAGER

Integración de WhatsApp y Email para envío automático de órdenes de compra, notificaciones a clientes y más.

## 🚀 Características

### WhatsApp
- ✅ **WhatsApp Web** (Gratis) - Usando pywhatkit
- ✅ **WhatsApp Business API** (Pago) - Usando Twilio
- Envío automático de órdenes de compra a proveedores
- Notificaciones a clientes cuando equipos están listos

### Email
- ✅ Soporte Gmail, Outlook y otros SMTP
- ✅ Adjuntar PDFs (órdenes de compra)
- ✅ Templates HTML profesionales
- Envío de órdenes de compra con formato profesional

## 📦 Instalación

Las librerías ya están instaladas automáticamente:
```bash
pip install pywhatkit twilio python-dotenv
```

## ⚙️ Configuración

### 1. WhatsApp Web (Gratis - Sin configuración)

No requiere configuración adicional. Funciona automáticamente:
- Abre WhatsApp Web en tu navegador
- Programa el mensaje automáticamente
- Solo necesitas escanear el código QR

**Ventajas:**
- ✅ Gratis
- ✅ Sin configuración
- ✅ Fácil de usar

**Desventajas:**
- ❌ Requiere WhatsApp Web abierto
- ❌ Requiere intervención manual
- ❌ No adjunta archivos automáticamente

### 2. WhatsApp Business API (Twilio - Pago)

Para envío completamente automático:

1. **Crear cuenta en Twilio**
   - Ir a https://www.twilio.com/
   - Registrarse (incluye crédito de prueba gratis)

2. **Obtener credenciales**
   - Account SID
   - Auth Token
   - WhatsApp Sandbox Number

3. **Configurar archivo .env**
   ```env
   TWILIO_ACCOUNT_SID=tu_account_sid_aqui
   TWILIO_AUTH_TOKEN=tu_auth_token_aqui
   TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
   ```

**Costo aproximado:** $0.005 USD por mensaje

### 3. Email (Gmail)

1. **Activar verificación en 2 pasos**
   - Ir a https://myaccount.google.com/security
   - Activar "Verificación en dos pasos"

2. **Generar contraseña de aplicación**
   - Ir a https://myaccount.google.com/apppasswords
   - Seleccionar "Correo" y "Windows Computer"
   - Copiar la contraseña generada (16 caracteres)

3. **Configurar archivo .env**
   ```env
   EMAIL_USER=tu_email@gmail.com
   EMAIL_PASSWORD=tu_contraseña_aplicacion_aqui
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   ```

**Outlook/Hotmail:**
```env
EMAIL_USER=tu_email@outlook.com
EMAIL_PASSWORD=tu_contraseña
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
```

## 📝 Archivo .env

Crear archivo `.env` en la carpeta `servitec_manager/`:

```env
# === TWILIO (WhatsApp Business API) ===
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# === EMAIL (Gmail) ===
EMAIL_USER=servitec@gmail.com
EMAIL_PASSWORD=abcd efgh ijkl mnop
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

**Importante:** Nunca compartir el archivo `.env` ni subirlo a GitHub

## 🎯 Uso en la Aplicación

### Enviar Orden de Compra

1. Ir a **Pedidos** → **POR PROVEEDOR**
2. Seleccionar proveedor
3. Click en **GENERAR ORDEN DE COMPRA**
4. El PDF se genera automáticamente
5. Aparece ventana con opciones:
   - 📱 **ENVIAR POR WHATSAPP**
   - 📧 **ENVIAR POR EMAIL**

### WhatsApp - Flujo

**Si NO tienes Twilio configurado:**
- Se abre WhatsApp Web automáticamente
- Mensaje pre-escrito listo para enviar
- Adjuntar PDF manualmente

**Si tienes Twilio configurado:**
- Envío completamente automático
- Sin intervención manual
- Mensaje entregado al instante

### Email - Flujo

- Valida configuración de SMTP
- Envía email profesional con:
  - Header corporativo
  - Información del pedido
  - PDF adjunto
  - Footer automático

## 🔧 Solución de Problemas

### WhatsApp Web no abre

**Problema:** `pywhatkit` no puede abrir navegador

**Solución:**
```python
# El sistema automáticamente muestra un mensaje con el teléfono
# Puedes enviar manualmente desde WhatsApp
```

### Gmail rechaza contraseña

**Error:** "Username and Password not accepted"

**Solución:**
1. Verificar que verificación en 2 pasos esté activa
2. Usar contraseña de aplicación (no tu contraseña normal)
3. Revisar que EMAIL_PASSWORD no tenga espacios adicionales

### Twilio no funciona

**Error:** "Account SID invalid"

**Solución:**
1. Verificar que Account SID esté correcto
2. Verificar que Auth Token esté correcto
3. Activar WhatsApp Sandbox en consola de Twilio
4. Enviar mensaje de activación al número Sandbox

## 📚 API Reference

### Métodos disponibles

```python
# Obtener gestor
mensajeria = logic.mensajeria

# WhatsApp Web (Gratis)
mensajeria.ENVIAR_WHATSAPP_WEB("+56912345678", "Mensaje")

# WhatsApp API (Twilio)
exito, sid = mensajeria.ENVIAR_WHATSAPP_API("+56912345678", "Mensaje")

# Email
exito, msg = mensajeria.ENVIAR_EMAIL(
    "cliente@email.com",
    "Asunto",
    "<html>...</html>",
    adjuntos=["orden.pdf"]
)

# Enviar orden de compra
mensajeria.ENVIAR_ORDEN_COMPRA_WHATSAPP(proveedor_id, "path/orden.pdf")
mensajeria.ENVIAR_ORDEN_COMPRA_EMAIL(proveedor_id, "path/orden.pdf")

# Notificar cliente
mensajeria.NOTIFICAR_RECEPCION_CLIENTE(orden_id, por_whatsapp=True, por_email=False)

# Verificar configuración
if mensajeria.ESTA_CONFIGURADO_WHATSAPP():
    print("Twilio configurado")

if mensajeria.ESTA_CONFIGURADO_EMAIL():
    print("Email configurado")
```

## 🔐 Seguridad

### Variables de entorno

- ✅ Usar archivo `.env` (ya configurado con python-dotenv)
- ✅ Agregar `.env` a `.gitignore`
- ✅ Proporcionar `.env.example` sin credenciales reales

### Buenas prácticas

1. **Nunca** compartir credenciales
2. **Rotar** tokens periódicamente
3. **Limitar** permisos de contraseñas de aplicación
4. **Monitorear** uso de Twilio para evitar cargos inesperados

## 💡 Ejemplos de Uso

### Notificar cliente por WhatsApp

```python
# En ui/workshop.py al completar una reparación
if logic.mensajeria:
    logic.mensajeria.NOTIFICAR_RECEPCION_CLIENTE(
        orden_id=123,
        por_whatsapp=True,
        por_email=False
    )
```

### Enviar múltiples órdenes por email

```python
for proveedor_id, pdf_path in ordenes_pendientes:
    exito, msg = logic.mensajeria.ENVIAR_ORDEN_COMPRA_EMAIL(
        proveedor_id,
        pdf_path
    )
    print(f"Proveedor {proveedor_id}: {msg}")
```

## 🆘 Soporte

**Documentación completa:**
- Twilio WhatsApp: https://www.twilio.com/docs/whatsapp
- Gmail App Passwords: https://support.google.com/accounts/answer/185833
- pywhatkit: https://github.com/Ankit404butfound/PyWhatKit

**Problemas comunes:** Ver sección "Solución de Problemas" arriba

## 📊 Estado de Configuración

El sistema detecta automáticamente qué servicios están configurados:

```
✅ WhatsApp Web - Siempre disponible (gratis)
⚠️ WhatsApp API - Requiere Twilio
⚠️ Email - Requiere configuración SMTP
```

En la UI, los botones se deshabilitan automáticamente si el servicio no está configurado.

---

**Versión:** 1.0.0  
**Última actualización:** Diciembre 2025  
**Desarrollado para:** SERVITEC MANAGER PRO

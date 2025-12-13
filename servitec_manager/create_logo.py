from PIL import Image, ImageDraw, ImageFont
import os
import math

# Crear imagen con fondo transparente
img = Image.new('RGBA', (800, 300), (255, 255, 255, 0))
draw = ImageDraw.Draw(img)

# Intentar cargar fuentes
try:
    font_title = ImageFont.truetype('arial.ttf', 80)
    font_subtitle = ImageFont.truetype('arial.ttf', 28)
except:
    try:
        font_title = ImageFont.truetype('C:\\Windows\\Fonts\\arial.ttf', 80)
        font_subtitle = ImageFont.truetype('C:\\Windows\\Fonts\\arial.ttf', 28)
    except:
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()

# Dibujar texto principal
draw.text((200, 80), 'SERVITEC', fill=(74, 144, 226, 255), font=font_title)
draw.text((250, 180), 'MANAGER PRO', fill=(120, 120, 120, 255), font=font_subtitle)

# Dibujar engranaje (gear/cog)
gear_center = (100, 150)
gear_radius = 50

# Círculo principal del engranaje
draw.ellipse(
    [gear_center[0]-gear_radius, gear_center[1]-gear_radius, 
     gear_center[0]+gear_radius, gear_center[1]+gear_radius], 
    outline=(74, 144, 226, 255), 
    width=8
)

# Dientes del engranaje (8 puntos)
for i in range(8):
    angle = i * (2 * math.pi / 8)
    x = gear_center[0] + int(gear_radius * 1.2 * math.cos(angle))
    y = gear_center[1] + int(gear_radius * 1.2 * math.sin(angle))
    draw.ellipse([x-8, y-8, x+8, y+8], fill=(74, 144, 226, 255))

# Centro del engranaje
draw.ellipse(
    [gear_center[0]-15, gear_center[1]-15, gear_center[0]+15, gear_center[1]+15], 
    fill=(255, 255, 255, 255), 
    outline=(74, 144, 226, 255), 
    width=4
)

# Guardar imagen
img.save(os.path.join('assets', 'servitec_logo.png'))
print("Logo creado exitosamente en assets/servitec_logo.png")

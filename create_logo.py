from PIL import Image, ImageDraw, ImageFont
import os

# Crear imagen de logo simple
width, height = 600, 200
img = Image.new('RGB', (width, height), color='#1a1a2e')

# Dibujar texto
draw = ImageDraw.Draw(img)

# Texto "GRUPO NODS"
try:
    # Intentar usar Arial (disponible en Windows)
    font = ImageFont.truetype("arial.ttf", 60)
except:
    # Usar fuente por defecto si falla
    font = ImageFont.load_default()

# Centrar texto
text = "GRUPO NODS"
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]

x = (width - text_width) // 2
y = (height - text_height) // 2

# Dibujar texto en cyan
draw.text((x, y), text, fill='#00d9ff', font=font)

# Guardar
img.save('assets/grupo_nods_logo.png')
print("Logo creado exitosamente: assets/grupo_nods_logo.png")

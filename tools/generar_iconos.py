# -*- coding: utf-8 -*-
"""Genera los iconos PNG del sitio (PWA, Apple touch icon y favicon).

Uso:  python3 tools/generar_iconos.py   (requiere Pillow)
"""

import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "icons")
NAVY = (26, 35, 126)
GOLD = (197, 160, 89)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def icono(size, radio, maskable=False):
    escala = 4
    s = size * escala
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if maskable:
        d.rectangle([0, 0, s, s], fill=NAVY)
    else:
        d.rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * radio), fill=NAVY)
    # Marco dorado interior
    m = int(s * (0.2 if maskable else 0.12))
    d.rounded_rectangle([m, m, s - m, s - m], radius=int(s * 0.12), outline=GOLD, width=max(2, s // 40))
    fuente = ImageFont.truetype(FONT, int(s * (0.3 if maskable else 0.36)))
    d.text((s / 2, s / 2), "AB", font=fuente, fill=GOLD, anchor="mm")
    return img.resize((size, size), Image.LANCZOS)


def main():
    os.makedirs(OUT, exist_ok=True)
    icono(192, 0.22).save(os.path.join(OUT, "icon-192.png"), optimize=True)
    icono(512, 0.22).save(os.path.join(OUT, "icon-512.png"), optimize=True)
    icono(512, 0, maskable=True).save(os.path.join(OUT, "icon-maskable-512.png"), optimize=True)
    # Apple aplica su propia máscara: icono cuadrado sin transparencia
    icono(180, 0, maskable=True).convert("RGB").save(os.path.join(OUT, "apple-touch-icon.png"), optimize=True)
    icono(32, 0.2).save(os.path.join(OUT, "favicon-32.png"), optimize=True)
    print("Iconos generados en", OUT)


if __name__ == "__main__":
    main()

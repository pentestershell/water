#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import hashlib
import os
import sys
from datetime import datetime
import io
import fitz
from PIL import Image, ImageDraw, ImageFont

# -------------------------
# Funciones utilitarias
# -------------------------
def compute_sha256(file_path, chunk=65536):
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

def build_watermark_text(recipient, purpose, extra_text, src_hash, include_date=True, include_hash=True):
    today = datetime.now().strftime("%Y-%m-%d") if include_date else ""
    parts = [
        recipient if recipient else None,
        purpose if purpose else None,
        f"FECHA: {today}" if today else None,
        f"HASH: {src_hash[:12]}" if include_hash else None,
        extra_text if extra_text else None
    ]
    return "  •  ".join([p for p in parts if p])

def is_image(path):
    ext = os.path.splitext(path.lower())[1]
    return ext in {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp"}

def is_pdf(path):
    return os.path.splitext(path.lower())[1] == ".pdf"

# -------------------------
# Generar tile de texto rotado
# -------------------------
def _mk_text_tile_png(text, angle_deg, font_size_pt, opacity, try_font="DejaVuSans.ttf"):
    a = max(0, min(255, int(255 * float(opacity))))
    try:
        font = ImageFont.truetype(try_font, int(font_size_pt))
    except Exception:
        font = ImageFont.load_default()
    tmp = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    canvas = Image.new("RGBA", (tw + 20, th + 20), (0, 0, 0, 0))
    dc = ImageDraw.Draw(canvas)
    dc.text((10, 10), text, font=font, fill=(0, 0, 0, a))
    rotated = canvas.rotate(angle_deg, expand=True)
    buf = io.BytesIO()
    rotated.save(buf, format="PNG")
    png_bytes = buf.getvalue()
    buf.close()
    return png_bytes, rotated.size

# -------------------------
# PDF watermark
# -------------------------
def watermark_pdf(input_path, output_path, text, angle=-35, opacity=0.18,
                  font_size=28, x_step=320, y_step=240, margin=36):
    doc = fitz.open(input_path)
    tile_png, (tile_w, tile_h) = _mk_text_tile_png(text, angle, font_size, opacity)
    for page in doc:
        width, height = page.rect.width, page.rect.height
        y = -margin
        while y < height + margin:
            x = -margin
            while x < width + margin:
                r = fitz.Rect(x - tile_w / 2, y - tile_h / 2, x + tile_w / 2, y + tile_h / 2)
                page.insert_image(r, stream=tile_png, keep_proportion=False, overlay=True)
                x += x_step
            y += y_step
    doc.save(output_path, deflate=True, garbage=4)
    doc.close()
    print(f"[OK] Marca de agua aplicada -> {output_path}")

# -------------------------
# Imagen watermark
# -------------------------
def watermark_image(input_path, output_path, text, angle=-35, opacity=0.18,
                    font_size_ratio=0.035, x_step_ratio=0.28, y_step_ratio=0.22,
                    margin_ratio=0.04):
    img = Image.open(input_path).convert("RGBA")
    W, H = img.size
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", int(max(W, H) * font_size_ratio))
    except Exception:
        font = ImageFont.load_default()
    a = max(0, min(255, int(255 * opacity)))
    x_step = int(W * x_step_ratio)
    y_step = int(H * y_step_ratio)
    margin = int(min(W, H) * margin_ratio)
    for y in range(-margin, H + margin, y_step):
        for x in range(-margin, W + margin, x_step):
            bbox = font.getbbox(text)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            tmp = Image.new("RGBA", (tw + 10, th + 10), (0, 0, 0, 0))
            dtmp = ImageDraw.Draw(tmp)
            dtmp.text((5, 5), text, font=font, fill=(0, 0, 0, a))
            rot = tmp.rotate(angle, expand=True)
            overlay.alpha_composite(rot, (x - rot.size[0] // 2, y - rot.size[1] // 2))
    out = Image.alpha_composite(img, overlay).convert("RGB")
    out.save(output_path, quality=92)
    print(f"[OK] Marca de agua aplicada -> {output_path}")

# -------------------------
# Main con menú interactivo
# -------------------------
def main():
    parser = argparse.ArgumentParser(description="Añadir marca de agua a PDFs o imágenes.")
    parser.add_argument("-i", "--input", required=True, help="Archivo de entrada")
    parser.add_argument("-o", "--output", required=True, help="Archivo de salida")
    parser.add_argument("--angle", type=float, default=-35.0, help="Ángulo en grados")
    parser.add_argument("--opacity", type=float, default=0.18, help="Opacidad 0..1")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        raise SystemExit(f"[!] Archivo no encontrado: {args.input}")

    # Menú interactivo
    print("\n=== CONFIGURACIÓN DE MARCA DE AGUA ===")
    recipient = input("¿Qué quieres poner como texto principal? (Ej: 'Copia para Banco XYZ')\n> ").strip()
    purpose = input("¿Quieres añadir un propósito/uso? (Ej: 'KYC 2025')\n> ").strip()
    extra = input("Texto adicional opcional:\n> ").strip()
    include_date = input("¿Incluir fecha automática? (s/n) [s]: ").strip().lower() != "n"
    include_hash = input("¿Incluir hash SHA-256 del original? (s/n) [s]: ").strip().lower() != "n"

    src_hash = compute_sha256(args.input)
    wm_text = build_watermark_text(recipient, purpose, extra, src_hash, include_date, include_hash)

    if is_pdf(args.input):
        watermark_pdf(args.input, args.output, wm_text, angle=args.angle, opacity=args.opacity)
    elif is_image(args.input):
        watermark_image(args.input, args.output, wm_text, angle=args.angle, opacity=args.opacity)
    else:
        raise SystemExit("[!] Formato no soportado.")

    print(f"[i] SHA-256 del original: {src_hash}")

if __name__ == "__main__":
    main()

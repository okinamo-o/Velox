#!/usr/bin/env python3
"""
Convert generated VELOX logo into Windows .ico and Chromium theme PNGs
"""

import os
from PIL import Image, ImageOps, ImageFilter

SOURCE_IMAGE = r"C:\Users\Louay\.gemini\antigravity\brain\2420c40e-e297-48a8-a4cb-348bf8dee995\velox_browser_logo_1790518046494.jpg"
THEME_DIR = r"D:\Velox\src\chrome\app\theme\chromium"
WIN_THEME_DIR = os.path.join(THEME_DIR, "win")

def main():
    print(f"Loading source logo: {SOURCE_IMAGE}")
    img = Image.open(SOURCE_IMAGE).convert("RGBA")
    w, h = img.size
    print(f"Source size: {w}x{h}")

    # Let's crop slightly into the rounded square container
    # The badge is nicely centered from approx (15% to 85%)
    # Let's inspect the center
    # Alternatively, the full image with its dark background can be used,
    # or we can make the outer corners transparent!
    # Let's make the background outside the rounded rectangle transparent:
    # First, let's crop to the inner 82% to eliminate the outer margin
    margin = int(w * 0.12)
    cropped = img.crop((margin, margin, w - margin, h - margin))
    cw, ch = cropped.size

    # Create a rounded rectangle alpha mask
    mask = Image.new("L", (cw, ch), 0)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(mask)
    corner_radius = int(cw * 0.22)
    draw.rounded_rectangle([(0, 0), (cw - 1, ch - 1)], radius=corner_radius, fill=255)

    # Apply mask
    cropped.putalpha(mask)

    # Also make a copy for square presentation with soft border
    base_icon = cropped

    # Target icon sizes
    ico_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    ico_images = []
    for s in ico_sizes:
        resized = base_icon.resize(s, Image.Resampling.LANCZOS)
        ico_images.append(resized)

    # Save chromium.ico
    ico_path = os.path.join(WIN_THEME_DIR, "chromium.ico")
    print(f"Writing {ico_path} with sizes: {ico_sizes}")
    ico_images[-1].save(
        ico_path,
        format="ICO",
        sizes=[(im.width, im.height) for im in ico_images],
        append_images=ico_images[:-1]
    )
    print(f"Saved {ico_path} ({os.path.getsize(ico_path):,} bytes)")

    # Also save product_logo PNGs in theme directory
    png_sizes = [16, 24, 48, 64, 128, 256]
    for s in png_sizes:
        png_path = os.path.join(THEME_DIR, f"product_logo_{s}.png")
        resized = base_icon.resize((s, s), Image.Resampling.LANCZOS)
        resized.save(png_path, format="PNG")
        print(f"Saved {png_path} ({s}x{s})")

    # Also save a backup in tests/fixtures
    backup_dir = r"D:\Velox\branding\assets"
    os.makedirs(backup_dir, exist_ok=True)
    base_icon.save(os.path.join(backup_dir, "velox_logo_512.png"), format="PNG")
    ico_images[-1].save(
        os.path.join(backup_dir, "velox.ico"),
        format="ICO",
        sizes=[(im.width, im.height) for im in ico_images],
        append_images=ico_images[:-1]
    )
    print(f"Saved branding backup in {backup_dir}")

if __name__ == "__main__":
    main()

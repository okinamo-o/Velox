#!/usr/bin/env python3
"""
Updates all product logos and brand assets across Velox codebase
using the official VELOX supersonic V logo asset.
"""

import os
import base64
from io import BytesIO
from PIL import Image

REPO_ROOT = r"D:\Velox"
SRC_ROOT = os.path.join(REPO_ROOT, "src")
SOURCE_LOGO = os.path.join(REPO_ROOT, "branding", "assets", "velox_logo_512.png")

def main():
    print(f"Loading VELOX source logo from {SOURCE_LOGO}...")
    base_img = Image.open(SOURCE_LOGO).convert("RGBA")
    w, h = base_img.size
    print(f"Loaded logo: {w}x{h}")

    # Targets to update
    png_targets = [
        # Scaled theme resources
        (os.path.join(SRC_ROOT, "chrome", "app", "theme", "default_100_percent", "chromium", "product_logo_16.png"), 16),
        (os.path.join(SRC_ROOT, "chrome", "app", "theme", "default_100_percent", "chromium", "product_logo_32.png"), 32),
        (os.path.join(SRC_ROOT, "chrome", "app", "theme", "default_200_percent", "chromium", "product_logo_16.png"), 32),
        (os.path.join(SRC_ROOT, "chrome", "app", "theme", "default_200_percent", "chromium", "product_logo_32.png"), 64),
        (os.path.join(SRC_ROOT, "chrome", "app", "theme", "default_100_percent", "chromium", "linux", "product_logo_16.png"), 16),
        (os.path.join(SRC_ROOT, "chrome", "app", "theme", "default_100_percent", "chromium", "linux", "product_logo_32.png"), 32),
        # Unscaled theme resources
        (os.path.join(SRC_ROOT, "chrome", "app", "theme", "chromium", "product_logo_16.png"), 16),
        (os.path.join(SRC_ROOT, "chrome", "app", "theme", "chromium", "product_logo_24.png"), 24),
        (os.path.join(SRC_ROOT, "chrome", "app", "theme", "chromium", "product_logo_32.png"), 32),
        (os.path.join(SRC_ROOT, "chrome", "app", "theme", "chromium", "product_logo_48.png"), 48),
        (os.path.join(SRC_ROOT, "chrome", "app", "theme", "chromium", "product_logo_64.png"), 64),
        (os.path.join(SRC_ROOT, "chrome", "app", "theme", "chromium", "product_logo_128.png"), 128),
        (os.path.join(SRC_ROOT, "chrome", "app", "theme", "chromium", "product_logo_256.png"), 256),
    ]

    for path, size in png_targets:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        resized = base_img.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(path, format="PNG")
        print(f"Generated {size}x{size} PNG: {path}")

    # Generate multi-size Windows .ico
    ico_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    ico_images = [base_img.resize(s, Image.Resampling.LANCZOS) for s in ico_sizes]
    ico_targets = [
        os.path.join(SRC_ROOT, "chrome", "app", "theme", "chromium", "win", "chromium.ico"),
        os.path.join(SRC_ROOT, "chrome", "installer", "mini_installer", "mini_installer.ico"),
    ]
    for ico_path in ico_targets:
        os.makedirs(os.path.dirname(ico_path), exist_ok=True)
        ico_images[-1].save(
            ico_path,
            format="ICO",
            sizes=[(im.width, im.height) for im in ico_images],
            append_images=ico_images[:-1]
        )
        print(f"Generated ICO: {ico_path}")

    # Generate SVGs with embedded high-resolution VELOX badge
    # 256x256 product_logo.svg
    buf256 = BytesIO()
    base_img.resize((256, 256), Image.Resampling.LANCZOS).save(buf256, format="PNG")
    b64_256 = base64.b64encode(buf256.getvalue()).decode("ascii")

    svg_256 = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 256 256" width="256" height="256">
  <image width="256" height="256" href="data:image/png;base64,{b64_256}"/>
</svg>'''

    product_logo_svg_path = os.path.join(SRC_ROOT, "chrome", "app", "theme", "chromium", "product_logo.svg")
    with open(product_logo_svg_path, "w", encoding="utf-8") as f:
        f.write(svg_256)
    print(f"Generated SVG: {product_logo_svg_path}")

    # 48x48 chrome_logo_dark.svg for toolbar
    buf48 = BytesIO()
    base_img.resize((48, 48), Image.Resampling.LANCZOS).save(buf48, format="PNG")
    b64_48 = base64.b64encode(buf48.getvalue()).decode("ascii")

    svg_toolbar = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 24 24" width="24" height="24">
  <image width="24" height="24" href="data:image/png;base64,{b64_48}"/>
</svg>'''

    toolbar_svg_path = os.path.join(SRC_ROOT, "ui", "webui", "resources", "images", "chrome_logo_dark.svg")
    with open(toolbar_svg_path, "w", encoding="utf-8") as f:
        f.write(svg_toolbar)
    print(f"Generated Toolbar Dark SVG: {toolbar_svg_path}")

    print("All image assets successfully updated to VELOX brand!")

if __name__ == "__main__":
    main()

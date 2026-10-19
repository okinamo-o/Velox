from PIL import Image, ImageDraw

img = Image.new("RGBA", (240, 240), (18, 24, 32, 255))
draw = ImageDraw.Draw(img)

# Dynamic supersonic VELOX V in 24x24 space (scaled by 10)
# Outer contour:
# Left tip at (20, 40), curves gracefully down to vertex at (120, 210)
# Right tip at (220, 40)
# Inner contour:
# Upper center valley at (120, 140)
# Left wing width ~ 45-50px, right wing width ~ 45-50px
pts = [
    (20, 40), (45, 45), (85, 100), (120, 210), (155, 100), (195, 45), (220, 40),
    (185, 60), (145, 125), (120, 155), (95, 125), (55, 60)
]
draw.polygon(pts, fill=(0, 229, 255, 255))

# Secondary aerodynamic blade
pts2 = [
    (40, 75), (75, 115), (120, 185), (165, 115), (200, 75),
    (170, 85), (135, 135), (120, 150), (105, 135), (70, 85)
]
# draw.polygon(pts2, fill=(0, 160, 255, 255))

img.save(r"D:\Velox\preview_v.png")
print("Saved preview_v.png")

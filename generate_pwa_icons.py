"""
Generate high quality PWA brand icons for 'خدماتي'
"""
import os
import math
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'static', 'images', 'pwa')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_pwa_icon(size, is_maskable=False):
    # Base image
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Margins and radii
    if is_maskable:
        # Maskable icons must have safe zone (at least 10% padding all around)
        bg_radius = 0
        bg_bbox = [0, 0, size, size]
        draw.rectangle(bg_bbox, fill=(15, 23, 42, 255)) # Dark slate background for maskable
        # Inner emerald circle / rounded rect
        inner_m = int(size * 0.05)
        # Gradient background
        for y in range(size):
            factor = y / size
            r = int(16 * (1 - factor) + 5 * factor)
            g = int(185 * (1 - factor) + 150 * factor)
            b = int(129 * (1 - factor) + 105 * factor)
            draw.line([(0, y), (size, y)], fill=(r, g, b, 255))
        
        content_box = [int(size * 0.18), int(size * 0.18), int(size * 0.82), int(size * 0.82)]
    else:
        # Standard rounded app icon with gradient
        corner_r = int(size * 0.22)
        # Create gradient image
        grad = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        grad_draw = ImageDraw.Draw(grad)
        for y in range(size):
            factor = y / size
            r = int(16 * (1 - factor) + 5 * factor)
            g = int(185 * (1 - factor) + 150 * factor)
            b = int(129 * (1 - factor) + 105 * factor)
            grad_draw.line([(0, y), (size, y)], fill=(r, g, b, 255))
        
        # Rounded rectangle mask
        mask = Image.new('L', (size, size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([0, 0, size, size], radius=corner_r, fill=255)
        img.paste(grad, (0, 0), mask)
        content_box = [int(size * 0.18), int(size * 0.18), int(size * 0.82), int(size * 0.82)]

    # Draw the "Layers / خ" Logo Symbol inside content_box
    draw = ImageDraw.Draw(img)
    cx = size / 2
    cy = size / 2

    # Draw 3 stacked isometric diamonds/layers (Khidamati brand emblem)
    layer_w = (content_box[2] - content_box[0]) * 0.85
    layer_h = layer_w * 0.42
    
    # 3 layers from bottom to top
    layer_y_offsets = [cy + layer_h * 0.45, cy, cy - layer_h * 0.45]
    opacities = [160, 210, 255]
    
    for idx, (ly, op) in enumerate(zip(layer_y_offsets, opacities)):
        points = [
            (cx, ly - layer_h / 2),           # top
            (cx + layer_w / 2, ly),           # right
            (cx, ly + layer_h / 2),           # bottom
            (cx - layer_w / 2, ly),           # left
        ]
        
        # Shadow underneath
        if idx > 0:
            shadow_points = [(p[0], p[1] + size * 0.015) for p in points]
            draw.polygon(shadow_points, fill=(0, 0, 0, 40))
            
        # Layer body
        draw.polygon(points, fill=(255, 255, 255, op))
        # Inner outline for depth
        draw.polygon(points, outline=(255, 255, 255, 255), width=max(1, int(size * 0.012)))

    return img

def main():
    sizes = [72, 96, 128, 144, 152, 180, 192, 384, 512]
    for s in sizes:
        icon = create_pwa_icon(s, is_maskable=False)
        filename = f'icon-{s}x{s}.png' if s != 180 else 'apple-touch-icon.png'
        icon.save(os.path.join(OUTPUT_DIR, filename), 'PNG')
        print(f"Generated {filename}")

    # Maskable icons
    for s in [192, 512]:
        mask_icon = create_pwa_icon(s, is_maskable=True)
        filename = f'icon-maskable-{s}x{s}.png'
        mask_icon.save(os.path.join(OUTPUT_DIR, filename), 'PNG')
        print(f"Generated {filename}")

    # Favicon
    fav = create_pwa_icon(64)
    fav.save(os.path.join(OUTPUT_DIR, 'favicon.png'), 'PNG')
    print("All PWA icons generated successfully!")

if __name__ == '__main__':
    main()

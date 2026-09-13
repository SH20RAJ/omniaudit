#!/usr/bin/env python3
"""
Generate PNG and ICO assets for OmniAudit-GEO from the canonical source logo:
- public/brand/logo.png (Canonical master source-of-truth logo)
- public/brand/logo-mark.png (Square icon crop)
- public/brand/og-image.png & public/og-image.png (1200x630 social card)
- public/favicon.ico (Multi-resolution: 16x16, 32x32, 48x48)
- public/favicon-16x16.png
- public/favicon-32x32.png
- public/favicon-48x48.png
- public/apple-touch-icon.png (180x180)
- public/icon-192.png
- public/icon-512.png
"""

import os

from PIL import Image

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC_DIR = os.path.join(REPO_ROOT, "omniaudit-geo", "public")
BRAND_DIR = os.path.join(PUBLIC_DIR, "brand")
os.makedirs(BRAND_DIR, exist_ok=True)


def generate_all_assets():
    master_logo_path = os.path.join(BRAND_DIR, "logo.png")
    if not os.path.isfile(master_logo_path):
        raise FileNotFoundError(f"Canonical master logo not found at {master_logo_path}")

    master_img = Image.open(master_logo_path)
    print(f"Loaded master logo: {master_logo_path} {master_img.size} {master_img.mode}")

    # 1. Generate Logo Mark (Square icon crop without wordmark)
    # The top graphic is located from y=17 to y=493, x=88 to x=964
    top_graphic = master_img.crop((88, 17, 964, 493))
    gw, gh = top_graphic.size
    side = int(gw * 1.08)
    logo_mark = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    logo_mark.paste(top_graphic, ((side - gw) // 2, (side - gh) // 2), top_graphic)

    brand_mark_path = os.path.join(BRAND_DIR, "logo-mark.png")
    logo_mark.save(brand_mark_path, "PNG", optimize=True)
    print(f"✓ public/brand/logo-mark.png ({logo_mark.size[0]}x{logo_mark.size[1]})")

    # 2. Standard Favicon & PWA Sizes
    sizes = {
        "favicon-16x16.png": 16,
        "favicon-32x32.png": 32,
        "favicon-48x48.png": 48,
        "apple-touch-icon.png": 180,
        "icon-192.png": 192,
        "icon-512.png": 512,
    }

    for filename, s in sizes.items():
        thumb = logo_mark.resize((s, s), Image.Resampling.LANCZOS)
        out_path = os.path.join(PUBLIC_DIR, filename)
        thumb.save(out_path, "PNG", optimize=True)
        print(f"✓ public/{filename} ({s}x{s})")

    # 3. Multi-resolution Favicon .ico
    ico_path = os.path.join(PUBLIC_DIR, "favicon.ico")
    ico_32 = logo_mark.resize((32, 32), Image.Resampling.LANCZOS)
    ico_32.save(ico_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])
    print("✓ public/favicon.ico (16, 32, 48)")

    # 4. OpenGraph Social Share Card (1200x630)
    brand_og_path = os.path.join(BRAND_DIR, "og-image.png")
    root_og_path = os.path.join(PUBLIC_DIR, "og-image.png")
    if os.path.isfile(brand_og_path):
        og_img = Image.open(brand_og_path)
        if og_img.size != (1200, 630):
            og_1200 = og_img.resize((1200, 630), Image.Resampling.LANCZOS)
            og_1200.save(brand_og_path, "PNG", optimize=True)
            og_1200.save(root_og_path, "PNG", optimize=True)
        else:
            og_img.save(root_og_path, "PNG", optimize=True)
        print("✓ public/brand/og-image.png and public/og-image.png (1200x630)")

    print("\n✅ All brand assets generated successfully from canonical source!")


if __name__ == "__main__":
    generate_all_assets()

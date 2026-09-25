# gen_bars.py — run once to create the 5 progress bar PNGs
from PIL import Image, ImageDraw, ImageFilter
import os

os.makedirs("bars", exist_ok=True)
W, H, RADIUS = 460, 26, 13

def make_bar(pct):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([2, 2, W-2, H-2], radius=RADIUS, outline=(46, 204, 113, 255), width=3)
    d.rounded_rectangle([6, 6, W-6, H-6], radius=RADIUS-2, fill=(28, 30, 34, 255))
    d.rounded_rectangle([6, 6, W-6, H-6], radius=RADIUS-2, outline=(10, 10, 10, 255), width=1)
    fill_w = int((W - 12) * pct / 100)
    if fill_w > 0:
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(glow).rounded_rectangle([6, 6, 6 + fill_w, H-6], radius=RADIUS-2, fill=(72, 222, 255, 255))
        img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(4)))
        ImageDraw.Draw(img).rounded_rectangle([6, 6, 6 + fill_w, H-6], radius=RADIUS-2, fill=(64, 200, 255, 255))
    return img

for pct in [0, 25, 50, 75, 100]:
    make_bar(pct).save(f"bars/bar_{pct}.png")
print("Bars generated in /bars")

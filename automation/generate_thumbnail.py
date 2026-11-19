from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from pathlib import Path

PROJECT_DIR = Path("projects/antikythera-mechanism-short")
ASSET_IMG = PROJECT_DIR / "assets" / "scene_02_antikythera_gear_closeup.jpg"
FALLBACK_IMG = PROJECT_DIR / "assets" / "scene_03_antikythera_dials_replica.jpg"

target_img_path = ASSET_IMG if ASSET_IMG.exists() else FALLBACK_IMG

# 1. Generate 1280x720 Landscape Thumbnail (for standard video card representation)
def generate_landscape_thumbnail():
    thumb_w, thumb_h = 1280, 720
    base = Image.new("RGB", (thumb_w, thumb_h), (5, 10, 20))
    
    with Image.open(target_img_path) as img:
        img = img.convert("RGB")
        # Enhance contrast and saturation for high CTR
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.35)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.25)
        
        # Scale to fit right/center portion of thumbnail
        img.thumbnail((780, 680), Image.Resampling.LANCZOS)
        # Paste with offset
        base.paste(img, (thumb_w - img.width - 30, (thumb_h - img.height) // 2))

    # Add dark vignette gradient on the left side for text readability
    draw = ImageDraw.Draw(base)
    for x in range(650):
        alpha = int(255 * (1.0 - (x / 650)))
        draw.line([(x, 0), (x, thumb_h)], fill=(5, 10, 20))

    # Try loading bold system font or fallback
    try:
        font_large = ImageFont.truetype("arialbd.ttf", 64)
        font_sub = ImageFont.truetype("arialbd.ttf", 36)
        font_badge = ImageFont.truetype("arialbd.ttf", 26)
    except IOError:
        font_large = ImageFont.load_default()
        font_sub = font_large
        font_badge = font_large

    # Draw Yellow Category Badge
    badge_x, badge_y = 60, 90
    draw.rectangle([badge_x, badge_y, badge_x + 290, badge_y + 44], fill=(220, 160, 20))
    draw.text((badge_x + 14, badge_y + 6), "ARCHAEOLOGICAL ANOMALY", fill=(10, 10, 10), font=font_badge)

    # Draw Bold High-Impact Hook Text
    draw.text((60, 160), "THE 2,000-YEAR-OLD", fill=(255, 255, 255), font=font_large)
    draw.text((60, 240), "ANALOG COMPUTER", fill=(255, 215, 0), font=font_large)
    
    # Subtitle / Proof detail
    draw.text((60, 340), "30+ Interlocking Bronze Gears", fill=(200, 215, 230), font=font_sub)
    draw.text((60, 395), "Confirmed by 3D CT Scans", fill=(160, 185, 205), font=font_sub)

    out_path = PROJECT_DIR / "thumbnail_1280x720.jpg"
    base.save(out_path, "JPEG", quality=95)
    print(f"Created landscape thumbnail: {out_path} ({out_path.stat().st_size} bytes)")

# 2. Generate 1080x1920 Vertical Shorts Thumbnail
def generate_vertical_shorts_thumbnail():
    thumb_w, thumb_h = 1080, 1920
    base = Image.new("RGB", (thumb_w, thumb_h), (5, 8, 16))
    
    with Image.open(target_img_path) as img:
        img = img.convert("RGB")
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.3)
        
        # Scale to prominent center framing
        img.thumbnail((980, 1100), Image.Resampling.LANCZOS)
        base.paste(img, ((thumb_w - img.width) // 2, 420))
        
    draw = ImageDraw.Draw(base)
    # Vignettes top and bottom
    for y in range(400):
        factor = 1.0 - (y / 400)
        draw.line([(0, y), (thumb_w, y)], fill=(5, 8, 16))
    for y in range(1450, thumb_h):
        draw.line([(0, y), (thumb_w, y)], fill=(5, 8, 16))

    try:
        font_large = ImageFont.truetype("arialbd.ttf", 78)
        font_badge = ImageFont.truetype("arialbd.ttf", 34)
    except IOError:
        font_large = ImageFont.load_default()
        font_badge = font_large

    # Top Badge
    draw.rectangle([140, 180, 140 + 800, 180 + 60], fill=(220, 160, 20))
    draw.text((210, 190), "GREEK BRONZE ANOMALY (100 BC)", fill=(10, 10, 10), font=font_badge)

    # Top Bold Hook
    draw.text((100, 270), "2,000-YEAR-OLD", fill=(255, 255, 255), font=font_large)
    draw.text((100, 360), "COMPUTER", fill=(255, 215, 0), font=font_large)

    # Bottom Callout
    draw.text((120, 1550), "30 Bronze Gears Found in Shipwreck", fill=(220, 230, 245), font=font_badge)
    draw.text((120, 1620), "1,400 Years Ahead of Its Time", fill=(255, 215, 0), font=font_badge)

    out_path = PROJECT_DIR / "thumbnail_shorts_1080x1920.jpg"
    base.save(out_path, "JPEG", quality=95)
    
    # Also save as default thumbnail.jpg
    shutil_copy = PROJECT_DIR / "thumbnail.jpg"
    base.save(shutil_copy, "JPEG", quality=95)
    print(f"Created vertical shorts thumbnail: {out_path} ({out_path.stat().st_size} bytes)")

generate_landscape_thumbnail()
generate_vertical_shorts_thumbnail()

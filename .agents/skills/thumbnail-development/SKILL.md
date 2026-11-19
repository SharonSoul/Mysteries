---
name: thumbnail-development
description: Design, compose, and generate high-CTR YouTube thumbnails using Pillow and local graphics tools. Use when formulating thumbnail visual concepts, compositing high-contrast artifact imagery, adding cinematic vignette effects, rendering bold typography overlays, or sizing exports to 1280x720.
license: MIT
metadata: {"dimensions": [1280, 720], "engine": "Pillow"}
---

# Thumbnail Development

This skill governs thumbnail conception, visual art direction, and automated generation using Python and **Pillow (PIL)**.

## Visual Design Strategy for Historical Mysteries

1. **The Curiosity Gap**: The thumbnail image must pose an instant question that words alone cannot answer (e.g., an eerie subterranean doorway carved into solid rock with warm torchlight emanating from within).
2. **Visual Simplicity (Mobile First)**: 70%+ of YouTube views occur on mobile screens. Thumbnails must be legible at 150x84 pixels. Avoid cluttered collages; focus on ONE striking subject.
3. **Typography Rule**: Use a maximum of **2 to 4 bold, high-contrast words** (e.g., *"BEFORE HISTORY?"*, *"FORBIDDEN RELIC"*, *"30 GEARS"*).
4. **Color Grading & Lighting**:
   - Deep obsidian blues, cold teals, and charcoal blacks for background mystery.
   - Warm golden amber, torchlight yellow, or incandescent cyan highlights on the primary subject.

## Pillow Thumbnail Generation Pipeline

```python
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from pathlib import Path

def create_mystery_thumbnail(
    base_image_path: Path,
    output_path: Path,
    headline_text: str = "FORGOTTEN GEARS",
    font_path: Path = None
) -> Path:
    """
    Creates a 1280x720 YouTube thumbnail with high contrast, 
    subtle edge vignette, and bold outlined typography.
    """
    # 1. Load and scale image to 1280x720 cover
    img = Image.open(base_image_path).convert("RGB")
    target_w, target_h = 1280, 720
    
    # Scale keeping aspect ratio
    img_ratio = img.width / img.height
    target_ratio = target_w / target_h
    if img_ratio > target_ratio:
        new_height = target_h
        new_width = int(target_h * img_ratio)
    else:
        new_width = target_w
        new_height = int(target_w / img_ratio)
        
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    left = (new_width - target_w) // 2
    top = (new_height - target_h) // 2
    img = img.crop((left, top, left + target_w, top + target_h))
    
    # 2. Boost Contrast & Saturation for punchy display
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.25)
    sat_enhancer = ImageEnhance.Color(img)
    img = sat_enhancer.enhance(1.15)
    
    # 3. Add dark bottom/edge vignette for text readability
    overlay = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Bottom gradient
    for y in range(400, 720):
        alpha = int(180 * ((y - 400) / 320))
        draw.line([(0, y), (target_w, y)], fill=(10, 15, 25, alpha))
        
    img = Image.alpha_composite(img.convert("RGBA"), overlay)
    
    # 4. Draw Typography
    draw_final = ImageDraw.Draw(img)
    font_size = 72
    font = ImageFont.truetype(str(font_path), font_size) if font_path and font_path.exists() else ImageFont.load_default()
    
    # Text positioning: Bottom-center or Bottom-left
    bbox = draw_final.textbbox((0, 0), headline_text, font=font)
    text_w = bbox[2] - bbox[0]
    pos_x = (target_w - text_w) // 2
    pos_y = 560
    
    # Thick black stroke / outline
    stroke_width = 4
    draw_final.text(
        (pos_x, pos_y),
        headline_text,
        font=font,
        fill=(255, 220, 50),  # Bright mystery amber/yellow
        stroke_width=stroke_width,
        stroke_fill=(0, 0, 0)
    )
    
    img.convert("RGB").save(output_path, "JPEG", quality=95)
    return output_path
```

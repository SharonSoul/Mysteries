"""
Thumbnail Generation Module using Pillow.
Composites 1280x720 YouTube thumbnails with cinematic contrast,
vignette grading, and high-impact mystery typography.
"""

import logging
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

logger = logging.getLogger(__name__)


class ThumbnailGenerator:
    """Generates high-contrast YouTube thumbnails for mystery documentaries."""

    TARGET_WIDTH = 1280
    TARGET_HEIGHT = 720

    @classmethod
    def generate_thumbnail(
        cls,
        base_image_path: Path,
        output_path: Path,
        headline_text: str = "FORBIDDEN RELIC",
        font_path: Optional[Path] = None,
        text_color: tuple[int, int, int] = (255, 220, 50),  # Amber yellow
        outline_color: tuple[int, int, int] = (0, 0, 0)
    ) -> Path:
        """
        Creates a finished 1280x720 thumbnail with enhanced contrast,
        bottom-gradient shading for legibility, and bold stroked text.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img = Image.open(base_image_path).convert("RGB")

        # 1. Scale and center-crop to 1280x720
        img_ratio = img.width / img.height
        target_ratio = cls.TARGET_WIDTH / cls.TARGET_HEIGHT

        if img_ratio > target_ratio:
            new_h = cls.TARGET_HEIGHT
            new_w = int(cls.TARGET_HEIGHT * img_ratio)
        else:
            new_w = cls.TARGET_WIDTH
            new_h = int(cls.TARGET_WIDTH / img_ratio)

        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        left = (new_w - cls.TARGET_WIDTH) // 2
        top = (new_h - cls.TARGET_HEIGHT) // 2
        img = img.crop((left, top, left + cls.TARGET_WIDTH, top + cls.TARGET_HEIGHT))

        # 2. Boost Contrast & Color Saturation for YouTube feed pop
        contrast = ImageEnhance.Contrast(img)
        img = contrast.enhance(1.20)
        color = ImageEnhance.Color(img)
        img = color.enhance(1.15)

        # 3. Add bottom vignette overlay for text contrast
        overlay = Image.new("RGBA", (cls.TARGET_WIDTH, cls.TARGET_HEIGHT), (0, 0, 0, 0))
        draw_ov = ImageDraw.Draw(overlay)
        vignette_start = int(cls.TARGET_HEIGHT * 0.55)

        for y in range(vignette_start, cls.TARGET_HEIGHT):
            progress = (y - vignette_start) / (cls.TARGET_HEIGHT - vignette_start)
            alpha = int(190 * progress)
            draw_ov.line([(0, y), (cls.TARGET_WIDTH, y)], fill=(5, 10, 20, alpha))

        img = Image.alpha_composite(img.convert("RGBA"), overlay)

        # 4. Render Headline Typography
        draw = ImageDraw.Draw(img)
        font = None
        if font_path and font_path.exists():
            try:
                font = ImageFont.truetype(str(font_path), size=68)
            except Exception:
                font = None

        if not font:
            font = ImageFont.load_default()

        # Measure text
        bbox = draw.textbbox((0, 0), headline_text, font=font)
        text_w = bbox[2] - bbox[0]
        pos_x = (cls.TARGET_WIDTH - text_w) // 2
        pos_y = cls.TARGET_HEIGHT - 130

        # Draw thick black outline + text
        draw.text(
            (pos_x, pos_y),
            headline_text,
            font=font,
            fill=text_color,
            stroke_width=4,
            stroke_fill=outline_color
        )

        final_img = img.convert("RGB")
        final_img.save(output_path, "JPEG", quality=95)
        logger.info("Generated thumbnail at %s", output_path)
        return output_path

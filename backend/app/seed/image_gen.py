from __future__ import annotations
from io import BytesIO
import hashlib
import random
from PIL import Image, ImageDraw, ImageFont


def _rng(seed_text: str) -> random.Random:
    h = hashlib.sha256(seed_text.encode("utf-8")).digest()
    seed = int.from_bytes(h[:8], "big")
    return random.Random(seed)


def generate_recipe_image(title: str, recipe_id: int, size=(640, 420)) -> bytes:
    r = _rng(f"{recipe_id}:{title}")

    w, h = size
    # Тёплый фон
    base_colors = [
        (248, 236, 220),
        (246, 228, 203),
        (252, 240, 225),
        (245, 233, 214),
    ]
    bg = r.choice(base_colors)

    img = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(img)

    # Абстрактные круги/пятна (но каждый раз по-разному)
    for _ in range(10):
        cx = r.randint(-50, w + 50)
        cy = r.randint(-50, h + 50)
        rad = r.randint(25, 110)
        col = (
            r.randint(160, 255),
            r.randint(140, 220),
            r.randint(140, 220),
        )
        d.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=col)

    # Белая карточка снизу (как в твоём дизайне)
    card_h = int(h * 0.33)
    d.rounded_rectangle(
        (24, h - card_h - 24, w - 24, h - 24),
        radius=18,
        fill=(255, 255, 255),
    )

    # Заголовок (обрезаем, чтобы не вылез)
    title_clean = title.strip()
    if len(title_clean) > 32:
        title_clean = title_clean[:29] + "…"

    # Шрифт: берём дефолтный (в контейнере он есть всегда)
    font = ImageFont.load_default()

    d.text(
        (44, h - card_h),
        title_clean,
        fill=(40, 40, 40),
        font=font,
    )

    # Экспорт в WebP
    buf = BytesIO()
    img.save(buf, format="WEBP", quality=72, method=6)
    return buf.getvalue()
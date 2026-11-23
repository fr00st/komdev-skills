#!/usr/bin/env python3
"""
Техническая проверка изображения под требования ЕПК / РСЯ Яндекс Директа
и генерация контрольного листа с обрезками (1:1, 3:4, 16:9) и тизерной миниатюрой (120x90).
"""

import argparse
import os
import sys
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ALLOWED_FORMATS = {"JPEG", "PNG", "GIF"}
MAX_BYTES = 10 * 1024 * 1024  # 10 MB


def center_crop_ratio(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """Центральная обрезка под заданное соотношение сторон (имитация смарт-центра по умолчанию)."""
    w, h = img.size
    target_ratio = target_w / target_h
    cur_ratio = w / h

    if cur_ratio > target_ratio:
        new_w = int(round(h * target_ratio))
        left = (w - new_w) // 2
        box = (left, 0, left + new_w, h)
    else:
        new_h = int(round(w / target_ratio))
        top = (h - new_h) // 2
        box = (0, top, w, top + new_h)

    return img.crop(box)


def classify_epk(w: int, h: int) -> tuple[str, list[str], list[str]]:
    """Проверка пропорций и размеров по спецификации ЕПК Яндекс Директа."""
    errors = []
    warnings = []
    ratio = w / h

    is_wide_ratio = abs(ratio - (16 / 9)) <= 0.012  # ~1.778 (допуск 1-2 px округления)
    is_almost_wide = (1.60 <= ratio <= 1.90) and not is_wide_ratio
    is_regular_ratio = (0.74 <= ratio <= 1.35)  # 3:4 (0.75) .. 4:3 (1.333)

    if is_wide_ratio:
        img_type = "WIDE (16:9)"
        if w < 1080 or h < 607:
            errors.append(f"Слишком малое разрешение для WIDE 16:9: {w}x{h} (минимум 1080x607)")
        if w > 5000 or h > 2812:
            errors.append(f"Превышено максимальное разрешение для WIDE 16:9: {w}x{h} (максимум 5000x2812)")
    elif is_regular_ratio:
        img_type = "REGULAR (1:1..4:3/3:4)"
        if w < 450 or h < 450:
            errors.append(f"Слишком малое разрешение для REGULAR: {w}x{h} (минимум 450 px по каждой стороне)")
        if w > 5000 or h > 5000:
            errors.append(f"Превышено максимальное разрешение для REGULAR: {w}x{h} (максимум 5000 px)")
    elif is_almost_wide:
        img_type = "INVALID_ALMOST_16_9"
        errors.append(
            f"Пропорция {ratio:.2f}:1 ({w}x{h}) — «почти 16:9». "
            "Директ не примет её как WIDE (нужны точные 16:9, например 1920x1080, 1280x720, 1080x607)."
        )
    else:
        img_type = "NON_STANDARD"
        warnings.append(
            f"Нестандартная пропорция {ratio:.2f}:1 ({w}x{h}). "
            "Для ЕПК рекомендуется набор из 1:1, 3:4/4:3 и точных 16:9."
        )

    return img_type, errors, warnings


def draw_safe_zone(img: Image.Image) -> Image.Image:
    """Рисует на копии оригинала красную рамку центральной безопасной зоны (60% ширины и высоты)."""
    out = img.copy().convert("RGB")
    draw = ImageDraw.Draw(out)
    w, h = out.size
    pad_x = int(w * 0.20)
    pad_y = int(h * 0.20)
    line_w = max(2, min(w, h) // 180)
    draw.rectangle([pad_x, pad_y, w - pad_x, h - pad_y], outline=(235, 50, 50), width=line_w)
    return out


def make_contact_sheet(img: Image.Image, out_path: Path, title: str) -> None:
    """Собирает контрольный лист: оригинал + safe-zone, кропы 1:1, 3:4, 16:9 и тизер 120x90."""
    rgb = img.convert("RGB")
    bg = (242, 244, 247)
    sheet = Image.new("RGB", (1240, 820), bg)
    draw = ImageDraw.Draw(sheet)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
    except Exception:
        font = ImageFont.load_default()
        small = font

    draw.text((20, 14), f"RSYA / EPK Check: {title}", fill=(20, 20, 25), font=font)

    def place_panel(panel_img: Image.Image, box: tuple[int, int, int, int], label: str) -> None:
        x, y, bw, bh = box
        draw.text((x, y - 22), label, fill=(40, 45, 55), font=small)
        draw.rectangle([x - 1, y - 1, x + bw + 1, y + bh + 1], outline=(190, 195, 205), width=1)
        fitted = ImageOps.contain(panel_img, (bw, bh), method=Image.Resampling.LANCZOS)
        ox = x + (bw - fitted.width) // 2
        oy = y + (bh - fitted.height) // 2
        sheet.paste(fitted, (ox, oy))

    # Верхний ряд: оригинал с safe-zone + кроп 16:9
    orig_safe = draw_safe_zone(rgb)
    place_panel(orig_safe, (20, 68, 580, 330), "Original + Safe Zone (center 60%)")

    crop_16_9 = center_crop_ratio(rgb, 16, 9)
    place_panel(crop_16_9, (630, 68, 590, 330), "Center Crop 16:9 (WIDE)")

    # Нижний ряд: 1:1, 3:4, и реальный тизер 120x90 px (без растягивания)
    crop_1_1 = center_crop_ratio(rgb, 1, 1)
    place_panel(crop_1_1, (20, 450, 340, 340), "Center Crop 1:1 (Square)")

    crop_3_4 = center_crop_ratio(rgb, 3, 4)
    place_panel(crop_3_4, (390, 450, 270, 340), "Center Crop 3:4 (Vertical)")

    # Миниатюра тизера 120x90 px в белой карточке (имитация мелкого блока РСЯ)
    tx, ty = 700, 450
    draw.text((tx, ty - 22), "Teaser Test: 120x90 px (actual size)", fill=(40, 45, 55), font=small)
    draw.rectangle([tx, ty, tx + 480, ty + 150], fill=(255, 255, 255), outline=(210, 215, 222), width=1)
    teaser_crop = center_crop_ratio(rgb, 4, 3).resize((120, 90), Image.Resampling.LANCZOS)
    sheet.paste(teaser_crop, (tx + 16, ty + 30))
    draw.text((tx + 152, ty + 34), "Ad Title Example (EPK)", fill=(25, 25, 30), font=font)
    draw.text((tx + 152, ty + 62), "Short description text appears", fill=(90, 95, 105), font=small)
    draw.text((tx + 152, ty + 82), "next to this 120x90 thumbnail.", fill=(90, 95, 105), font=small)
    draw.text((tx + 152, ty + 110), "Реклама · example.ru", fill=(140, 145, 155), font=small)

    # Второй тест: миниатюра 80x80 px (мобильный квадратный тизер)
    ty2 = 635
    draw.text((tx, ty2 - 22), "Mobile Square Teaser: 80x80 px", fill=(40, 45, 55), font=small)
    draw.rectangle([tx, ty2, tx + 480, ty2 + 115], fill=(255, 255, 255), outline=(210, 215, 222), width=1)
    teaser_sq = crop_1_1.resize((80, 80), Image.Resampling.LANCZOS)
    sheet.paste(teaser_sq, (tx + 16, ty2 + 17))
    draw.text((tx + 112, ty2 + 24), "Mobile EPK Block Preview", fill=(25, 25, 30), font=font)
    draw.text((tx + 112, ty2 + 52), "Can you recognize the subject", fill=(90, 95, 105), font=small)
    draw.text((tx + 112, ty2 + 72), "in 0.5 seconds?", fill=(90, 95, 105), font=small)

    sheet.save(out_path, format="JPEG", quality=90)


def main() -> int:
    parser = argparse.ArgumentParser(description="Проверка изображения для РСЯ / ЕПК Яндекс Директа.")
    parser.add_argument("image", help="Путь к файлу изображения")
    parser.add_argument("--out-dir", help="Папка для сохранения контрольного листа", default=None)
    args = parser.parse_args()

    img_path = Path(args.image).expanduser().resolve()
    if not img_path.is_file():
        print(f"ERROR: Файл не найден: {img_path}", file=sys.stderr)
        return 2

    file_size = img_path.stat().st_size
    errors = []
    warnings = []

    if file_size > MAX_BYTES:
        errors.append(f"Вес файла {file_size / (1024 * 1024):.2f} МБ превышает лимит 10 МБ")

    try:
        with Image.open(img_path) as img:
            fmt = (img.format or "UNKNOWN").upper()
            w, h = img.size
            if fmt not in ALLOWED_FORMATS:
                errors.append(f"Формат {fmt} не поддерживается Директом (нужны JPG, PNG или GIF)")
            if fmt == "GIF" and getattr(img, "is_animated", False):
                warnings.append("Анимированный GIF: Директ использует только первый кадр")

            img_type, epk_errors, epk_warnings = classify_epk(w, h)
            errors.extend(epk_errors)
            warnings.extend(epk_warnings)

            out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else Path(tempfile.gettempdir())
            out_dir.mkdir(parents=True, exist_ok=True)
            preview_path = out_dir / f"rsya_preview_{img_path.stem}.jpg"
            make_contact_sheet(img, preview_path, f"{img_path.name} ({w}x{h}, {fmt})")
    except Exception as exc:
        print(f"ERROR: Не удалось открыть изображение: {exc}", file=sys.stderr)
        return 2

    status = "FAIL" if errors else ("WARN" if warnings else "PASS")
    print(f"STATUS: {status}")
    print(f"FILE: {img_path}")
    print(f"FORMAT: {fmt} | SIZE: {w}x{h} | RATIO: {w / h:.3f}:1 | WEIGHT: {file_size / 1024:.1f} KB")
    print(f"EPK_TYPE: {img_type}")
    print(f"PREVIEW: {preview_path}")
    for e in errors:
        print(f"ERROR: {e}")
    for w_msg in warnings:
        print(f"WARNING: {w_msg}")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

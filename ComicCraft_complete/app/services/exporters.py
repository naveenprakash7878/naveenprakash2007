from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from fpdf import FPDF

from app.config import get_settings
from app.models import ComicLayout


def _clean_text(value: str) -> str:
    # FPDF core fonts are not Unicode-complete. Keep text printable for broad compatibility.
    return value.encode("latin-1", "replace").decode("latin-1")


def _local_image_path(image_url: str) -> Path:
    settings = get_settings()
    prefix = "/static/panels/"
    if not image_url.startswith(prefix):
        raise ValueError("Invalid image URL.")
    filename = Path(image_url[len(prefix):]).name
    path = settings.panels_dir / filename
    if not path.is_file():
        raise FileNotFoundError(f"Panel image not found: {filename}")
    return path


def save_pdf(layout: ComicLayout) -> str:
    settings = get_settings()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_title = re.sub(r"[^a-zA-Z0-9_-]+", "_", layout.character_name)[:40]
    filename = f"comic_{safe_title}_{stamp}.pdf"
    output = settings.exports_dir / filename

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for panel in layout.panels:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.multi_cell(0, 10, _clean_text(f"Panel {panel.panel_number}: {panel.title}"))

        image_path = _local_image_path(panel.image_url)
        x = 15
        y = pdf.get_y() + 5
        max_w = 180
        max_h = 105

        from PIL import Image
        with Image.open(image_path) as im:
            width, height = im.size
        ratio = min(max_w / width, max_h / height)
        display_w = width * ratio
        display_h = height * ratio
        pdf.image(str(image_path), x=x, y=y, w=display_w, h=display_h)
        pdf.set_y(y + display_h + 8)

        pdf.set_font("Helvetica", "I", 10)
        pdf.multi_cell(0, 6, _clean_text(panel.scene_description))
        pdf.ln(2)

        pdf.set_font("Helvetica", "B", 11)
        if panel.caption:
            pdf.multi_cell(0, 7, _clean_text(f"Caption: {panel.caption}"))
        pdf.set_font("Helvetica", "", 11)
        if panel.narration:
            pdf.multi_cell(0, 7, _clean_text(f"Narration: {panel.narration}"))
        if panel.dialogue:
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 7, _clean_text(f"Dialogue: {panel.dialogue}"))

    pdf.output(str(output))
    return f"/static/exports/{filename}"

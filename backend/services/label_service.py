"""Service pour la génération d'étiquettes 3×5cm @ 300dpi (PDF via ReportLab)."""

import io
import os
import zipfile

import qrcode
from PIL import Image
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from sqlalchemy.orm import Session

import models

# ── Dimensions (points = px de la maquette @ 300dpi) ──
LABEL_W = 354   # ≈ 3cm  @ 300dpi
LABEL_H = 591   # ≈ 5cm  @ 300dpi
CX = LABEL_W / 2

# ── Positions exactes fournies ──
# Coord "top" = distance depuis le HAUT de l'étiquette.
# En ReportLab (0,0 en bas), bottom_y = LABEL_H - top - element_height.
QR_TOP = 20
QR_SIZE = 140
YEAR_TOP = 180
NAME_TOP = 220
PHASE_TOP = 340
FOOTER_BOTTOM = 14       # distance depuis le BAS
NAME_MAX_H = 100         # zone maximale disponible pour le nom (220 -> 320)
NAME_AVAILABLE_BOTTOM = NAME_TOP + NAME_MAX_H  # 320 depuis le haut

# ── Polices ──
FONTS_DIR = os.path.join(os.path.dirname(__file__), "..", "fonts")


def _register_fonts() -> None:
    """Enregistre les fonts TTF une seule fois."""
    if getattr(_register_fonts, "_done", False):
        return
    _register_fonts._done = True
    pdfmetrics.registerFont(
        TTFont("Montserrat-Bold", os.path.join(FONTS_DIR, "Montserrat-Bold.ttf"))
    )
    pdfmetrics.registerFont(
        TTFont("NunitoSans-Bold", os.path.join(FONTS_DIR, "NunitoSans-Bold.ttf"))
    )
    pdfmetrics.registerFont(
        TTFont("NunitoSans-Regular", os.path.join(FONTS_DIR, "NunitoSans-Regular.ttf"))
    )


def _generate_qr_image(url: str, size: int) -> Image.Image:
    """Génère un QR code PIL.Image blanc/noir."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
    return img.resize((size, size), Image.LANCZOS)


def _fmt_phase(bottle: models.Bottle) -> str:
    """Formate toutes les phases de maturité (multi-lignes HTML)."""
    lines = []
    # Jeunesse (si pas de maturité → on affiche juste la jeunesse)
    if bottle.jeunesse_end and not bottle.maturite_end:
        lines.append(f"Jeunesse jusqu'à {bottle.jeunesse_end}")
    # Maturité
    if bottle.maturite_end:
        lines.append(f"Maturité : {bottle.jeunesse_end or '?'} – {bottle.maturite_end}")
    # Apogée
    if bottle.apogee_end:
        lines.append(f"Apogée : {bottle.maturite_end or '?'} – {bottle.apogee_end}")
    return "<br />".join(lines) if lines else ""


def _build_label_pdf(bottle: models.Bottle, qr_code: str, url: str) -> bytes:
    """Génère le PDF d'une seule étiquette et retourne les bytes."""
    _register_fonts()

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(LABEL_W, LABEL_H))

    # ---------------------------------------------------------------
    # 1. QR (top = QR_TOP, centré horizontalement)
    # ---------------------------------------------------------------
    qr_img = _generate_qr_image(url, size=QR_SIZE)
    from reportlab.lib.utils import ImageReader

    img_reader = ImageReader(qr_img)
    qr_x = (LABEL_W - QR_SIZE) / 2
    # Le bas du QR en coord RL = LABEL_H - QR_TOP - QR_SIZE
    qr_y = LABEL_H - QR_TOP - QR_SIZE
    c.drawImage(img_reader, qr_x, qr_y, width=QR_SIZE, height=QR_SIZE, mask="auto")

    # ---------------------------------------------------------------
    # 2. Millésime (top = YEAR_TOP, centré)
    # ---------------------------------------------------------------
    if bottle.year:
        year_style = ParagraphStyle(
            "Year",
            fontName="NunitoSans-Regular",
            fontSize=20,
            leading=24,
            alignment=1,  # centre
            textColor=colors.HexColor("#1a1a1a"),
        )
        year_p = Paragraph(str(bottle.year), year_style)
        max_w = LABEL_W - 32
        w, h = year_p.wrap(max_w, 30)
        # top = YEAR_TOP → bottom_y = LABEL_H - YEAR_TOP - h
        year_y = LABEL_H - YEAR_TOP - h
        year_p.drawOn(c, 16, year_y)

    # ---------------------------------------------------------------
    # 3. Nom MAJUSCULES (top = NAME_TOP, centré, multi-lignes)
    # ---------------------------------------------------------------
    name = (bottle.name or "Vin").upper()
    name_style = ParagraphStyle(
        "Name",
        fontName="Montserrat-Bold",
        fontSize=15,
        leading=20,
        alignment=1,
        textColor=colors.HexColor("#111111"),
    )
    name_p = Paragraph(name, name_style)
    max_w = LABEL_W - 32
    w, h = name_p.wrap(max_w, NAME_MAX_H)
    # on cale le haut du bloc exactement à NAME_TOP
    name_y = LABEL_H - NAME_TOP - h
    name_p.drawOn(c, 16, name_y)

    # ---------------------------------------------------------------
    # 4. Phases (top = PHASE_TOP, centré, multi-lignes)
    # ---------------------------------------------------------------
    phase = _fmt_phase(bottle)
    if phase:
        phase_style = ParagraphStyle(
            "Phase",
            fontName="NunitoSans-Bold",
            fontSize=11,
            leading=18,
            alignment=1,
            textColor=colors.HexColor("#222222"),
        )
        phase_p = Paragraph(phase, phase_style)
        w, h = phase_p.wrap(LABEL_W - 20, 55)
        phase_y = LABEL_H - PHASE_TOP - h
        phase_p.drawOn(c, 10, phase_y)

    # ---------------------------------------------------------------
    # 5. Footer (bottom = FOOTER_BOTTOM)
    # ---------------------------------------------------------------
    c.setFont("NunitoSans-Regular", 9)
    c.setFillColor(colors.HexColor("#777777"))
    c.drawCentredString(CX, FOOTER_BOTTOM, "Made with love for Pinarr lovers")

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.getvalue()


def generate_single_label_pdf(
    db: Session, bottle_id: int, qr_code: str, frontend_url: str = ""
) -> bytes:
    """Génère le PDF d'une étiquette individuelle pour une bouteille physique donnée."""
    bottle = db.query(models.Bottle).filter(models.Bottle.id == bottle_id).first()
    if not bottle:
        raise ValueError(f"Bottle {bottle_id} not found")

    # Vérifier que le QR appartient bien à cette bouteille et est en cave
    pb = (
        db.query(models.PhysicalBottle)
        .filter(
            models.PhysicalBottle.bottle_id == bottle_id,
            models.PhysicalBottle.qr_code == qr_code,
            models.PhysicalBottle.status == "in_cellar",
        )
        .first()
    )
    if not pb:
        raise ValueError(f"Physical bottle with QR {qr_code} not found or not in cellar")

    url = f"{frontend_url.rstrip('/')}/bottle/{pb.qr_code}"
    return _build_label_pdf(bottle, pb.qr_code, url)


def generate_label_zip(
    db: Session, bottle_id: int, frontend_url: str = ""
) -> bytes:
    """Génère un ZIP contenant les étiquettes PDF de toutes les bouteilles
    physiques en cave pour un vin donné.
    """
    bottle = db.query(models.Bottle).filter(models.Bottle.id == bottle_id).first()
    if not bottle:
        raise ValueError(f"Bottle {bottle_id} not found")

    physical_bottles = (
        db.query(models.PhysicalBottle)
        .filter(
            models.PhysicalBottle.bottle_id == bottle_id,
            models.PhysicalBottle.status == "in_cellar",
        )
        .order_by(models.PhysicalBottle.id)
        .all()
    )

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for pb in physical_bottles:
            url = f"{frontend_url.rstrip('/')}/bottle/{pb.qr_code}"
            pdf_bytes = _build_label_pdf(bottle, pb.qr_code, url)

            safe_name = (
                (bottle.name or "Vin")
                .replace("/", "-")
                .replace("\\", "-")
                .replace(" ", "_")[:25]
            )
            filename = f"Etiquette_{safe_name}_{pb.qr_code}.pdf"
            zipf.writestr(filename, pdf_bytes)

        readme = (
            "Instructions d'impression :\n"
            "==============================\n\n"
            "Format : 3 cm x 5 cm @ 300 dpi.\n\n"
            "1. Ouvrez chaque PDF dans votre lecteur PDF.\n"
            "2. Dans les options d'impression, réglez la taille\n"
            "   de sortie sur 3 cm x 5 cm (format 'Actual size').\n"
            "3. Désactivez les en-têtes et pieds de page.\n\n"
            "4. Collez chaque étiquette sur sa bouteille physique.\n"
        )
        zipf.writestr("README.txt", readme.encode("utf-8"))

    zip_buffer.seek(0)
    return zip_buffer.getvalue()

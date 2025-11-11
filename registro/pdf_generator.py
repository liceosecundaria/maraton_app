import io
import os
from datetime import datetime, timedelta

from django.conf import settings
from pytz import timezone

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor, black

from .models import Participant

AZUL  = HexColor("#001B5E")
ROJO  = HexColor("#C62828")
VERDE = HexColor("#2E7D32")
GRIS  = HexColor("#666666")


def generar_credencial_pdf(participant: Participant) -> str:
    """
    Genera un PDF tamaño carta con dos gafetes:
    - Arriba: Acompañante (adulto)
    - Abajo: Alumno
    Devuelve la ruta absoluta del PDF generado.
    """
    # Tamaño carta en puntos (72 dpi)
    page_width  = 8.5 * 72
    page_height = 11  * 72
    badge_height = page_height / 2.0
    badge_width  = page_width

    # Rutas de imágenes
    logo_path  = os.path.join(settings.BASE_DIR, "static", "logo_lma.png")
    zorro_path = os.path.join(settings.BASE_DIR, "static", "zorro_maraton.png")
    liceo_path = os.path.join(settings.BASE_DIR, "static", "liceo.png")

    logo_img  = ImageReader(logo_path)  if os.path.exists(logo_path)  else None
    zorro_img = ImageReader(zorro_path) if os.path.exists(zorro_path) else None
    liceo_img = ImageReader(liceo_path) if os.path.exists(liceo_path) else None

    # Carpeta de salida
    out_dir = os.path.join(settings.MEDIA_ROOT, "credenciales")
    os.makedirs(out_dir, exist_ok=True)
    folio = participant.clave or "SIN-FOLIO"
    pdf_path = os.path.join(out_dir, f"{folio}.pdf")

    c = canvas.Canvas(pdf_path, pagesize=(page_width, page_height))

    # -----------------------------------
    # Función interna para cada gafete
    # -----------------------------------
    def dibujar_gafete(x0, y0, alto, modo: str):
        margin = 18
        ix = x0 + margin
        iy = y0 + margin
        iw = badge_width - 2 * margin
        ih = alto - 2 * margin

        # Marca de agua (logo LMA)
        try:
            if liceo_img:
                c.saveState()
                if hasattr(c, "setFillAlpha"):
                    c.setFillAlpha(0.08)
                center_x = ix + iw / 2.0
                center_y = iy + ih / 2.0
                wm_size = min(iw, ih) * 0.60
                c.drawImage(
                    liceo_img,
                    center_x - wm_size / 2.0,
                    center_y - wm_size / 2.0,
                    width=wm_size,
                    height=wm_size,
                    preserveAspectRatio=True,
                    mask="auto",
                )
                c.restoreState()
        except Exception:
            # no rompemos el PDF si falla la imagen
            pass

        # Marco
        c.setStrokeColor(AZUL)
        c.setLineWidth(2)
        c.rect(ix, iy, iw, ih, stroke=1, fill=0)

        # ========== ENCABEZADO ==========
        header_top_pad = 16
        header_h       = 110
        header_top     = iy + ih - header_top_pad

        # Logo LMA
        if logo_img:
            LOGO_H = 100
            LOGO_W = 200
            y_logo = header_top - LOGO_H
            c.drawImage(
                logo_img,
                ix + 6,
                y_logo,
                width=LOGO_W,
                height=LOGO_H,
                preserveAspectRatio=True,
                mask="auto",
            )

        # Zorro
        if zorro_img:
            ZORRO_H = 100
            ZORRO_W = 210
            y_zorro = header_top - ZORRO_H
            x_zorro = ix + iw - ZORRO_W - 6
            c.drawImage(
                zorro_img,
                x_zorro,
                y_zorro,
                width=ZORRO_W,
                height=ZORRO_H,
                preserveAspectRatio=True,
                mask="auto",
            )

        # Título
        c.setFillColor(AZUL)
        c.setFont("Helvetica-Bold", 26)
        c.drawCentredString(ix + iw / 2, header_top - 22, "MARATÓN LMA 2025")

        # Franjas
        c.setLineWidth(4)
        base = header_top - 50
        margen_lateral = 150

        c.setStrokeColor(AZUL)
        c.line(ix + margen_lateral, base, ix + iw - margen_lateral, base)
        c.setStrokeColor(ROJO)
        c.line(ix + margen_lateral, base - 8, ix + iw - margen_lateral, base - 8)
        c.setStrokeColor(VERDE)
        c.line(ix + margen_lateral, base - 16, ix + iw - margen_lateral, base - 16)

        # ========= CONTENIDO =========
        y = header_top - header_h - 40

        nombre_adulto = (participant.full_name or "").upper()
        nombre_alumno = (participant.child_name or "").upper()
        grado_txt     = (participant.grado or "").upper()

        try:
            rol_txt = (participant.get_role_display() or "").upper()
        except Exception:
            rol_txt = (participant.role or "").upper()

        cx = ix + iw / 2

        if modo == "ADULTO":
            # Nombre acompañante
            c.setFillColor(black)
            c.setFont("Helvetica-Bold", 28)
            c.drawCentredString(cx, y, nombre_adulto or "ACOMPAÑANTE")
            y -= 36

            # Alumno / grado
            c.setFillColor(GRIS)
            c.setFont("Helvetica", 13)
            c.drawCentredString(
                cx,
                y,
                f"Alumno(a): {nombre_alumno or '--'}   |   Grado: {grado_txt or '--'}",
            )
            y -= 28

            # Categoría (rol)
            c.setFillColor(AZUL)
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(cx, y, rol_txt or "--")
            y -= 60

            # Folio
            c.setFillColor(black)
            c.setFont("Helvetica-Bold", 42)
            c.drawCentredString(cx, (participant.clave or "SIN FOLIO"))
            y -= 40

        else:  # ALUMNO
            # Nombre alumno
            c.setFillColor(black)
            c.setFont("Helvetica-Bold", 30)
            c.drawCentredString(cx, nombre_alumno or "ALUMNO")
            y -= 36

            # Grado
            c.setFillColor(black)
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(cx, f"GRADO: {grado_txt or '--'}")
            y -= 35

            # Categoría (mismo rol, pero centrado)
            c.setFillColor(AZUL)
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(cx, rol_txt or "--")
            y -= 45

            # Folio
            c.setFillColor(black)
            c.setFont("Helvetica-Bold", 40)
            c.drawCentredString(cx, (participant.clave or "SIN FOLIO"))
            y -= 40

        # Leyenda inferior
        c.setFillColor(GRIS)
        c.setFont("Helvetica-Oblique", 11)
        c.drawCentredString(cx, iy + 20, "Imprime y presenta este gafete el día del evento")

        # Fecha (hora de CDMX aprox. UTC-6)
        mx_timezone = timezone(timedelta(hours=-6))
        hora_local = datetime.now(mx_timezone).strftime("%d/%m/%Y %H:%M")
        c.setFillColor(GRIS)
        c.setFont("Helvetica", 9)
        c.drawRightString(ix + iw - 10, iy + 16, f"Generado: {hora_local}")

    # Dibuja los dos gafetes
    dibujar_gafete(0, badge_height, badge_height, "ADULTO")
    dibujar_gafete(0, 0,           badge_height, "ALUMNO")

    # Línea punteada de corte
    c.setStrokeColor(HexColor("#9E9E9E"))
    c.setDash(3, 3)
    c.line(0, page_height / 2, page_width, page_height / 2)
    c.setDash()

    c.showPage()
    c.save()
    return pdf_path

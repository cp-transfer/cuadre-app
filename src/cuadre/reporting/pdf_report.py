
"""PDF report generation for completed reconciliations."""

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

from cuadre.calculations import calculate_expected_cash, format_cop
from cuadre.models import Reconciliation

NOTE_FIELD_LABELS = (
    ("net_sales", "Ventas netas"),
    ("coupons_sold_cash", "Bonos vendidos en efectivo"),
    ("coupons_sold_other_method", "Otros ingresos"),
    ("coupons_redeemed", "Bonos redimidos"),
    ("cards", "Tarjeta"),
    ("qr", "QR"),
    ("sistecredito", "Sistecrédito"),
    ("addi", "Addi"),
    ("expenses", "Gastos"),
    ("sistecredito_collections", "Recaudo Sistecrédito"),
    ("bags", "Bolsas"),
    ("garments", "Prendas"),
    ("garments_exchange", "Prendas por canje"),
)

def build_report_sections(
    reconciliation: Reconciliation,
) -> tuple[tuple[str | None, tuple[tuple[str, str], ...]], ...]:
    """Build ordered report sections from a completed reconciliation."""

    if not reconciliation.is_complete:
        raise ValueError(
            "Cash verification is required before generating the report."
        )

    amounts = reconciliation.amounts

    sections = [
        (
            None,
            (
                (
                    "Tienda",
                    f"{reconciliation.store_code} · {reconciliation.store_name}",
                ),
                ("Fecha", reconciliation.date.strftime("%d/%m/%Y")),
                ("Ventas netas", format_cop(amounts.net_sales)),
            ),
        ),
        (
            "BONOS",
            (
                ("Bonos vendidos en efectivo", format_cop(amounts.coupons_sold_cash)),
                (
                    "Otros ingresos",
                    f"{format_cop(amounts.coupons_sold_other_method)} "
                    f"({amounts.coupons_sold_other_method_details})",
                ),
                ("Bonos redimidos", format_cop(amounts.coupons_redeemed)),
            ),
        ),
        (
            "MEDIOS DE PAGO",
            (
                ("QR", format_cop(amounts.qr)),
                ("Tarjeta", format_cop(amounts.cards)),
                ("Sistecrédito", format_cop(amounts.sistecredito)),
                ("Addi", format_cop(amounts.addi)),
            ),
        ),
        (
            "GASTOS Y RECAUDOS",
            (
                ("Gastos", format_cop(amounts.expenses)),
                (
                    "Recaudo Sistecrédito",
                    format_cop(amounts.sistecredito_collections),
                ),
            ),
        ),
        (
            "INFORMACIÓN",
            (
                ("Bolsas", str(amounts.bags)),
                ("Prendas", str(amounts.garments)),
                ("Prendas por canje", str(amounts.garments_exchange)),
            ),
        ),
    ]

    expected_cash = calculate_expected_cash(amounts)
    verification = reconciliation.cash_verification

    verification_text = (
        "OK" if verification.matches_expected else "NO COINCIDE"
    )

    sections.append(
        (
            "EFECTIVO",
            (
                ("Efectivo esperado", format_cop(expected_cash)),
                ("Verificación", verification_text),
            ),
        )
    )

    notes = []

    for field_name, label in NOTE_FIELD_LABELS:
        note = amounts.field_notes.get(field_name, "")

        if note:
            notes.append((label, note))

    if verification.discrepancy_note:
        notes.append(
            ("Diferencia de efectivo", verification.discrepancy_note)
        )

    if notes:
        sections.append(("NOTAS", tuple(notes)))

    return tuple(sections)


def generate_reconciliation_pdf(
    reconciliation: Reconciliation,
    output_path: str | Path,
) -> Path:
    """Generate a compact A4 PDF report and return its path."""

    output_path = Path(output_path)

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        alignment=TA_CENTER,
        spaceAfter=8,
    )

    section_style = ParagraphStyle(
        "ReportSection",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        spaceBefore=4,
        spaceAfter=2,
    )

    entry_style = ParagraphStyle(
        "ReportEntry",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=11,
        spaceAfter=1,
    )

    story = [
        Paragraph("C.P. COMPANY", title_style),
    ]

    for section_title, entries in build_report_sections(reconciliation):
        if section_title:
            story.append(Paragraph(escape(section_title), section_style))

        for label, value in entries:
            safe_label = escape(label)
            safe_value = escape(value)

            story.append(
                Paragraph(
                    f"<b>{safe_label}:</b> {safe_value}",
                    entry_style,
                )
            )

        story.append(Spacer(1, 3 * mm))
        story.append(
            HRFlowable(
                width="100%",
                thickness=0.4,
                color=colors.lightgrey,
            )
        )
        story.append(Spacer(1, 2 * mm))

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title="Conciliación de caja",
        author="C.P. COMPANY",
    )

    document.build(story)

    return output_path


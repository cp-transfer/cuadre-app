
"""System printing integration through CUPS."""

import subprocess
import tempfile
from pathlib import Path

from cuadre.models import Reconciliation
from cuadre.reporting.pdf_report import generate_reconciliation_pdf


def print_reconciliation(reconciliation: Reconciliation) -> str:
    """Generate a temporary PDF and send it to the default CUPS printer."""

    if not reconciliation.is_complete:
        raise ValueError(
            "Cash verification is required before printing."
        )

    with tempfile.TemporaryDirectory(prefix="cuadre-print-") as temp_dir:
        pdf_path = Path(temp_dir) / "conciliacion.pdf"
        generate_reconciliation_pdf(reconciliation, pdf_path)

        try:
            result = subprocess.run(
                ["lp", str(pdf_path)],
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError as error:
            raise RuntimeError(
                "No se encontró el comando de impresión 'lp'. "
                "Verifique que CUPS esté instalado."
            ) from error

        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip()
            raise RuntimeError(
                f"No fue posible enviar el documento a imprimir: {detail}"
            )

        return (
            result.stdout.strip()
            or "Documento enviado a la cola de impresión."
        )

"""Cross-platform system printing for archived reconciliation PDFs."""

import ctypes
import subprocess
import sys
from pathlib import Path


def print_reconciliation(pdf_path: Path | str) -> str:
    """Send an existing reconciliation PDF to the system printer."""

    pdf_path = Path(pdf_path)

    if not pdf_path.is_file():
        raise FileNotFoundError(f"No existe el archivo PDF: {pdf_path}")

    if sys.platform == "win32":
        return _print_with_windows(pdf_path)

    return _print_with_cups(pdf_path)


def _print_with_windows(pdf_path: Path) -> str:
    """Ask the registered Windows PDF application to print the document."""

    shell32 = ctypes.WinDLL("shell32", use_last_error=True)
    shell_execute = shell32.ShellExecuteW
    shell_execute.argtypes = [
        ctypes.c_void_p,
        ctypes.c_wchar_p,
        ctypes.c_wchar_p,
        ctypes.c_wchar_p,
        ctypes.c_wchar_p,
        ctypes.c_int,
    ]
    shell_execute.restype = ctypes.c_void_p

    result = shell_execute(
        None,
        "print",
        str(pdf_path),
        None,
        None,
        0,
    )

    result_code = int(result or 0)
    if result_code <= 32:
        raise RuntimeError(
            "Windows no pudo iniciar la impresión del PDF "
            f"(código ShellExecute: {result_code}). "
            "Verifique que haya una aplicación PDF instalada "
            "y asociada con archivos .pdf."
        )

    return "Solicitud de impresión enviada a la aplicación PDF predeterminada."


def _print_with_cups(pdf_path: Path) -> str:
    """Send the existing PDF to the default CUPS printer."""

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

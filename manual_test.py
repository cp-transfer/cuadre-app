import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from cuadre.models import INFORMATIONAL_FIELDS, Reconciliation
from cuadre.validation import (
    build_reconciliation_amounts,
    parse_money,
    validate_cash_verification,
)
from cuadre.calculations import calculate_expected_cash, format_cop


LABELS = {
    "net_sales": "Ventas netas",
    "coupons_sold_cash": "Bonos vendidos en efectivo",
    "coupons_sold_other_method": "Bonos vendidos en otro medio",
    "coupons_redeemed": "Bonos redimidos",
    "cards": "Tarjetas",
    "qr": "QR",
    "sistecredito": "Sistecrédito",
    "addi": "Addi",
    "expenses": "Gastos",
    "sistecredito_collections": "Recaudo Sistecrédito",
    "bags": "Bolsas",
    "garments": "Prendas",
    "garments_exchange": "Cambios de prendas",
}

INPUT_ORDER = (
    "net_sales",
    "coupons_sold_cash",
    "coupons_sold_other_method",
    "coupons_redeemed",
    "cards",
    "qr",
    "sistecredito",
    "addi",
    "expenses",
    "sistecredito_collections",
    "bags",
    "garments",
    "garments_exchange",
)


def main():
    print("\n=== PRUEBA MANUAL DE CUADRE ===\n")

    store_code = input("Código de tienda: ").strip()
    store_name = input("Nombre de tienda: ").strip()

    started_at = datetime.now().astimezone()
    reconciliation_date = started_at.date()

    print("\nIngrese los valores. Deje vacío cuando no haya movimiento.")
    print("Puede usar puntos o comas como separadores de miles.\n")

    raw_values = {}
    other_method_details = ""

    for field in INPUT_ORDER:
        value = input(f"{LABELS[field]}: ").strip()
        raw_values[field] = value

        if field == "coupons_sold_other_method" and parse_money(value) > 0:
            other_method_details = input(
                "¿Qué medios de pago se utilizaron?: "
            ).strip()

    amounts = build_reconciliation_amounts(
        raw_values,
        coupons_sold_other_method_details=other_method_details,
    )
    expected_cash = calculate_expected_cash(amounts)

    print("\n--- INFORMACIÓN DEL CUADRE ---")
    print(f"Tienda: {store_name} ({store_code})")
    print(f"Fecha y hora: {started_at.strftime('%Y-%m-%d %H:%M:%S %Z')}")

    print("\n--- DETALLE DE VALORES ---")

    for field in INPUT_ORDER:
        value = getattr(amounts, field)

        if field in INFORMATIONAL_FIELDS:
            print(f"{LABELS[field]}: {value}")
        else:
            print(f"{LABELS[field]}: {format_cop(value)}")

    if amounts.coupons_sold_other_method > 0:
        print(
            "Medios de pago de bonos vendidos: "
            f"{amounts.coupons_sold_other_method_details}"
        )

    print("\n--- RESULTADO DEL CÁLCULO ---")
    print(f"EFECTIVO ESPERADO: {format_cop(expected_cash)}")

    while True:
        answer = input(
            "\n¿El efectivo contado coincide? [s/n]: "
        ).strip().lower()

        if answer in ("s", "si", "sí"):
            matches = True
            break

        if answer in ("n", "no"):
            matches = False
            break

        print("Respuesta no válida. Escriba s o n.")

    note = ""
    if not matches:
        note = input("Motivo de la diferencia: ").strip()

    verification = validate_cash_verification(
        expected_cash,
        matches,
        note,
    )

    reconciliation = Reconciliation(
        date=reconciliation_date,
        store_code=store_code,
        store_name=store_name,
        amounts=amounts,
        cash_verification=verification,
    )

    reconciliation.validate_for_submission()

    print("\n========== REPORTE DE CUADRE ==========")
    print(f"Tienda: {reconciliation.store_name} ({reconciliation.store_code})")
    print(f"Fecha y hora: {started_at.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print("---------------------------------------")

    for field in INPUT_ORDER:
        value = getattr(amounts, field)

        if field in INFORMATIONAL_FIELDS:
            print(f"{LABELS[field]}: {value}")
        else:
            print(f"{LABELS[field]}: {format_cop(value)}")

    if amounts.coupons_sold_other_method > 0:
        print(
            "Medios de pago de bonos vendidos: "
            f"{amounts.coupons_sold_other_method_details}"
        )

    print("---------------------------------------")
    print(f"EFECTIVO ESPERADO: {format_cop(expected_cash)}")
    print(f"Verificación: {'COINCIDE' if matches else 'NO COINCIDE'}")

    if note:
        print(f"Observación: {note}")

    print(
        f"Estado: {'LISTO PARA ENVÍO' if reconciliation.is_complete else 'INCOMPLETO'}"
    )
    print("=======================================\n")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, TypeError) as error:
        print(f"\nERROR: {error}")
        sys.exit(1)


import pytest

from cuadre.models import ReconciliationAmounts
from cuadre.calculations import calculate_expected_cash, format_cop


def test_normal_reconciliation():
    amounts = ReconciliationAmounts(
        net_sales=1_000_000,
        cards=300_000,
        qr=100_000,
        sistecredito=100_000,
        addi=50_000,
        coupons_redeemed=10_000,
        coupons_sold_cash=5_000,
        coupons_sold_other_method=8_000,
        coupons_sold_other_method_details="Tarjeta y QR",
        expenses=20_000,
        sistecredito_collections=30_000,
    )
    assert calculate_expected_cash(amounts) == 447_000


def test_all_zero_values():
    assert calculate_expected_cash(ReconciliationAmounts()) == 0


def test_negative_expected_cash_is_preserved():
    amounts = ReconciliationAmounts(net_sales=100_000, cards=150_000)
    assert calculate_expected_cash(amounts) == -50_000


def test_informational_fields_do_not_affect_cash():
    amounts = ReconciliationAmounts(
        net_sales=100_000,
        bags=20,
        garments=15,
        garments_exchange=3,
    )
    assert calculate_expected_cash(amounts) == 100_000


def test_field_notes_do_not_affect_cash():
    amounts = ReconciliationAmounts(
        net_sales=100_000,
        field_notes={"net_sales": "Net sales from POS"},
    )
    assert calculate_expected_cash(amounts) == 100_000


def test_other_method_coupon_sales_require_payment_details():
    with pytest.raises(ValueError):
        ReconciliationAmounts(coupons_sold_other_method=5_000)


def test_other_method_coupon_details_are_trimmed():
    amounts = ReconciliationAmounts(
        coupons_sold_other_method=5_000,
        coupons_sold_other_method_details="  Tarjeta y QR  ",
    )
    assert amounts.coupons_sold_other_method_details == "Tarjeta y QR"


def test_other_method_coupon_details_must_be_text():
    with pytest.raises(TypeError):
        ReconciliationAmounts(
            coupons_sold_other_method_details=123
        )


def test_negative_input_is_rejected():
    with pytest.raises(ValueError):
        ReconciliationAmounts(net_sales=-1)


def test_float_input_is_rejected():
    with pytest.raises(TypeError):
        ReconciliationAmounts(net_sales=100.5)


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        (0, "$0"),
        (1250000, "$1.250.000"),
        (-500, "-$500"),
    ],
)
def test_format_cop(amount, expected):
    assert format_cop(amount) == expected

def test_field_notes_are_immutable():
    amounts = ReconciliationAmounts(
        net_sales=100000,
        field_notes={"net_sales": "POS"},
    )

    with pytest.raises(TypeError):
        amounts.field_notes["net_sales"] = "Changed"

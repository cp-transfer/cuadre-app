from cuadre.gui.questions import (
    OTHER_METHOD_DETAILS_FIELD,
    QUESTION_DEFINITIONS,
)
from cuadre.models import INFORMATIONAL_FIELDS


def test_question_order_and_labels():
    expected = (
        ("net_sales", "Ventas netas"),
        ("coupons_sold_cash", "Bonos vendidos en efectivo"),
        ("coupons_sold_other_method", "Bonos vendidos en otro medio"),
        ("coupons_redeemed", "Bonos redimidos"),
        ("cards", "Tarjetas"),
        ("qr", "QR"),
        ("sistecredito", "Sistecrédito"),
        ("addi", "Addi"),
        ("expenses", "Gastos"),
        ("sistecredito_collections", "Recaudo Sistecrédito"),
        ("bags", "Bolsas"),
        ("garments", "Prendas"),
        ("garments_exchange", "Prendas por canje"),
    )

    actual = tuple(
        (question.field_name, question.label)
        for question in QUESTION_DEFINITIONS
    )

    assert actual == expected


def test_question_value_types():
    for question in QUESTION_DEFINITIONS:
        expected_type = (
            "quantity"
            if question.field_name in INFORMATIONAL_FIELDS
            else "money"
        )
        assert question.value_type == expected_type


def test_other_method_details_field_name():
    assert OTHER_METHOD_DETAILS_FIELD == "coupons_sold_other_method_details"

"""Question definitions for the reconciliation GUI."""

from dataclasses import dataclass

from cuadre.models import INFORMATIONAL_FIELDS


@dataclass(frozen=True)
class QuestionDefinition:
    field_name: str
    label: str
    value_type: str


QUESTION_DEFINITIONS = (
    QuestionDefinition("net_sales", "Ventas netas", "money"),
    QuestionDefinition("coupons_sold_cash", "Bonos vendidos en efectivo", "money"),
    QuestionDefinition(
        "coupons_sold_other_method",
        "Bonos vendidos en otro medio",
        "money",
    ),
    QuestionDefinition("coupons_redeemed", "Bonos redimidos", "money"),
    QuestionDefinition("cards", "Tarjetas", "money"),
    QuestionDefinition("qr", "QR", "money"),
    QuestionDefinition("sistecredito", "Sistecrédito", "money"),
    QuestionDefinition("addi", "Addi", "money"),
    QuestionDefinition("expenses", "Gastos", "money"),
    QuestionDefinition(
        "sistecredito_collections",
        "Recaudo Sistecrédito",
        "money",
    ),
    QuestionDefinition("bags", "Bolsas", "quantity"),
    QuestionDefinition("garments", "Prendas", "quantity"),
    QuestionDefinition(
        "garments_exchange",
        "Prendas por canje",
        "quantity",
    ),
)

OTHER_METHOD_DETAILS_FIELD = "coupons_sold_other_method_details"


def get_question_value_type(field_name: str) -> str:
    """Return the parser type for a reconciliation field."""
    return "quantity" if field_name in INFORMATIONAL_FIELDS else "money"

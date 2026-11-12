from cuadre.models import ReconciliationAmounts


def calculate_expected_cash(amounts: ReconciliationAmounts) -> int:
    """
    Calculate expected cash in whole Colombian pesos.

    NET_SALES must already have refunds deducted.
    Coupons sold through other payment methods are excluded because
    they are not part of net sales.
    Informational fields do not affect this calculation.
    """

    return (
        amounts.net_sales
        - amounts.cards
        - amounts.qr
        - amounts.sistecredito
        - amounts.addi
        - amounts.coupons_redeemed
        + amounts.coupons_sold_cash
        - amounts.expenses
        + amounts.sistecredito_collections
    )


def format_cop(amount: int) -> str:
    """Format an integer amount using Colombian thousands separators."""

    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("Amount must be an integer.")

    sign = "-" if amount < 0 else ""
    formatted = f"{abs(amount):,}".replace(",", ".")

    return f"{sign}${formatted}"


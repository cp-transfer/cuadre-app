from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date
from types import MappingProxyType
from typing import Optional


MONETARY_FIELDS = (
    "net_sales",
    "cards",
    "qr",
    "sistecredito",
    "addi",
    "coupons_redeemed",
    "coupons_sold_cash",
    "coupons_sold_other_method",
    "expenses",
    "sistecredito_collections",
)

INFORMATIONAL_FIELDS = (
    "bags",
    "garments",
    "garments_exchange",
)

ALL_FIELDS = MONETARY_FIELDS + INFORMATIONAL_FIELDS


@dataclass(frozen=True)
class ReconciliationAmounts:
    net_sales: int = 0
    cards: int = 0
    qr: int = 0
    sistecredito: int = 0
    addi: int = 0
    coupons_redeemed: int = 0
    coupons_sold_cash: int = 0
    coupons_sold_other_method: int = 0
    expenses: int = 0
    sistecredito_collections: int = 0

    bags: int = 0
    garments: int = 0
    garments_exchange: int = 0

    coupons_sold_other_method_details: str = ""
    field_notes: Mapping[str, str] = field(default_factory=dict, hash=False)

    def __post_init__(self):
        for name in ALL_FIELDS:
            value = getattr(self, name)

            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an integer.")

            if value < 0:
                raise ValueError(f"{name} cannot be negative.")

        if not isinstance(self.field_notes, Mapping):
            raise TypeError("field_notes must be a mapping.")

        if not isinstance(self.coupons_sold_other_method_details, str):
            raise TypeError("Other coupon payment method details must be text.")

        details = self.coupons_sold_other_method_details.strip()

        if self.coupons_sold_other_method > 0 and not details:
            raise ValueError(
                "Payment method details are required for coupons sold through other methods."
            )

        for name, note in self.field_notes.items():
            if name not in ALL_FIELDS:
                raise ValueError(f"Unknown field note: {name}")

            if not isinstance(note, str):
                raise TypeError(f"Note for {name} must be text.")

        object.__setattr__(
            self,
            "field_notes",
            MappingProxyType(dict(self.field_notes)),
        )
        object.__setattr__(
            self,
            "coupons_sold_other_method_details",
            details,
        )


@dataclass(frozen=True)
class CashVerification:
    matches_expected: bool
    discrepancy_note: str = ""

    def __post_init__(self):
        if not isinstance(self.matches_expected, bool):
            raise TypeError("Cash confirmation must be True or False.")

        if not isinstance(self.discrepancy_note, str):
            raise TypeError("Discrepancy note must be text.")

        note = self.discrepancy_note.strip()

        if not self.matches_expected and not note:
            raise ValueError(
                "A discrepancy note is required when cash does not match."
            )

        object.__setattr__(self, "discrepancy_note", note)


@dataclass(frozen=True)
class Reconciliation:
    date: date
    store_code: str
    store_name: str
    amounts: ReconciliationAmounts
    cash_verification: Optional[CashVerification] = None
    employee_name: Optional[str] = None

    def __post_init__(self):
        if type(self.date) is not date:
            raise TypeError("Reconciliation date must be a date object.")

        if not isinstance(self.store_code, str):
            raise TypeError("Store code must be text.")

        if not isinstance(self.store_name, str):
            raise TypeError("Store name must be text.")

        if self.employee_name is not None and not isinstance(self.employee_name, str):
            raise TypeError("Employee name must be text or None.")

        employee_name = (
            self.employee_name.strip() or None
            if self.employee_name is not None
            else None
        )

        store_code = self.store_code.strip()
        store_name = self.store_name.strip()

        if not store_code:
            raise ValueError("Store code cannot be empty.")

        if not store_name:
            raise ValueError("Store name cannot be empty.")

        if not isinstance(self.amounts, ReconciliationAmounts):
            raise TypeError(
                "amounts must be a ReconciliationAmounts instance."
            )

        if (
            self.cash_verification is not None
            and not isinstance(self.cash_verification, CashVerification)
        ):
            raise TypeError(
                "cash_verification must be a CashVerification instance or None."
            )

        if self.cash_verification is not None:
            from cuadre.calculations import calculate_expected_cash

            expected_cash = calculate_expected_cash(self.amounts)

            if expected_cash < 0 and self.cash_verification.matches_expected:
                raise ValueError(
                    "Negative expected cash cannot be confirmed as a match."
                )

        object.__setattr__(self, "store_code", store_code)
        object.__setattr__(self, "store_name", store_name)
        object.__setattr__(self, "employee_name", employee_name)

    @property
    def is_complete(self) -> bool:
        """Whether cash verification has been recorded."""
        return self.cash_verification is not None

    def validate_for_submission(self) -> None:
        """Ensure cash verification exists before submission."""
        if not self.is_complete:
            raise ValueError(
                "Cash verification is required before submission."
            )

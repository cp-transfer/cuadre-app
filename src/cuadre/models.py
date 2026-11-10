from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping


MONETARY_FIELDS = (
    "net_sales",
    "cards",
    "qr",
    "sistecredito",
    "addi",
    "coupons_redeemed",
    "expenses",
    "sistecredito_collections",
    "coupons_sold",
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
    expenses: int = 0
    sistecredito_collections: int = 0
    coupons_sold: int = 0

    bags: int = 0
    garments: int = 0
    garments_exchange: int = 0

    field_notes: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self):
        for name in ALL_FIELDS:
            value = getattr(self, name)

            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an integer.")

            if value < 0:
                raise ValueError(f"{name} cannot be negative.")

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

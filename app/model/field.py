from dataclasses import dataclass, field
from decimal import Decimal

from database.types import FieldType


@dataclass
class Field:
    pass
    # type: FieldType  # Ackerland
    # area: Decimal
    # red_region: bool  # Rotes Gebiet -> 20% weniger Düngung

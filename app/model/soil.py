from dataclasses import dataclass
from decimal import Decimal

from database.types import HumusType, SoilType


@dataclass
class Soil:
    type: SoilType  # schwach lehmiger Sand
    humus: HumusType  # < 4%
    ph: Decimal
    p2o5: Decimal
    k2o: Decimal
    mg: Decimal

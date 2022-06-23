from dataclasses import dataclass, field
from decimal import Decimal

from database.types import CropClass, CropType, RemainsType


@dataclass
class Crop:
    crop_class: CropClass  # Hauptfrucht
    # type: CropType  # Acker-/Saatgras
    # crop_yield: Decimal  # 15
    # remains: RemainsType  # None
    # legume_rate: str  # 25%

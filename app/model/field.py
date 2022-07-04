from dataclasses import dataclass
from decimal import Decimal

import database.model as db
from database.types import DemandType, FieldType


@dataclass
class Field:
    field: db.Field

    def __post_init__(self):
        self.base_id = self.field.base_id
        self.area: Decimal = self.field.area
        self.year: int = self.field.year
        self.field_type: FieldType = self.field.field_type
        self.red_region: bool = self.field.red_region
        self.soil_sample: db.SoilSample = (
            max(self.field.soil_samples, key=lambda x: x.year) if self.field.soil_samples else None
        )
        self.demand_option: DemandType = self.field.demand_type

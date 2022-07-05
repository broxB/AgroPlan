from dataclasses import dataclass
from decimal import Decimal

import database.model as db
from database.types import DemandType, FieldType
from model.soil import Soil


@dataclass
class Field:
    Field: db.Field

    def __post_init__(self):
        self.base_id: int = self.Field.base_id
        self.area: Decimal = self.Field.area
        self.year: int = self.Field.year
        self.field_type: FieldType = self.Field.field_type
        self.red_region: bool = self.Field.red_region
        self.demand_option: DemandType = self.Field.demand_type
        self.saldo: db.Saldo = self.Field.saldo

    @property
    def soil_sample(self):
        soil_sample = (
            max(self.Field.soil_samples, key=lambda x: x.year) if self.Field.soil_samples else None
        )
        if soil_sample:
            return Soil(soil_sample)
        return None

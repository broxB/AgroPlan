from dataclasses import dataclass
from decimal import Decimal

import database.model as db
from database.types import FieldType


@dataclass
class Field:
    field: db.Field

    def __post_init__(self):
        self.area = self.field.area
        self.year = self.field.year
        self.type_: FieldType = self.field.type

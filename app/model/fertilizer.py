from __future__ import annotations

from decimal import Decimal

import app.database.model as db
import app.model.guidelines as guidelines
from app.database.types import FertClass, FertType, FieldType


def create_fertilizer(fertilizer: db.Fertilizer) -> Organic | Mineral:
    if fertilizer.fert_class is FertClass.organic:
        return Organic(fertilizer)
    elif fertilizer.fert_class is FertClass.mineral:
        return Mineral(fertilizer)


class Fertilizer:
    def __init__(self, Fertilizer: db.Fertilizer):
        self.name: str = Fertilizer.name
        self.fert_class: FertClass = Fertilizer.fert_class
        self.fert_type: FertType = Fertilizer.fert_type
        self.n: Decimal = Fertilizer.n
        self.p2o5: Decimal = Fertilizer.p2o5
        self.k2o: Decimal = Fertilizer.k2o
        self.mgo: Decimal = Fertilizer.mgo
        self.s: Decimal = Fertilizer.s
        self.cao: Decimal = Fertilizer.cao
        self.nh4: Decimal = Fertilizer.nh4

    def is_class(self, fert_class: FertClass) -> bool:
        return self.fert_class is fert_class if fert_class else True

    @property
    def is_organic(self) -> bool:
        return self.fert_class is FertClass.organic

    @property
    def is_mineral(self) -> bool:
        return self.fert_class is FertClass.mineral

    @property
    def is_lime(self) -> bool:
        return self.fert_type is FertType.lime


class Organic(Fertilizer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._org_factor: dict = guidelines.org_factor()

    def factor(self, field_type: FieldType) -> Decimal:
        return Decimal(str(self._org_factor[self.fert_type.value][field_type.value]))

    def storage_loss(self) -> Decimal:
        return Decimal(str(self._org_factor[self.fert_type.value]["Lagerverluste"]))

    def n_total(self, netto: bool = False) -> Decimal:
        if netto:
            return self.n * self.storage_loss()
        return self.n

    def n_verf(self, field_type: FieldType) -> Decimal:
        return max(self.n * self.factor(field_type), self.nh4)

    def __repr__(self) -> str:
        return f"<Org fertilizer: {self.name}>"


class Mineral(Fertilizer):
    def n_total(self, *arg, **kwargs) -> Decimal:
        return self.n

    def n_verf(self, *arg, **kwargs) -> Decimal:
        return max(self.n, self.nh4)

    def __repr__(self) -> str:
        return f"<Min fertilizer: {self.name}>"

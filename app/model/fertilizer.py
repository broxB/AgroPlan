from dataclasses import dataclass
from decimal import Decimal

import database.model as db
from database.types import FertClass, FertType, FieldType
from utils import load_json


@dataclass
class Fertilizer:
    Fertilizer: db.Fertilizer

    def __post_init__(self):
        self.name: str = self.Fertilizer.name
        self.fert_class: FertClass = self.Fertilizer.fert_class
        self.fert_type: FertType = self.Fertilizer.fert_type
        self.n: Decimal = self.Fertilizer.n
        self.p2o5: Decimal = self.Fertilizer.p2o5
        self.k2o: Decimal = self.Fertilizer.k2o
        self.mgo: Decimal = self.Fertilizer.mgo
        self.s: Decimal = self.Fertilizer.s
        self.cao: Decimal = self.Fertilizer.cao
        self.nh4: Decimal = self.Fertilizer.nh4
        self._factor_dict = load_json("data/Richtwerte/Abschläge/wirkungsfaktoren.json")

    def n_ges(self, netto: bool = False) -> Decimal:
        if self.fert_class == FertClass.organic:
            if netto:
                return self.n * self.storage_loss()
            return self.n

    def n_verf(self, field_type: FieldType) -> Decimal:
        if self.fert_class == FertClass.organic:
            n_verf = self.n * self.factor(field_type)
            if self.nh4 > n_verf:
                n_verf = self.nh4
            return n_verf
        return self.n

    def is_class(self, fert_class: FertClass) -> bool:
        return self.fert_class == fert_class if fert_class else True

    def factor(self, field_type: FieldType) -> Decimal:
        return Decimal(str(self._factor_dict[self.fert_type.value][field_type.value]))

    def storage_loss(self) -> Decimal:
        return Decimal(str(self._factor_dict[self.fert_type.value]["Lagerverluste"]))

    @property
    def is_organic(self) -> bool:
        return self.fert_class == FertClass.organic

    @property
    def is_mineral(self) -> bool:
        return self.fert_class == FertClass.mineral

    @property
    def is_lime(self) -> bool:
        return self.fert_type == FertType.lime

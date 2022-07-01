from dataclasses import dataclass
from decimal import Decimal

import database.model as db
from database.types import FertClass, FertType, FieldType
from utils import load_json


@dataclass
class Fertilizer:
    fertilizer: db.Fertilizer

    def __post_init__(self):
        self.name = self.fertilizer.name
        self.class_ = self.fertilizer.fert_class
        self.type_ = self.fertilizer.fert_type.value
        self.n = self.fertilizer.n
        self.p2o5 = self.fertilizer.p2o5
        self.k2o = self.fertilizer.k2o
        self.mgo = self.fertilizer.mgo
        self.s = self.fertilizer.s
        self.cao = self.fertilizer.cao
        self.nh4 = self.fertilizer.nh4
        self.factor_dict = load_json("data/Richtwerte/Abschläge/wirkungsfaktoren.json")

    def n_ges(self, netto: bool = False) -> Decimal:
        if self.class_ == FertClass.organic:
            if netto:
                return self.n * Decimal(str(self.factor_dict[self.type_]["Lagerverluste"]))
            return self.n

    def n_verf(self, field_type: FieldType) -> Decimal:
        if self.class_ == FertClass.organic:
            n_verf = self.n * Decimal(str(self.factor_dict[self.type_][field_type.value]))
            if self.nh4 > n_verf:
                n_verf = self.nh4
            return n_verf
        return self.n

    def is_class(self, fert_class: FertClass) -> bool:
        return self.class_ == fert_class if fert_class else True

    @property
    def is_organic(self) -> bool:
        return self.class_ == FertClass.organic

    @property
    def is_mineral(self) -> bool:
        return self.class_ == FertClass.mineral

    @property
    def is_lime(self) -> bool:
        return self.type_ == FertType.lime

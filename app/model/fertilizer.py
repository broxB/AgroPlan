from dataclasses import dataclass, field
from decimal import Decimal

from database.types import CropClass, FertClass, FertType, FieldType, MeasureType
from utils import load_json


@dataclass()
class Fertilizer:
    # name: str
    fert_class: FertClass
    fert_type: FertType
    n: Decimal
    # p2o5: Decimal
    # k2o: Decimal
    # mgo: Decimal
    # s: Decimal
    # cao: Decimal
    # nh4: Decimal
    # amount: Decimal

    def __post_init__(self):
        self.factor = load_json("data/Richtwerte/Abschläge/wirkungsfaktoren.json")

    def nges(self, netto: bool = False) -> Decimal:
        if self.fert_class == FertClass.organic:
            if netto:
                return self.n * Decimal(str(self.factor[self.fert_type.value]["Lagerverluste"]))
            return self.n

from dataclasses import dataclass
from decimal import Decimal

from database.types import CropClass, FertClass, FertType, FieldType, MeasureType
from model.crop import Crop
from model.fertilizer import Fertilizer
from model.field import Field
from utils import load_json


@dataclass
class Fertilization:
    measure: MeasureType  # Herbst
    amount: Decimal
    field: Field
    fertilizer: Fertilizer
    crop: Crop

    # def __post_init__(self):
    # self.factors = load_json("data/Richtwerte/wirkungsfaktoren.json")

    def nges(self, *, measure: MeasureType, crop_class: CropClass, netto: bool = False) -> Decimal:

        sum_nges = Decimal()
        if (
            self.fertilizer.fert_class == FertClass.organic
            and self.measure == measure
            and self.crop.crop_class == crop_class
        ):
            sum_nges += Decimal(self.amount) * self.fertilizer.nges(netto)
        return sum_nges

    def sum_organic(self):
        pass

    def sum_mineral(self):
        pass

    def sum_lime(self):
        pass

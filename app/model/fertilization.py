from decimal import Decimal

import app.database.model as db
from app.database.types import CropClass, FieldType, MeasureType
from app.model.crop import Crop
from app.model.fertilizer import Fertilizer


class Fertilization:
    def __init__(
        self,
        Fertilization: db.Fertilization,
        fertilizer: Fertilizer,
        crop: Crop,
        crop_class: CropClass,
    ):
        self.fertilizer = fertilizer
        self.crop = crop
        self.crop_class = crop_class
        self.amount: Decimal = Fertilization.amount
        self.measure: MeasureType = Fertilization.measure

    def n_total(self, measure: MeasureType, crop_class: CropClass, netto: bool) -> Decimal:
        if self.fertilizer.is_organic:
            if self.is_measure(measure) and self.crop.is_class(crop_class):
                return self.amount * self.fertilizer.n_total(netto)
        return Decimal()

    def nutrients(self, field_type: FieldType) -> list[Decimal]:
        return [
            self.amount * self.n_verf(field_type),
            self.amount * self.fertilizer.p2o5,
            self.amount * self.fertilizer.k2o,
            self.amount * self.fertilizer.mgo,
            self.amount * self.fertilizer.s,
            self.amount * self.fertilizer.cao,
        ]

    def n_verf(self, field_type: FieldType) -> Decimal:
        if self.crop.crop_class == CropClass.catch_crop and self.fertilizer.is_organic:
            return Decimal()
        if self.crop.feedable:
            return self.fertilizer.n_verf(FieldType.grassland)
        return self.fertilizer.n_verf(field_type)

    def is_measure(self, measure: MeasureType) -> bool:
        return self.measure == measure if measure else True

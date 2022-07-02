from dataclasses import dataclass
from decimal import Decimal

import database.model as db
from database.types import CropClass, FieldType, MeasureType
from model.crop import Crop
from model.fertilizer import Fertilizer


@dataclass
class Fertilization:
    fertilization: db.Fertilization
    fertilizer: Fertilizer

    def __post_init__(self):
        self.amount = self.fertilization.amount
        self.measure = self.fertilization.measure
        self.crop: Crop = Crop(
            self.fertilization.cultivation.crop, self.fertilization.cultivation.crop_class
        )

    def n_ges(self, measure: MeasureType, crop_class: CropClass, netto: bool) -> Decimal:
        if self.fertilizer.is_organic:
            if self._is_measure(measure) and self.crop.is_class(crop_class):
                return self.amount * self.fertilizer.n_ges(netto)
        return Decimal()

    def nutrients(self, field_type) -> list[Decimal]:
        return [
            self.amount * self._n_verf(field_type),
            self.amount * self.fertilizer.p2o5,
            self.amount * self.fertilizer.k2o,
            self.amount * self.fertilizer.mgo,
            self.amount * self.fertilizer.s,
            self.amount * self.fertilizer.cao,
        ]

    def _n_verf(self, field_type: FieldType) -> Decimal:
        if self.crop.class_ == CropClass.catch_crop and self.fertilizer.is_organic:
            return self.fertilizer.n * Decimal("0.1")
        if self.crop.feedable:
            return self.fertilizer.n_verf(FieldType.grassland)
        return self.fertilizer.n_verf(field_type)

    def _is_measure(self, measure) -> bool:
        match = self.measure == measure if measure else True
        return match

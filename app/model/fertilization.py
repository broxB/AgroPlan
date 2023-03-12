from decimal import Decimal

import app.database.model as db
from app.database.types import CultivationType, FieldType, MeasureType

from .balance import Balance
from .crop import Crop
from .fertilizer import Fertilizer


class Fertilization:
    def __init__(
        self,
        Fertilization: db.Fertilization,
        fertilizer: Fertilizer,
        crop: Crop,
        cultivation_type: CultivationType,
    ):
        self.fertilizer = fertilizer
        self.crop = crop
        self.cultivation_type = cultivation_type
        self.amount: Decimal = Fertilization.amount
        self.measure: MeasureType = Fertilization.measure

    def n_total(
        self, measure_type: MeasureType, cultivation_type: CultivationType, netto: bool
    ) -> Decimal:
        if self.fertilizer.is_organic:
            if self.is_measure(measure_type) and self.cultivation_type is cultivation_type:
                return self.amount * self.fertilizer.n_total(netto)
        return Decimal()

    def nutrients(self, field_type: FieldType) -> Balance:
        return Balance(
            title=self.fertilizer.name,
            n=self.amount * self.n_verf(field_type),
            p2o5=self.amount * self.fertilizer.p2o5,
            k2o=self.amount * self.fertilizer.k2o,
            mgo=self.amount * self.fertilizer.mgo,
            s=self.amount * self.fertilizer.s,
            cao=self.amount * self.fertilizer.cao,
            nh4=self.amount * self.fertilizer.nh4,
        )

    def n_verf(self, field_type: FieldType) -> Decimal:
        if self.crop.feedable:
            return self.fertilizer.n_verf(FieldType.grassland)
        return self.fertilizer.n_verf(field_type)

    def is_measure(self, measure_type: MeasureType) -> bool:
        return self.measure is measure_type if measure_type else True

    def __repr__(self) -> str:
        return f"<Fertilization: {self.cultivation_type.name}>"

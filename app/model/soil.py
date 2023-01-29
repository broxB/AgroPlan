from __future__ import annotations

from bisect import bisect_left, bisect_right
from decimal import Decimal

import app.database.model as db
import app.model.guidelines as guidelines
from app.database.types import FieldType, HumusType, SoilType
from app.utils import round_to_nearest


def create_soil_sample(soil_samples: list[db.SoilSample], year) -> Soil | None:
    soil_samples = list(filter(lambda x: x.year <= year, soil_samples))
    soil_sample = max(soil_samples, key=lambda x: x.year) if soil_samples else None
    if soil_sample:
        return Soil(soil_sample, guidelines)
    return None


class Soil:
    def __init__(self, SoilSample: db.SoilSample, guidelines: guidelines = guidelines):
        self.year: int = SoilSample.year
        self.soil_type: SoilType = SoilSample.soil_type
        self.humus: HumusType = SoilSample.humus
        self.ph: Decimal = SoilSample.ph
        self.p2o5: Decimal = SoilSample.p2o5
        self.k2o: Decimal = SoilSample.k2o
        self.mg: Decimal = SoilSample.mg
        self._classes: list[str] = ["A", "B", "C", "D", "E"]
        self.guidelines = guidelines

    def reduction_n(self, field_type: FieldType) -> Decimal:
        soil_reductions = self.guidelines.soil_reductions()
        return Decimal(soil_reductions[self.humus.value][field_type.value])

    def reduction_p2o5(self, field_type: FieldType) -> Decimal:
        if self.p2o5 is None:
            return Decimal()
        p2o5_reductions = self.guidelines.p2o5_reductions()
        value = round_to_nearest(self.p2o5 / Decimal("2.291"), 1)  # calc element form
        values = p2o5_reductions[field_type.value]["Werte"]
        reduction = p2o5_reductions[field_type.value]["Abschläge"]
        index = bisect_right(values, value) - 1
        return Decimal(reduction[index])

    def reduction_k2o(self, field_type: FieldType) -> Decimal:
        if self.k2o is None:
            return Decimal()
        k2o_reductions = self.guidelines.k2o_reductions()
        value = round_to_nearest(self.k2o / Decimal("1.205"), 1)  # calc element form
        values = k2o_reductions[field_type.value][self.soil_type.value][self.humus.value]["Werte"]
        reduction = k2o_reductions[field_type.value][self.soil_type.value][self.humus.value][
            "Abschläge"
        ]
        index = bisect_right(values, value) - 1
        return Decimal(reduction[index])

    def reduction_mg(self, field_type: FieldType) -> Decimal:
        if self.mg is None:
            return Decimal()
        mgo_reductions = self.guidelines.mg_reductions()
        value = round_to_nearest(self.mg, 1)
        values = mgo_reductions[field_type.value][self.soil_type.value][self.humus.value]["Werte"]
        reduction = mgo_reductions[field_type.value][self.soil_type.value][self.humus.value][
            "Abschläge"
        ]
        index = bisect_right(values, value) - 1
        return Decimal(reduction[index])

    def reduction_s(self, s_demand: Decimal, n_total: Decimal) -> Decimal:
        sulfur_reductions = self.guidelines.sulfur_reductions()
        sulfur_needs = sulfur_reductions["Grenzwerte"]["Bedarf"]
        needs_index = bisect_right(sulfur_needs, s_demand) - 1
        reduction = sulfur_reductions["Humusgehalt"][self.humus.value][needs_index]
        n_total_values = sulfur_reductions["Grenzwerte"]["Nges"]
        n_total_index = str(n_total_values[bisect_right(n_total_values, n_total) - 1])
        reduction_n_total = sulfur_reductions["Nges"][n_total_index][needs_index]
        return Decimal(reduction + reduction_n_total)

    def reduction_cao(self, field_type: FieldType, preservation: bool = False) -> Decimal:
        if self.ph is None:
            return Decimal()
        else:
            value = self.ph
        if preservation:
            value = self.optimal_ph(field_type)
        cao_reductions = self.guidelines.cao_reductions()
        ph_values = cao_reductions[field_type.value]["phWert"]
        index = bisect_left(self.to_decimal(ph_values), round_to_nearest(value, 1))
        reduction = cao_reductions[field_type.value][self.soil_type.value][self.humus.value]
        try:
            return Decimal(-reduction[index] * 100 / 4)
        except IndexError:
            return Decimal(-reduction[-1] * 100 / 4)

    def class_p2o5(self, field_type: FieldType) -> str:
        if self.p2o5 is None:
            return ""
        p2o5_classes = self.guidelines.p2o5_classes()
        values = p2o5_classes[field_type.value]
        index = bisect_right(values, self.p2o5) - 1
        return self._classes[index]

    def class_k2o(self, field_type: FieldType) -> str:
        if self.k2o is None:
            return ""
        k2o_classes = self.guidelines.k2o_classes()
        values = k2o_classes[field_type.value][self.soil_type.value][self.humus.value]
        index = bisect_right(values, self.k2o) - 1
        return self._classes[index]

    def class_mg(self, field_type: FieldType) -> str:
        if self.mg is None:
            return ""
        mgo_classes = self.guidelines.mg_classes()
        values = mgo_classes[field_type.value][self.soil_type.value][self.humus.value]
        index = bisect_right(values, self.mg) - 1
        return self._classes[index]

    def class_ph(self, field_type: FieldType) -> str:
        if self.ph is None:
            return ""
        ph_classes = self.guidelines.ph_classes()
        values = ph_classes[field_type.value][self.soil_type.value][self.humus.value]
        index = bisect_right(values, self.ph) - 1
        return self._classes[index]

    def optimal_ph(self, field_type: FieldType) -> Decimal:
        ph_classes = self.guidelines.ph_classes()
        return Decimal(
            str(ph_classes[field_type.value][self.soil_type.value][self.humus.value][2])
        )

    @staticmethod
    def to_decimal(values: list[float]) -> list[Decimal]:
        return [Decimal(str(value)) for value in values]

from __future__ import annotations

from bisect import bisect_left, bisect_right
from decimal import Decimal

import app.database.model as db
from app.database.types import FieldType, HumusType, SoilClass, SoilType
from app.utils import round_to_nearest

from . import guidelines


def create_soil_sample(
    soil_samples: list[db.SoilSample], field_type: FieldType, year: int
) -> Soil | None:
    soil_samples = list(filter(lambda x: x.year <= year, soil_samples))
    soil_sample = max(soil_samples, key=lambda x: x.year) if soil_samples else None
    if soil_sample:
        return Soil(soil_sample, field_type, guidelines)
    return None


class Soil:
    """
    Class that handles all soil related tasks.
    """

    def __init__(
        self, SoilSample: db.SoilSample, field_type: FieldType, guidelines: guidelines = guidelines
    ):
        self.year: int = SoilSample.year
        self.field_type: FieldType = field_type
        self.soil_type: SoilType = SoilSample.soil_type
        self.humus: HumusType = SoilSample.humus
        self.ph: Decimal = SoilSample.ph
        self.p2o5: Decimal = SoilSample.p2o5
        self.k2o: Decimal = SoilSample.k2o
        self.mg: Decimal = SoilSample.mg
        self._classes: list[SoilClass] = list(SoilClass)
        self._guidelines = guidelines

    def reduction_n(self) -> Decimal:
        soil_reductions = self._guidelines.soil_reductions()
        return Decimal(soil_reductions[self.humus.value][self.field_type.value])

    def reduction_p2o5(self) -> Decimal:
        if self.p2o5 is None:
            return Decimal()
        p2o5_reductions = self._guidelines.p2o5_reductions()
        value = round_to_nearest(self.p2o5 / Decimal("2.291"), 1)  # calc element form
        values = p2o5_reductions[self.field_type.value]["Werte"]
        reduction = p2o5_reductions[self.field_type.value]["Abschläge"]
        index = bisect_right(values, value) - 1
        return Decimal(reduction[index])

    def reduction_k2o(self) -> Decimal:
        if self.k2o is None:
            return Decimal()
        k2o_reductions = self._guidelines.k2o_reductions()
        value = round_to_nearest(self.k2o / Decimal("1.205"), 1)  # calc element form
        values = k2o_reductions[self.field_type.value][self.soil_type.value][self.humus.value][
            "Werte"
        ]
        reduction = k2o_reductions[self.field_type.value][self.soil_type.value][self.humus.value][
            "Abschläge"
        ]
        index = bisect_right(values, value) - 1
        return Decimal(reduction[index])

    def reduction_mg(self) -> Decimal:
        if self.mg is None:
            return Decimal()
        mgo_reductions = self._guidelines.mg_reductions()
        value = round_to_nearest(self.mg, 1)
        values = mgo_reductions[self.field_type.value][self.soil_type.value][self.humus.value][
            "Werte"
        ]
        reduction = mgo_reductions[self.field_type.value][self.soil_type.value][self.humus.value][
            "Abschläge"
        ]
        index = bisect_right(values, value) - 1
        return Decimal(reduction[index])

    def reduction_s(self, s_demand: Decimal, n_total: Decimal) -> Decimal:
        sulfur_reductions = self._guidelines.sulfur_reductions()
        sulfur_needs = sulfur_reductions["Grenzwerte"]["Bedarf"]
        needs_index = bisect_right(sulfur_needs, s_demand) - 1
        reduction = sulfur_reductions["Humusgehalt"][self.humus.value][needs_index]
        n_total_values = sulfur_reductions["Grenzwerte"]["Nges"]
        n_total_index = str(n_total_values[bisect_right(n_total_values, n_total) - 1])
        reduction_n_total = sulfur_reductions["Nges"][n_total_index][needs_index]
        return Decimal(reduction + reduction_n_total)

    def reduction_cao(self, preservation: bool = False) -> Decimal:
        if self.ph is None:
            return Decimal()
        else:
            value = self.ph
        if preservation:
            value = self.optimal_ph()
        cao_reductions = self._guidelines.cao_reductions()
        ph_values = cao_reductions[self.field_type.value]["phWert"]
        index = bisect_left(self._to_decimal(ph_values), round_to_nearest(value, 1))
        reduction = cao_reductions[self.field_type.value][self.soil_type.value][self.humus.value]
        try:
            return Decimal(-reduction[index] * 100 / 4)
        except IndexError:
            return Decimal(-reduction[-1] * 100 / 4)

    def class_p2o5(self) -> str:
        if self.p2o5 is None:
            return ""
        value = round_to_nearest(self.p2o5 / Decimal("2.291"), 1)  # calc element form
        p2o5_classes = self._guidelines.p2o5_classes()
        try:
            values = p2o5_classes[self.field_type.value]
            index = bisect_right(values, value) - 1
            return self._classes[index]
        except KeyError:
            return ""

    def class_k2o(self) -> str:
        if self.k2o is None:
            return ""
        value = round_to_nearest(self.k2o / Decimal("1.205"), 1)  # calc element form
        k2o_classes = self._guidelines.k2o_classes()
        try:
            values = k2o_classes[self.field_type.value][self.soil_type.value][self.humus.value]
            index = bisect_right(values, value) - 1
            return self._classes[index]
        except KeyError:
            return ""

    def class_mg(self) -> str:
        if self.mg is None:
            return ""
        value = round_to_nearest(self.mg, 1)
        mgo_classes = self._guidelines.mg_classes()
        try:
            values = mgo_classes[self.field_type.value][self.soil_type.value][self.humus.value]
            index = bisect_right(values, value) - 1
            return self._classes[index]
        except KeyError:
            return ""

    def class_ph(self) -> str:
        if self.ph is None:
            return ""
        ph_classes = self._guidelines.ph_classes()
        try:
            values = ph_classes[self.field_type.value][self.soil_type.value][self.humus.value]
            index = bisect_right(values, self.ph) - 1
            return self._classes[index]
        except KeyError:
            return ""

    def optimal_ph(self) -> Decimal:
        ph_classes = self._guidelines.ph_classes()
        return Decimal(
            str(ph_classes[self.field_type.value][self.soil_type.value][self.humus.value][2])
        )

    @staticmethod
    def _to_decimal(values: list[float]) -> list[Decimal]:
        """
        Convert all list items from `Float` to `Decimal`.

        :param values:
            List of floats.
        :return:
            List of decimals.
        """
        return [Decimal(str(value)) for value in values]

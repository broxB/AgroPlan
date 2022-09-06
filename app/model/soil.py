from bisect import bisect_left, bisect_right
from dataclasses import dataclass
from decimal import Decimal

import database.model as db
from database.types import FieldType, HumusType, SoilType
from utils import load_json, round_to_nearest


@dataclass
class Soil:
    SoilSample: db.SoilSample

    def __post_init__(self):
        self.year: int = self.SoilSample.year
        self.soil_type: SoilType = self.SoilSample.soil_type
        self.humus: HumusType = self.SoilSample.humus
        self.ph: Decimal = self.SoilSample.ph
        self.p2o5: Decimal = self.SoilSample.p2o5
        self.k2o: Decimal = self.SoilSample.k2o
        self.mg: Decimal = self.SoilSample.mg
        self._p2o5_dict = load_json("data/Richtwerte/Abschläge/abschlag_p2o5.json")
        self._k2o_dict = load_json("data/Richtwerte/Abschläge/abschlag_k2o.json")
        self._mgo_dict = load_json("data/Richtwerte/Abschläge/abschlag_mgo.json")
        self._cao_dict = load_json("data/Richtwerte/Abschläge/abschlag_cao_4jahre.json")
        self._s_dict = load_json("data/Richtwerte/Abschläge/abschlag_s.json")
        self._soil_dict = load_json("data/Richtwerte/Abschläge/bodenvorrat.json")
        self._classes = ["A", "B", "C", "D", "E"]
        self._p2o5_class_dict = load_json("data/Richtwerte/Gehaltsklassen/klassen_p2o5.json")
        self._k2o_class_dict = load_json("data/Richtwerte/Gehaltsklassen/klassen_k2o.json")
        self._mgo_class_dict = load_json("data/Richtwerte/Gehaltsklassen/klassen_mgo.json")
        self._cao_class_dict = load_json("data/Richtwerte/Gehaltsklassen/klassen_ph_wert.json")

    def reduction_n(self, field_type: FieldType) -> Decimal:
        return Decimal(self._soil_dict[self.humus.value][field_type.value])

    def reduction_p2o5(self, field_type: FieldType) -> Decimal:
        if self.p2o5 is None:
            return Decimal()
        value = round_to_nearest(self.p2o5 / Decimal("2.291"), 1)  # calc element form
        values = self._p2o5_dict[field_type.value]["Werte"]
        reduction = self._p2o5_dict[field_type.value]["Abschläge"]
        index = bisect_right(values, value) - 1
        return Decimal(reduction[index])

    def reduction_k2o(self, field_type: FieldType) -> Decimal:
        if self.k2o is None:
            return Decimal()
        value = round_to_nearest(self.k2o / Decimal("1.205"), 1)  # calc element form
        values = self._k2o_dict[field_type.value][self.soil_type.value][self.humus.value]["Werte"]
        reduction = self._k2o_dict[field_type.value][self.soil_type.value][self.humus.value][
            "Abschläge"
        ]
        index = bisect_right(values, value) - 1
        return Decimal(reduction[index])

    def reduction_mgo(self, field_type: FieldType) -> Decimal:
        if self.mg is None:
            return Decimal()
        value = round_to_nearest(self.mg, 1)
        values = self._mgo_dict[field_type.value][self.soil_type.value][self.humus.value]["Werte"]
        reduction = self._mgo_dict[field_type.value][self.soil_type.value][self.humus.value][
            "Abschläge"
        ]
        index = bisect_right(values, value) - 1
        return Decimal(reduction[index])

    def reduction_s(self, s_demand: Decimal, n_total: Decimal) -> Decimal:
        s_values = self._s_dict["Grenzwerte"]["Bedarf"]
        n_total_values = self._s_dict["Grenzwerte"]["Nges"]
        s_index = bisect_right(s_values, s_demand) - 1
        n_total_index = str(n_total_values[bisect_right(n_total_values, n_total) - 1])
        reduction_s = self._s_dict["Humusgehalt"][self.humus.value][s_index]
        reduction_n_total = self._s_dict["Nges"][n_total_index][s_index]
        return Decimal(reduction_s + reduction_n_total)

    def reduction_cao(self, field_type: FieldType, preservation: bool = False) -> Decimal:
        if self.ph is None:
            return Decimal()
        else:
            value = self.ph
        if preservation:
            value = self.optimal_ph(field_type)
        ph_values = self._cao_dict[field_type.value]["phWert"]
        index = bisect_left(self.to_decimal(ph_values), round_to_nearest(value, 1))
        reduction = self._cao_dict[field_type.value][self.soil_type.value][self.humus.value]
        try:
            return Decimal(-reduction[index] * 100 / 4)
        except IndexError:
            return Decimal(-reduction[-1] * 100 / 4)

    def optimal_ph(self, field_type) -> Decimal:
        return Decimal(
            str(self._cao_class_dict[field_type.value][self.soil_type.value][self.humus.value][2])
        )

    def class_p2o5(self, field_type: FieldType) -> str:
        if self.p2o5 is None:
            return ""
        values = self._p2o5_class_dict[field_type.value]
        index = bisect_right(values, self.p2o5) - 1
        return self._classes[index]

    def class_k2o(self, field_type: FieldType) -> str:
        if self.k2o is None:
            return ""
        values = self._k2o_class_dict[field_type.value][self.soil_type.value][self.humus.value]
        index = bisect_right(values, self.k2o) - 1
        return self._classes[index]

    def class_mgo(self, field_type: FieldType) -> str:
        if self.mg is None:
            return ""
        values = self._mgo_class_dict[field_type.value][self.soil_type.value][self.humus.value]
        index = bisect_right(values, self.mgo) - 1
        return self._classes[index]

    def class_ph(self, field_type: FieldType) -> str:
        if self.ph is None:
            return ""
        values = self._cao_class_dict[field_type.value][self.soil_type.value][self.humus.value]
        index = bisect_right(values, self.ph) - 1
        return self._classes[index]

    @staticmethod
    def to_decimal(values: list[float]):
        return [Decimal(str(value)) for value in values]

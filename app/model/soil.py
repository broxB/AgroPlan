from bisect import bisect_left, bisect_right
from dataclasses import dataclass
from decimal import Decimal

from database.model import Cultivation, SoilSample
from database.types import (
    CropClass,
    CropType,
    FieldType,
    HumusType,
    LegumeType,
    RemainsType,
    SoilType,
)
from utils import load_json


@dataclass
class Soil:
    soil_sample: SoilSample

    def __post_init__(self):
        self.year: int = self.soil_sample.year
        self.type: SoilType = self.soil_sample.soil_type  # schwach lehmiger Sand
        self.humus: HumusType = self.soil_sample.humus  # < 4%
        self.ph: Decimal = self.soil_sample.ph
        self.p2o5: Decimal = self.soil_sample.p2o5
        self.k2o: Decimal = self.soil_sample.k2o
        self.mg: Decimal = self.soil_sample.mg
        self._p2o5_dict = load_json("data/Richtwerte/Abschläge/abschlag_p2o5.json")
        self._k2o_dict = load_json("data/Richtwerte/Abschläge/abschlag_k2o.json")
        self._mgo_dict = load_json("data/Richtwerte/Abschläge/abschlag_mgo.json")
        self._cao_dict = load_json("data/Richtwerte/Abschläge/abschlag_cao_4jahre.json")
        self._s_dict = load_json("data/Richtwerte/Abschläge/abschlag_s.json")
        self._soil_dict = load_json("data/Richtwerte/Abschläge/bodenvorrat.json")
        self._pre_crop_dict = load_json("data/Richtwerte/Abschläge/vorfrucht.json")
        self._legume_dict = load_json("data/Richtwerte/Abschläge/leguminosen.json")
        self._classes = ["A", "B", "C", "D", "E"]
        self._p2o5_class = load_json("data/Richtwerte/Gehaltsklassen/klassen_p2o5.json")
        self._k2o_class = load_json("data/Richtwerte/Gehaltsklassen/klassen_k2o.json")
        self._mgo_class = load_json("data/Richtwerte/Gehaltsklassen/klassen_mgo.json")
        self._cao_class = load_json("data/Richtwerte/Gehaltsklassen/klassen_ph_wert.json")

    def main_crop_reductions(self, field_type: FieldType, nges: Decimal) -> list[Decimal]:
        sum = []
        for reduction in (
            self.reduction_n(field_type),
            self.reduction_p2o5(field_type),
            self.reduction_k2o(field_type),
            self.reduction_mgo(field_type),
            self.reduction_s(nges),
            self.reduction_cao(field_type),
        ):
            sum.append(reduction)

    def second_crop_reductions(self, cultivation: Cultivation) -> list[Decimal]:
        crop_class, crop_type, legume_rate = (
            cultivation.crop_class,
            cultivation.crop.crop_type,
            cultivation.legume_rate,
        )
        sum = [Decimal() for _ in range(6)]
        sum[0] += self.pre_crop_effect(crop_class, crop_type)
        sum[0] += self.legume_delivery(crop_type, legume_rate)
        return sum

    def reduction_n(self, field_type: FieldType) -> Decimal:
        return Decimal(self._soil_dict[self.humus.value][field_type.value])

    def reduction_p2o5(self, field_type: FieldType) -> Decimal:
        if self.p2o5 is None:
            return ""
        value = self.p2o5 / Decimal("2.291")  # calc element form
        values = self._p2o5_dict[field_type.value]["Werte"]
        reduction = self._p2o5_dict[field_type.value]["Abschläge"]
        index = bisect_right(values, value) - 1
        return Decimal(reduction[index])

    def reduction_k2o(self, field_type: FieldType) -> Decimal:
        if self.k2o is None:
            return ""
        value = self.k2o / Decimal("1.205")  # calc element form
        values = self._k2o_dict[field_type.value][self.type.value][self.humus.value]["Werte"]
        reduction = self._k2o_dict[field_type.value][self.type.value][self.humus.value][
            "Abschläge"
        ]
        index = bisect_right(values, value) - 1
        return Decimal(reduction[index])

    def reduction_mgo(self, field_type: FieldType) -> Decimal:
        if self.mgo is None:
            return ""
        value = self.mgo
        values = self._mgo_dict[field_type.value][self.type.value][self.humus.value]["Werte"]
        reduction = self._mgo_dict[field_type.value][self.type.value][self.humus.value][
            "Abschläge"
        ]
        index = bisect_right(values, value) - 1
        return Decimal(reduction[index])

    def reduction_s(self, nges: Decimal) -> Decimal:
        s_values = self._s_dict["Grenzwerte"]["Bedarf"]
        nges_values = self._s_dict["Grenzwerte"]["Nges"]
        s_index = bisect_right(s_values, self.humus) - 1
        nges_index = str(nges_values[bisect_right(nges_values, nges) - 1])
        reduction_s = self._s_dict["Humusgehalt"][self.humus.value][s_index]
        reduction_nges = self._s_dict["Nges"][nges_index][s_index]
        return Decimal(reduction_s + reduction_nges)

    def reduction_cao(self, field_type: FieldType) -> Decimal:
        if self.ph is None:
            return ""
        ph_values = self._cao_dict[field_type.value][self.type.value]["phWert"]
        index = bisect_right(ph_values, self.ph) - 1 if self.ph < ph_values[0] else 0
        reduction = self._cao_dict[field_type.value][self.type.value]
        return Decimal(reduction[index] * 100 / 4)

    def class_p2o5(self, field_type: FieldType) -> str:
        values = self._p2o5_class[field_type.value]
        index = bisect_right(values, self.p2o5) - 1
        return self._classes[index]

    def class_k2o(self, field_type: FieldType) -> str:
        values = self._k2o_class[field_type.value][self.type.value][self.humus.value]
        index = bisect_right(values, self.k2o) - 1
        return self._classes[index]

    def class_mgo(self, field_type: FieldType) -> str:
        values = self._mgo_class[field_type.value][self.type.value][self.humus.value]
        index = bisect_right(values, self.mgo) - 1
        return self._classes[index]

    def class_ph(self, field_type: FieldType) -> str:
        values = self._cao_class[field_type.value][self.type.value][self.humus.value]
        index = bisect_right(values, self.ph) - 1
        return self._classes[index]

    def optimal_ph(self, field_type) -> Decimal:
        return Decimal(self._cao_class[field_type.value][self.type.value][self.humus.value][2])

    def pre_crop_effect(
        self, crop_class: CropClass, crop_type: CropType, remains: RemainsType
    ) -> Decimal:
        if crop_class == CropClass.catch_crop:
            return Decimal(self._pre_crop_dict[crop_type.value][remains.value])
        else:
            return Decimal(self._pre_crop_dict[crop_type.value])

    def legume_delivery(self, crop_type: CropType, legume_rate: LegumeType) -> Decimal:
        if crop_type == CropType.permanent_grassland or crop_type == CropType.permanent_fallow:
            return Decimal(self._legume_dict["Grünland"][legume_rate.value])
        elif crop_type == CropType.alfalfa_grass or crop_type == CropType.clover_grass:
            rate = int(legume_rate.name.split("_")[1]) / 10
            return Decimal(self._legume_dict[crop_type.value] * rate)
        elif crop_type == CropType.alfalfa or crop_type == CropType.clover:
            return Decimal(self._legume_dict[crop_type.value])

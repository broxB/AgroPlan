from dataclasses import dataclass
from decimal import Decimal

import database.model as db
from database.types import CropClass, CropType, LegumeType, RemainsType
from model.crop import Crop
from utils import load_json


@dataclass
class Cultivation:
    cultivation: db.Cultivation
    crop: Crop

    def __post_init__(self):
        self.crop_class: CropClass = self.cultivation.crop_class
        self.crop_type: CropType = self.crop.crop_type
        self.crop_yield: Decimal = self.cultivation.crop_yield
        self.crop_protein: Decimal = (
            self.cultivation.crop_protein
            if self.cultivation.crop_protein
            else self.crop.target_protein
        )
        self.nmin_depth: int = self.crop.nmin_depth
        self.nmin: list[int] = self.cultivation.nmin
        self.legume_rate: LegumeType = self.cultivation.legume_rate
        self.remains: RemainsType = self.cultivation.remains
        self._pre_crop_dict = load_json("data/Richtwerte/Abschläge/vorfrucht.json")
        self._legume_dict = load_json("data/Richtwerte/Abschläge/leguminosen.json")

    def demand(self, demand_option, negative_output: bool = False):
        return self.crop.demand(
            crop_yield=self.crop_yield,
            crop_protein=self.crop_protein,
            demand_option=demand_option,
            negative_output=negative_output,
        )

    def reduction_nmin(self) -> Decimal:
        if self.crop.feedable:
            return Decimal()
        match self.nmin_depth:
            case 30:
                return Decimal(self.nmin[0])
            case 60:
                return Decimal(sum(self.nmin[:2]))
            case 90:
                return Decimal(sum(self.nmin[:2])) + Decimal(self.nmin[2]) / 2
            case _:
                return Decimal()

    def pre_crop_effect(self) -> Decimal:
        if self.crop_class == CropClass.catch_crop:
            return Decimal(self._pre_crop_dict[self.crop_type.value][self.remains.value])
        else:
            return Decimal(self._pre_crop_dict[self.crop_type.value])

    def legume_delivery(self) -> Decimal:
        if not self.crop.feedable:
            return Decimal()
        if (
            self.crop_type == CropType.permanent_grassland
            or self.crop_type == CropType.permanent_fallow
        ):
            return Decimal(self._legume_dict["Grünland"][self.legume_rate.value])
        elif self.crop_type == CropType.alfalfa_grass or self.crop_type == CropType.clover_grass:
            rate = int(self.legume_rate.name.split("_")[1]) / 10
            return Decimal(self._legume_dict[self.crop_type.value] * rate)
        elif self.crop_type == CropType.alfalfa or self.crop_type == CropType.clover:
            return Decimal(self._legume_dict[self.crop_type.value])
        return Decimal()

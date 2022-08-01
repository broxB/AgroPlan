from dataclasses import dataclass
from decimal import Decimal

import database.model as db
from database.types import CropClass, CropType, DemandType, LegumeType, RemainsType
from model.crop import Crop
from utils import load_json


def create_cultivation(cultivation, crop):
    if cultivation.crop_class == CropClass.catch_crop:
        return CatchCrop(cultivation, crop)
    elif cultivation.crop_class == CropClass.main_crop:
        return MainCrop(cultivation, crop)
    else:
        return SecondCrop(cultivation, crop)


@dataclass
class Cultivation:
    Cultivation: db.Cultivation
    crop: Crop

    def __post_init__(self):
        self.crop_class: CropClass = self.Cultivation.crop_class
        self.crop_type: CropType = self.crop.crop_type
        self.crop_yield: Decimal = self.Cultivation.crop_yield
        self.crop_protein: Decimal = (
            self.Cultivation.crop_protein
            if self.Cultivation.crop_protein
            else self.crop.target_protein
        )
        self.nmin_depth: int = self.crop.nmin_depth
        self.nmin: list[int] = self.Cultivation.nmin
        self.legume_rate: LegumeType = self.Cultivation.legume_rate
        self.remains: RemainsType = self.Cultivation.remains
        self._pre_crop_dict = load_json("data/Richtwerte/Abschläge/vorfrucht.json")
        self._legume_dict = load_json("data/Richtwerte/Abschläge/leguminosen.json")

    def demand(self, demand_option, negative_output: bool = True) -> list[Decimal]:
        demands = []
        demands.append(
            self.crop.demand_crop(
                crop_yield=self.crop_yield,
                crop_protein=self.crop_protein,
            )
        )
        if demand_option == DemandType.demand or self.remains == RemainsType.removed:
            demands.append(self.crop.demand_byproduct(self.crop_yield))
        demands = [sum(demand) for demand in zip(*demands)]
        if negative_output:
            demands = [(demand * -1) for demand in demands]
        return demands

    def pre_crop_effect(self) -> Decimal:
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

    def reduction(self) -> Decimal:
        return Decimal()


class MainCrop(Cultivation):
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

    def reduction(self) -> list[Decimal]:
        return self.reduction_nmin() + self.legume_delivery()


class SecondCrop(Cultivation):
    def reduction(self) -> Decimal:
        return self.legume_delivery()


class CatchCrop(Cultivation):
    def demand(self, *args, **kwargs) -> list[Decimal]:
        return [Decimal("-60"), *[Decimal()] * 5]

    def pre_crop_effect(self) -> Decimal:
        return Decimal(self._pre_crop_dict[self.crop_type.value][self.remains.value])

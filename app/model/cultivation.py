from __future__ import annotations

from decimal import Decimal

import app.database.model as db
import app.model.guidelines as guidelines
from app.database.types import CropClass, CropType, DemandType, LegumeType, ResidueType
from app.model.crop import Crop


def create_cultivation(
    cultivation: db.Cultivation, crop: Crop
) -> MainCrop | SecondCrop | CatchCrop:
    if cultivation.crop_class == CropClass.catch_crop:
        return CatchCrop(cultivation, crop, guidelines)
    elif cultivation.crop_class == CropClass.main_crop:
        return MainCrop(cultivation, crop, guidelines)
    else:
        return SecondCrop(cultivation, crop, guidelines)


class Cultivation:
    def __init__(self, Cultivation: db.Cultivation, crop: Crop, guidelines: guidelines):
        self.crop = crop
        self.crop_class: CropClass = Cultivation.crop_class
        self.crop_type: CropType = crop.crop_type
        self.crop_yield: Decimal = Cultivation.crop_yield
        self.crop_protein: Decimal = (
            Cultivation.crop_protein if Cultivation.crop_protein else crop.target_protein
        )
        self.nmin_depth: int = crop.nmin_depth
        self.nmin: list[int] = Cultivation.nmin
        self.legume_rate: LegumeType = Cultivation.legume_rate
        self.residues: ResidueType = Cultivation.residues
        self.guidelines = guidelines

    def demand(self, demand_option, negative_output: bool = True) -> list[Decimal]:
        demands = []
        demands.append(
            self.crop.demand_crop(
                crop_yield=self.crop_yield,
                crop_protein=self.crop_protein,
            )
        )
        if demand_option == DemandType.demand or self.residues == ResidueType.removed:
            demands.append(self.crop.demand_byproduct(self.crop_yield))
        demands = [sum(demand) for demand in zip(*demands)]
        if negative_output:
            demands = [(demand * -1) for demand in demands]
        return demands

    def pre_crop_effect(self) -> Decimal:
        pre_crop_effect: dict = self.guidelines.pre_crop_effect()
        return Decimal(pre_crop_effect[self.crop_type.value])

    def legume_delivery(self) -> Decimal:
        if not self.crop.feedable:
            return Decimal()
        legume_delivery: dict = self.guidelines.legume_delivery()
        if (
            self.crop_type == CropType.permanent_grassland
            or self.crop_type == CropType.permanent_fallow
        ):
            return Decimal(legume_delivery["Grünland"][self.legume_rate.value])
        elif self.crop_type == CropType.alfalfa_grass or self.crop_type == CropType.clover_grass:
            rate = int(self.legume_rate.name.split("_")[1]) / 10
            return Decimal(legume_delivery[self.crop_type.value] * rate)
        elif self.crop_type == CropType.alfalfa or self.crop_type == CropType.clover:
            return Decimal(legume_delivery[self.crop_type.value])
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
        return Decimal(self._pre_crop_dict[self.crop_type.value][self.residues.value])

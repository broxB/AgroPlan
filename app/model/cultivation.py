from __future__ import annotations

from decimal import Decimal

from loguru import logger

import app.database.model as db
from app.database.types import (
    CropType,
    CultivationType,
    DemandType,
    LegumeType,
    NminType,
    ResidueType,
)

from . import guidelines
from .balance import Balance
from .crop import Crop


def create_cultivation(
    cultivation: db.Cultivation, crop: Crop
) -> MainCrop | SecondCrop | CatchCrop:
    if cultivation.cultivation_type is CultivationType.catch_crop:
        return CatchCrop(cultivation, crop)
    elif cultivation.cultivation_type is CultivationType.main_crop:
        return MainCrop(cultivation, crop)
    else:
        return SecondCrop(cultivation, crop)


class Cultivation:
    """
    Class to represent a cultivation containing a crop.
    """

    def __init__(
        self, Cultivation: db.Cultivation, crop: Crop, guidelines: guidelines = guidelines
    ):
        self.crop = crop
        self.cultivation_type: CultivationType = Cultivation.cultivation_type
        self.crop_type: CropType = crop.crop_type
        self.crop_yield: Decimal = Cultivation.crop_yield
        self.crop_protein: Decimal = (
            Cultivation.crop_protein if Cultivation.crop_protein else crop.target_protein
        )
        self.nmin_depth: NminType = crop.nmin_depth
        self.nmin_30: int = Cultivation.nmin_30
        self.nmin_60: int = Cultivation.nmin_60
        self.nmin_90: int = Cultivation.nmin_90
        self.legume_rate: LegumeType = Cultivation.legume_rate
        self.residues: ResidueType = Cultivation.residues
        self._guidelines = guidelines

    def demand(
        self,
        option_p2o5: DemandType,
        option_k2o: DemandType,
        option_mgo: DemandType,
        negative_output: bool = True,
    ) -> Balance:
        """
        Calculate the nutrient demand of the cultivated crop.

        :param option_p2o5:
            `DemandType` for P2O5
        :param option_k2o:
            `DemandType` for K2O
        :param option_mgo:
            `DemandType` for MgO
        :param negative_output:
            If demand should be output in negative numbers, defaults to `True`
        :return:
            `Balance` containing all the nutrient values.
        """
        crop_demand = self.crop.demand_crop(
            crop_yield=self.crop_yield,
            crop_protein=self.crop_protein,
        )
        if (
            any(option is DemandType.demand for option in [option_p2o5, option_k2o, option_mgo])
            or self.residues is ResidueType.main_removed
        ):
            byp_demand = self.crop.demand_byproduct(self.crop_yield)
            if option_p2o5 is DemandType.removal:
                byp_demand.p2o5 = 0
            if option_k2o is DemandType.removal:
                byp_demand.k2o = 0
            if option_mgo is DemandType.removal:
                byp_demand.mgo = 0
        else:
            byp_demand = Balance()
        demand = Balance("Crop needs")
        if negative_output:
            demand -= crop_demand + byp_demand
        else:
            demand += crop_demand + byp_demand
        return demand

    def pre_crop_effect(self) -> Decimal:
        """
        Delayed nitrogen supply of the previous crop through degradation.
        """
        pre_crop_effect: dict = self._guidelines.pre_crop_effect()
        return Decimal(pre_crop_effect[self.crop_type.value])

    def legume_delivery(self) -> Decimal:
        """
        Provided nitrogen through legume nitrogen fixation.
        """
        if not self.crop.feedable:
            return Decimal()
        legume_delivery: dict = self._guidelines.legume_delivery()
        if self.crop_type is CropType.permanent_grassland:
            return Decimal(legume_delivery["Grünland"][self.legume_rate.value])
        elif self.crop_type is CropType.alfalfa_grass or self.crop_type is CropType.clover_grass:
            try:
                rate = int(self.legume_rate.name.split("_")[-1]) / 10
            except ValueError or TypeError:
                logger.warning(f"{self} has {self.legume_rate} which is not valid.")
                rate = 0
            return Decimal(legume_delivery[self.crop_type.value] * rate)
        elif self.crop_type is CropType.alfalfa or self.crop_type is CropType.clover:
            return Decimal(legume_delivery[self.crop_type.value])
        return Decimal()

    def reduction(self) -> Decimal:
        return Decimal()

    def is_class(self, cultivation_type: CultivationType) -> bool:
        return self.cultivation_type is cultivation_type if cultivation_type else True


class MainCrop(Cultivation):
    def reduction_nmin(self) -> Decimal:
        """
        Available mineral nitrogen in the soil.
        """
        if self.crop.feedable:
            return Decimal()
        match self.nmin_depth:
            case NminType.nmin_0:
                return Decimal()
            case NminType.nmin_30:
                return Decimal(self.nmin_30)
            case NminType.nmin_60:
                return Decimal(self.nmin_30 + self.nmin_60)
            case NminType.nmin_90:
                return Decimal(self.nmin_30 + self.nmin_60) + Decimal(self.nmin_90) / 2

    def reduction(self) -> Decimal:
        return self.reduction_nmin() + self.legume_delivery()

    def __repr__(self) -> str:
        return f"<Main crop: {self.crop.name}>"


class SecondCrop(Cultivation):
    def reduction(self) -> Decimal:
        return self.legume_delivery()

    def __repr__(self) -> str:
        return f"<Second crop: {self.crop.name}>"


class CatchCrop(Cultivation):
    def demand(self, *args, negative_output: bool = True, **kwargs) -> Balance:
        if negative_output:
            return Balance("Crop demand", n=Decimal(-60))
        return Balance("Crop demand", n=Decimal(60))

    def pre_crop_effect(self) -> Decimal:
        pre_crop_effect: dict = self._guidelines.pre_crop_effect()
        return Decimal(pre_crop_effect[self.crop_type.value][self.residues.value])

    def __repr__(self) -> str:
        return f"<Catch crop: {self.crop.name}>"

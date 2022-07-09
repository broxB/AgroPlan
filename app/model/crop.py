from dataclasses import dataclass
from decimal import Decimal

import database.model as db
from database.types import CropClass, CropType, DemandType, RemainsType
from utils import load_json


@dataclass
class Crop:
    Crop: db.Crop
    crop_class: CropClass

    def __post_init__(self):
        self.name: str = self.Crop.name  # W.-Gerste
        self.kind: str = self.Crop.kind  # Wintergerste
        self.crop_class: CropClass = self.crop_class  # Hauptfrucht
        self.crop_type: CropType = self.Crop.crop_type  # Getreide
        self.feedable: bool = self.Crop.feedable  # Feldfutter
        self.remains: list[RemainsType] = self.Crop.remains
        self.nmin_depth: int = self.Crop.nmin_depth
        self.target_demand: Decimal = self.Crop.target_demand
        self.target_yield: Decimal = self.Crop.target_yield
        self.var_yield: list[Decimal] = self.Crop.var_yield
        self.target_protein: Decimal = self.Crop.target_protein
        self.var_protein: list[Decimal] = self.Crop.var_protein
        self.n: Decimal = self.Crop.n
        self.p2o5: Decimal = self.Crop.p2o5
        self.k2o: Decimal = self.Crop.k2o
        self.mgo: Decimal = self.Crop.mgo
        self.byproduct: Decimal = self.Crop.byproduct
        self.byp_ratio: Decimal = self.Crop.byp_ratio
        self.byp_n: Decimal = self.Crop.byp_n
        self.byp_p2o5: Decimal = self.Crop.byp_p2o5
        self.byp_k2o: Decimal = self.Crop.byp_k2o
        self.byp_mgo: Decimal = self.Crop.byp_mgo
        self._s_dict = load_json("data/Richtwerte/Nährstoffwerte/schwefelbedarf.json")

    def demand_crop(
        self,
        crop_yield: Decimal,
        crop_protein: Decimal,
    ) -> list[Decimal]:
        demands = [
            self._n(crop_yield, crop_protein),
            self._nutrient(crop_yield, self.p2o5),
            self._nutrient(crop_yield, self.k2o),
            self._nutrient(crop_yield, self.mgo),
            self.s_demand,
            Decimal(),  # Kalk
        ]
        return demands

    def demand_byproduct(self, crop_yield: Decimal) -> list[Decimal]:
        demands = [
            Decimal(),  # Stickstoff
            self._nutrient_byproduct(crop_yield, self.byp_p2o5),
            self._nutrient_byproduct(crop_yield, self.byp_k2o),
            self._nutrient_byproduct(crop_yield, self.byp_mgo),
            Decimal(),  # Schwefel
            Decimal(),  # Kalk
        ]
        return demands

    def is_class(self, crop_class: CropClass) -> bool:
        return self.crop_class == crop_class if crop_class else True

    @property
    def s_demand(self) -> Decimal:
        return Decimal(str(self._s_dict.get(self.name, 0)))

    def _n(self, crop_yield: Decimal, crop_protein: Decimal) -> Decimal:
        i = 0 if self.target_yield > crop_yield else 1
        return (
            self.target_demand
            + Decimal(str(self.var_yield[i])) * (crop_yield - self.target_yield)
            + self.target_protein * (crop_protein - self.target_protein)
        )

    @staticmethod
    def _nutrient(crop_yield: Decimal, nutrient: Decimal) -> Decimal:
        return nutrient * crop_yield

    def _nutrient_byproduct(self, crop_yield: Decimal, byp_nutrient: Decimal) -> Decimal:
        return self.byp_ratio * byp_nutrient * crop_yield

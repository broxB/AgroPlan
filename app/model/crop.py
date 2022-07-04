from dataclasses import dataclass
from decimal import Decimal

import database.model as db
from database.types import CropClass, CropType, DemandType, RemainsType
from utils import load_json


@dataclass
class Crop:
    crop: db.Crop
    crop_class: CropClass

    def __post_init__(self):
        self.name: str = self.crop.name  # W.-Gerste
        self.kind: str = self.crop.kind  # Wintergerste
        self.crop_class: CropClass = self.crop_class  # Hauptfrucht
        self.crop_type: CropType = self.crop.crop_type  # Getreide
        self.feedable: bool = self.crop.feedable  # Feldfutter
        self.remains: list[RemainsType] = self.crop.remains
        self.nmin_depth: int = self.crop.nmin_depth
        self.target_demand: Decimal = self.crop.target_demand
        self.target_yield: Decimal = self.crop.target_yield
        self.var_yield: list[Decimal] = self.crop.var_yield
        self.target_protein: Decimal = self.crop.target_protein
        self.var_protein: list[Decimal] = self.crop.var_protein
        self.n: Decimal = self.crop.n
        self.p2o5: Decimal = self.crop.p2o5
        self.k2o: Decimal = self.crop.k2o
        self.mgo: Decimal = self.crop.mgo
        self.byproduct: Decimal = self.crop.byproduct
        self.byp_ratio: Decimal = self.crop.byp_ratio
        self.byp_n: Decimal = self.crop.byp_n
        self.byp_p2o5: Decimal = self.crop.byp_p2o5
        self.byp_k2o: Decimal = self.crop.byp_k2o
        self.byp_mgo: Decimal = self.crop.byp_mgo
        self._s_dict = load_json("data/Richtwerte/Nährstoffwerte/schwefelbedarf.json")

    def demand_crop(
        self,
        crop_yield: Decimal,
        crop_protein: Decimal,
    ) -> list[Decimal]:
        nutrients = [self.p2o5, self.k2o, self.mgo]
        demands = [
            self._n(crop_yield, crop_protein),
            *[self._nutrient(crop_yield, x) for x in nutrients],
            self.s_demand,
            Decimal(),  # Kalk
        ]
        return demands

    def demand_byproduct(self, crop_yield: Decimal) -> list[Decimal]:
        nutrients = [self.byp_p2o5, self.byp_k2o, self.byp_mgo]
        demands = [
            Decimal(),  # Stickstoff
            *[self._nutrient_byproduct(crop_yield, x) for x in nutrients],
            Decimal(),  # Schwefel
            Decimal(),  # Kalk
        ]
        return demands

    def is_class(self, crop_class: CropClass) -> bool:
        return self.crop_class == crop_class if crop_class else True

    def _n(self, crop_yield: Decimal, crop_protein: Decimal) -> Decimal:
        i = 0 if self.target_yield > crop_yield else 1
        return (
            self.target_demand
            + Decimal(str(self.var_yield[i])) * (crop_yield - self.target_yield)
            + self.target_protein * (crop_protein - self.target_protein)
        )

    def _nutrient(self, crop_yield: Decimal, nutrient: Decimal) -> Decimal:
        return nutrient * crop_yield

    def _nutrient_byproduct(self, crop_yield: Decimal, byp_nutrient: Decimal) -> Decimal:
        return self.byp_ratio * byp_nutrient * crop_yield

    @property
    def s_demand(self) -> Decimal:
        return Decimal(str(self._s_dict.get(self.name, 0)))

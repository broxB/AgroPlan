from decimal import Decimal

import app.database.model as db
import app.model.guidelines as guidelines
from app.database.types import CropClass, CropType, RemainsType


class Crop:
    def __init__(self, Crop: db.Crop, crop_class: CropClass, guidelines: guidelines = guidelines):
        self.name: str = Crop.name  # W.-Gerste
        self.kind: str = Crop.kind  # Wintergerste
        self.crop_class: CropClass = crop_class  # Hauptfrucht
        self.crop_type: CropType = Crop.crop_type  # Getreide
        self.feedable: bool = Crop.feedable  # Feldfutter
        self.remains: list[RemainsType] = Crop.remains
        self.nmin_depth: int = Crop.nmin_depth
        self.target_demand: Decimal = Crop.target_demand
        self.target_yield: Decimal = Crop.target_yield
        self.var_yield: list[Decimal] = Crop.var_yield
        self.target_protein: Decimal = Crop.target_protein
        self.var_protein: list[Decimal] = Crop.var_protein
        self.n: Decimal = Crop.n
        self.p2o5: Decimal = Crop.p2o5
        self.k2o: Decimal = Crop.k2o
        self.mgo: Decimal = Crop.mgo
        self.byproduct: str = Crop.byproduct
        self.byp_ratio: Decimal = Crop.byp_ratio
        self.byp_n: Decimal = Crop.byp_n
        self.byp_p2o5: Decimal = Crop.byp_p2o5
        self.byp_k2o: Decimal = Crop.byp_k2o
        self.byp_mgo: Decimal = Crop.byp_mgo
        self.guidelines = guidelines

    def demand_crop(
        self,
        crop_yield: Decimal,
        crop_protein: Decimal,
    ) -> list[Decimal]:
        demands = [
            self._n_demand(crop_yield, crop_protein),
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
        sulfur_needs: dict = self.guidelines.sulfur_needs()
        return Decimal(str(sulfur_needs.get(self.name, 0)))

    def _n_demand(self, crop_yield: Decimal, crop_protein: Decimal) -> Decimal:
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

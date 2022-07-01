from dataclasses import dataclass
from dataclasses import field as field_
from decimal import Decimal

import database.model as db
from database.types import CropClass, FertClass, MeasureType
from model import Crop, Fertilization, Field


@dataclass
class Cultivation:
    field: Field
    cultivations: list[db.Cultivation] = field_(default_factory=list)
    fertilizations: list[Fertilization] = field_(default_factory=list)

    # summe nges
    def n_ges(
        self, *, measure: MeasureType = None, crop_class: CropClass = None, netto: bool = False
    ) -> Decimal:
        nges = Decimal()
        for fertilization in self.fertilizations:
            nges += fertilization.n_ges(measure, crop_class, netto)
        return nges

    # summe düngung
    def sum_fertilizations(self, fert_class: FertClass = None):
        nutrients = []
        for fertilization in self.fertilizations:
            nutrients.append(fertilization.nutrients(self.field.type_, fert_class))
        return [sum(nutrient) for nutrient in zip(*nutrients)]

    # summe bedarf
    def sum_demands(self, crop_class: CropClass = None):
        demands = []
        for cultivation in self.cultivations:
            if cultivation.crop_class == crop_class if crop_class else True:
                crop = Crop(cultivation.crop, cultivation.crop_class)
                demands.append(
                    crop.demand(
                        crop_yield=cultivation.crop_yield,
                        crop_protein=cultivation.crop_protein,
                        demand_option=cultivation.demand_option,
                    )
                )
            else:
                demands.append([Decimal() for _ in range(5)])
        return [sum(demand) for demand in zip(*demands)]

    # summe bodenvorrat
    def sum_reductions(self):
        pass

    # vorfrucht

from dataclasses import dataclass
from dataclasses import field as field_
from decimal import Decimal

import database.model as db
from database.types import CropClass, FertClass, MeasureType
from model.crop import Crop
from model.fertilization import Fertilization
from model.field import Field
from model.soil import Soil


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
    def sum_fertilizations(self, fert_class: FertClass = None) -> list[Decimal]:
        nutrients = []
        for fertilization in self.fertilizations:
            if fertilization.fertilizer.is_class(fert_class):
                nutrients.append(fertilization.nutrients(self.field.type_))
        return [sum(nutrient) for nutrient in zip(*nutrients)]

    # summe bedarf
    def sum_demands(
        self, crop_class: CropClass = None, negative_output: bool = True
    ) -> list[Decimal]:
        demands = []
        for cultivation in self.cultivations:
            if cultivation.crop_class == crop_class if crop_class else True:
                crop = Crop(cultivation.crop, cultivation.crop_class)
                demands.append(
                    crop.demand(
                        crop_yield=cultivation.crop_yield,
                        crop_protein=cultivation.crop_protein,
                        demand_option=cultivation.demand_option,
                        negative_output=negative_output,
                    )
                )
            else:
                demands.append([Decimal() for _ in range(5)])
        return [sum(demand) for demand in zip(*demands)]

    # summe bodenvorrat
    def sum_reductions(self, crop_class: CropClass = None) -> list[Decimal]:
        prev_year = self.field.year - 1
        # Vorjahres CaO Saldo
        saldo = [prev_year.sum_fertilizations(), prev_year.sum_demands()]
        cao_saldo = [sum(num) for num in zip(*saldo)][6]

        # Vorjahres Nges
        spring_nges = prev_year.n_ges(measure=MeasureType.spring)
        # Aktuelle Herbst Nges zur Zwischenfrucht
        fall_nges = prev_year.n_ges(measure=MeasureType.fall, crop_class=CropClass.catch_crop)
        # N Nachlieferung aus Vorjahr
        nges = (spring_nges + fall_nges) * Decimal("0.1")

        soil = Soil(self.field.soil_sample)
        reductions = []
        for cultivation in self.cultivations:
            if cultivation.crop_class == crop_class:
                if crop_class == CropClass.main_crop:
                    nges = self.n_ges()
                    reductions.append(soil.main_crop_reductions(self.field.type_, nges))
                elif crop_class == CropClass.second_crop:
                    reductions.append(soil.second_crop_reductions(self.field.type_))
            elif crop_class is None:
                reductions = [
                    soil.main_crop_reductions(self.field.type_),
                    soil.second_crop_reductions(self.field.type_),
                ]
                return [sum(reduction) for reduction in zip(*reductions)]
                # else:
                #     raise ValueError(
                #         f"CropClass {crop_class} is not supported, use main_crop or second_crop."
                #     )
        return [Decimal() for _ in range(6)]

    # vorfrucht
    def previous_crop(self):
        pass

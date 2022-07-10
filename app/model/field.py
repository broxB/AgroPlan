from dataclasses import dataclass
from dataclasses import field as field_
from decimal import Decimal

import database.model as db
import model as md
from database.types import CropClass, DemandType, FertClass, FieldType, MeasureType
from database.utils import create_session
from loguru import logger
from model.soil import Soil


@dataclass
class Field:
    Field: db.Field
    first_year: bool = True
    cultivations: list[md.Cultivation] = field_(default_factory=list)
    fertilizations: list[md.Fertilization] = field_(default_factory=list)

    def __post_init__(self):
        self.base_id: int = self.Field.base_id
        self.area: Decimal = self.Field.area
        self.year: int = self.Field.year
        self.field_type: FieldType = self.Field.field_type
        self.red_region: bool = self.Field.red_region
        self.demand_option: DemandType = self.Field.demand_type
        self.saldo: db.Saldo = self.Field.saldo
        self.field_prev_year = self._field_prev_year()

    def n_total(
        self, *, measure: MeasureType = None, crop_class: CropClass = None, netto: bool = False
    ) -> Decimal:
        n_total = Decimal()
        for fertilization in self.fertilizations:
            n_total += fertilization.n_total(measure, crop_class, netto)
        return n_total

    def sum_fertilizations(self, fert_class: FertClass = None) -> list[Decimal]:
        nutrients = []
        for fertilization in self.fertilizations:
            if fertilization.fertilizer.is_class(fert_class):
                nutrients.append(fertilization.nutrients(self.field_type))
        if not nutrients:
            nutrients.append([Decimal()] * 6)
        return [sum(nutrient) for nutrient in zip(*nutrients)]

    def sum_demands(self, negative_output: bool = True) -> list[Decimal]:
        demands = []
        for cultivation in self.cultivations:
            if cultivation.crop_class == CropClass.catch_crop:
                continue
            demands.append(
                cultivation.demand(
                    demand_option=self.demand_option,
                    negative_output=negative_output,
                )
            )
        if not demands:
            demands.append([Decimal()] * 6)
        return [sum(demand) for demand in zip(*demands)]

    def sum_reductions(self) -> list[Decimal]:
        reductions = []
        for cultivation in self.cultivations:
            if cultivation.crop_class == CropClass.main_crop:
                reductions.append(self.main_crop_reductions(self.soil_sample))
            elif cultivation.crop_class == CropClass.second_crop:
                reductions.append(self.second_crop_reductions())
        if not reductions:
            reductions.append([Decimal()] * 6)
        return [sum(reduction) for reduction in zip(*reductions)]

    def main_crop_reductions(self, soil: Soil) -> list[Decimal]:
        reductions = [Decimal()] * 6
        if not self.main_crop:
            return reductions
        if soil:
            if self.demand_option == DemandType.demand:
                for i, reduction in enumerate(
                    (
                        soil.reduction_p2o5(self.field_type),
                        soil.reduction_k2o(self.field_type),
                        soil.reduction_mgo(self.field_type),
                    ),
                    start=1,
                ):
                    reductions[i] += reduction
            reductions[0] += soil.reduction_n(self.field_type)
            reductions[4] += soil.reduction_s(
                self.n_total(crop_class=CropClass.main_crop), self.main_crop.crop.s_demand
            )
            if soil.year + 3 < self.year:
                reductions[5] += soil.reduction_cao(self.field_type, preservation=True)
            else:
                reductions[5] += soil.reduction_cao(self.field_type)
        if self.field_prev_year:
            reductions[5] += self.cao_saldo()
            reductions[0] += self.n_redelivery()
        if self.field_type == FieldType.cropland and self.previous_crop:
            reductions[0] += self.previous_crop.pre_crop_effect()
        reductions[0] += self.main_crop.reduction_nmin()
        reductions[0] += self.main_crop.legume_delivery()
        return reductions

    def second_crop_reductions(self) -> list[Decimal]:
        reductions = [Decimal()] * 6
        if not self.second_crop:
            return reductions
        reductions[0] += self.main_crop.pre_crop_effect()
        reductions[0] += self.second_crop.legume_delivery()
        return reductions

    def n_redelivery(self) -> Decimal:
        prev_spring_n_total = self.field_prev_year.n_total(measure=MeasureType.spring)
        fall_n_total = self.n_total(measure=MeasureType.fall, crop_class=CropClass.catch_crop)
        n_total = (prev_spring_n_total + fall_n_total) * Decimal("0.1")
        return n_total

    def cao_saldo(self) -> Decimal:
        return self.field_prev_year.saldo.cao

    @property
    def main_crop(self) -> md.Cultivation:
        for cultivation in self.cultivations:
            if cultivation.crop_class == CropClass.main_crop:
                return cultivation
        return None

    @property
    def second_crop(self) -> md.Cultivation:
        for cultivation in self.cultivations:
            if cultivation.crop_class == CropClass.second_crop:
                return cultivation
        return None

    @property
    def catch_crop(self) -> md.Cultivation:
        for cultivation in self.cultivations:
            if cultivation.crop_class == CropClass.catch_crop:
                return cultivation
        return None

    @property
    def previous_crop(self) -> md.Cultivation:
        if self.catch_crop:
            return self.catch_crop
        elif self.field_prev_year:
            if self.field_prev_year.second_crop:
                return self.field_prev_year.second_crop
            elif self.field_prev_year.main_crop:
                return self.field_prev_year.main_crop
        else:
            return None

    @property
    def soil_sample(self):
        soil_sample = (
            max(self.Field.soil_samples, key=lambda x: x.year) if self.Field.soil_samples else None
        )
        if soil_sample:
            return md.Soil(soil_sample)
        return None

    @property
    def overfertilization(self) -> bool:
        n_total, nh4 = self._sum_fall_fertilizations()
        if (
            self.field_type == FieldType.grassland
            or self.main_crop
            and self.main_crop.crop.feedable
        ):
            if n_total > (80 if not self.red_region else 60):
                logger.info(
                    f"{self.Field.base_field.name}: {n_total=:.0f} is violating the maximum value for fall fertilizations."
                )
                return True
        elif n_total > 60 or nh4 > 30:
            logger.info(
                f"{self.Field.base_field.name}: {n_total=:.0f} or {nh4=:.0f} are violating the maximum values for fall fertilizations."
            )
            return True
        return False

    def _sum_fall_fertilizations(self):
        sum_n = [(0, 0)]
        for fertilization in self.fertilizations:
            if (
                fertilization.fertilizer.is_class(FertClass.organic)
                and fertilization.measure == MeasureType.fall
            ):
                n_total, nh4 = [
                    fertilization.amount * n
                    for n in (fertilization.fertilizer.n, fertilization.fertilizer.nh4)
                ]
                sum_n.append((n_total, nh4))
        return [sum(n) for n in zip(*sum_n)]

    def _field_prev_year(self):
        if not self.first_year:
            return
        session = create_session()
        year = self.year - 1
        db_field = (
            session.query(db.Field)
            .filter(db.Field.base_id == self.base_id, db.Field.year == year)
            .one_or_none()
        )
        if db_field:
            field = md.Field(db_field, False)
            for db_cultivation in db_field.cultivations:
                crop = md.Crop(db_cultivation.crop, db_cultivation.crop_class)
                cultivation = md.Cultivation(db_cultivation, crop)
                field.cultivations.append(cultivation)
            for db_fertilization in db_field.fertilizations:
                fertilizer = md.Fertilizer(db_fertilization.fertilizer)
                crop = md.Crop(
                    db_fertilization.cultivation.crop, db_fertilization.cultivation.crop_class
                )
                fertilization = md.Fertilization(
                    db_fertilization, fertilizer, crop, db_fertilization.cultivation.crop_class
                )
                field.fertilizations.append(fertilization)
        else:
            field = None
        return field

from dataclasses import dataclass
from dataclasses import field as field_
from decimal import Decimal

import database.model as db
import model as md
from database.types import CropClass, FertClass, FieldType, MeasureType
from database.utils import create_session
from model.soil import Soil


@dataclass
class Plan:
    field: md.Field
    cultivations: list[md.Cultivation] = field_(default_factory=list)
    fertilizations: list[md.Fertilization] = field_(default_factory=list)

    def __post_init__(self):
        self.field_type = self.field.field_type
        self.soil_sample = self.field.soil_sample

    def n_ges(
        self, *, measure: MeasureType = None, crop_class: CropClass = None, netto: bool = False
    ) -> Decimal:
        nges = Decimal()
        for fertilization in self.fertilizations:
            nges += fertilization.n_ges(measure, crop_class, netto)
        return nges

    def sum_fertilizations(self, fert_class: FertClass = None) -> list[Decimal]:
        nutrients = []
        for fertilization in self.fertilizations:
            if fertilization.fertilizer.is_class(fert_class):
                nutrients.append(fertilization.nutrients(self.field.field_type))
        if not nutrients:
            nutrients.append([Decimal()] * 6)
        return [sum(nutrient) for nutrient in zip(*nutrients)]

    def sum_demands(self, negative_output: bool = True) -> list[Decimal]:
        demands = []
        for cultivation in self.cultivations:
            demands.append(
                cultivation.demand(
                    demand_option=self.field.demand_option,
                    negative_output=negative_output,
                )
            )
        if not demands:
            demands.append([Decimal()] * 6)
        return [sum(demand) for demand in zip(*demands)]

    def sum_reductions(self) -> list[Decimal]:
        reductions = []
        if self.soil_sample:
            soil = md.Soil(self.soil_sample)
            for cultivation in self.cultivations:
                if cultivation.crop_class == CropClass.main_crop:
                    reductions.append(self.main_crop_reductions(soil))
                elif cultivation.crop_class == CropClass.second_crop:
                    reductions.append(self.second_crop_reductions())
        if self.prev_year:
            # reductions.append(self.cao_saldo)
            reductions.append(self.n_redelivery)
        if not reductions:
            reductions.append([Decimal()] * 6)
        return [sum(reduction) for reduction in zip(*reductions)]

    def main_crop_reductions(self, soil: Soil) -> list[Decimal]:
        sum = []
        for reduction in (
            soil.reduction_n(self.field_type),
            soil.reduction_p2o5(self.field_type),
            soil.reduction_k2o(self.field_type),
            soil.reduction_mgo(self.field_type),
            soil.reduction_s(
                self.n_ges(crop_class=CropClass.main_crop), self.main_crop.crop.s_demand
            ),
            soil.reduction_cao(self.field_type),
        ):
            sum.append(reduction)
        if self.field_type == FieldType.cropland and self.previous_crop:
            sum[0] += self.previous_crop.pre_crop_effect()
        sum[0] += self.main_crop.reduction_nmin()
        sum[0] += self.main_crop.legume_delivery()
        return sum

    def second_crop_reductions(self) -> list[Decimal]:
        sum = [Decimal()] * 6
        sum[0] += self.main_crop.pre_crop_effect()
        sum[0] += self.second_crop.legume_delivery()
        return sum

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
    def n_redelivery(self) -> Decimal:
        nges = [Decimal()] * 6
        prev_spring_nges = self.prev_year.n_ges(measure=MeasureType.spring)
        fall_nges = self.n_ges(measure=MeasureType.fall, crop_class=CropClass.catch_crop)
        nges[0] = (prev_spring_nges + fall_nges) * Decimal("0.1")
        return nges

    @property
    def cao_saldo(self) -> Decimal:
        cao_saldo = [Decimal()] * 6
        saldo = [self.prev_year.sum_fertilizations(), self.prev_year.sum_demands()]
        cao_saldo[5] = [sum(num) for num in zip(*saldo)][5]
        return cao_saldo

    @property
    def previous_crop(self) -> md.Cultivation:
        if self.catch_crop is None and self.prev_year:
            if self.prev_year.second_crop:
                return self.prev_year.second_crop
            elif self.prev_year.main_crop:
                return self.prev_year.main_crop
        else:
            return self.catch_crop
        return None

    @property
    def prev_year(self):
        session = create_session()
        year = self.field.year - 1
        db_field = (
            session.query(db.Field)
            .filter(db.Field.base_id == self.field.base_id, db.Field.year == year)
            .one_or_none()
        )
        if db_field:
            field = md.Field(db_field)
            planning = Plan(field)
            for db_cultivation in db_field.cultivations:
                crop = md.Crop(db_cultivation.crop, db_cultivation.crop_class)
                cultivation = md.Cultivation(db_cultivation, crop)
                planning.cultivations.append(cultivation)
            for db_fertilizaiton in db_field.fertilizations:
                fertilizer = md.Fertilizer(db_fertilizaiton.fertilizer)
                crop = md.Crop(
                    db_fertilizaiton.cultivation.crop, db_fertilizaiton.cultivation.crop_class
                )
                fertilization = md.Fertilization(db_fertilizaiton, fertilizer, crop)
                planning.fertilizations.append(fertilization)
        else:
            planning = None
        return planning

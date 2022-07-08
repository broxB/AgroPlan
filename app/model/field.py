from dataclasses import dataclass
from dataclasses import field as field_
from decimal import Decimal

import database.model as db
import model as md
from database.types import CropClass, DemandType, FertClass, FieldType, MeasureType
from database.utils import create_session
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
                self.n_ges(crop_class=CropClass.main_crop), self.main_crop.crop.s_demand
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
        reductions[0] += self.main_crop.pre_crop_effect()
        reductions[0] += self.second_crop.legume_delivery()
        return reductions

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

    def n_redelivery(self) -> Decimal:
        prev_spring_nges = self.field_prev_year.n_ges(measure=MeasureType.spring)
        fall_nges = self.n_ges(measure=MeasureType.fall, crop_class=CropClass.catch_crop)
        nges = (prev_spring_nges + fall_nges) * Decimal("0.1")
        return nges

    def cao_saldo(self) -> Decimal:
        return self.field_prev_year.saldo.cao

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

    @property
    def soil_sample(self):
        soil_sample = (
            max(self.Field.soil_samples, key=lambda x: x.year) if self.Field.soil_samples else None
        )
        if soil_sample:
            return md.Soil(soil_sample)
        return None

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field as field_
from decimal import Decimal

from flask_login import current_user
from loguru import logger

import app.database.model as db
import app.model as md
from app.database.model import BaseField as BaseFieldModel
from app.database.model import Field as FieldModel
from app.database.types import CropClass, DemandType, FertClass, FieldType, MeasureType
from app.model.crop import Crop
from app.model.cultivation import CatchCrop, MainCrop, SecondCrop, create_cultivation
from app.model.fertilization import Fertilization
from app.model.fertilizer import create_fertilizer
from app.model.soil import Soil


def create_field(base_field_id: int, year: int, first_year: bool = True) -> Field | None:
    field = (
        FieldModel.query.join(BaseFieldModel)
        .filter(
            BaseFieldModel.id == base_field_id,
            BaseFieldModel.user_id == current_user.id,
            FieldModel.year == year,
        )
        .one_or_none()
    )

    if field is None:
        return None
    field_data = Field(field, first_year=first_year)

    for cultivation in field.cultivations:
        crop_data = Crop(cultivation.crop, cultivation.crop_class)
        cultivation_data = create_cultivation(cultivation, crop_data)
        field_data.cultivations.append(cultivation_data)

    for fertilization in field.fertilizations:
        fertilizer_data = create_fertilizer(fertilization.fertilizer)
        crop_data = Crop(fertilization.cultivation.crop, fertilization.cultivation.crop_class)
        fertilization_data = Fertilization(
            fertilization, fertilizer_data, crop_data, fertilization.cultivation.crop_class
        )
        field_data.fertilizations.append(fertilization_data)

    return field_data


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
        self.field_prev_year: Field = self._field_prev_year()

    def total_saldo(self) -> list[Decimal]:
        saldo = zip(*[self.sum_demands(), self.sum_reductions(), self.sum_fertilizations()])
        return [sum(num) for num in saldo]

    def n_total(
        self, *, measure: MeasureType = None, crop_class: CropClass = None, netto: bool = False
    ) -> Decimal:
        """Summarizes the nitrogen values of all fertilizations specified.

        Args:
            measure (MeasureType, optional): MeasureType that should be counted. Defaults to None.
            crop_class (CropClass, optional): CropClass that should be counted. Defaults to None.
            netto (bool, optional): If storage loss should be applied. Defaults to False.

        Returns:
            Decimal: Sum for nitrogen of all fertilizations.
        """
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
        reductions.append(self.soil_reductions(self.soil_sample))
        reductions.append(self.redelivery())
        for cultivation in self.cultivations:
            reductions.append(self.crop_reductions(cultivation))
        return [sum(reduction) for reduction in zip(*reductions)]

    def soil_reductions(self, soil: Soil) -> list[Decimal]:
        reductions = [Decimal()] * 6
        if soil and self.field_type in [FieldType.cropland, FieldType.grassland]:
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
            if self.main_crop:
                reductions[4] += soil.reduction_s(
                    self.n_total(crop_class=CropClass.main_crop), self.main_crop.crop.s_demand
                )
            if soil.year + 3 < self.year:
                reductions[5] += soil.reduction_cao(self.field_type, preservation=True)
            else:
                reductions[5] += soil.reduction_cao(self.field_type)
        return reductions

    def redelivery(self) -> list[Decimal]:
        """Sum the nutrient values left in the soil from last period."""
        reductions = [Decimal()] * 6
        if self.field_prev_year:
            reductions[5] += self.cao_saldo()
            reductions[0] += self.n_redelivery()
        return reductions

    def crop_reductions(self, cultivation: md.Cultivation) -> list[Decimal]:
        reductions = [Decimal()] * 6
        reductions[0] += cultivation.reduction()
        reductions[0] += self.pre_crop_effect(cultivation)
        return reductions

    def pre_crop_effect(self, cultivation: md.Cultivation) -> Decimal:
        if self.field_type != FieldType.cropland or cultivation.crop_class == CropClass.catch_crop:
            return Decimal()
        if cultivation.crop_class == CropClass.main_crop:
            crop = self.previous_crop
        else:
            crop = self.main_crop
        try:
            return crop.pre_crop_effect()
        except AttributeError:
            return Decimal()

    def n_redelivery(self) -> Decimal:
        prev_spring_n_total = self.field_prev_year.n_total(measure=MeasureType.spring)
        fall_n_total = self.n_total(measure=MeasureType.fall, crop_class=CropClass.catch_crop)
        n_total = (prev_spring_n_total + fall_n_total) * Decimal("0.1")
        return n_total

    def cao_saldo(self) -> Decimal:
        return self.field_prev_year.saldo.cao

    @property
    def main_crop(self) -> MainCrop:
        for cultivation in self.cultivations:
            if cultivation.crop_class == CropClass.main_crop:
                return cultivation
        return None

    @property
    def second_crop(self) -> SecondCrop:
        for cultivation in self.cultivations:
            if cultivation.crop_class == CropClass.second_crop:
                return cultivation
        return None

    @property
    def catch_crop(self) -> CatchCrop:
        for cultivation in self.cultivations:
            if cultivation.crop_class == CropClass.catch_crop:
                return cultivation
        return None

    @property
    def previous_crop(self) -> MainCrop | SecondCrop | CatchCrop:
        if self.catch_crop:
            return self.catch_crop
        elif self.field_prev_year:
            if self.field_prev_year.second_crop:
                return self.field_prev_year.second_crop
            elif self.field_prev_year.main_crop:
                return self.field_prev_year.main_crop
        return None

    @property
    def soil_sample(self) -> Soil | None:
        soil_sample = (
            max(self.Field.soil_samples, key=lambda x: x.year) if self.Field.soil_samples else None
        )
        if soil_sample:
            return md.Soil(soil_sample)
        return None

    @property
    def overfertilization(self) -> bool:
        """Checks if fertilization applied in fall exceeds the regulations"""
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

    def _sum_fall_fertilizations(self) -> list[Decimal]:
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

    def _field_prev_year(self) -> Field | None:
        if not self.first_year:
            return
        year = self.year - 1
        field = create_field(self.base_id, year, first_year=False)
        return field

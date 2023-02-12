from __future__ import annotations

from decimal import Decimal

from flask_login import current_user
from loguru import logger

import app.database.model as db
from app.database.model import BaseField as BaseFieldModel
from app.database.model import Field as FieldModel
from app.database.types import (
    CultivationType,
    DemandType,
    FertClass,
    FieldType,
    MeasureType,
)
from app.model.balance import Balance
from app.model.crop import Crop
from app.model.cultivation import (
    CatchCrop,
    Cultivation,
    MainCrop,
    SecondCrop,
    create_cultivation,
)
from app.model.fertilization import Fertilization
from app.model.fertilizer import create_fertilizer
from app.model.soil import Soil, create_soil_sample


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
    field_data.soil_sample = create_soil_sample(field.soil_samples, year)

    for cultivation in field.cultivations:
        crop_data = Crop(cultivation.crop)
        cultivation_data = create_cultivation(cultivation, crop_data)
        field_data.cultivations.append(cultivation_data)

    for fertilization in field.fertilizations:
        fertilizer_data = create_fertilizer(fertilization.fertilizer)
        crop_data = Crop(fertilization.cultivation.crop)
        fertilization_data = Fertilization(
            fertilization, fertilizer_data, crop_data, fertilization.cultivation.cultivation_type
        )
        field_data.fertilizations.append(fertilization_data)

    return field_data


class Field:
    def __init__(self, Field: db.Field, first_year: bool = False):
        self.base_id: int = Field.base_id
        self.name: str = Field.base_field.name
        self.area: Decimal = Field.area
        self.year: int = Field.year
        self.field_type: FieldType = Field.field_type
        self.red_region: bool = Field.red_region
        self.demand_option: DemandType = Field.demand_type
        self.saldo: db.Saldo = Field.saldo
        self.first_year: bool = first_year
        self.soil_sample: Soil = None
        self.cultivations: list[Cultivation] = []
        self.fertilizations: list[Fertilization] = []
        self.field_prev_year: Field = self._field_prev_year()

    def total_balance(self) -> Balance:
        """Summarize the balance of all crop demands, reductions and fertilizations."""
        saldo = Balance("Total")
        saldo += self.sum_demands() + self.sum_reductions() + self.sum_fertilizations()
        return saldo

    def sum_fertilizations(self, fert_class: FertClass = None) -> Balance:
        """
        Summarize the balance of all fertilizations or only of a specific `FertClass`.

        Args:
            `fert_class`: Specify a `FertClass` to summarize.
        """
        nutrients = Balance("Fertilizations")
        for fertilization in self.fertilizations:
            if fertilization.fertilizer.is_class(fert_class):
                nutrients += Balance("nutrients", *fertilization.nutrients(self.field_type))
        return nutrients

    def sum_demands(self, negative_output: bool = True) -> Balance:
        """
        Summarize the balance of all crop demands.

        Args:
            `negative_output`: Specify if demand should be output as negative digits.
        """
        demands = Balance("Demands")
        for cultivation in self.cultivations:
            if cultivation.cultivation_type is CultivationType.catch_crop:
                continue
            demands += cultivation.demand(
                demand_option=self.demand_option,
                negative_output=negative_output,
            )
        return demands

    def sum_reductions(self) -> Balance:
        """Summarize the balance of all reductions from soil, previous crops and fertilizations."""
        reductions = Balance("Reductions")
        reductions += self.soil_reductions()
        reductions += self.redelivery()
        for cultivation in self.cultivations:
            reductions += self.crop_reductions(cultivation)
        return reductions

    def soil_reductions(self) -> Balance:
        """Summarize all reductions that are related to the soil composition and values."""
        reductions = Balance("Soil reductions")
        if not (self.soil_sample and self.field_type in (FieldType.cropland, FieldType.grassland)):
            return reductions
        reductions.n += self.soil_sample.reduction_n(self.field_type)
        if self.demand_option is DemandType.demand:
            reductions.p2o5 += self.soil_sample.reduction_p2o5(self.field_type)
            reductions.k2o += self.soil_sample.reduction_k2o(self.field_type)
            reductions.mgo += self.soil_sample.reduction_mg(self.field_type)
        if self.main_crop:
            reductions.s += self.soil_sample.reduction_s(
                self.n_total(cultivation_type=CultivationType.main_crop),
                self.main_crop.crop.s_demand,
            )
        if self.soil_sample.year + 3 < self.year:
            reductions.cao += self.soil_sample.reduction_cao(self.field_type, preservation=True)
        else:
            reductions.cao += self.soil_sample.reduction_cao(self.field_type)
        return reductions

    def redelivery(self) -> Balance:
        """Summarize the nutrient values left in the soil from last period."""
        reductions = Balance("Redelivery (N + CaO)")
        if self.field_prev_year:
            reductions.cao += self.cao_saldo()
            reductions.n += self.n_redelivery()
        return reductions

    def crop_reductions(self, cultivation: Cultivation) -> Balance:
        reductions = Balance("Crop reductions (Nmin + Pre-crop)")
        reductions.n += cultivation.reduction()
        reductions.n += self.pre_crop_effect(cultivation)
        return reductions

    def pre_crop_effect(self, cultivation: Cultivation) -> Decimal:
        if (
            self.field_type != FieldType.cropland
            or cultivation.cultivation_type is CultivationType.catch_crop
        ):
            return Decimal()
        if cultivation.cultivation_type is CultivationType.main_crop:
            crop = self.previous_crop
        else:
            crop = self.main_crop
        try:
            return crop.pre_crop_effect()
        except AttributeError:
            return Decimal()

    def n_redelivery(self) -> Decimal:
        prev_spring_n_total = self.field_prev_year.n_total(measure_type=MeasureType.org_spring)
        fall_n_total = self.n_total(
            measure_type=MeasureType.org_fall, cultivation_type=CultivationType.catch_crop
        )
        n_total = (prev_spring_n_total + fall_n_total) * Decimal("0.1")
        return n_total

    def cao_saldo(self) -> Decimal:
        return self.field_prev_year.saldo.cao

    def n_total(
        self,
        *,
        measure_type: MeasureType = None,
        cultivation_type: CultivationType = None,
        netto: bool = False,
    ) -> Decimal:
        """
        Summarizes the nitrogen values of all fertilizations specified.

        Args:
            measure (MeasureType, optional): MeasureType that should be counted. Defaults to None.
            crop_class (CultivationType, optional): CultivationType that should be counted. Defaults to None.
            netto (bool, optional): If storage loss should be applied. Defaults to False.
        """
        n_total = Decimal()
        for fertilization in self.fertilizations:
            n_total += fertilization.n_total(measure_type, cultivation_type, netto)
        return n_total

    @property
    def main_crop(self) -> MainCrop:
        for cultivation in self.cultivations:
            if cultivation.cultivation_type is CultivationType.main_crop:
                return cultivation
        return None

    @property
    def second_crop(self) -> SecondCrop:
        for cultivation in self.cultivations:
            if (
                cultivation.cultivation_type is CultivationType.second_main_crop
                or cultivation.cultivation_type is CultivationType.second_crop
            ):
                return cultivation
        return None

    @property
    def catch_crop(self) -> CatchCrop:
        for cultivation in self.cultivations:
            if cultivation.cultivation_type is CultivationType.catch_crop:
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

    def _field_prev_year(self) -> Field | None:
        if not self.first_year:
            return
        year = self.year - 1
        field = create_field(self.base_id, year, first_year=False)
        return field

    def __repr__(self) -> str:
        return f"<Field: {self.name} - {self.year}>"

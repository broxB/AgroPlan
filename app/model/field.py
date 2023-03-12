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

from .balance import Balance, create_modifier
from .crop import Crop
from .cultivation import (
    CatchCrop,
    Cultivation,
    MainCrop,
    SecondCrop,
    create_cultivation,
)
from .fertilization import Fertilization
from .fertilizer import create_fertilizer
from .soil import Soil, create_soil_sample


def create_field(
    user_id: int, base_field_id: int, year: int, first_year: bool = True
) -> Field | None:
    """Class Factory to create `field` from sqlalchemy database queries.

    Args:
        base_field_id (int): Id of the basefield to query from the database.
        year (int): Year of field to query from the database.
        first_year (bool, optional): Specify as `false` to stop recursively create previous years. Defaults to True.

    Returns:
        Field | None: Field class that contains all `cultivations` and `fertilizations` of the year and basefield.
    """

    field = (
        FieldModel.query.join(BaseFieldModel)
        .filter(
            BaseFieldModel.id == base_field_id,
            BaseFieldModel.user_id == user_id,
            FieldModel.year == year,
        )
        .one_or_none()
    )

    if field is None:
        return None
    new_field = Field(field, first_year=first_year)
    new_field.soil_sample = create_soil_sample(field.soil_samples, field.field_type, year)

    for cultivation in field.cultivations:
        crop_data = Crop(cultivation.crop)
        cultivation_data = create_cultivation(cultivation, crop_data)
        new_field.cultivations.append(cultivation_data)

    for fertilization in field.fertilizations:
        fertilizer_data = create_fertilizer(fertilization.fertilizer)
        crop_data = Crop(fertilization.cultivation.crop)
        fertilization_data = Fertilization(
            fertilization, fertilizer_data, crop_data, fertilization.cultivation.cultivation_type
        )
        new_field.fertilizations.append(fertilization_data)

    for modifier in field.modifiers:
        new_field.modifiers.append(
            create_modifier(modifier.description, modifier.modification, modifier.amount)
        )

    return new_field


class Field:
    """
    Field class contains all `cultivations` and `fertilizations` that happen on a basefield for a specific year.
    """

    def __init__(self, Field: db.Field, first_year: bool = False):
        self.user_id: int = Field.base_field.user_id
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
        self.modifiers: list[Balance] = []
        self.field_prev_year: Field = self._field_prev_year()

    def set_balance(self) -> None:
        """Adds balances of demands and reductions to available cultivations and nutrients to fertilizations."""

        for cultivation in self.cultivations:
            cultivation.balances = {}
            cult_balances = [cultivation.demand(self.demand_option)]
            if cultivation is not self.catch_crop:
                cult_balances.append(Balance("Nmin", n=cultivation.reduction()))
                cult_balances.append(
                    Balance("Pre-crop effect", n=self._pre_crop_effect(cultivation))
                )
            if cultivation is self.main_crop:
                cult_balances.append(self.soil_reductions())
                cult_balances.append(self.fertilization_redelivery())
                cult_balances.append(Balance("Lime balance", cao=self._cao_saldo()))
                for modifier in self.modifiers:
                    cult_balances.append(modifier)
            cult_total = Balance("Total")
            cult_total += sum(cult_balances)
            cult_balances.append(cult_total)
            cultivation.balances["cultivation"] = cult_balances

            org_balances, min_balances = [], []
            for fertilization in self.fertilizations:
                if fertilization.cultivation_type is cultivation.cultivation_type:
                    if fertilization.fertilizer.fert_class is FertClass.organic:
                        org_balances.append(fertilization.nutrients(self.field_type))
                    elif fertilization.fertilizer.fert_class is FertClass.mineral:
                        min_balances.append(fertilization.nutrients(self.field_type))
            for key, balances in zip(["organic", "mineral"], [org_balances, min_balances]):
                total = Balance("Total")
                total += sum(balances)
                remaining = Balance(f"Remaining demand")
                cult_total += total
                remaining += cult_total
                balances.append(remaining)
                cultivation.balances[key] = balances

    def total_balance(self) -> Balance:
        """Summarize the balance of all crop demands, reductions, fertilizations and modifiers."""
        saldo = Balance("Total")
        saldo += (
            self.sum_demands()
            + self.sum_reductions()
            + self.sum_fertilizations()
            + self.sum_modifiers()
        )
        return saldo

    def sum_fertilizations(self, fert_class: FertClass = None) -> Balance:
        """
        Summarize the balance of all `fertilizations` or only of a specific `FertClass`.

        Args:
            `fert_class`: Specify a `FertClass` to summarize.
        """
        nutrients = Balance("Fertilizations")
        for fertilization in self.fertilizations:
            if fertilization.fertilizer.is_class(fert_class):
                if fertilization.cultivation_type is not CultivationType.catch_crop:
                    nutrients += fertilization.nutrients(self.field_type)
        return nutrients

    def sum_demands(self, negative_output: bool = True) -> Balance:
        """
        Summarize the balance of all crop `demands`.

        Args:
            `negative_output`: Specify if demand should be output as negative values.
        """
        demands = Balance("Demands")
        for cultivation in self.cultivations:
            if cultivation.cultivation_type is not CultivationType.catch_crop:
                demands += cultivation.demand(
                    demand_option=self.demand_option,
                    negative_output=negative_output,
                )
        return demands

    def sum_reductions(self) -> Balance:
        """Summarize the balance of all `reductions` from soil, previous crops and fertilizations."""
        reductions = Balance("Reductions")
        reductions += self.soil_reductions()
        reductions += self.redelivery()
        for cultivation in self.cultivations:
            reductions += self.crop_reductions(cultivation)
        return reductions

    def sum_modifiers(self) -> Balance:
        """Summarize all available `modifiers`."""
        modifiers = Balance("Modifiers")
        for modifier in self.modifiers:
            modifiers += modifier
        return modifiers

    def soil_reductions(self) -> Balance:
        """Summarize all reductions that are related to the soil composition and values."""
        reductions = Balance("Soil reductions")
        if not (self.soil_sample and self.field_type in (FieldType.cropland, FieldType.grassland)):
            return reductions
        reductions.n += self.soil_sample.reduction_n()
        if self.demand_option is DemandType.demand:
            reductions.p2o5 += self.soil_sample.reduction_p2o5()
            reductions.k2o += self.soil_sample.reduction_k2o()
            reductions.mgo += self.soil_sample.reduction_mg()
        if self.main_crop:
            reductions.s += self.soil_sample.reduction_s(
                n_total=self.n_total(cultivation_type=CultivationType.main_crop),
                s_demand=self.main_crop.crop.s_demand,
            )
        if self.soil_sample.year + 3 < self.year:
            reductions.cao += self.soil_sample.reduction_cao(preservation=True)
        else:
            reductions.cao += self.soil_sample.reduction_cao()
        return reductions

    def crop_reductions(self, cultivation: Cultivation) -> Balance:
        """Reductions in nutrient demand left from previous crops and made by the current crop."""
        reductions = Balance("Crop reductions")
        reductions.n += cultivation.reduction()
        reductions.n += self._pre_crop_effect(cultivation)
        return reductions

    def redelivery(self) -> Balance:
        """Summarize the nutrient values left in the soil from last period."""
        reductions = Balance("Redelivery")
        reductions.cao += self._cao_saldo()
        reductions += self.fertilization_redelivery()
        return reductions

    def fertilization_redelivery(self) -> Balance:
        redelivery = Balance("Organic redelivery")
        try:
            prev_spring_n_total = self.field_prev_year.n_total(measure_type=MeasureType.org_spring)
        except AttributeError:
            prev_spring_n_total = Decimal()
        fall_n_total = self.n_total(
            measure_type=MeasureType.org_fall, cultivation_type=CultivationType.catch_crop
        )

        for fertilization in self.fertilizations:
            if fertilization.cultivation_type is CultivationType.catch_crop:
                redelivery += fertilization.nutrients(self.field_type)
        redelivery.n = (fall_n_total + prev_spring_n_total) * Decimal("0.1")
        redelivery.nh4 = 0
        return redelivery

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

    def _pre_crop_effect(self, cultivation: Cultivation) -> Decimal:
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

    def _cao_saldo(self) -> Decimal:
        try:
            return self.field_prev_year.saldo.cao
        except AttributeError:
            return Decimal()

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
        field = create_field(self.user_id, self.base_id, year, first_year=False)
        return field

    def __repr__(self) -> str:
        return f"<Field: {self.name} - {self.year}>"

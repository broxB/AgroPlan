from decimal import Decimal

import app.database.model as db
from app.database.types import CultivationType, FieldType, MeasureType

from .balance import Balance
from .fertilizer import Fertilizer


class Fertilization:
    """
    Class that contains functions and attributes that illustrate fertilizations.
    """

    def __init__(
        self,
        fertilization: db.Fertilization,
        fertilizer: Fertilizer,
        crop_feedable: bool,
        cultivation_type: CultivationType,
    ):
        self.fertilizer: Fertilizer = fertilizer
        self.amount: Decimal = fertilization.amount
        self.measure: MeasureType = fertilization.measure
        self.cultivation_type: CultivationType = cultivation_type
        self._crop_feedable: bool = crop_feedable

    def n_total(
        self, measure_type: MeasureType, cultivation_type: CultivationType, netto: bool
    ) -> Decimal:
        """
        Calculate the total nitrogen content for organic fertilizers,
        if they fit into the `MeasureType` and `CultivationType`.

        :param measure_type:
            `MeasureType` which should be checked.
        :param cultivation_type:
            `CultivationType` which should be checked.
        :param netto:
            If storage losses should be deducted.
        """
        if not self.fertilizer.is_organic:
            return Decimal()
        if (
            self.measure is measure_type
            or measure_type is None
            and self.cultivation_type is cultivation_type
            or cultivation_type is None
        ):
            return self.amount * self.fertilizer.n_total(netto)
        return Decimal()

    def nutrients(self, field_type: FieldType) -> Balance:
        """
        Returns the nutriential quantities of the fertilization,
        factoring in the available nitrogen and the lime starvation
        of the fertilizer.

        :param field_type:
            `FieldType` of the field it's used on.
        """
        return Balance(
            title=self.fertilizer.name,
            n=self.amount * self._n_verf(field_type),
            p2o5=self.amount * self.fertilizer.p2o5,
            k2o=self.amount * self.fertilizer.k2o,
            mgo=self.amount * self.fertilizer.mgo,
            s=self.amount * self.fertilizer.s,
            cao=self.amount * self.fertilizer.lime_starvation(field_type),
            nh4=self.amount * self.fertilizer.nh4,
        )

    def _n_verf(self, field_type: FieldType) -> Decimal:
        if self._crop_feedable:
            return self.fertilizer.n_verf(FieldType.grassland)
        return self.fertilizer.n_verf(field_type)

    def __repr__(self) -> str:
        return f"<Fertilization: {self.cultivation_type.name}>"

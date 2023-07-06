from __future__ import annotations

from typing import Union

from flask_bootstrap import SwitchField
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DecimalField,
    IntegerField,
    MonthField,
    SelectField,
    StringField,
)
from wtforms.validators import DataRequired, InputRequired, NumberRange, ValidationError

from app.database.model import (
    BaseField,
    Crop,
    Cultivation,
    Fertilization,
    Fertilizer,
    Field,
    Modifier,
    SoilSample,
)
from app.database.types import (
    CropClass,
    CropType,
    CultivationType,
    CutTiming,
    DemandType,
    FertClass,
    FertType,
    FieldType,
    FieldTypeForCrops,
    HumusType,
    LegumeType,
    MeasureType,
    NminType,
    NutrientType,
    ResidueType,
    SoilType,
    UnitType,
)

__all__ = [
    "create_form",
    "BaseFieldForm",
    "FieldForm",
    "CultivationForm",
    "CropForm",
    "FertilizationForm",
    "FertilizerForm",
    "SoilForm",
    "ModifierForm",
]
ModelType = Union[BaseField, Field, Cultivation, Crop, Fertilization, Fertilizer, Modifier]


class FormHelper:
    def get_data(self, id: int):
        self.model_data: ModelType = self.model_type.query.get(id)

    def populate(self: Form, id: int):
        if not hasattr(self, "model_data"):
            self.get_data(id)
        self.process(obj=self.model_data)

    def default_selects(self):
        self.model_data = Field.query.get(self.field_id)
        for field in self._fields.values():
            if field.type != "SelectField":
                continue
            if field.name == "cultivation":
                field.choices = [
                    (cultivation.id, cultivation.crop.name)
                    for cultivation in self.model_data.cultivations
                ]
            elif field.name == "crop":
                field.choices = [
                    (crop.id, crop.name)
                    for crop in current_user.get_crops(field_type=self.model_data.field_type)
                ]
            elif field.name == "fertilizer":
                field.choices = [(fert.id, fert.name) for fert in current_user.get_fertilizers()]

    # credit: https://stackoverflow.com/a/71562719/16256581
    def set_disabled(self, input_field: Form.Field):
        """
        disable the given input

        Args:
            inputField(Input): the WTForms input to disable
            disabled(bool): if true set the disabled attribute of the input
        """
        if input_field.render_kw is None:
            input_field.render_kw = {}
        input_field.render_kw["disabled"] = "disabled"

    def set_hidden(self, input_field):
        """
        disable the given input

        Args:
            inputField(Input): the WTForms input to disable
        """
        if input_field.render_kw is None:
            input_field.render_kw = {}
        input_field.render_kw["hidden"] = "hidden"


Form = Union[FormHelper, FlaskForm]


def create_form(form_type: str) -> FlaskForm | FormHelper | None:
    """Factory for forms that can be filled with new data."""
    form_types = {
        "base_field": BaseFieldForm,
        "field": FieldForm,
        "cultivation": CultivationForm,
        "fertilization": FertilizationForm,
        "crop": CropForm,
        "fertilizer": FertilizerForm,
        "soil": SoilForm,
        "modifier": ModifierForm,
    }
    try:
        form = form_types[form_type]
    except KeyError:
        form = None
    return form


class BaseFieldForm(FlaskForm, FormHelper):
    prefix = IntegerField("Prefix:", validators=[InputRequired()])
    suffix = IntegerField("Suffix:", validators=[InputRequired()])
    name = StringField("Name:", validators=[DataRequired()])

    def __init__(self, _, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def default_selects(self):
        ...

    def validate(self, **kwargs):
        valid = super().validate(**kwargs)
        if not valid:
            return False
        basefield = BaseField.query.filter(
            BaseField.prefix == self.prefix.data, BaseField.suffix == self.suffix.data
        ).first()
        if basefield is not None:
            self.suffix.errors.append(
                f"Basefield with Prefix: {self.prefix.data} and Suffix: {self.suffix.data} already exists."
            )
            return False
        return True


class FieldForm(FlaskForm, FormHelper):
    sub_suffix = IntegerField(
        "Sub-Partition:", default=0, validators=[InputRequired(), NumberRange(min=0)]
    )
    year = IntegerField("Year:", validators=[InputRequired(), NumberRange(min=2000)])
    area = DecimalField("Area in ha:", validators=[InputRequired(), NumberRange(min=0)])
    red_region = SwitchField("Red region?")
    field_type = SelectField(
        "Select field type:",
        choices=[(enum.name, enum.value) for enum in FieldType],
        validators=[InputRequired()],
    )
    demand_type = SelectField(
        "Select demand type:",
        choices=[(enum.name, enum.value) for enum in DemandType],
        validators=[InputRequired()],
    )

    def __init__(self, base_field_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_id = base_field_id

    def default_selects(self):
        ...

    def validate_sub_suffix(self, sub_suffix):
        if sub_suffix.data:
            field = Field.query.filter(
                Field.base_id == self.base_id,
                Field.sub_suffix == sub_suffix.data,
                Field.year == self.year.data,
            ).first()
            if field is not None:
                self.sub_suffix.errors.append(
                    f"Field with Sub-Suffix:{sub_suffix} already exists."
                )
                return False

    def validate_year(self, year):
        field = Field.query.filter(
            Field.base_id == self.base_id,
            Field.sub_suffix == self.sub_suffix.data,
            Field.year == year.data,
        ).first()
        if field is not None:
            self.year.errors.append(f"Field in {year.data} already exists.")
            return False


class CultivationForm(FlaskForm, FormHelper):
    cultivation_type = SelectField(
        "Select type of cultivation:",
        choices=[(enum.name, enum.value) for enum in CultivationType],
        validators=[InputRequired()],
        render_kw={"class": "reload"},
    )
    crop = SelectField("Select crop to grow:", validators=[InputRequired()])
    crop_yield = IntegerField("Estimated yield in dt/ha:", validators=[InputRequired()])
    crop_protein = DecimalField("Estimated protein in % DM/ha:", validators=[InputRequired()])
    residue_type = SelectField(
        "Estimated residues:",
        choices=[(enum.name, enum.value) for enum in ResidueType],
        validators=[InputRequired()],
    )
    legume_type = SelectField(
        "Share of legumes:",
        choices=[(enum.name, enum.value) for enum in LegumeType],
        validators=[InputRequired()],
    )
    nmin_30 = IntegerField("Nmin 30cm:", validators=[InputRequired()])
    nmin_60 = IntegerField("Nmin 60cm:", validators=[InputRequired()])
    nmin_90 = IntegerField("Nmin 90cm:", validators=[InputRequired()])

    def __init__(self, field_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_id = field_id

    def validate_cultivation_type(self, cultivation_type):
        cultivation = (
            Cultivation.query.join(Field)
            .filter(Field.id == self.field_id, Cultivation.cultivation_type == cultivation_type)
            .first()
        )
        if cultivation is not None:
            raise ValidationError("This type of cultivation already exists.")


class FertilizationForm(FlaskForm, FormHelper):
    cultivation = SelectField("Select a crop to fertilize:", validators=[InputRequired()])
    fert_class = SelectField(
        "Select a fertilizer type:",
        choices=[(enum.name, enum.value) for enum in FertClass],
        validators=[InputRequired()],
        render_kw={"class": "reload"},
    )
    cut_timing = SelectField(
        "Select a cut timing:", choices=[(enum.name, enum.value) for enum in CutTiming]
    )
    measure_type = SelectField(
        "Select a measure:",
        choices=[(enum.name, enum.value) for enum in MeasureType],
        validators=[InputRequired()],
        render_kw={"class": "reload"},
    )
    fertilizer = SelectField("Select a fertilizer:", validators=[InputRequired()])
    month = IntegerField("Month:")
    amount = DecimalField("Amount", validators=[InputRequired()])

    def __init__(self, field_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_id = field_id

    def validate_measure(self, measure):
        if self.fert_class.data == FertClass.mineral.value:
            fertilization = (
                Fertilization.query.join(Field)
                .filter(
                    Field.id == self.field_id,
                    Fertilization.measure == measure,
                )
                .first()
            )
            if fertilization is not None:
                raise ValidationError(f"{measure} for mineral fertilization already exists.")

    def validate_amount(self, amount):
        ...
        # implement from field model class

        # def fall_violation(self) -> bool:
        #     """Checks if fertilization applied in fall exceeds the regulations"""
        #     n_total, nh4 = self._sum_fall_fertilizations()
        #     if (
        #         self.field_type == FieldType.grassland
        #         or self.main_crop
        #         and self.main_crop.crop.feedable
        #     ):
        #         if n_total > (80 if not self.red_region else 60):
        #             logger.info(
        #                 f"{self.name}: {n_total=:.0f} is violating the maximum value of Nges for fall fertilizations."
        #             )
        #             return True
        #     elif n_total > 60 or nh4 > 30:
        #         logger.info(
        #             f"{self.name}: {n_total=:.0f} or {nh4=:.0f} are violating the maximum values of NH4 for fall fertilizations."
        #         )
        #         return True
        #     return False

        # def _sum_fall_fertilizations(self) -> list[Decimal]:
        #     sum_n = [(0, 0)]
        #     for fertilization in self.fertilizations:
        #         if (
        #             fertilization.fertilizer.is_class(FertClass.organic)
        #             and fertilization.measure == MeasureType.org_fall
        #         ):
        #             n_total, nh4 = [
        #                 fertilization.amount * n
        #                 for n in (fertilization.fertilizer.n, fertilization.fertilizer.nh4)
        #             ]
        #             sum_n.append((n_total, nh4))
        #     return [sum(n) for n in zip(*sum_n)]


class FertilizerForm(FlaskForm, FormHelper):
    name = StringField("Name:", validators=[DataRequired()])
    year = IntegerField("Year:", validators=[InputRequired()])
    fert_class = SelectField(
        "Select fertilizer class:",
        choices=[(enum.name, enum.value) for enum in FertClass],
        validators=[InputRequired()],
        render_kw={"class": "reload"},
    )
    fert_type = SelectField(
        "Select fertilizer type:",
        choices=[(enum.name, enum.value) for enum in FertType],
        validators=[InputRequired()],
    )
    active = BooleanField("Show fertilizer in list?")
    unit_type = SelectField(
        "Select measurement unit:",
        choices=[(enum.name, enum.value) for enum in UnitType],
        validators=[InputRequired()],
    )
    price = DecimalField("Price in €:", default=0.00)
    n = DecimalField("N:", validators=[InputRequired()])
    p2o5 = DecimalField("P2O5:", validators=[InputRequired()])
    k2o = DecimalField("K2O:", validators=[InputRequired()])
    mgo = DecimalField("MgO:", validators=[InputRequired()])
    s = DecimalField("S:", validators=[InputRequired()])
    cao = DecimalField("CaO:", validators=[InputRequired()])
    nh4 = DecimalField("NH4:", validators=[InputRequired()])

    def __init__(self, _, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def default_selects(self):
        ...

    def validate(self):
        valid = super().validate()
        if not valid:
            return False
        # organic fertilizer where year.data is important
        if self.fert_class.data == FertClass.organic.value:
            fertilizer = Fertilizer.query.filter(
                Fertilizer.user_id == current_user.id,
                Fertilizer.name == self.name.data,
                Fertilizer.year == self.year.data,
            ).first()
            if fertilizer is not None:
                self.name.errors.append(f"{self.name.data} already exists in {self.year.data}.")
                self.year.errors.append(f"{self.name.data} already exists in {self.year.data}.")
                return False
        # mineral fertilizer with no yearly changes
        else:
            fertilizer = Fertilizer.query.filter(
                Fertilizer.user_id == current_user.id,
                Fertilizer.name == self.name.data,
            ).first()
            if fertilizer is not None:
                self.name.errors.append(f"{self.name.data} already exists.")
        return True


class CropForm(FlaskForm, FormHelper):
    name = StringField("Name:", validators=[DataRequired()])
    field_type = SelectField(
        "Select on which type of field the crop grows:",
        choices=[(enum.name, enum.value) for enum in FieldTypeForCrops],
        validators=[InputRequired()],
        render_kw={"class": "reload"},
    )
    crop_class = SelectField(
        "Select a crop class:",
        choices=[(enum.name, enum.value) for enum in CropClass],
        validators=[InputRequired()],
        render_kw={"class": "reload"},
    )
    crop_type = SelectField(
        "Select a crop type:",
        choices=[(enum.name, enum.value) for enum in CropType],
        validators=[InputRequired()],
    )
    kind = StringField(
        "Fruit subtype (e.g. 'barley' for 'winter barley'):", validators=[DataRequired()]
    )
    feedable = BooleanField("Is feedable?")
    residue = BooleanField("Has residues?")
    nmin_depth = SelectField(
        "Select Nmin depth:",
        choices=[(enum.name, enum.value) for enum in NminType],
        validators=[InputRequired()],
    )
    target_demand = IntegerField("Target demand in kg N/ha:", validators=[InputRequired()])
    target_yield = IntegerField("Target yield in dt/ha:", validators=[InputRequired()])
    pos_yield = DecimalField(
        "Change in demand with positive yield difference in kg N/ha:", validators=[InputRequired()]
    )
    neg_yield = DecimalField(
        "Change in demand with negative yield difference in kg N/ha:", validators=[InputRequired()]
    )
    target_protein = DecimalField("Target protein in 0.1% DM/ha:", validators=[InputRequired()])
    var_protein = DecimalField(
        "Change in demand with protein difference in kg N/ha:", validators=[InputRequired()]
    )
    n = DecimalField("Fruit N:", validators=[InputRequired()])
    p2o5 = DecimalField("Fruit P2O5:", validators=[InputRequired()])
    k2o = DecimalField("Fruit K2O:", validators=[InputRequired()])
    mgo = DecimalField("Fruit MgO:", validators=[InputRequired()])
    byproduct = StringField("Byproduct name:")
    byp_ratio = DecimalField("Byproduct ratio in %:", validators=[InputRequired()])
    byp_n = DecimalField("Byproduct N:", validators=[InputRequired()])
    byp_p2o5 = DecimalField("Byproduct P2O5:", validators=[InputRequired()])
    byp_k2o = DecimalField("Byproduct K2O:", validators=[InputRequired()])
    byp_mgo = DecimalField("Byproduct MgO:", validators=[InputRequired()])

    def __init__(self, _, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def default_selects(self):
        ...

    def validate_name(self, name):
        crop = Crop.query.filter(Crop.user_id == current_user.id, Crop.name == name.data).first()
        if crop is not None:
            self.name.errors.append(f"{name.data} already exists.")
            return False


class SoilForm(FlaskForm, FormHelper):
    year = IntegerField("Year:", validators=[InputRequired()])
    soil_type = SelectField(
        "Select soil composition:",
        choices=[(enum.name, enum.value) for enum in SoilType],
        validators=[InputRequired()],
    )
    humus_type = SelectField(
        "Select humus ratio:",
        choices=[(enum.name, enum.value) for enum in HumusType],
        validators=[InputRequired()],
    )
    ph = DecimalField("pH:", validators=[InputRequired()])
    p2o5 = DecimalField("P2O5:", validators=[InputRequired()])
    k2o = DecimalField("K2O:", validators=[InputRequired()])
    mg = DecimalField("Mg:", validators=[InputRequired()])

    def __init__(self, base_field_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_id = base_field_id

    def default_selects(self):
        ...

    def validate_year(self, year):
        soil_sample = SoilSample.query.filter(
            SoilSample.base_id == self.base_id, SoilSample.year == year.data
        ).first()
        if soil_sample is not None:
            self.year.errors.append(f"Soil sample for {year.data} already exists.")
            return False


class ModifierForm(FlaskForm, FormHelper):
    description = StringField("Description:", validators=[InputRequired()])
    modification = SelectField(
        "Select a modifier:",
        choices=[(enum.name, enum.value) for enum in NutrientType],
        validators=[InputRequired()],
    )
    amount = IntegerField("Amount in kg/ha:", validators=[InputRequired()])

    def __init__(self, field_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_id = field_id

    def validate_amount(self, amount):
        if amount.data > 1000:
            self.amount.errors.append(f"Only values under 1000kg/ha are allowed.")
            return False

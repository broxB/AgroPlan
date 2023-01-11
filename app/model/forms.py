from __future__ import annotations

from typing import TypeVar

from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import BooleanField, FloatField, IntegerField, SelectField, StringField
from wtforms.validators import DataRequired, ValidationError

from app.database.model import (
    BaseField,
    Crop,
    Cultivation,
    Fertilization,
    Fertilizer,
    Field,
    SoilSample,
)
from app.database.types import (
    CropClass,
    CropType,
    DemandType,
    FertClass,
    FertType,
    FieldType,
    HumusType,
    LegumeType,
    MeasureType,
    NminType,
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
]
ModelType = TypeVar("ModelType", BaseField, Field, Cultivation, Crop, Fertilization, Fertilizer)


class FormHelper:
    def populate(self: Form, id: int):
        self.model_data: ModelType = self.model_type.query.get(int(id))
        self.process(obj=self.model_data)

    def default_selects(self):
        for field in self._fields.values():
            if field.type == "SelectField":
                field.choices.insert(0, ("default", "Select one"))

    # credit: https://stackoverflow.com/a/71562719/16256581
    def set_disabled(self, input_field):
        """
        disable the given input

        Args:
            inputField(Input): the WTForms input to disable
            disabled(bool): if true set the disabled attribute of the input
        """
        if input_field.render_kw is None:
            input_field.render_kw = {}
        input_field.render_kw["disabled"] = "disabled"

    def set_hidden(self, input_field: Field):
        """
        disable the given input

        Args:
            inputField(Input): the WTForms input to disable
        """
        if input_field.render_kw is None:
            input_field.render_kw = {}
        input_field.render_kw["hidden"] = "hidden"


Form = TypeVar("Form", FormHelper, FlaskForm)


def create_form(form_type: str, params: list) -> Form:
    """Factory for forms that can be filled with new data."""
    form_types = {
        "base_field": BaseFieldForm,
        "field": FieldForm,
        "cultivation": CultivationForm,
        "fertilization": FertilizationForm,
        "crop": CropForm,
        "fertilizer": FertilizerForm,
        "soil": SoilForm,
    }
    try:
        form = form_types[form_type](*params)
    except KeyError:
        form = None
    return form


class BaseFieldForm(FlaskForm, FormHelper):
    prefix = IntegerField("Prefix:", validators=[DataRequired()])
    suffix = IntegerField("Suffix:", validators=[DataRequired()])
    name = StringField("Name:", validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_type = BaseField

    def validate(self):
        valid = super().validate()
        if not valid:
            return False
        basefield = BaseField.query.filter(
            BaseField.prefix == self.prefix.data, BaseField.suffix == self.suffix.data
        ).first()
        if basefield is not None:
            self.prefix.errors.append(
                f"Basefield with Prefix:{self.prefix.data} and Suffix:{self.suffix.data} already exists."
            )
            self.suffix.errors.append(
                f"Basefield with Prefix:{self.prefix.data} and Suffix:{self.suffix.data} already exists."
            )
            return False
        return True


class FieldForm(FlaskForm, FormHelper):
    sub_suffix = IntegerField("Sub-Suffix:")
    year = IntegerField("Year:", validators=[DataRequired()])
    area = FloatField("Area in ha:", validators=[DataRequired()])
    red_region = BooleanField("In red region?", validators=[DataRequired()])
    field_type = SelectField(
        "Select field type:",
        choices=[(enum.name, enum.value) for enum in FieldType],
        validators=[DataRequired()],
    )
    demand_type = SelectField(
        "Select demand type:",
        choices=[(enum.name, enum.value) for enum in DemandType],
        validators=[DataRequired()],
    )

    def __init__(self, base_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_id = base_id
        self.model_type = Field
        self.sub_suffix.data = 0

    def validate_sub_suffix(self, sub_suffix):
        if sub_suffix:
            field = Field.query.filter(
                Field.base_id == self.base_id,
                Field.sub_suffix == sub_suffix,
                Field.year == self.year.data,
            ).first()
            if field is not None:
                ValidationError(f"Field with Sub-Suffix:{sub_suffix} already exists.")

    def validate_year(self, year):
        field = Field.query.filter(
            Field.base_id == self.base_id,
            Field.sub_suffix == self.sub_suffix.data,
            Field.year == year,
        ).first()
        if field is not None:
            ValidationError(f"Field in {year} already exists.")


class CultivationForm(FlaskForm, FormHelper):
    crop_class = SelectField(
        "Select class of crop:",
        choices=[(enum.name, enum.value) for enum in list(CropClass)[:3]],
        validators=[DataRequired()],
    )
    crop = SelectField("Select crop to grow:", validators=[DataRequired()])
    crop_yield = IntegerField("Estimated yield in dt/ha:", validators=[DataRequired()])
    crop_protein = FloatField("Estimated protein in % DM/ha:", validators=[DataRequired()])
    residues = SelectField(
        "Estimated residues:",
        choices=[(enum.name, enum.value) for enum in ResidueType],
        validators=[DataRequired()],
    )
    legume_rate = SelectField(
        "Share of legumes:",
        choices=[(enum.name, enum.value) for enum in LegumeType],
        validators=[DataRequired()],
    )
    nmin_30 = IntegerField("Nmin 30cm:", validators=[DataRequired()])
    nmin_60 = IntegerField("Nmin 60cm:", validators=[DataRequired()])
    nmin_90 = IntegerField("Nmin 90cm:", validators=[DataRequired()])

    def __init__(self, field_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_id = field_id
        self.model_type = Cultivation

    def validate_crop_class(self, crop_class):
        cultivation = (
            Cultivation.query.join(Field)
            .filter(Field.id == self.field_id, Cultivation.crop_class == crop_class)
            .first()
        )
        if cultivation is not None:
            raise ValidationError("Class already exists.")


class FertilizationForm(FlaskForm, FormHelper):
    crop = SelectField("Select crop to fertilize:", validators=[DataRequired()])
    fert_class = SelectField(
        "Select fertilizer type:",
        choices=[(enum.name, enum.value) for enum in FertClass],
        validators=[DataRequired()],
    )
    measure = SelectField(
        "Select measure:",
        choices=[(enum.name, enum.value) for enum in MeasureType],
        validators=[DataRequired()],
    )
    fertilizer = SelectField("Select fertilizer:", validators=[DataRequired()])
    amount = FloatField("Amount", validators=[DataRequired()])
    month = IntegerField("Month:")

    def __init__(self, field_id, *args, **kwargs):
        super(FlaskForm, self).__init__(*args, **kwargs)
        self.field_id = field_id
        self.model_type = Fertilization

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


class FertilizerForm(FlaskForm, FormHelper):
    name = StringField("Name:", validators=[DataRequired()])
    year = IntegerField("Year:", validators=[DataRequired()])
    fert_class = SelectField(
        "Select fertilizer class:",
        choices=[(enum.name, enum.value) for enum in FertClass],
        validators=[DataRequired()],
    )
    fert_type = SelectField(
        "Select fertilizer type:",
        choices=[(enum.name, enum.value) for enum in FertType],
        validators=[DataRequired()],
    )
    active = BooleanField("Show fertilizer in list?")
    unit = SelectField(
        "Select measurement unit:",
        choices=[(enum.name, enum.value) for enum in UnitType],
        validators=[DataRequired()],
    )
    price = FloatField("Price in €:", default=0.00)
    n = FloatField("N:", validators=[DataRequired()])
    p2o5 = FloatField("P2O5:", validators=[DataRequired()])
    k2o = FloatField("K2O:", validators=[DataRequired()])
    mgo = FloatField("MgO:", validators=[DataRequired()])
    s = FloatField("S:", validators=[DataRequired()])
    cao = FloatField("CaO:", validators=[DataRequired()])
    nh4 = FloatField("NH4:", validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_type = Fertilizer
        self.fert_class.data = ("default", "")
        self.fert_type.data = ("default", "")

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
    crop_class = SelectField(
        "Select a crop class:",
        choices=[(enum.name, enum.value) for enum in CropClass],
        validators=[DataRequired()],
    )
    crop_type = SelectField(
        "Select a crop type:",
        choices=[(enum.name, enum.value) for enum in CropType],
        validators=[DataRequired()],
    )
    kind = StringField(
        "Fruit subtype (e.g. 'barley' for 'winter barley'):", validators=[DataRequired()]
    )
    feedable = BooleanField("Is feedable?")
    residue = BooleanField("Has residues?")
    nmin_depth = SelectField(
        "Select Nmin depth:",
        choices=[(enum.name, enum.value) for enum in NminType],
        validators=[DataRequired()],
    )
    target_demand = IntegerField("Target demand in kg N/ha:", validators=[DataRequired()])
    target_yield = IntegerField("Target yield in dt/ha:", validators=[DataRequired()])
    positive_yield = FloatField(
        "Change in demand with positive yield difference in kg N/ha:", validators=[DataRequired()]
    )
    negative_yield = FloatField(
        "Change in demand with negative yield difference in kg N/ha:", validators=[DataRequired()]
    )
    target_protein = FloatField("Target protein in 0.1% DM/ha:", validators=[DataRequired()])
    var_protein = FloatField(
        "Change in demand with protein difference in kg N/ha:", validators=[DataRequired()]
    )
    n = FloatField("Fruit N:", validators=[DataRequired()])
    p2o5 = FloatField("Fruit P2O5:", validators=[DataRequired()])
    k2o = FloatField("Fruit K2O:", validators=[DataRequired()])
    mgo = FloatField("Fruit MgO:", validators=[DataRequired()])
    byproduct = StringField("Byproduct:")
    byp_ratio = FloatField("Byproduct ratio:", validators=[DataRequired()])
    byp_n = FloatField("Byproduct N:", validators=[DataRequired()])
    byp_p2o5 = FloatField("Byproduct P2O5:", validators=[DataRequired()])
    byp_k2o = FloatField("Byproduct K2O:", validators=[DataRequired()])
    byp_mgo = FloatField("Byproduct MgO:", validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_type = Crop

    def validate_name(self, name):
        crop = Crop.query.filter(Crop.user_id == current_user.id, Crop.name == name).first()
        if crop is not None:
            raise ValidationError(f"{name} already exists.")


class SoilForm(FlaskForm, FormHelper):
    year = IntegerField("Year:", validators=[DataRequired()])
    soil_type = SelectField(
        "Select soil composition:",
        choices=[(enum.name, enum.value) for enum in SoilType],
        validators=[DataRequired()],
    )
    humus = SelectField(
        "Select humus ratio:",
        choices=[(enum.name, enum.value) for enum in HumusType],
        validators=[DataRequired()],
    )
    ph = FloatField("pH:", validators=[DataRequired()])
    p2o5 = FloatField("P2O5:", validators=[DataRequired()])
    k2o = FloatField("K2O:", validators=[DataRequired()])
    mg = FloatField("Mg:", validators=[DataRequired()])

    def __init__(self, base_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_type = SoilSample
        self.base_id = int(base_id)

    def validate_year(self, year):
        soil_sample = SoilSample.query.filter(
            SoilSample.base_id == self.base_id, SoilSample.year == year
        ).first()
        if soil_sample is not None:
            raise ValidationError(f"Soil sample for {year} already exists.")

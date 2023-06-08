from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError

from app.database.model import User
from app.database.types import (
    CultivationType,
    FertClass,
    FertType,
    MeasureType,
    MineralFertType,
    MineralMeasureType,
    NminType,
    OrganicFertType,
    OrganicMeasureType,
    ResidueType,
    find_crop_class,
    find_nmin_type,
)
from app.model.forms import (
    BaseFieldForm,
    CropForm,
    CultivationForm,
    FertilizationForm,
    FertilizerForm,
    FieldForm,
    Form,
    SoilForm,
)

__all__ = [
    "create_edit_form",
    "EditProfileForm",
    "EmptyForm",
    "YearForm",
    "EditBaseFieldForm",
    "EditFieldForm",
    "EditCultivationForm",
    "EditCropForm",
    "EditFertilizationForm",
    "EditFertilizerForm",
    "EditSoilForm",
]


def create_edit_form(form_type: str, param: list) -> Form:
    """Factory for forms that edit existing data."""
    form_types = {
        "base_field": EditBaseFieldForm,
        "field": EditFieldForm,
        "cultivation": EditCultivationForm,
        "fertilization": EditFertilizationForm,
        "crop": EditCropForm,
        "fertilizer": EditFertilizerForm,
        "soil": EditSoilForm,
    }
    try:
        form = form_types[form_type](param)
    except KeyError:
        form = None
    return form


class EditProfileForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Submit")

    def __init__(self, original_username, original_email, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError("Please use a different username.")

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=self.email.data).first()
            if user is not None:
                raise ValidationError("Please use a different email.")


class EmptyForm(FlaskForm):
    submit = SubmitField("Submit")


class YearForm(FlaskForm):
    year = HiddenField("Year")
    submit = SubmitField("Submit")

    def __init__(self, *args, **kwargs):
        super().__init__(prefix="year", *args, **kwargs)

    def validate_year(self, year):
        year = int(year.data)
        if year != current_user.year:
            if year not in current_user.get_years():
                raise ValidationError("Invalid year selected.")


class EditBaseFieldForm(BaseFieldForm):
    def __init__(self, prefix, suffix, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_prefix = prefix
        self.original_suffix = suffix

    def validate(self):
        if self.original_prefix != self.prefix.data or self.original_suffix != self.suffix.data:
            return super().validate()
        return True

    def populate(self, id: int):
        super().populate(id)
        self.soil_type.data = self.model_data.soil_type.name
        self.humus.data = self.model_data.humus.name


class EditFieldForm(FieldForm):
    def __init__(self, sub_suffix, year, base_id, *args, **kwargs):
        super().__init__(base_id, *args, **kwargs)
        self.original_sub_suffix = sub_suffix
        self.original_year = year

    def validate_sub_suffix(self, sub_suffix):
        if sub_suffix != self.original_sub_suffix:
            super().validate_sub_suffix(sub_suffix)

    def validate_year(self, year):
        if year != self.original_year:
            super().validate_year(year)

    def populate(self, id: int):
        super().populate(id)
        self.field_type.data = self.model_data.field_type.name
        self.demand_type.data = self.model_data.demand_type.name


class EditCultivationForm(CultivationForm):
    def __init__(self, field_id, *args, **kwargs):
        super().__init__(field_id, *args, **kwargs)

    def validate_cultivation_type(self, cultivation_type):
        if cultivation_type != self.original_cultivation_type:
            super().validate_cultivation_type(cultivation_type)

    def populate(self, id: int):
        super().populate(id)
        self.cultivation_type.data = self.model_data.cultivation_type.name
        self.residue_type.data = self.model_data.residues.name
        self.legume_type.data = self.model_data.legume_rate.name
        self.crop.choices = [
            (crop.id, crop.name)
            for crop in current_user.get_crops(
                crop_class=find_crop_class(self.model_data.cultivation_type),
                field_type=self.model_data.field.field_type,
            )
        ]
        self.crop.data = str(self.model_data.crop.id)
        self.original_cultivation_type = self.cultivation_type.data
        # remove non-relevant inputs
        feedable = self.model_data.crop.feedable
        cultivation = self.model_data.cultivation_type
        residues = self.model_data.residues
        nmin_depth = self.model_data.crop.nmin_depth
        if feedable or cultivation is not CultivationType.main_crop:
            del self.nmin_30
            del self.nmin_60
            del self.nmin_90
        if nmin_depth is NminType.nmin_30:
            del self.nmin_60
            del self.nmin_90
        if nmin_depth is NminType.nmin_60:
            del self.nmin_90
        if not feedable:
            del self.crop_protein
        if not (feedable or cultivation is CultivationType.catch_crop):
            del self.legume_type
        if cultivation is CultivationType.catch_crop:
            del self.crop_yield
        if residues is ResidueType.main_no_residues:
            del self.residue_type


class EditFertilizationForm(FertilizationForm):
    def __init__(self, field_id, *args, **kwargs):
        super().__init__(field_id, *args, **kwargs)

    def validate_measure(self, measure):
        if measure != self.original_measure:
            super().validate_measure(measure)

    def populate(self, id: int):
        super().populate(id)
        self.crop.choices = [
            (cult.id, cult.crop.name) for cult in self.model_data.field[0].cultivations
        ]
        self.crop.data = str(self.model_data.cultivation.id)
        self.fert_class.data = self.model_data.fertilizer.fert_class.name
        self.cut_timing.data = self.model_data.cut_timing.name
        measure_type = (
            OrganicMeasureType
            if self.model_data.fertilizer.fert_class == FertClass.organic
            else MineralMeasureType
        )
        self.measure_type.choices = [(enum.name, enum.value) for enum in measure_type]
        self.measure_type.data = self.model_data.measure.name
        if self.model_data.fertilizer.fert_class == FertClass.organic:
            fertilizers = current_user.get_fertilizers(
                fert_class=self.fert_class.data, year=self.model_data.field[0].year
            )
        else:
            fertilizers = current_user.get_fertilizers(
                fert_class=self.fert_class.data, fert_type=self.model_data.fertilizer.fert_type
            )
        self.fertilizer.choices = [(fert.id, fert.name) for fert in fertilizers]
        self.fertilizer.data = str(self.model_data.fertilizer.id)
        self.original_measure = self.measure_type.data
        self.amount.label.text += f" in {self.model_data.fertilizer.unit.value}:"
        # remove non-relevant inputs
        fert_class = self.model_data.fertilizer.fert_class
        feedable = self.model_data.cultivation.crop.feedable
        if fert_class is FertClass.mineral:
            del self.month
        if not feedable:
            del self.cut_timing
        del self.fert_class


class EditFertilizerForm(FertilizerForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self):
        if self.name.data != self.original_name or self.year.data != self.original_year:
            return super().validate()
        return True

    def populate(self, id: int):
        super().populate(id)
        self.fert_class.data = self.model_data.fert_class.name
        self.fert_type.data = self.model_data.fert_type.name
        self.unit_type.data = self.model_data.unit.name
        self.original_year = self.model_data.year
        self.original_name = self.model_data.name
        # remove non-relevant inputs
        fert_class = self.model_data.fert_class
        del self.fert_class
        if fert_class is FertClass.mineral:
            del self.year
        if fert_class is FertClass.organic:
            del self.active
            del self.price


class EditCropForm(CropForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate_name(self, name):
        if name != self.original_name:
            super().validate_name(name)

    def populate(self, id: int):
        super().populate(id)
        self.field_type.data = self.model_data.field_type.name
        self.crop_class.data = self.model_data.crop_class.name
        self.crop_type.data = self.model_data.crop_type.name
        self.nmin_depth.data = self.model_data.nmin_depth.name
        self.original_name = self.model_data.name


class EditSoilForm(SoilForm):
    def __init__(self, base_id, *args, **kwargs):
        super().__init__(base_id, *args, **kwargs)

    def validate_year(self, year):
        if year != self.year.data:
            super().validate_year(year)

    def populate(self, id: int):
        super().populate(id)
        self.soil_type.data = self.model_data.soil_type.name
        self.humus_type.data = self.model_data.humus.name

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

from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError

from app.database.model import Crop, Fertilizer, User
from app.database.types import CropClass
from app.model.forms import (
    BaseFieldForm,
    CropForm,
    CultivationForm,
    FertilizationForm,
    FertilizerForm,
    FieldForm,
    SoilForm,
)


def create_edit_form(modal: str, param: list) -> FlaskForm | None:
    modal_types = {
        "base_field": EditBaseFieldForm,
        "field": EditFieldForm,
        "cultivation": EditCultivationForm,
        "fertilization": EditFertilizationForm,
        "crop": EditCropForm,
        "fertilizer": EditFertilizerForm,
        "soil": EditSoilForm,
    }
    try:
        form = modal_types[modal](param)
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

    def validate_crop_class(self, crop_class):
        if crop_class != self.original_crop_class:
            super().validate_crop_class(crop_class)

    def populate(self, id: int):
        super().populate(id)
        self.crop_class.data = self.model_data.crop_class.name
        self.residues.data = self.model_data.residues.name
        self.legume_rate.data = self.model_data.legume_rate.name
        self.nmin_30.data = self.model_data.nmin[0]
        self.nmin_60.data = self.model_data.nmin[1]
        self.nmin_90.data = self.model_data.nmin[2]
        self.crop.choices = [
            (crop.id, crop.name)
            for crop in current_user.get_crops(
                (
                    CropClass.main_crop
                    if self.model_data.crop_class == CropClass.second_crop
                    else self.model_data.crop_class
                )
            )
        ]
        self.crop.data = str(self.model_data.crop.id)
        self.original_crop_class = self.crop_class.data
        # remove non-relevant inputs
        feedable = self.model_data.crop.feedable
        crop_class = self.model_data.crop_class
        residues = self.model_data.residues.value
        if feedable or crop_class != CropClass.main_crop:
            del self.nmin_30
            del self.nmin_60
            del self.nmin_90
        if not feedable:
            del self.crop_protein
        if not (feedable or crop_class == CropClass.catch_crop):
            del self.legume_rate
        if crop_class == CropClass.catch_crop:
            del self.crop_yield
        if residues is None:
            del self.residues


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
        self.measure.data = self.model_data.measure.name
        self.fertilizer.choices = [
            (fert.id, fert.name) for fert in current_user.get_fertilizer(self.fert_class.data)
        ]
        self.original_measure = self.measure.data


class EditFertilizerForm(FertilizerForm):
    def __init__(self, name, year, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_name = name
        self.original_year = year

    def validate(self):
        if self.name.data != self.original_name or self.year.data != self.original_year:
            return super().validate()
        return True

    def populate(self, id: int):
        super().populate(id)
        self.fert_class.data = self.data.fert_class.name
        self.fert_type.data = self.data.fert_type.name
        self.unit.data = self.data.unit.name


class EditCropForm(CropForm):
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_name = name

    def validate_name(self, name):
        if name != self.original_name:
            super().validate_name(name)

    def populate(self, id: int):
        super().populate(id)
        self.positiv_yield.data = self.model_data.var_yield[0]
        self.negativ_yield.data = self.model_data.var_yield[1]
        self.crop_class.data = self.model_data.crop_class.name
        self.crop_type.data = self.model_data.crop_type.name


class EditSoilForm(SoilForm):
    def __init__(self, base_id, *args, **kwargs):
        super().__init__(base_id, *args, **kwargs)

    def validate_year(self, year):
        if year != self.year.data:
            super().validate_year(year)

    def populate(self, id: int):
        super().populate(id)
        self.soil_type.data = self.model_data.soil_type.name
        self.humus.data = self.model_data.humus.name

from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError

from app.database.model import User
from app.model.forms import (
    BaseFieldForm,
    CropForm,
    CultivationFrom,
    FertilizationFrom,
    FertilizerForm,
    FieldForm,
    SoilForm,
)


def fill_form(form, **kwargs):
    for key, v in kwargs:
        arg = form.__dict__[key]
        arg.data = v
    # return form


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


class EditCultivationFrom(CultivationFrom):
    def __init__(self, crop_class, field_id, *args, **kwargs):
        super().__init__(field_id, *args, **kwargs)
        self.original_crop_class = crop_class

    def validate_crop_class(self, crop_class):
        if crop_class != self.original_crop_class:
            super().validate_crop_class(crop_class)


class EditFertilizationForm(FertilizationFrom):
    def __init__(self, measure, field_id, *args, **kwargs):
        super().__init__(field_id, *args, **kwargs)
        self.original_measure = measure

    def validate_measure(self, measure):
        if measure != self.original_measure:
            super().validate_measure(measure)


class EditFertilizerForm(FertilizerForm):
    def __init__(self, name, year, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_name = name
        self.original_year = year

    def validate(self):
        if self.name.data != self.original_name or self.year.data != self.original_year:
            return super().validate()
        return True


class EditCropForm(CropForm):
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_name = name

    def validate_name(self, name):
        if name != self.original_name:
            super().validate_name(name)


class EditSoilForm(SoilForm):
    def __init__(self, year, base_id, *args, **kwargs):
        super().__init__(base_id, *args, **kwargs)
        self.original_year = year

    def validate_year(self, year):
        if year != self.original_year:
            super().validate_year(year)

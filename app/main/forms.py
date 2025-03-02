from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (
    HiddenField,
    RadioField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired, Email, InputRequired, ValidationError

from app.api.forms import FormHelper
from app.database import Field, User, confirm_id
from app.database.model import BaseField, Crop, Cultivation, Fertilization, Fertilizer
from app.database.types import DemandType, FertClass, NutrientType
from app.extensions import db

__all__ = ["EditProfileForm", "EmptyForm", "YearForm"]


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


class DemandForm(FlaskForm):
    field_id = HiddenField("Field ID")
    demand_option = HiddenField("Demand Option")
    nutrient = HiddenField("Nutrient")
    submit = SubmitField("Submit")

    def __init__(self, *args, **kwargs):
        super().__init__(prefix="demand_option", *args, **kwargs)

    def validate_field_id(self, field_id):
        id = confirm_id(field_id.data, current_user.id, "field", "edit")
        if not id:
            raise ValidationError("Invalid form inputs.")

    def validate_demand_option(self, demand_option):
        try:
            demand_option.data = DemandType(demand_option.data)
        except KeyError:
            try:
                demand_option.data = DemandType[demand_option.data.lower()]
            except ValueError:
                raise ValidationError("Invalid demand option.")

    def validate_nutrient(self, nutrient):
        try:
            nutrient.data = NutrientType[nutrient.data]
        except KeyError:
            raise ValidationError("Invalid nutrient input.")

    def save(self):
        field = Field.query.get(self.field_id.data)
        if self.nutrient.data is NutrientType.p2o5:
            field.demand_p2o5 = self.demand_option.data
        elif self.nutrient.data is NutrientType.k2o:
            field.demand_k2o = self.demand_option.data
        elif self.nutrient.data is NutrientType.mgo:
            field.demand_mgo = self.demand_option.data
        db.session.commit()


class ListForm(FormHelper, FlaskForm):
    list_type = RadioField(
        "Which type of list do you need?",
        validators=[InputRequired()],
        render_kw={"onclick": "handleRadio(this)"},
    )
    # item_type = RadioField("Which type of items do you want to select?")
    year = SelectField("Select the year you need.", validators=[InputRequired()])
    fields = SelectMultipleField(
        "Select the fields you need.",
        validators=[InputRequired()],
        render_kw={
            "multiselect-search": "true",
            "multiselect-select-all": "true",
            "multiselect-max-items": "10",
            "multiselect-hide-x": "true",
            # "size": 10,
        },
    )
    crops = SelectMultipleField(
        "Select the crops you need.",
        render_kw={
            "multiselect-search": "true",
            "multiselect-select-all": "true",
            "multiselect-max-items": "10",
            "multiselect-hide-x": "false",
            "size": 10,
        },
    )
    fertilizers = SelectMultipleField(
        "Select the fertilizers you need.",
        render_kw={
            "multiselect-search": "true",
            "multiselect-select-all": "true",
            "multiselect-max-items": "10",
            "multiselect-hide-x": "false",
            "size": 10,
        },
    )
    submit = SubmitField("Show")

    def __init__(self, user_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = user_id
        self.list_type.choices = [
            ("mineral", "Mineral Fertilizations"),
            ("organic", "Organic Fertilizations"),
            ("crops", "Cultivations"),
            ("fields", "Field balance"),
        ]
        # self.item_type.choices = ["Fields", "Crops", "Fertilizers"]
        self.year.choices = sorted(
            list(set((field.year for field in Field.query.all()))), reverse=True
        )
        fields = (
            Field.query.join(BaseField)
            .filter(BaseField.user_id == current_user.id, Field.year == current_user.year)
            .all()
        )
        self.fields.choices = [
            (
                field.id,
                f"{field.base_field.prefix:02}-{field.base_field.suffix} {field.base_field.name}",
            )
            for field in fields
        ]
        # crops = Crop.query.filter(Crop.user_id == current_user.id).all()
        crops = (
            Crop.query.join(Cultivation).join(Field).filter(Field.year == current_user.year).all()
        )
        self.crops.choices = sorted([(crop.id, crop.name) for crop in crops], key=lambda x: x[1])
        fertilizers = Fertilizer.query.filter(
            Fertilizer.user_id == current_user.id, Fertilizer.year.in_([current_user.year, 0])
        ).all()
        self.fertilizers.choices = [(fertilizer.id, fertilizer.name) for fertilizer in fertilizers]

    def update_choices(self):
        if self.year.data:
            fields = (
                Field.query.join(BaseField)
                .filter(BaseField.user_id == current_user.id, Field.year == self.year.data)
                .all()
            )
            self.fields.choices = [
                (
                    field.id,
                    f"{field.base_field.prefix:02}-{field.base_field.suffix} {field.base_field.name}",
                )
                for field in fields
            ]

            fertilizers = (
                Fertilizer.query.join(Fertilization)
                .join(Field)
                .filter(Field.year == self.year.data)
            )
            if self.list_type.data == "mineral":
                fertilizers = fertilizers.filter(Fertilizer.fert_class == FertClass.mineral)
            elif self.list_type.data == "organic":
                fertilizers = fertilizers.filter(Fertilizer.fert_class == FertClass.organic)
            elif self.list_type.data == "crops":
                self.add_render_kw(self.fertilizers, "disabled", "")
            elif self.list_type.data == "fields":
                self.add_render_kw(self.crops, "disabled", "")
                self.add_render_kw(self.fertilizers, "disabled", "")
            self.fertilizers.choices = sorted(
                [(fertilizer.id, fertilizer.name) for fertilizer in fertilizers.all()],
                key=lambda x: x[1],
            )
            crops = (
                Crop.query.join(Cultivation).join(Field).filter(Field.year == self.year.data).all()
            )
            self.crops.choices = sorted(
                [(crop.id, crop.name) for crop in crops], key=lambda x: x[1]
            )

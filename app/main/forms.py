from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError

from app.database import Field, User, confirm_id
from app.database.types import DemandType, NutrientType
from app.extensions import db

__all__ = [
    "EditProfileForm",
    "EmptyForm",
    "YearForm",
]


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

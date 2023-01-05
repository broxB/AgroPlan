__all__ = [
    "BaseFieldForm",
    "FieldForm",
    "CultivationForm",
    "CropForm",
    "FertilizationForm",
    "FertilizerForm",
    "SoilForm",
]

from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    FloatField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
)
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
    ResidueType,
    SoilType,
    UnitType,
)


class BaseFieldForm(FlaskForm):
    prefix = IntegerField("Prefix:", validators=[DataRequired()])
    suffix = IntegerField("Suffix:", validators=[DataRequired()])
    name = StringField("Name:", validators=[DataRequired()])
    submit = SubmitField("Add")

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


class FieldForm(FlaskForm):
    sub_suffix = IntegerField("Sub-Suffix:")
    year = IntegerField("Year:", validators=[DataRequired()])
    area = FloatField("Area:", validators=[DataRequired()])
    red_region = BooleanField("In red region?", validators=[DataRequired()])
    field_type = SelectField(
        "Select field type:",
        choices=[enum.value for enum in FieldType],
        validators=[DataRequired()],
    )
    demand_type = SelectField(
        "Select demand type:",
        choices=[enum.value for enum in DemandType],
        validators=[DataRequired()],
    )
    submit = SubmitField("Submit")

    def __init__(self, base_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_id = base_id
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


class CultivationFrom(FlaskForm):
    crop_class = SelectField(
        "Select crop class:",
        choices=[enum.value for enum in CropClass],
        validators=[DataRequired()],
    )
    crop = SelectField("Select fruit to grow:", validators=[DataRequired()])
    est_yield = IntegerField("Estimated yield:", validators=[DataRequired()])
    est_protein = FloatField("Estimated protein:")
    residues = SelectField(
        "Estimated residues:",
        choices=[enum.value for enum in ResidueType],
        validators=[DataRequired()],
    )
    legume_rate = SelectField(
        "Share of legumes:",
        choices=[enum.value for enum in LegumeType],
        validators=[DataRequired()],
    )
    nmin_30 = IntegerField("Nmin 30cm:", validators=[DataRequired()])
    nmin_60 = IntegerField("Nmin 60cm:", validators=[DataRequired()])
    nmin_90 = IntegerField("Nmin 90cm:", validators=[DataRequired()])
    submit = SubmitField("Submit")

    def __init__(self, field_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_id = field_id
        # js implementation
        # choices = [
        #     (crop.id, crop.name)
        #     for crop in Crop.query.filter(
        #         Crop.user_id == current_user.id,
        #         Crop.crop_class == self.crop_class.data,
        #     ).all()
        # ]
        # self.crop.choices = choices

    def validate_crop_class(self, crop_class):
        cultivation = (
            Cultivation.query.join(Field)
            .filter(Field.id == self.field_id, Cultivation.crop_class == crop_class)
            .first()
        )
        if cultivation is not None:
            raise ValidationError("Class already exists.")


class FertilizationFrom(FlaskForm):
    fert_class = SelectField(
        "Select fertilizer type:",
        choices=[enum.value for enum in FertClass],
        validators=[DataRequired()],
    )
    fertilizer = SelectField("Select fertilizer:", validators=[DataRequired()])
    amount = FloatField("Amount:", validators=[DataRequired()])
    measure = SelectField(
        "Select measure:",
        choices=[enum.value for enum in MeasureType],
        validators=[DataRequired()],
    )
    month = IntegerField("Month:")
    submit = SubmitField("Submit:")

    def __init__(self, field_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_id = field_id
        # js implementation
        # choices = [
        #     (fert.id, fert.name)
        #     for fert in Fertilizer.query.filter(
        #         Fertilizer.user_id == current_user.id,
        #         Fertilizer.fert_class == self.fert_class.data,
        #     ).all()
        # ]
        # self.fertilizer.choices = choices

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


class FertilizerForm(FlaskForm):
    name = StringField("Name:", validators=[DataRequired()])
    year = IntegerField("Year:", validators=[DataRequired()])
    fert_class = SelectField(
        "Select fertilizer class:",
        choices=[enum.value for enum in FertClass],
        validators=[DataRequired()],
    )
    fert_type = SelectField(
        "Select fertilizer type:",
        choices=[enum.value for enum in FertType],
        validators=[DataRequired()],
    )
    unit = SelectField(
        "Select measurement unit:",
        choices=[enum.value for enum in UnitType],
        validators=[DataRequired()],
    )
    active = BooleanField("Show fertilizer in list?")
    n = FloatField("N:", validators=[DataRequired()])
    p2o5 = FloatField("P2O5:", validators=[DataRequired()])
    k2o = FloatField("K2O:", validators=[DataRequired()])
    mgo = FloatField("MgO:", validators=[DataRequired()])
    sulfur = FloatField("S:", validators=[DataRequired()])
    cao = FloatField("CaO:", validators=[DataRequired()])
    nh4 = FloatField("NH4:", validators=[DataRequired()])

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


class CropForm(FlaskForm):
    name = StringField("Name:", validators=[DataRequired()])
    crop_class = SelectField(
        "Select a fruit class:",
        choices=[enum.value for enum in CropClass],
        validators=[DataRequired()],
    )
    crop_type = SelectField(
        "Select a fruit type:",
        choices=[enum.value for enum in CropType],
        validators=[DataRequired()],
    )
    crop_kind = StringField("Fruit subtype:", validators=[DataRequired()])
    feedable = BooleanField("Is feedable?", validators=[DataRequired()])
    residue = BooleanField("Has residues?", validators=[DataRequired()])
    nmin_depth = IntegerField("Nmin to depth:", validators=[DataRequired()])
    target_demand = IntegerField("Target demand:", validators=[DataRequired()])
    target_yield = IntegerField("Target yield:", validators=[DataRequired()])
    positiv_yield = StringField(
        "Demand change if yield delta is positive:", validators=[DataRequired()]
    )
    negativ_yield = IntegerField(
        "Demand change if yield delta is negative:", validators=[DataRequired()]
    )
    target_protein = IntegerField("Target protein:", validators=[DataRequired()])
    delta_protein = FloatField("Demand change with protein delta:", validators=[DataRequired()])
    n_fruit = FloatField("Fruit N:", validators=[DataRequired()])
    p_fruit = FloatField("Fruit P2O5:", validators=[DataRequired()])
    k_fruit = FloatField("Fruit K2O:", validators=[DataRequired()])
    mg_fruit = FloatField("Fruit MgO:", validators=[DataRequired()])
    byproduct = StringField("Residue:")
    byproduct_ratio = FloatField("Residue ratio:", validators=[DataRequired()])
    n_byp = FloatField("Residue N:", validators=[DataRequired()])
    p_byp = FloatField("Residue P2O5:", validators=[DataRequired()])
    k_byp = FloatField("Residue K2O:", validators=[DataRequired()])
    mg_byp = FloatField("Residue MgO:", validators=[DataRequired()])

    def validate_name(self, name):
        crop = Crop.query.filter(Crop.user_id == current_user.id, Crop.name == name).first()
        if crop is not None:
            raise ValidationError(f"{name} already exists.")


class SoilForm(FlaskForm):
    year = IntegerField("Year:", validators=[DataRequired()])
    ph = FloatField("pH:", validators=[DataRequired()])
    p2o5 = FloatField("P2O5:", validators=[DataRequired()])
    k2o = FloatField("K2O:", validators=[DataRequired()])
    mg = FloatField("Mg:", validators=[DataRequired()])
    soil_type = SelectField(
        "Select soil composition:",
        choices=[enum.value for enum in SoilType],
        validators=[DataRequired()],
    )
    humus = SelectField(
        "Select humus ratio:",
        choices=[enum.value for enum in HumusType],
        validators=[DataRequired()],
    )

    def __init__(self, base_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_id = base_id

    def validate_year(self, year):
        soil_sample = SoilSample.query.filter(
            SoilSample.base_id == self.base_id, SoilSample.year == year
        ).first()
        if soil_sample is not None:
            raise ValidationError(f"Soil sample for {year} already exists.")

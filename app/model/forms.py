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


def create_form(modal: str, params: list) -> FlaskForm | None:
    modal_types = {
        "base_field": BaseFieldForm,
        "field": FieldForm,
        "cultivation": CultivationForm,
        "fertilization": FertilizationForm,
        "crop": CropForm,
        "fertilizer": FertilizerForm,
        "soil": SoilForm,
    }
    try:
        form = modal_types[modal](*params)
    except KeyError:
        form = None
    return form


class FormHelper:
    def populate(self: FlaskForm, id):
        self.model_data = self.model_type.query.filter_by(id=int(id)).first()
        self.process(obj=self.model_data)

    # credit: https://stackoverflow.com/a/71562719/16256581
    def disable(self, input_field):
        """
        disable the given input

        Args:
            inputField(Input): the WTForms input to disable
            disabled(bool): if true set the disabled attribute of the input
        """
        if input_field.render_kw is None:
            input_field.render_kw = {}
        input_field.render_kw["disabled"] = "disabled"


class BaseFieldForm(FlaskForm, FormHelper):
    prefix = IntegerField("Prefix:", validators=[DataRequired()])
    suffix = IntegerField("Suffix:", validators=[DataRequired()])
    name = StringField("Name:", validators=[DataRequired()])
    submit = SubmitField("Add")

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
    area = FloatField("Area:", validators=[DataRequired()])
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
    submit = SubmitField("Submit")

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
        "Select crop class:",
        choices=[(enum.name, enum.value) for enum in list(CropClass)[:3]],
        validators=[DataRequired()],
    )
    crop = SelectField("Select fruit to grow:", validators=[DataRequired()])
    crop_yield = IntegerField("Estimated yield:", validators=[DataRequired()])
    crop_protein = FloatField("Estimated protein:")
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
    submit = SubmitField("Submit")

    def __init__(self, field_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_id = field_id
        self.model_type = Cultivation
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


class FertilizationForm(FlaskForm, FormHelper):
    crop = SelectField("Select crop to fertilize:", validators=[DataRequired()])
    fert_class = SelectField(
        "Select fertilizer type:",
        choices=[(enum.name, enum.value) for enum in FertClass],
        validators=[DataRequired()],
    )
    fertilizer = SelectField("Select fertilizer:", validators=[DataRequired()])
    measure = SelectField(
        "Select measure:",
        choices=[(enum.name, enum.value) for enum in MeasureType],
        validators=[DataRequired()],
    )
    amount = FloatField("Amount:", validators=[DataRequired()])
    month = IntegerField("Month:")
    submit = SubmitField("Submit")

    def __init__(self, field_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_id = field_id
        self.model_type = Fertilization
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
    submit = SubmitField("Submit")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_type = Fertilizer

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
        "Select a fruit class:",
        choices=[(enum.name, enum.value) for enum in CropClass],
        validators=[DataRequired()],
    )
    crop_type = SelectField(
        "Select a fruit type:",
        choices=[(enum.name, enum.value) for enum in CropType],
        validators=[DataRequired()],
    )
    kind = StringField("Fruit subtype:", validators=[DataRequired()])
    feedable = BooleanField("Is feedable?", validators=[DataRequired()])
    residue = BooleanField("Has residues?", validators=[DataRequired()])
    nmin_depth = IntegerField("Nmin to depth:", validators=[DataRequired()])
    target_demand = IntegerField("Target demand:", validators=[DataRequired()])
    target_yield = IntegerField("Target yield:", validators=[DataRequired()])
    positive_yield = StringField(
        "Demand change if yield delta is positive:", validators=[DataRequired()]
    )
    negative_yield = IntegerField(
        "Demand change if yield delta is negative:", validators=[DataRequired()]
    )
    target_protein = IntegerField("Target protein:", validators=[DataRequired()])
    var_protein = FloatField("Demand change with protein delta:", validators=[DataRequired()])
    n = FloatField("Fruit N:", validators=[DataRequired()])
    p2o5 = FloatField("Fruit P2O5:", validators=[DataRequired()])
    k2o = FloatField("Fruit K2O:", validators=[DataRequired()])
    mgo = FloatField("Fruit MgO:", validators=[DataRequired()])
    byproduct = StringField("Residue:")
    byp_ratio = FloatField("Residue ratio:", validators=[DataRequired()])
    byp_n = FloatField("Residue N:", validators=[DataRequired()])
    byp_p2o5 = FloatField("Residue P2O5:", validators=[DataRequired()])
    byp_k2o = FloatField("Residue K2O:", validators=[DataRequired()])
    byp_mgo = FloatField("Residue MgO:", validators=[DataRequired()])
    submit = SubmitField("Submit")

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
    submit = SubmitField("Submit")

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

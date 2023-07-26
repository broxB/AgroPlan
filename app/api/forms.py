from __future__ import annotations

from typing import Any, Union

import wtforms
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
from wtforms.validators import (
    DataRequired,
    InputRequired,
    NumberRange,
    Optional,
    ValidationError,
)

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
    CatchCropLegumeType,
    CatchCropResidueType,
    CropClass,
    CropType,
    CultivationType,
    CutTiming,
    DemandType,
    FertClass,
    FertType,
    FieldType,
    FieldTypeForCrops,
    GrasslandLegumeType,
    HumusType,
    LegumeType,
    MainCropLegumeType,
    MainCropResidueType,
    MainCultivationType,
    MeasureType,
    MineralMeasureType,
    NminType,
    NutrientType,
    OrganicMeasureType,
    ResidueType,
    SoilType,
    UnitType,
    UsedCultivationType,
    find_crop_class,
    find_min_fert_type,
    find_org_fert_type,
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
    """
    Class under which form functionality is handled.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # reset render keywords because wtforms caches them between requests
        for field in self._fields.values():
            self.remove_render_kw(field, "selected")

    @staticmethod
    def add_render_kw(field: wtforms.Field, name: str, value: Any):
        """
        Add `name` to `render_kw` for `WTForms.Field`.
        Doesn't override other render_kws.

            :param field:
                WTForm input to which `render_kw` should be add.
            :param name:
                `name` of the render_kw.
            :param value:
                `value` for the render_kw.
        """
        if field.render_kw is None:
            field.render_kw = {}
        field.render_kw[name] = value

    @staticmethod
    def remove_render_kw(field: wtforms.Field, name: str):
        """
        Removes `render_kw` with `name` for `WTForms.Field`,
        because WTForms seems to cache them.

        :param field:
            WTForm input which `render_kw` should be reset.
        :param name:
            `name` of the render_kw.
        """
        try:
            field.render_kw.pop(name)
        except (AttributeError, KeyError):
            pass

    @staticmethod
    def field_data(field: wtforms.Field) -> Any | None:
        """
        Tries to get data from input. Looks at data and raw_data attributes.

        :param field:
            WTForm input from which data should be extracted.
        :return:
            Returns input data or None.
        """
        if field.data is not None:
            return field.data
        try:
            return field.raw_data[0]
        except (IndexError, TypeError):
            return None

    def reset_data(self, field: wtforms.Field):
        """
        Reset inputs data and remove `selected` from `render_kw`.

        :param field:
            WTForm input which should be reset.
        """
        try:
            field.data = None
            field.raw_data = None
            self.remove_render_kw(field, "selected")
        except AttributeError:
            pass

    def set_selected_inputs(self):
        """
        Sets `selected` render_kw for inputs that have data.
        """
        for name, data in self.data.items():
            if data is not None:
                field = self._fields.get(name)
                if field.render_kw is None:
                    field.render_kw = {}
                field.render_kw |= {"selected": ""}

    def get_data(self, id: int):
        """
        Fetches data for form specific model from database.

        :param id:
            Form specific database model `id`.
        """
        self.model_data: ModelType = self.model_type.query.get(id)

    def populate(self: Form, id: int):
        """
        Populate form with data from provided database `id`.

        :param id:
            Form specific database `id`.
        """
        if not hasattr(self, "model_data"):
            self.get_data(id)
        self.process(obj=self.model_data)

    def default_selects(self):
        """
        Creates default choices for form specific SelectFields.
        """
        ...

    def update_content(self):
        """
        Updates form data based on selected SelectField choices.
        """
        ...


Form = Union[FormHelper, FlaskForm]


def create_form(form_type: str) -> FlaskForm | FormHelper | None:
    """
    Factory for forms that can be filled with new data.
    """
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


class BaseFieldForm(FormHelper, FlaskForm):
    prefix = IntegerField("Prefix:", validators=[InputRequired()])
    suffix = IntegerField("Suffix:", validators=[InputRequired()])
    name = StringField("Name:", validators=[DataRequired()])

    def __init__(self, _, *args, **kwargs):
        super().__init__(*args, **kwargs)

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


class FieldForm(FormHelper, FlaskForm):
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


class CultivationForm(FormHelper, FlaskForm):
    cultivation_type = SelectField(
        "Select type of cultivation:",
        choices=[(enum.name, enum.value) for enum in UsedCultivationType],
        validators=[InputRequired()],
        render_kw={"class": "reload"},
    )
    crop = SelectField(
        "Select crop to grow:", validators=[InputRequired()], render_kw={"class": "reload"}
    )
    crop_yield = IntegerField("Estimated yield in dt/ha:", validators=[Optional()])
    crop_protein = DecimalField("Estimated protein in % DM/ha:", validators=[Optional()])
    residue_type = SelectField(
        "Estimated residues:",
        choices=[(enum.name, enum.value) for enum in ResidueType],
        validators=[Optional()],
    )
    legume_type = SelectField(
        "Share of legumes:",
        choices=[(enum.name, enum.value) for enum in LegumeType],
        validators=[Optional()],
    )
    nmin_30 = IntegerField("Nmin 30cm:", validators=[Optional()])
    nmin_60 = IntegerField("Nmin 60cm:", validators=[Optional()])
    nmin_90 = IntegerField("Nmin 90cm:", validators=[Optional()])

    def __init__(self, field_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_id = field_id

    def default_selects(self):
        field = Field.query.get(self.field_id)
        self.crop.choices = [
            (crop.id, crop.name) for crop in current_user.get_crops(field_type=field.field_type)
        ]
        if field.field_type is FieldType.grassland:
            self.cultivation_type.choices = [
                (e.name, e.value) for e in [CultivationType.main_crop]
            ]

    def update_content(self):
        self.default_selects()
        self.set_selected_inputs()

        def reset_data():
            self.reset_data(self.crop)
            self.reset_data(self.legume_type)
            self.reset_data(self.residue_type)

        if self.cultivation_type.data != CultivationType.main_crop.name:
            del self.nmin_30
            del self.nmin_60
            del self.nmin_90

        field_type = Field.query.get(self.field_id).field_type
        try:
            crop_class = find_crop_class(CultivationType[self.cultivation_type.data])
        except TypeError:
            crop_class = None

        if self.cultivation_type.data in [e.name for e in MainCultivationType]:
            crop = Crop.query.filter(
                Crop.id == self.crop.data, Crop.crop_class == crop_class
            ).first()
            if crop is None:
                reset_data()

            crop_choices = current_user.get_crops(
                crop_class=CropClass.main_crop, field_type=field_type
            )
            residue_type = MainCropResidueType

            if field_type is FieldType.grassland:
                legume_type = GrasslandLegumeType
            elif field_type is FieldType.cropland:
                legume_type = MainCropLegumeType
            else:
                legume_type = LegumeType

        elif self.cultivation_type.data == CultivationType.catch_crop.name:
            crop = Crop.query.filter(
                Crop.user_id == current_user.id,
                Crop.id == self.crop.data,
                Crop.crop_class == crop_class,
            ).first()
            if crop is None:
                reset_data()

            crop_choices = current_user.get_crops(crop_class=CropClass.catch_crop)
            residue_type = CatchCropResidueType
            legume_type = CatchCropLegumeType

            del self.crop_yield
            del self.crop_protein

        self.crop.choices = [(crop.id, crop.name) for crop in crop_choices]
        self.residue_type.choices = [(e.name, e.value) for e in residue_type]
        self.legume_type.choices = [(e.name, e.value) for e in legume_type]

        if crop:
            match crop.nmin_depth:
                case NminType.nmin_0:
                    del self.nmin_30
                    del self.nmin_60
                    del self.nmin_90
                case NminType.nmin_30:
                    del self.nmin_60
                    del self.nmin_90
                case NminType.nmin_60:
                    del self.nmin_90

            if not crop.residue:
                del self.residue_type

            if not crop.feedable:
                del self.crop_protein
                if crop.crop_class is not CropClass.catch_crop:
                    del self.legume_type

            if self.crop_yield and not self.crop_yield.data:
                self.add_render_kw(self.crop_yield, "value", crop.target_yield)

            if self.crop_protein and not self.crop_protein.data:
                self.add_render_kw(self.crop_protein, "value", crop.target_protein)

    def validate_cultivation_type(self, cultivation_type):
        """
        Verifies that cultivations are unique on a field.

        :raises ValidationError: Raises error when cultivation already exists.
        """
        cultivation = (
            Cultivation.query.join(Field)
            .filter(
                Field.id == self.field_id, Cultivation.cultivation_type == cultivation_type.data
            )
            .first()
        )
        if cultivation is not None:
            self.cultivation_type.errors.append("This type of cultivation type already exists.")
            return False
        return True


class FertilizationForm(FormHelper, FlaskForm):
    cultivation = SelectField(
        "Select a crop to fertilize:", validators=[Optional()], render_kw={"class": "reload"}
    )
    cut_timing = SelectField(
        "Select a cut timing:",
        choices=[(enum.name, enum.value) for enum in CutTiming],
        validators=[Optional()],
    )
    fert_class = SelectField(
        "Select a fertilizer type:",
        choices=[(enum.name, enum.value) for enum in FertClass],
        validators=[Optional()],
        render_kw={"class": "reload"},
    )
    measure_type = SelectField(
        "Select a measure:",
        choices=[(enum.name, enum.value) for enum in MeasureType],
        validators=[InputRequired()],
        render_kw={"class": "reload"},
    )
    fertilizer = SelectField(
        "Select a fertilizer:", validators=[InputRequired()], render_kw={"class": "reload"}
    )
    month = IntegerField("Month:", validators=[Optional()])
    amount = DecimalField("Amount:", validators=[InputRequired()])

    def __init__(self, field_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_id = field_id

    def default_selects(self):
        field = Field.query.get(self.field_id)
        self.cultivation.choices = [
            (cultivation.id, cultivation.crop.name) for cultivation in field.cultivations
        ]
        self.fertilizer.choices = [(fert.id, fert.name) for fert in current_user.get_fertilizers()]

        if not any(cultivation.crop.feedable for cultivation in field.cultivations):
            del self.cut_timing

    def update_content(self):
        self.default_selects()
        self.set_selected_inputs()

        def reset_data():
            self.reset_data(self.measure_type)
            self.reset_data(self.fertilizer)
            self.reset_data(self.month)
            self.reset_data(self.amount)

        cultivation = (
            Cultivation.query.join(Field)
            .filter(Cultivation.id == self.cultivation.data, Field.id == self.field_id)
            .one_or_none()
        )
        if cultivation is None:
            raise ValidationError(f"Selected cultivation doesn't exists.")

        if not cultivation.crop.feedable:
            del self.cut_timing

        if self.fert_class.data == FertClass.mineral.name:
            del self.month
            measure_type = MineralMeasureType
            if self.measure_type.data:
                try:
                    fert_types = find_min_fert_type_from_measure(self.measure_type.data)
                except TypeError:
                    reset_data()
                    choices = current_user.get_fertilizers(fert_class=FertClass.mineral)
                else:
                    choices = Fertilizer.query.filter(
                        Fertilizer.fert_type.in_([e.name for e in fert_types])
                    )
            else:
                choices = current_user.get_fertilizers(fert_class=FertClass.mineral)

        elif self.fert_class.data == FertClass.organic.name:
            measure_type = OrganicMeasureType
            try:
                fert_types = find_org_fert_type_from_measure(self.measure_type.data)
            except TypeError:
                reset_data()
            choices = current_user.get_fertilizers(
                fert_class=FertClass.organic, year=cultivation.field.year
            )

        else:
            # no fert_class option selected, needed for editform without fert_class shown
            measure_type = MeasureType
            choices = current_user.get_fertilizers()

        if self.fertilizer.data:
            fertilizer = Fertilizer.query.get(self.fertilizer.data)
            self.amount.label.text = f"Amount in {fertilizer.unit.value}/ha:"

        self.measure_type.choices = [(measure.name, measure.value) for measure in measure_type]
        self.fertilizer.choices = [(fertilizer.id, fertilizer.name) for fertilizer in choices]

    def validate_measure_type(self, measure_type):
        """
        Verifies that mineral measures are unique.
        """
        if self.measure_type.data in [e.name for e in MineralMeasureType]:
            fertilization = (
                Fertilization.query.join(Cultivation)
                .filter(
                    Cultivation.id == self.cultivation.data,
                    Fertilization.measure == measure_type.data,
                )
                .first()
            )
            if fertilization is not None:
                self.measure_type.errors.append(f"Measure already exists for cultivation.")
                return False

    def validate_amount(self, amount, edit_value=False) -> bool:
        """
        Verifies that amount of fertilizer is within the organic fall fertilization limit.
        """
        try:
            fert_amount = amount.data
        except AttributeError:
            fert_amount = amount

        if self.measure_type.data != MeasureType.org_fall.name:
            return True

        try:
            fertilizer = current_user.get_fertilizers(id=self.fertilizer.data)[0]
        except IndexError:
            self.fertilizer.errors.append(f"Invalid fertilizer selected.")
            return False
        cultivation = Cultivation.query.get(self.cultivation.data)
        field = cultivation.field

        n, nh4 = 0, 0
        for fertilization in field.fertilizations:
            if fertilization.measure is MeasureType.org_fall:
                n += fertilization.fertilizer.n * fertilization.amount
                nh4 += fertilization.fertilizer.nh4 * fertilization.amount
        fert_n = fertilizer.n * fert_amount
        fert_nh4 = fertilizer.nh4 * fert_amount
        sum_n = n + fert_n
        sum_nh4 = nh4 + fert_nh4

        if sum_n <= 60 and sum_nh4 <= 30:
            return True
        # Grassland or perennial field forage have a different limit.
        cultivations = [cultivation.cultivation_type for cultivation in field.cultivations]
        if (
            field.field_type is FieldType.grassland
            or cultivation.cultivation_type is CultivationType.main_crop
            and cultivation.crop.feedable
            and (
                CultivationType.second_main_crop not in cultivations
                or CultivationType.second_crop not in cultivations
            )
        ):
            if sum_n < (80 if not field.red_region else 60):
                return True
            else:
                fert_amount = ((80 if not field.red_region else 60) - n) // fertilizer.n
        else:
            fert_amount = min((30 - nh4) // fertilizer.nh4, (60 - n) // fertilizer.n)
        self.amount.errors.append(
            f"Maximum amount for fall fertilizations: {(fert_amount if not edit_value else fert_amount + self.model_data.amount)} {fertilizer.unit.value}/ha"
        )
        return False


class FertilizerForm(FormHelper, FlaskForm):
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


class CropForm(FormHelper, FlaskForm):
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

    def validate_name(self, name):
        crop = Crop.query.filter(Crop.user_id == current_user.id, Crop.name == name.data).first()
        if crop is not None:
            self.name.errors.append(f"{name.data} already exists.")
            return False


class SoilForm(FormHelper, FlaskForm):
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

    def validate_year(self, year):
        soil_sample = SoilSample.query.filter(
            SoilSample.base_id == self.base_id, SoilSample.year == year.data
        ).first()
        if soil_sample is not None:
            self.year.errors.append(f"Soil sample for {year.data} already exists.")
            return False


class ModifierForm(FormHelper, FlaskForm):
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

from __future__ import annotations

from typing import Any, Union

import wtforms
from flask_bootstrap import SwitchField
from flask_login import current_user
from flask_wtf import FlaskForm
from loguru import logger
from wtforms import BooleanField, DecimalField, IntegerField, SelectField, StringField
from wtforms.validators import InputRequired, Length, NumberRange, Optional

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
    CatchCropType,
    CropClass,
    CropType,
    CultivationType,
    CutTiming,
    DemandType,
    FallowCropType,
    FertClass,
    FertType,
    FieldType,
    FieldTypeForCrops,
    GrasslandCropType,
    GrasslandLegumeType,
    HumusType,
    LegumeType,
    MainCropLegumeType,
    MainCropResidueType,
    MainCropType,
    MeasureType,
    MineralMeasureType,
    NminType,
    NutrientType,
    OrganicMeasureType,
    ResidueType,
    SoilType,
    UnitType,
    UsedCultivationType,
)
from app.extensions import db

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
        self._reset_render_kw()

    def _reset_render_kw(self):
        """
        Resets certain render_kw because WTForms seems to cache them between requests.
        """
        for field in self._fields.values():
            self.remove_render_kw(field, "selected")
            self.remove_render_kw(field, "disabled")

    @staticmethod
    def add_render_kw(field: wtforms.Field, key: str, value: Any):
        """
        Add `key` to `render_kw` for `WTForms.Field`.
        Does override render_kw with the same key.

        :param field:
            WTForm input to which `key` should be add.
        :param key:
            `key` of the render_kw.
        :param value:
            `value` for the `key`.
        """
        if field.render_kw is None:
            field.render_kw = {}
        field.render_kw[key] = value

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
        except Exception as e:
            logger.warning(f"{e} with params {field=} and {name=}")

    @staticmethod
    def get(field: wtforms.Field, default=None) -> Any | None:
        """
        Tries to get data from input. Looks at data and raw_data attributes.

        :param field:
            WTForm input from which data should be extracted.
        :param default:
            If there is not data returns default value.
        :return:
            Returns input field data or default value if there is none.
        """
        try:
            if field.data is not None:
                return field.data
        except AttributeError:
            pass
        try:
            return field.raw_data[0]
        except (IndexError, TypeError, AttributeError):
            return default

    def has_field(self, field: wtforms.Field) -> bool:
        """
        Check if form has `field`.

        :param field:
            WTForms input field.
        """
        try:
            return hasattr(self, field.name)
        except (ValueError, AttributeError):
            return False

    def reset_field(self, field: wtforms.Field):
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
                if field.type == "SelectField":
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

    def populate(self: Form, id: int, **kwargs):
        """
        Populate form with data from provided database entry.

        :param id:
            Form specific database model `id`.
        """
        if not hasattr(self, "model_data"):
            self.get_data(id)
        self.process(obj=self.model_data, **kwargs)

    def save(self):
        """
        Save form data to database.
        """
        raise NotImplementedError

    def default_selects(self):
        """
        Creates default choices for form specific SelectFields.
        """
        ...

    def update_fields(self):
        """
        Updates form fields based on chosen SelectField choices.
        """
        ...


Form = Union[FormHelper, FlaskForm]


def create_form(form_type: str, id: int) -> FlaskForm | FormHelper:
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
        form = form_types[form_type](id)
    except TypeError:
        form = form_types[form_type]()
    return form


class BaseFieldForm(FormHelper, FlaskForm):
    prefix = IntegerField("Prefix:", validators=[InputRequired()])
    suffix = IntegerField("Suffix:", validators=[InputRequired()])
    name = StringField("Name:", validators=[InputRequired(), Length(min=1, max=25)])

    def __init__(self):
        super().__init__()

    def validate(self, **kwargs):
        valid = super().validate()
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

    def save(self):
        base_field = BaseField(
            user_id=current_user.id,
            prefix=self.prefix.data,
            suffix=self.suffix.data,
            name=self.name.data,
        )
        base_field.user = current_user
        db.session.add(base_field)
        db.session.commit()


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

    def __init__(self, base_field_id):
        super().__init__()
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

    def save(self):
        field = Field(
            base_id=self.base_id,
            sub_suffix=self.sub_suffix.data,
            year=self.year.data,
            area=self.area.data,
            red_region=self.red_region.data,
            field_type=self.field_type.data,
        )
        base_field = BaseField.query.get(self.base_id)
        field.base_field = base_field
        db.session.add(field)
        db.session.commit()


class CultivationForm(FormHelper, FlaskForm):
    cultivation_type = SelectField(
        "Select type of cultivation:",
        choices=[(enum.name, enum.value) for enum in UsedCultivationType],
        validators=[InputRequired()],
        render_kw={"class": "reload"},
    )
    crop_id = SelectField(
        "Select crop to grow:", validators=[InputRequired()], render_kw={"class": "reload"}
    )
    crop_yield = IntegerField(
        "Estimated yield in dt/ha:", validators=[InputRequired(), NumberRange(min=0)]
    )
    crop_protein = DecimalField(
        "Estimated protein in 0.1% DM/ha:",
        validators=[InputRequired(), NumberRange(min=0)],
        places=1,
    )
    residues = SelectField(
        "Estimated residues:",
        validators=[InputRequired()],
    )
    legume_rate = SelectField(
        "Share of legumes:",
        validators=[InputRequired()],
    )
    nmin_30 = IntegerField("Nmin 30cm:", validators=[InputRequired(), NumberRange(min=0)])
    nmin_60 = IntegerField("Nmin 60cm:", validators=[InputRequired(), NumberRange(min=0)])
    nmin_90 = IntegerField("Nmin 90cm:", validators=[InputRequired(), NumberRange(min=0)])

    def __init__(self, field_id):
        super().__init__()
        self.field_id = field_id

    def update_fields(self):
        def reset_form_data():
            """Resets data of multiple fields"""
            self.reset_field(self.crop_id)
            self.reset_field(self.legume_rate)
            self.reset_field(self.residues)
            self.reset_field(self.crop_yield)
            self.reset_field(self.crop_protein)

        self.set_selected_inputs()

        field_type = Field.query.get(self.field_id).field_type
        if field_type is FieldType.grassland:
            self.cultivation_type.choices = [
                (e.name, e.value) for e in [CultivationType.main_crop]
            ]

        if not self.cultivation_type.data:
            if not any(self.data.values()):
                return
            self.cultivation_type.errors = ["Please select a cultivation type first."]
            reset_form_data()
            return
        if self.cultivation_type.data != CultivationType.main_crop:
            del self.nmin_30
            del self.nmin_60
            del self.nmin_90

        try:
            crop_class = CropClass.from_cultivation(CultivationType[self.cultivation_type.data])
        except (TypeError, KeyError):
            crop_class = None

        if crop_class is CropClass.main_crop:
            if field_type is FieldType.grassland:
                legume_type = GrasslandLegumeType
            elif field_type is FieldType.cropland:
                legume_type = MainCropLegumeType
            else:
                legume_type = LegumeType

            residue_type = MainCropResidueType
            crop_choices = current_user.get_crops(
                crop_class=CropClass.main_crop, field_type=field_type
            )

            crop = Crop.query.filter(
                Crop.id == self.crop_id.data, Crop.crop_class == crop_class
            ).first()
            if crop is None:
                reset_form_data()

        elif crop_class is CropClass.catch_crop:
            del self.crop_yield
            del self.crop_protein
            legume_type = CatchCropLegumeType
            residue_type = CatchCropResidueType
            crop_choices = current_user.get_crops(crop_class=CropClass.catch_crop)

            crop = Crop.query.filter(
                Crop.user_id == current_user.id,
                Crop.id == self.crop_id.data,
                Crop.crop_class == crop_class,
            ).first()
            if crop is None:
                reset_form_data()

        self.crop_id.choices = [(crop.id, crop.name) for crop in crop_choices]
        self.residues.choices = [(e.name, e.value) for e in residue_type]
        self.legume_rate.choices = [(e.name, e.value) for e in legume_type]

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
                del self.residues

            if not crop.feedable:
                del self.crop_protein
                if crop.crop_class is not CropClass.catch_crop:
                    del self.legume_rate

            if self.crop_yield:
                self.add_render_kw(self.crop_yield, "placeholder", f"eg. {crop.target_yield}")

            if self.crop_protein:
                # hacky solution for decimal locale
                self.add_render_kw(
                    self.crop_protein,
                    "placeholder",
                    f"eg. {crop.target_protein}".replace(".", ","),
                )

    def validate_cultivation_type(self, cultivation_type):
        """
        Verifies that cultivations are unique on a field.
        """
        cultivation = (
            Cultivation.query.join(Field)
            .filter(
                Field.id == self.field_id, Cultivation.cultivation_type == cultivation_type.data
            )
            .first()
        )
        if cultivation is not None:
            self.cultivation_type.errors.append("This type of cultivation already exists.")
            return False
        return True

    def save(self):
        field = Field.query.get(self.field_id)
        crop = Crop.query.get(self.crop_id.data)
        cultivation = Cultivation(
            cultivation_type=self.cultivation_type.data,
            crop_yield=self.get(self.crop_yield, 0),
            crop_protein=self.get(self.crop_protein, None),
            residues=self.get(self.residues, ResidueType.none),
            legume_rate=self.get(self.legume_rate, LegumeType.none),
            nmin_30=self.get(self.nmin_30, 0),
            nmin_60=self.get(self.nmin_60, 0),
            nmin_90=self.get(self.nmin_90, 0),
        )
        cultivation.crop = crop
        cultivation.field = field
        db.session.add(cultivation)
        db.session.commit()


class FertilizationForm(FormHelper, FlaskForm):
    cultivation_id = SelectField(
        "Select a crop to fertilize:", validators=[InputRequired()], render_kw={"class": "reload"}
    )
    cut_timing = SelectField(
        "Select a cut timing:",
        choices=[(enum.name, enum.value) for enum in CutTiming],
        validators=[InputRequired()],
    )
    fert_class = SelectField(
        "Select a fertilizer type:",
        choices=[(enum.name, enum.value) for enum in FertClass],
        validators=[InputRequired()],
        render_kw={"class": "reload"},
    )
    measure_type = SelectField(
        "Select a measure:",
        choices=[(enum.name, enum.value) for enum in MeasureType],
        validators=[InputRequired()],
        render_kw={"class": "reload"},
    )
    fertilizer_id = SelectField(
        "Select a fertilizer:", validators=[InputRequired()], render_kw={"class": "reload"}
    )
    month = IntegerField("Month:", validators=[InputRequired(), NumberRange(min=1, max=12)])
    amount = DecimalField("Amount:", validators=[InputRequired(), NumberRange(min=0)])

    def __init__(self, field_id):
        super().__init__()
        self.field_id = field_id

    def update_fields(self):
        def reset_form_data():
            """Resets data of multiple fields"""
            self.reset_field(self.measure_type)
            self.reset_field(self.fertilizer_id)
            self.reset_field(self.month)
            self.reset_field(self.amount)

        self.set_selected_inputs()

        field = Field.query.get(self.field_id)
        self.cultivation_id.choices = [
            (cultivation.id, cultivation.crop.name) for cultivation in field.cultivations
        ]

        cultivation = (
            Cultivation.query.join(Field)
            .filter(Cultivation.id == self.cultivation_id.data, Field.id == self.field_id)
            .one_or_none()
        )
        if cultivation is None:
            if not any(self.data.values()):
                return
            self.cultivation_id.errors = ["Please select a cultivation first."]
            reset_form_data()
            self.reset_field(self.fert_class)
            # self.default_selects()
            return
        if not cultivation.crop.feedable:
            del self.cut_timing

        if self.fert_class.data == FertClass.mineral.name:
            del self.month
            self.amount.places = 1
            measure_type = MineralMeasureType
            if self.measure_type.data:
                fert_type = FertType.from_measure(MeasureType[self.measure_type.data])
                if not FertType.is_mineral(fert_type):
                    reset_form_data()
                    choices = current_user.get_fertilizers(fert_class=FertClass.mineral)
                else:
                    choices = Fertilizer.query.filter(
                        Fertilizer.fert_type.in_([e.name for e in fert_type])
                    )
            else:
                choices = current_user.get_fertilizers(fert_class=FertClass.mineral)
        elif self.fert_class.data == FertClass.organic.name:
            self.amount.places = 0
            measure_type = OrganicMeasureType
            if self.measure_type.data:
                fert_type = FertType.from_measure(MeasureType[self.measure_type.data])
                if not FertType.is_organic(fert_type):
                    reset_form_data()
            choices = current_user.get_fertilizers(
                fert_class=FertClass.organic, year=cultivation.field.year
            )
        # no fert_class option selected
        else:
            measure_type = MeasureType
            choices = current_user.get_fertilizers()

        if self.fertilizer_id.data:
            fertilizer = Fertilizer.query.get(self.fertilizer_id.data)
            self.amount.label.text = f"Amount in {fertilizer.unit.value}/ha:"

        self.measure_type.choices = [(measure.name, measure.value) for measure in measure_type]
        self.fertilizer_id.choices = [(fertilizer.id, fertilizer.name) for fertilizer in choices]

    def validate_measure_type(self, measure_type):
        """
        Verifies that mineral measures are unique.
        """
        if self.measure_type.data in [e.name for e in MineralMeasureType]:
            fertilization = (
                Fertilization.query.join(Cultivation)
                .filter(
                    Cultivation.id == self.cultivation_id.data,
                    Fertilization.measure == measure_type.data,
                )
                .first()
            )
            if fertilization is not None:
                self.measure_type.errors.append("Measure already exists for cultivation.")
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
            fertilizer = current_user.get_fertilizers(id=self.fertilizer_id.data)[0]
        except IndexError:
            self.fertilizer_id.errors.append("Invalid fertilizer selected.")
            return False
        cultivation = Cultivation.query.get(self.cultivation_id.data)
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

    def save(self):
        field = Field.query.get(self.field_id)
        cultivation = Cultivation.query.get(self.cultivation_id.data)
        fertilizer = Fertilizer.query.get(self.fertilizer_id.data)
        fertilization = Fertilization(
            cut_timing=self.get(self.cut_timing, CutTiming.none),
            measure=self.measure_type.data,
            month=self.get(self.month, None),
            amount=self.amount.data,
        )
        fertilization.cultivation = cultivation
        fertilization.fertilizer = fertilizer
        field.fertilizations.append(fertilization)
        db.session.add(fertilization)
        db.session.commit()


class FertilizerForm(FormHelper, FlaskForm):
    name = StringField("Name:", validators=[InputRequired(), Length(min=1, max=25)])
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
    unit_type = SelectField(
        "Select measurement unit:",
        choices=[(enum.name, enum.value) for enum in UnitType],
        validators=[InputRequired()],
    )
    year = IntegerField("Year:", validators=[InputRequired()])
    price = DecimalField("Price in €:", default=0.00)
    n = DecimalField("N:", validators=[InputRequired()])
    p2o5 = DecimalField("P2O5:", validators=[InputRequired()])
    k2o = DecimalField("K2O:", validators=[InputRequired()])
    mgo = DecimalField("MgO:", validators=[InputRequired()])
    s = DecimalField("S:", validators=[InputRequired()])
    cao = DecimalField("CaO:", validators=[InputRequired()])
    nh4 = DecimalField("NH4:", validators=[InputRequired()])
    active = BooleanField("Show fertilizer in list?")

    def __init__(self):
        super().__init__()

    def update_fields(self):
        self.set_selected_inputs()

        if self.fert_class.data in FertClass._member_map_:
            fert_type = FertType.from_fert_class(FertClass[self.fert_class.data])
            self.fert_type.choices = [(e.name, e.value) for e in fert_type]

        if self.fert_class.data == FertClass.mineral:
            del self.year

    def validate(self, **kwargs):
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
        # mineral fertilizer with no annual changes
        else:
            fertilizer = Fertilizer.query.filter(
                Fertilizer.user_id == current_user.id,
                Fertilizer.name == self.name.data,
            ).first()
            if fertilizer is not None:
                self.name.errors.append(f"{self.name.data} already exists.")
        return True

    def save(self):
        fertilizer = Fertilizer(
            user_id=current_user.id,
            name=self.name.data,
            year=self.get(self.year, 0),
            fert_class=self.fert_class.data,
            fert_type=self.fert_type.data,
            active=self.active.data,
            unit=self.unit_type.data,
            price=self.price.data,
            n=self.n.data,
            p2o5=self.p2o5.data,
            k2o=self.k2o.data,
            mgo=self.mgo.data,
            s=self.s.data,
            cao=self.cao.data,
            nh4=self.nh4.data,
        )
        db.session.add(fertilizer)
        db.session.commit()


class CropForm(FormHelper, FlaskForm):
    name = StringField("Name:", validators=[InputRequired()])
    field_type = SelectField(
        "Select on which type of field the crop grows:",
        choices=[(enum.name, enum.value) for enum in FieldTypeForCrops],
        validators=[InputRequired()],
        render_kw={"class": "reload"},
    )
    crop_class = SelectField(
        "Select a cultivation type:",
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
        "Fruit description (e.g. 'barley' for 'winter barley'):", validators=[InputRequired()]
    )
    nmin_depth = SelectField(
        "Select Nmin depth:",
        choices=[(enum.name, enum.value) for enum in NminType],
        validators=[InputRequired()],
    )
    target_demand = IntegerField(
        "Target need in kg N/ha:", validators=[InputRequired(), NumberRange(min=0)]
    )
    target_yield = IntegerField(
        "Target yield in dt/ha:", validators=[InputRequired(), NumberRange(min=0)]
    )
    pos_yield = DecimalField(
        "Change in need with positive yield difference in kg N/ha:",
        validators=[InputRequired(), NumberRange(min=0)],
    )
    neg_yield = DecimalField(
        "Change in need with negative yield difference in kg N/ha:",
        validators=[InputRequired(), NumberRange(min=0)],
    )
    p2o5 = DecimalField("P2O5:", validators=[InputRequired(), NumberRange(min=0)])
    k2o = DecimalField("K2O:", validators=[InputRequired(), NumberRange(min=0)])
    mgo = DecimalField("MgO:", validators=[InputRequired(), NumberRange(min=0)])
    feedable = SwitchField("Forage?", render_kw={"class": "reload"})
    target_protein = DecimalField(
        "Target protein in 0.1% DM/ha:", validators=[InputRequired(), NumberRange(min=0)]
    )
    var_protein = DecimalField(
        "Change in need with protein difference in kg N/ha:",
        validators=[InputRequired(), NumberRange(min=0)],
    )
    residue = SwitchField("Harvest residues?", render_kw={"class": "reload"})
    byproduct = StringField("Byproduct name:")
    byp_ratio = DecimalField(
        "Byproduct ratio in %:", validators=[InputRequired(), NumberRange(min=0)]
    )
    byp_n = DecimalField("Byproduct N:", validators=[InputRequired(), NumberRange(min=0)])
    byp_p2o5 = DecimalField("Byproduct P2O5:", validators=[InputRequired(), NumberRange(min=0)])
    byp_k2o = DecimalField("Byproduct K2O:", validators=[InputRequired(), NumberRange(min=0)])
    byp_mgo = DecimalField("Byproduct MgO:", validators=[InputRequired(), NumberRange(min=0)])

    def __init__(self):
        super().__init__()

    def update_fields(self):
        self.set_selected_inputs()

        if self.field_type.data == FieldType.grassland.name:
            self.crop_class.choices = [(e.name, e.value) for e in [CropClass.main_crop]]
            self.crop_type.choices = [(e.name, e.value) for e in GrasslandCropType]
            self.feedable.data = True
            self.add_render_kw(self.feedable, "disabled", "")
            del self.nmin_depth
            del self.residue
        elif self.field_type.data == FieldType.cropland.name:
            if self.crop_class.data == CropClass.catch_crop.name:
                self.crop_type.choices = [(e.name, e.value) for e in CatchCropType]
            else:
                self.crop_type.choices = [(e.name, e.value) for e in MainCropType]
        else:
            self.crop_class.choices = [(e.name, e.value) for e in [CropClass.main_crop]]
            self.crop_type.choices = [(e.name, e.value) for e in FallowCropType]
            del self.target_demand
            del self.target_yield
            del self.neg_yield
            del self.pos_yield
            del self.residue
            del self.feedable
            del self.p2o5
            del self.k2o
            del self.mgo
            del self.nmin_depth

        if not self.get(self.feedable):
            del self.target_protein
            del self.var_protein

        if not self.get(self.residue):
            del self.byproduct
            del self.byp_ratio
            del self.byp_n
            del self.byp_p2o5
            del self.byp_k2o
            del self.byp_mgo

    def validate_name(self, name):
        crop = Crop.query.filter(Crop.user_id == current_user.id, Crop.name == name.data).first()
        if crop is not None:
            self.name.errors.append(f"{name.data} already exists.")
            return False

    def save(self):
        crop = Crop(
            user_id=current_user.id,
            name=self.name.data,
            field_type=self.field_type.data,
            crop_class=self.crop_class.data,
            crop_type=self.crop_type.data,
            kind=self.kind.data,
            feedable=self.get(self.feedable, False),
            residue=self.get(self.residue, False),
            nmin_depth=self.get(self.nmin_depth, NminType.nmin_0),
            target_demand=self.get(self.target_demand, 0),
            target_yield=self.get(self.target_yield, 0),
            pos_yield=self.get(self.pos_yield, 0),
            neg_yield=self.get(self.neg_yield, 0),
            target_protein=self.get(self.target_protein, 0),
            var_protein=self.get(self.var_protein, 0),
            p2o5=self.get(self.p2o5, 0),
            k2o=self.get(self.k2o, 0),
            mgo=self.get(self.mgo, 0),
            byproduct=self.get(self.byproduct, False),
            byp_ratio=self.get(self.byp_ratio, 0),
            byp_n=self.get(self.byp_n, 0),
            byp_p2o5=self.get(self.byp_p2o5, 0),
            byp_k2o=self.get(self.byp_k2o, 0),
            byp_mgo=self.get(self.byp_mgo, 0),
        )
        db.session.add(crop)
        db.session.commit()


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
    ph = DecimalField("pH:", validators=[Optional()])
    p2o5 = DecimalField("P2O5:", validators=[Optional()])
    k2o = DecimalField("K2O:", validators=[Optional()])
    mg = DecimalField("Mg:", validators=[Optional()])

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

    def save(self):
        soil_sample = SoilSample(
            year=self.year.data,
            ph=self.ph.data,
            p2o5=self.p2o5.data,
            k2o=self.k2o.data,
            mg=self.mg.data,
            soil_type=self.soil_type.data,
            humus=self.humus_type.data,
        )
        base_field = BaseField.query.get(self.base_id)
        soil_sample.base_field = base_field
        db.session.add(soil_sample)
        db.session.commit()


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
        if abs(amount.data) > 1000:
            self.amount.errors.append("Only values up to 1000 kg/ha are allowed.")
            return False

    def save(self):
        modifier = Modifier(
            description=self.description.data,
            modification=self.modification.data,
            amount=self.amount.data,
        )
        field = Field.query.get(self.field_id)
        modifier.field = field
        db.session.add(modifier)
        db.session.commit()

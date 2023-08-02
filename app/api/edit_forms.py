from flask_login import current_user
from flask_wtf import FlaskForm

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
    CropClass,
    CultivationType,
    FertClass,
    FertType,
    FieldType,
    GrasslandLegumeType,
    LegumeType,
    MineralMeasureType,
    NminType,
    OrganicMeasureType,
    ResidueType,
    UsedCultivationType,
)

from .forms import (
    BaseFieldForm,
    CropForm,
    CultivationForm,
    FertilizationForm,
    FertilizerForm,
    FieldForm,
    FormHelper,
    ModifierForm,
    SoilForm,
)

__all__ = [
    "create_edit_form",
    "EditBaseFieldForm",
    "EditFieldForm",
    "EditCultivationForm",
    "EditCropForm",
    "EditFertilizationForm",
    "EditFertilizerForm",
    "EditSoilForm",
    "EditModifierForm",
]


def create_edit_form(form_type: str) -> FlaskForm | FormHelper | None:
    """Factory for forms that edit existing data."""
    form_types = {
        "base_field": EditBaseFieldForm,
        "field": EditFieldForm,
        "cultivation": EditCultivationForm,
        "fertilization": EditFertilizationForm,
        "crop": EditCropForm,
        "fertilizer": EditFertilizerForm,
        "soil": EditSoilForm,
        "modifier": EditModifierForm,
    }
    try:
        form = form_types[form_type]
    except KeyError:
        form = None
    return form


class EditBaseFieldForm(BaseFieldForm):
    def __init__(self, id, *args, **kwargs):
        self.model_type = BaseField
        self.get_data(id)
        super().__init__(id, *args, **kwargs)

    def validate(self, **kwargs):
        if (
            self.model_data.prefix != self.prefix.data
            or self.model_data.suffix != self.suffix.data
        ):
            return super().validate(**kwargs)
        return True

    def populate(self, id: int):
        super().populate(id)
        self.prefix.data = self.model_data.prefix
        self.suffix.data = self.model_data.suffix
        self.name.data = self.model_data.name


class EditFieldForm(FieldForm):
    def __init__(self, id: int, *args, **kwargs):
        self.model_type = Field
        self.get_data(id)
        base_field_id = self.model_data.base_field.id
        super().__init__(base_field_id, *args, **kwargs)

    def validate_sub_suffix(self, sub_suffix):
        if sub_suffix.data != self.model_data.sub_suffix:
            super().validate_sub_suffix(sub_suffix)

    def validate_year(self, year):
        if year.data != self.model_data.year:
            super().validate_year(year)

    def populate(self, id: int):
        super().populate(id)
        self.field_type.data = self.model_data.field_type.name
        self.demand_type.data = self.model_data.demand_type.name


class EditCultivationForm(CultivationForm):
    def __init__(self, id, *args, **kwargs):
        self.model_type = Cultivation
        self.get_data(id)
        field_id = self.model_data.field.id
        super().__init__(field_id, *args, **kwargs)

    def validate_cultivation_type(self, cultivation_type):
        if cultivation_type.data != self.model_data.cultivation_type.name:
            super().validate_cultivation_type(cultivation_type)

    def populate(self, id: int):
        super().populate(id)
        self.cultivation_type.data = self.model_data.cultivation_type.name
        self.residue_type.data = self.model_data.residues.name
        self.legume_type.data = self.model_data.legume_rate.name
        self.crop.choices = [
            (crop.id, crop.name)
            for crop in current_user.get_crops(
                crop_class=CropClass.from_cultivation(self.model_data.cultivation_type),
                field_type=self.model_data.field.field_type,
            )
        ]
        self.crop.data = str(self.model_data.crop.id)

        if self.model_data.field.field_type is FieldType.grassland:
            cultivation_types = [CultivationType.main_crop]
            legume_types = GrasslandLegumeType
        else:
            cultivation_types = UsedCultivationType
            legume_types = LegumeType.from_cultivation(self.model_data.cultivation_type)
        residue_types = ResidueType.from_cultivation(self.model_data.cultivation_type)

        self.cultivation_type.choices = [(e.name, e.value) for e in cultivation_types]
        self.residue_type.choices = [(e.name, e.value) for e in residue_types]
        self.legume_type.choices = [(e.name, e.value) for e in legume_types]
        # remove non-relevant inputs
        self.remove_inputs()

    def remove_inputs(self):
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
    def __init__(self, id, *args, **kwargs):
        self.model_type = Fertilization
        self.get_data(id)
        field_id = self.model_data.field[0].id
        super().__init__(field_id, *args, **kwargs)

    def update_content(self, *args, **kwargs):
        self.fert_class.data = self.model_data.fertilizer.fert_class.name
        self.cultivation.data = self.model_data.cultivation.id
        super().update_content(*args, **kwargs)
        self.remove_inputs()

    def validate_measure_type(self, measure_type):
        if measure_type.data != self.model_data.measure.name:
            self.cultivation.data = self.model_data.cultivation.id
            super().validate_measure_type(measure_type)
        return True

    def validate_amount(self, amount) -> bool:
        if amount.data != self.model_data.amount:
            self.cultivation.data = self.model_data.cultivation.id
            fert_amount = amount.data - self.model_data.amount
            return super().validate_amount(fert_amount, edit_value=True)
        return True

    def populate(self, id: int):
        super().populate(id)
        self.cultivation.choices = [
            (cult.id, cult.crop.name) for cult in self.model_data.field[0].cultivations
        ]
        self.cultivation.data = str(self.model_data.cultivation.id)
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
            fert_types = FertType.from_measure(self.model_data.measure)
            fertilizers = Fertilizer.query.filter(
                Fertilizer.fert_type.in_([e.name for e in fert_types])
            )
        self.fertilizer.choices = [(fert.id, fert.name) for fert in fertilizers]
        self.fertilizer.data = str(self.model_data.fertilizer.id)
        self.amount.label.text += f" in {self.model_data.fertilizer.unit.value}/ha:"
        # remove non-relevant inputs
        self.remove_inputs()

    def remove_inputs(self):
        fert_class = self.model_data.fertilizer.fert_class
        feedable = self.model_data.cultivation.crop.feedable
        if fert_class is FertClass.mineral:
            del self.month
        if not feedable:
            del self.cut_timing
        del self.fert_class
        del self.cultivation


class EditFertilizerForm(FertilizerForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_type = Fertilizer

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
        self.remove_inputs()

    def remove_inputs(self):
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
        self.model_type = Crop

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
    def __init__(self, id, *args, **kwargs):
        self.model_type = SoilSample
        self.get_data(id)
        base_field_id = self.model_data.base_field.id
        super().__init__(base_field_id, *args, **kwargs)

    def validate_year(self, year):
        if year != self.year.data:
            super().validate_year(year)

    def populate(self, id: int):
        super().populate(id)
        self.soil_type.data = self.model_data.soil_type.name
        self.humus_type.data = self.model_data.humus.name


class EditModifierForm(ModifierForm):
    def __init__(self, id, *args, **kwargs):
        self.model_type = Modifier
        self.get_data(id)
        field_id = self.model_data.field.id
        super().__init__(field_id, *args, **kwargs)

    def validate(self):
        super().validate()

    def populate(self, id: int):
        super().populate(id)
        self.description.data = self.model_data.description
        self.modification.data = self.model_data.modification.name
        self.amount.data = self.model_data.amount

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


def create_edit_form(form_type: str, id: int) -> FlaskForm | FormHelper:
    """
    Factory for forms that edit existing data.
    """
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
        form = form_types[form_type](id)
    except TypeError:
        form = form_types[form_type]()
    return form


class EditBaseFieldForm(BaseFieldForm):
    def __init__(self, id):
        self.model_type = BaseField
        self.get_data(id)
        super().__init__()

    def validate(self, **kwargs):
        if (
            self.model_data.prefix != self.prefix.data
            or self.model_data.suffix != self.suffix.data
        ):
            return super().validate()
        return True


class EditFieldForm(FieldForm):
    def __init__(self, id: int):
        self.model_type = Field
        self.get_data(id)
        base_field_id = self.model_data.base_field.id
        super().__init__(base_field_id)

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
    def __init__(self, id):
        self.model_type = Cultivation
        self.get_data(id)
        field_id = self.model_data.field.id
        super().__init__(field_id)

    def validate_cultivation_type(self, cultivation_type):
        if cultivation_type.data != self.model_data.cultivation_type.name:
            super().validate_cultivation_type(cultivation_type)

    def populate(self, id: int):
        super().populate(id)
        self.cultivation_type.data = self.model_data.cultivation_type.name
        self.residue_type.data = self.model_data.residues.name
        self.legume_type.data = self.model_data.legume_rate.name
        self.crop.data = str(self.model_data.crop.id)


class EditFertilizationForm(FertilizationForm):
    def __init__(self, id):
        self.model_type = Fertilization
        self.get_data(id)
        field_id = self.model_data.field[0].id
        super().__init__(field_id)

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
        self.cultivation.data = str(self.model_data.cultivation_id)
        self.fert_class.data = self.model_data.fertilizer.fert_class.name
        self.cut_timing.data = self.model_data.cut_timing.name
        self.measure_type.data = self.model_data.measure.name
        self.fertilizer.data = str(self.model_data.fertilizer_id)


class EditFertilizerForm(FertilizerForm):
    def __init__(self, id):
        super().__init__()
        self.model_type = Fertilizer
        self.get_data(id)

    def validate(self, **kwargs):
        if self.name.data != self.model_data.name or self.year.data != self.model_data.year:
            return super().validate()
        return True

    def populate(self, id: int):
        super().populate(id)
        self.fert_class.data = self.model_data.fert_class.name
        self.fert_type.data = self.model_data.fert_type.name
        self.unit_type.data = self.model_data.unit.name


class EditCropForm(CropForm):
    def __init__(self, id):
        super().__init__()
        self.model_type = Crop
        self.get_data(id)

    def validate_name(self, name):
        if name.data != self.model_data.name:
            super().validate_name(name)

    def populate(self, id: int):
        super().populate(id)
        self.field_type.data = self.model_data.field_type.name
        self.crop_class.data = self.model_data.crop_class.name
        self.crop_type.data = self.model_data.crop_type.name
        self.nmin_depth.data = self.model_data.nmin_depth.name


class EditSoilForm(SoilForm):
    def __init__(self, id, *args, **kwargs):
        self.model_type = SoilSample
        self.get_data(id)
        base_field_id = self.model_data.base_field.id
        super().__init__(base_field_id, *args, **kwargs)

    def validate_year(self, year):
        if year.data != self.model_data.year:
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

    def populate(self, id: int):
        super().populate(id)
        self.modification.data = self.model_data.modification.name

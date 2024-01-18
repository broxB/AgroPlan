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
from app.database.types import CutTiming, FertClass, LegumeType, NminType, ResidueType
from app.extensions import db

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

    def save(self):
        self.model_data.prefix = self.prefix.data
        self.model_data.suffix = self.suffix.data
        self.model_data.name = self.name.data
        db.session.commit()


class EditFieldForm(FieldForm):
    def __init__(self, id: int):
        self.model_type = Field
        self.get_data(id)
        base_field_id = self.model_data.base_field.id
        super().__init__(base_field_id)

    def populate(self, id: int):
        super().populate(id)
        self.field_type.data = self.model_data.field_type.name
        self.demand_type.data = self.model_data.demand_type.name

    def validate_sub_suffix(self, sub_suffix):
        if sub_suffix.data != self.model_data.sub_suffix:
            super().validate_sub_suffix(sub_suffix)

    def validate_year(self, year):
        if year.data != self.model_data.year:
            super().validate_year(year)

    def save(self):
        self.model_data.sub_suffix = self.sub_suffix.data
        self.model_data.year = self.year.data
        self.model_data.area = self.area.data
        self.model_data.red_region = self.red_region.data
        self.model_data.field_type = self.field_type.data
        self.model_data.demand_type = self.demand_type.data
        db.session.commit()


class EditCultivationForm(CultivationForm):
    def __init__(self, id):
        self.model_type = Cultivation
        self.get_data(id)
        field_id = self.model_data.field.id
        super().__init__(field_id)

    def populate(self, id: int):
        super().populate(id)
        self.cultivation_type.data = self.model_data.cultivation_type.name
        self.residues.data = self.model_data.residues.name
        self.legume_rate.data = self.model_data.legume_rate.name
        self.crop_id.data = str(self.model_data.crop.id)

    def validate_cultivation_type(self, cultivation_type):
        if cultivation_type.data != self.model_data.cultivation_type.name:
            super().validate_cultivation_type(cultivation_type)

    def save(self):
        crop = Crop.query.get(self.crop_id.data)
        self.model_data.crop = crop
        self.model_data.cultivation_type = self.cultivation_type.data
        self.model_data.crop_yield = self.crop_yield.data
        self.model_data.crop_protein = self.get(self.crop_protein, None)
        self.model_data.residues = self.get(self.residues, ResidueType.none)
        self.model_data.legume_rate = self.get(self.legume_rate, LegumeType.none)
        self.model_data.nmin_30 = self.get(self.nmin_30, 0)
        self.model_data.nmin_60 = self.get(self.nmin_60, 0)
        self.model_data.nmin_90 = self.get(self.nmin_90, 0)
        db.session.commit()


class EditFertilizationForm(FertilizationForm):
    def __init__(self, id):
        self.model_type = Fertilization
        self.get_data(id)
        field_id = self.model_data.field.id
        super().__init__(field_id)

    def populate(self, id: int):
        super().populate(id)
        self.cultivation_id.data = str(self.model_data.cultivation_id)
        self.fert_class.data = self.model_data.fertilizer.fert_class.name
        self.cut_timing.data = self.model_data.cut_timing.name
        self.measure_type.data = self.model_data.measure.name
        self.fertilizer_id.data = str(self.model_data.fertilizer_id)

    def validate_measure_type(self, measure_type):
        if measure_type.data != self.model_data.measure.name:
            self.cultivation_id.data = self.model_data.cultivation.id
            super().validate_measure_type(measure_type)
        return True

    def validate_amount(self, amount) -> bool:
        if amount.data != self.model_data.amount:
            self.cultivation_id.data = self.model_data.cultivation.id
            fert_amount = amount.data - self.model_data.amount
            return super().validate_amount(fert_amount, edit_value=True)
        return True

    def save(self):
        cultivation = Cultivation.query.get(self.cultivation_id.data)
        fertilizer = Fertilizer.query.get(self.fertilizer_id.data)
        self.model_data.measure = self.measure_type.data
        self.model_data.amount = self.amount.data
        self.model_data.cut_timing = self.get(self.cut_timing, CutTiming.none)
        self.model_data.month = self.get(self.month, None)
        self.model_data.cultivation = cultivation
        self.model_data.fertilizer = fertilizer
        db.session.commit()


class EditFertilizerForm(FertilizerForm):
    def __init__(self, id):
        super().__init__()
        self.model_type = Fertilizer
        self.get_data(id)

    def populate(self, id: int):
        super().populate(id)
        self.fert_class.data = self.model_data.fert_class.name
        self.fert_type.data = self.model_data.fert_type.name
        self.unit_type.data = self.model_data.unit.name

    def validate(self, **kwargs):
        if (
            self.name.data != self.model_data.name
            or self.fert_class.data == FertClass.organic
            and self.year.data != self.model_data.year
        ):
            return super().validate()
        return True

    def save(self):
        self.model_data.name = self.name.data
        self.model_data.year = self.get(self.year, 0)
        self.model_data.fert_class = self.fert_class.data
        self.model_data.fert_type = self.fert_type.data
        self.model_data.active = self.active.data
        self.model_data.unit = self.unit_type.data
        self.model_data.price = self.price.data
        self.model_data.n = self.n.data
        self.model_data.p2o5 = self.p2o5.data
        self.model_data.k2o = self.k2o.data
        self.model_data.mgo = self.mgo.data
        self.model_data.s = self.s.data
        self.model_data.cao = self.cao.data
        self.model_data.nh4 = self.nh4.data
        db.session.commit()


class EditCropForm(CropForm):
    def __init__(self, id):
        super().__init__()
        self.model_type = Crop
        self.get_data(id)

    def populate(self, id: int):
        super().populate(id)
        self.field_type.data = self.model_data.field_type.name
        self.crop_class.data = self.model_data.crop_class.name
        self.crop_type.data = self.model_data.crop_type.name
        self.nmin_depth.data = self.model_data.nmin_depth.name

    def validate_name(self, name):
        if name.data != self.model_data.name:
            super().validate_name(name)

    def save(self):
        self.model_data.name = self.name.data
        self.model_data.field_type = self.field_type.data
        self.model_data.crop_class = self.crop_class.data
        self.model_data.crop_type = self.crop_type.data
        self.model_data.kind = self.kind.data
        self.model_data.feedable = self.get(self.feedable, False)
        self.model_data.residue = self.get(self.residue, False)
        self.model_data.nmin_depth = self.get(self.nmin_depth, NminType.nmin_0)
        self.model_data.target_demand = self.get(self.target_demand, 0)
        self.model_data.target_yield = self.get(self.target_yield, 0)
        self.model_data.pos_yield = self.get(self.pos_yield, 0)
        self.model_data.neg_yield = self.get(self.neg_yield, 0)
        self.model_data.target_protein = self.get(self.target_protein, 0)
        self.model_data.var_protein = self.get(self.var_protein, 0)
        self.model_data.p2o5 = self.get(self.p2o5, 0)
        self.model_data.k2o = self.get(self.k2o, 0)
        self.model_data.mgo = self.get(self.mgo, 0)
        self.model_data.byproduct = self.get(self.byproduct, False)
        self.model_data.byp_ratio = self.get(self.byp_ratio, 0)
        self.model_data.byp_n = self.get(self.byp_n, 0)
        self.model_data.byp_p2o5 = self.get(self.byp_p2o5, 0)
        self.model_data.byp_k2o = self.get(self.byp_k2o, 0)
        self.model_data.byp_mgo = self.get(self.byp_mgo, 0)
        db.session.commit()


class EditSoilForm(SoilForm):
    def __init__(self, id, *args, **kwargs):
        self.model_type = SoilSample
        self.get_data(id)
        base_field_id = self.model_data.base_field.id
        super().__init__(base_field_id, *args, **kwargs)

    def populate(self, id: int):
        super().populate(id)
        self.soil_type.data = self.model_data.soil_type.name
        self.humus_type.data = self.model_data.humus.name

    def validate_year(self, year):
        if year.data != self.model_data.year:
            super().validate_year(year)

    def save(self):
        self.model_data.year = self.year.data
        self.model_data.ph = self.ph.data
        self.model_data.p2o5 = self.p2o5.data
        self.model_data.k2o = self.k2o.data
        self.model_data.mg = self.mg.data
        self.model_data.soil_type = self.soil_type.data
        self.model_data.humus = self.humus_type.data
        db.session.commit()


class EditModifierForm(ModifierForm):
    def __init__(self, id, *args, **kwargs):
        self.model_type = Modifier
        self.get_data(id)
        field_id = self.model_data.field.id
        super().__init__(field_id, *args, **kwargs)

    def populate(self, id: int):
        super().populate(id)
        self.modification.data = self.model_data.modification.name

    def save(self):
        self.model_data.description = self.description.data
        self.model_data.modification = self.modification.data
        self.model_data.amount = self.amount.data
        db.session.commit()

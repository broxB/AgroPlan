from flask_login import current_user

from app.database.model import BaseField as BaseFieldModel
from app.database.model import Field as FieldModel

from .crop import Crop
from .cultivation import Cultivation, create_cultivation
from .fertilization import Fertilization
from .fertilizer import Fertilizer, create_fertilizer
from .field import Field
from .soil import Soil


def create_field(base_field_id):
    field = (
        FieldModel.query.join(BaseFieldModel)
        .filter(
            BaseFieldModel.id == base_field_id,
            BaseFieldModel.user_id == current_user.id,
            FieldModel.year == current_user.year,
        )
        .one_or_none()
    )

    if field is None:
        return None
    field_data = Field(field)

    for cultivation in field.cultivations:
        crop_data = Crop(cultivation.crop, cultivation.crop_class)
        cultivation_data = create_cultivation(cultivation, crop_data)
        field_data.cultivations.append(cultivation_data)

    for fertilization in field.fertilizations:
        fertilizer_data = create_fertilizer(fertilization.fertilizer)
        crop_data = Crop(fertilization.cultivation.crop, fertilization.cultivation.crop_class)
        fertilization_data = Fertilization(
            fertilization, fertilizer_data, crop_data, fertilization.cultivation.crop_class
        )
        field_data.fertilizations.append(fertilization_data)

    return field_data

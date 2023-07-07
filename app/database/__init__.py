from loguru import logger

from app.extensions import db

from .model import *

model_hierachie = {
    "base_field": (BaseField, User),
    "field": (Field, BaseField, User),
    "cultivation": (Cultivation, Field, BaseField, User),
    "fertilization": (Fertilization, Cultivation, Field, BaseField, User),
    "crop": (Crop, User),
    "fertilizer": (Fertilizer, User),
    "soil": (SoilSample, BaseField, User),
    "modifier": (Modifier, Field, BaseField, User),
}


def confirm_id(id: str, user_id: int, form_type: str, modal_type: str) -> int | bool:
    if id in (None, "undefined"):
        if form_type in ("base_field", "crop", "fertilizer"):
            return True
        else:
            return False

    try:
        id = int(id)
    except (ValueError, TypeError):
        return False

    if modal_type == "new":
        _, model, *join_tables = model_hierachie[form_type]
    else:
        model, *join_tables = model_hierachie[form_type]

    query = model.query
    for table in join_tables:
        query = query.join(table)
    data = query.filter(User.id == user_id, model.id == id).one_or_none()

    if data is None:
        return False
    return id


def delete_database_entry(id: int, form_type: str) -> bool:
    model, *_ = model_hierachie[form_type]
    try:
        model.query.filter(model.id == id).delete()
        logger.info(f"Deleted {form_type=} with {id=}")
        db.session.commit()
    except Exception as e:
        logger.warning(e)
        return False
    return True

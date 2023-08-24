from loguru import logger

from app.extensions import db

from .model import *

MODEL_HIERACHIE = {
    "base_field": (BaseField, User),
    "field": (Field, BaseField, User),
    "cultivation": (Cultivation, Field, BaseField, User),
    "fertilization": (Fertilization, Cultivation, Field, BaseField, User),
    "crop": (Crop, User),
    "fertilizer": (Fertilizer, User),
    "soil": (SoilSample, BaseField, User),
    "modifier": (Modifier, Field, BaseField, User),
}


class UnvalidFormTypeError(Exception):
    def __init__(self, value) -> None:
        self.message = f"Unvalid form type passed: '{value}'"
        super().__init__(self.message)


def confirm_id(id: str, user_id: int, form_type: str, modal_type: str) -> tuple[bool, int]:
    """
    Verifies if send data is coherent with database.

    :param id:
        ID of the content that gets manipulated.
    :param user_id:
        User ID.
    :param form_type:
        Form type which should be used.
    :param modal_type:
        Variable for the root of the manipulation, eg. `new` or `edit` data.
    :return:
        Validation, `ID`
    """
    if id in (None, "undefined"):
        if form_type in ("base_field", "crop", "fertilizer"):
            return True, id
        else:
            return False, id

    try:
        id = int(id)
    except (ValueError, TypeError):
        return False, id

    try:
        if modal_type == "new":
            _, model, *join_tables = MODEL_HIERACHIE[form_type]
        else:
            model, *join_tables = MODEL_HIERACHIE[form_type]
    except KeyError as e:
        raise UnvalidFormTypeError(form_type) from e

    query = model.query
    for table in join_tables:
        query = query.join(table)
    data = query.filter(User.id == user_id, model.id == id).one_or_none()

    if data is None:
        return False, id
    return True, id


def delete_database_entry(id: int, form_type: str) -> bool:
    model, *_ = MODEL_HIERACHIE[form_type]
    try:
        m = model.query.get(id)
        db.session.delete(m)
        db.session.commit()
        logger.info(f"Deleted {form_type=} with {id=}")
    except Exception as e:
        logger.warning(e)
        return False
    return True

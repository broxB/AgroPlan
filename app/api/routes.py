from flask import Request, Response, jsonify, render_template, request
from flask_login import current_user, login_required
from loguru import logger

from app.api import Form, bp, create_edit_form, create_form
from app.database import confirm_id, delete_database_entry
from app.extensions import db, login


def accept_request(request: Request) -> list[str | int]:
    form_type = request.form.get("form_type")
    id = request.form.get("data_id")
    modal_type = {"POST": "new", "PUT": "edit", "DELETE": "edit"}

    id = confirm_id(id, current_user.id, form_type, modal_type[request.method])
    if not id:
        raise ValueError("Request data is not valid")

    return form_type, modal_type[request.method], id


def rendered_form(
    form: Form, form_type: str, modal_type: str, id: int, refreshed_content: bool = False
) -> str:
    return render_template(
        "modal_content.html",
        form=form,
        modal_type=(modal_type, form_type),
        data_id=id,
        refreshed_content=refreshed_content,
    )


@bp.route("/modal", methods=["GET"])
@login_required
def get_modal():
    modal_type = request.args.get("modal")
    form_type = request.args.get("form")
    id: str = request.args.get("id")
    id = confirm_id(id, current_user.id, form_type, modal_type)
    if not id:
        return jsonify("Unvalid request data."), 400

    if modal_type == "edit":
        form: Form = create_edit_form(form_type)(id)
        form.populate(id)
    else:
        form = create_form(form_type)(id)
        form.default_selects()

    return jsonify(rendered_form(form, form_type, modal_type, id))


@bp.route("/modal/refresh", methods=["POST"])
@login_required
def refresh_form():
    form_type = request.form.get("form_type")
    modal_type = request.form.get("modal_type")
    id = request.form.get("data_id")
    id = confirm_id(id, current_user.id, form_type, modal_type)
    if not id:
        return jsonify("Unvalid request data."), 400

    if modal_type == "new":
        form: Form = create_form(form_type)(id)
    else:
        form: Form = create_edit_form(form_type)(id)
    form.update_content()

    return jsonify(rendered_form(form, form_type, modal_type, id, refreshed_content=True)), 206


@bp.route("/form/new", methods=["POST"])
@login_required
def new_data():
    try:
        form_type, modal_type, id = accept_request(request)
    except ValueError:
        return jsonify("Unvalid request data."), 400

    form: Form = create_form(form_type)(id)
    form.default_selects()
    form.update_content(validation=True)
    if form.validate_on_submit():
        logger.info(f"{request.form}")
        return jsonify("Data saved successfully."), 201
    else:
        logger.error(f"Not valid: {request.form}")
        return jsonify(rendered_form(form, form_type, modal_type, id)), 206


@bp.route("/form/edit", methods=["PUT"])
@login_required
def edit_data():
    try:
        form_type, modal_type, id = accept_request(request)
    except ValueError:
        return jsonify("Unvalid request data."), 400

    form: Form = create_edit_form(form_type)(id)
    form.default_selects()
    form.update_content(validation=True)
    if form.validate_on_submit():
        logger.info(f"{request.form}")
        return jsonify("Data saved successfully."), 201
    else:
        logger.info(f"{request.form} not valid")
        return jsonify(rendered_form(form, form_type, modal_type, id)), 206


@bp.route("/form/delete", methods=["DELETE"])
@login_required
def delete_data():
    try:
        form_type, _, id = accept_request(request)
    except ValueError:
        return jsonify("Unvalid request data."), 400

    valid = delete_database_entry(id, form_type)
    if valid:
        return jsonify("Entry successfully deleted."), 201
    else:
        return jsonify("Deletion not available."), 400

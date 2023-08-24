from flask import Request, jsonify, render_template, request
from flask_login import current_user, login_required
from loguru import logger

from app.api import Form, bp, create_edit_form, create_form
from app.database import confirm_id, delete_database_entry
from app.extensions import login


def accept_request(request: Request) -> list[str | int]:
    if request.form:
        form_type = request.form.get("form_type")
        id = request.form.get("data_id")
        modal_type = request.form.get("modal_type")
    else:
        form_type = request.args.get("form")
        modal_type = request.args.get("modal")
        id = request.args.get("id")

    valid, id = confirm_id(id, current_user.id, form_type, modal_type)
    if not valid:
        raise ValueError("Request data is not valid")

    return form_type, modal_type, id


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
    try:
        form_type, modal_type, id = accept_request(request)
    except ValueError:
        return jsonify("Unvalid request data."), 400

    if modal_type == "new":
        form: Form = create_form(form_type, id)
    else:
        form = create_edit_form(form_type, id)
        form.populate(id)
    form.update_fields()

    return jsonify(rendered_form(form, form_type, modal_type, id))


@bp.route("/modal/refresh", methods=["POST"])
@login_required
def refresh_form():
    try:
        form_type, modal_type, id = accept_request(request)
    except ValueError:
        return jsonify("Unvalid request data."), 400

    if modal_type == "new":
        form: Form = create_form(form_type, id)
    else:
        form: Form = create_edit_form(form_type, id)
    form.update_fields()

    return jsonify(rendered_form(form, form_type, modal_type, id, refreshed_content=True)), 206


@bp.route("/modal/submit", methods=["POST", "PUT", "DELETE"])
@login_required
def submit_data():
    try:
        form_type, modal_type, id = accept_request(request)
    except ValueError:
        return jsonify("Unvalid request data."), 400

    if request.method == "DELETE":
        if delete_database_entry(id, form_type):
            return jsonify("Entry successfully deleted."), 201
        else:
            return jsonify("Deletion not available."), 400

    if request.method == "POST":
        form: Form = create_form(form_type, id)
    elif request.method == "PUT":
        form: Form = create_edit_form(form_type, id)
    form.update_fields()

    if form.validate_on_submit():
        logger.info(f"{request.form}")
        return jsonify("Data saved successfully."), 201
    else:
        logger.error(f"Not valid: {request.form}")
        return jsonify(rendered_form(form, form_type, modal_type, id)), 206

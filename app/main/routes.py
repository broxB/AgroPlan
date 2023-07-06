from dataclasses import asdict

from flask import flash, g, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from loguru import logger

from app.database.model import BaseField, Field, User
from app.extensions import db, login
from app.main import bp
from app.main.forms import EditProfileForm, YearForm
from app.model import Form, create_edit_form, create_field, create_form


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# @bp.before_app_request
# def before_request():
#     user_agent = request.headers.get("User-Agent")
#     print (user_agent)
#     if current_user.is_authenticated:
#     current_user.last_seen = datetime.utcnow()
#     db.session.commit()


@bp.route("/", methods=["GET", "POST"])
def home():
    if current_user.is_anonymous:
        return redirect(url_for("auth.login"))
    return redirect(url_for("main.index"))


@bp.route("/index", methods=["GET", "POST"])
@login_required
def index():
    # page = request.args.get("page", 1, type=int)
    fields = current_user.get_fields()  # .paginate(page, 10, False)
    form = YearForm()
    # next_url = url_for("main.index", page=fields.next_num) if fields.has_next else None
    # prev_url = url_for("main.index", page=fields.prev_num) if fields.has_prev else None
    return render_template(
        "index.html",
        title="Home",
        fields=fields,
        active_page="home",
        form=form
        # next_url=next_url,
        # prev_url=prev_url,
    )


@bp.route("/user/<username>")
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template("user.html", title="Profile", user=user, active_page="profile")


@bp.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username, current_user.email)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for("main.user", username=current_user.username))
    if request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template("edit_profile.html", title="Edit Profile", form=form)


@bp.route("/set_year", methods=["POST"])
@login_required
def set_year():
    form = YearForm()
    year = int(form.year.data)
    if form.validate_on_submit():
        current_user.year = year
        db.session.commit()
        flash(f"Cultivation year has been set to {year}.")
    else:
        flash(f"Invalid year selected.")
    return redirect(request.referrer)


@bp.route("/field", methods=["GET", "POST"])
@login_required
def field_overview():
    base_fields = current_user.get_fields(year=current_user.year)
    return render_template("fields.html", title="Fields", base_fields=base_fields)


@bp.route("/field/<base_field_id>", methods=["GET", "POST"])
@login_required
def field(base_field_id):
    if request.method == "GET":
        base_field = BaseField.query.filter_by(id=base_field_id).first_or_404()
        fields = current_user.get_fields(year=current_user.year)
        field = create_field(current_user.id, base_field_id, current_user.year)
        field.create_balances()
        form = YearForm()
        return render_template(
            "field.html",
            title=field.name,
            base_field=base_field,
            fields=fields,
            form=form,
            field=field,
        )
    else:
        return jsonify("Invalid request."), 503


@bp.route("/field/<base_field_id>/data", methods=["GET"])
@login_required
def field_data(base_field_id):
    field = create_field(current_user.id, base_field_id, current_user.year)
    return asdict(field.total_balance())


@bp.route("/modal", methods=["GET"])
@login_required
def modal():
    if request.method == "GET":
        modal_type = request.args.get("modal")
        form_type = request.args.get("form")
        id: str = request.args.get("id")
        if id == "undefined" or not id:
            id = None
        elif id.isnumeric():
            id = int(id)
        else:
            return jsonify("Unvalid request data."), 400

        if modal_type == "edit":
            form: Form = create_edit_form(form_type)(id)
            form.populate(id)
            modal = render_template(
                "modal_content.html",
                form=form,
                modal_type=(modal_type, form_type),
                data_id=id,
            )
        else:
            form = create_form(form_type)(id)
            form.default_selects()
            modal = render_template(
                "modal_content.html",
                form=form,
                modal_type=(modal_type, form_type),
                data_id=id,
            )
        return jsonify(modal)


@bp.route("/form/refresh", methods=["POST"])
@login_required
def refresh_form():
    form_type = request.form.get("form_type")
    id = request.form.get("data_id")
    if id == "undefined" or not id:
        id = None
    elif id.isnumeric():
        id = int(id)
    else:
        return jsonify("Unvalid request data."), 400

    form = create_form(form_type)(id)
    form.update(request.form)
    modal_type = "new"
    modal = jsonify(
        render_template(
            "modal_content.html",
            form=form,
            modal_type=(modal_type, form_type),
            data_id=id,
        )
    )
    return modal, 206


@bp.route("/form/new", methods=["POST"])
@login_required
def new_data():
    form_type = request.form.get("form_type")
    id = request.form.get("data_id")
    if id == "undefined" or not id:
        id = None
    elif id.isnumeric():
        id = int(id)
    else:
        return jsonify("Unvalid request data."), 400

    form = create_form(form_type)(id)
    modal_type = "new"

    if form.validate_on_submit():
        return jsonify("Data saved successfully."), 201

    else:
        modal = jsonify(
            render_template(
                "modal_content.html",
                form=form,
                modal_type=(modal_type, form_type),
                data_id=id,
            )
        )
        return modal, 206


@bp.route("/form/update", methods=["POST"])
@login_required
def update_data():
    form_type = request.form.get("form_type")
    id = request.form.get("data_id")
    if id == "undefined" or not id:
        id = None
    elif id.isnumeric():
        id = int(id)
    else:
        return jsonify("Unvalid request data."), 400

    form = create_edit_form(form_type)(id)
    modal_type = "edit"

    if form.validate_on_submit():
        return jsonify("Data saved successfully."), 201

    else:
        modal = jsonify(
            render_template(
                "modal_content.html",
                form=form,
                modal_type=(modal_type, form_type),
                data_id=id,
            )
        )
        return modal, 206


@bp.route("/form/delete", methods=["DELETE"])
@login_required
def delete_data():
    form_type = request.form.get("form_type")
    id = request.form.get("data_id")
    if id == "undefined" or not id:
        id = None
    elif id.isnumeric():
        id = int(id)
    else:
        return jsonify("Unvalid request data."), 400

    return jsonify("Entry deleted."), 201


@bp.route("/crop", methods=["GET", "POST"])
@login_required
def crop():
    crops = current_user.get_crops()
    return render_template("crops.html", title="Crops", crops=crops)


@bp.route("/fertilizer", methods=["GET", "POST"])
@login_required
def fertilizer():
    fertilizers = sorted(current_user.get_fertilizers(), key=lambda x: (x.year), reverse=True)
    usage = current_user.get_fertilizer_usage()
    return render_template(
        "fertilizers.html", title="Fertilizers", fertilizers=fertilizers, usage=usage
    )


@bp.route("/crop/<crop_class>", methods=["GET"])
@login_required
def get_crops(crop_class):
    kwargs = {k: v for k, v in request.args.items()}
    crops = current_user.get_crops(crop_class=crop_class, **kwargs)
    crop_data = [{"id": crop.id, "name": crop.name} for crop in crops]
    return jsonify(crop_data)


@bp.route("/fertilizer/<fert_class>", methods=["GET"])
@login_required
def get_fertilizers(fert_class):
    kwargs = {k: v for k, v in request.args.items()}
    fertilizers = current_user.get_fertilizers(fert_class=fert_class, **kwargs)
    fertilizer_data = [{"id": fert.id, "name": fert.name} for fert in fertilizers]
    return jsonify(fertilizer_data)


@bp.route("/test", methods=["GET", "POST"])
@login_required
def test():
    return render_template("_test.html")
    # logger.info(f"Received request args: {request.args.to_dict().items()}")
    # return {"task": "finished"}, 201

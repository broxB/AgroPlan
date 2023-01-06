from datetime import datetime

from flask import (
    current_app,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from loguru import logger

from app.database.model import BaseField, User
from app.extensions import db, login
from app.main import bp
from app.main.forms import EditProfileForm, YearForm, create_edit_form
from app.model import Field, create_field
from app.model.forms import create_form


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


@bp.route("/preset", methods=["GET", "POST"])
@login_required
def preset():
    return render_template("preset.html")


@bp.route("/user/<username>")
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template(
        "user.html", title="Profile", user=user, sidebar_disabled=True, active_page="profile"
    )


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
    return render_template(
        "edit_profile.html", title="Edit Profile", form=form, sidebar_disabled=True
    )


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


@bp.route("/field/<base_field_id>", methods=["GET", "POST"])
@login_required
def field(base_field_id):
    if request.method == "GET":
        base_field = BaseField.query.filter_by(id=base_field_id).first_or_404()
        fields = current_user.get_fields(year=current_user.year)
        form = YearForm()
        return render_template(
            "field.html", title=base_field.name, base_field=base_field, fields=fields, form=form
        )
    elif request.method == "POST":
        pass


@bp.route("/field/<base_field_id>/data", methods=["GET"])
@login_required
def field_data(base_field_id):
    field: Field = create_field(base_field_id, current_user.year)
    elements = ["n", "p2o5", "k2o", "mgo", "s", "cao"]
    return jsonify(dict(zip(elements, field.total_saldo())))


@bp.route("/modal", methods=["GET"])
@login_required
def edit_modal():
    modal_type = request.args.get("type")
    param = request.args.get("params")
    id = request.args.get("id")
    form = create_edit_form(modal_type, param)
    form.populate(id)
    modal = render_template("edit_modal.html", form=form, modal_type=modal_type)
    return jsonify(modal)

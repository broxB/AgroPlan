import re
from dataclasses import asdict
from functools import cmp_to_key

from flask import flash, jsonify, make_response, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.api.edit_forms import EditFieldForm
from app.api.forms import FieldForm
from app.database import BaseField, User
from app.database.model import Cultivation, Fertilization, Field
from app.database.types import MeasureType
from app.extensions import db, login
from app.main import bp
from app.main.forms import DemandForm, EditProfileForm, ListForm, YearForm
from app.model import create_field

current_user: User


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
    page_number = request.args.get("page", 1, type=int)
    sidebar = current_user.get_fields(year=current_user.year)
    page = db.paginate(sidebar, page=page_number, per_page=27)
    if not page.has_prev:
        form = YearForm()
        return render_template(
            "index.html", title="Home", sidebar=sidebar, active_page="home", form=form, page=page
        )
    else:
        return render_template("_index_fields.html", page=page)


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
        if match := re.search("\/field\/(\d+)$", request.referrer):
            field_id = match[1]
            field = Field.query.get(field_id)
            new_field = (
                Field.query.join(BaseField)
                .filter(
                    BaseField.id == field.base_id,
                    Field.year == year,
                    Field.partition == field.partition,
                )
                .one_or_none()
            )
            if new_field is None:
                new_field = (
                    Field.query.join(BaseField)
                    .filter(BaseField.id == field.base_id, Field.year == year)
                    .one_or_none()
                )
                if new_field is None:
                    return redirect(url_for("main.index"))
            return redirect(url_for("main.field", id=new_field.id))
        else:
            return redirect(request.referrer)
    else:
        flash("Invalid year selected.")
        return redirect(request.referrer)


@bp.route("/set_demand", methods=["POST"])
@login_required
def set_demand():
    form = DemandForm()
    if form.validate_on_submit():
        form.save()
        flash(f"Demand option for {form.nutrient.data} has been set to {form.demand_option.data}.")
    else:
        flash("Invalid option selected.")
    return redirect(request.referrer)


@bp.route("/fields", methods=["GET"])
@login_required
def fields():
    base_fields = BaseField.query.filter_by(user_id=current_user.id)
    sidebar = current_user.get_fields(year=current_user.year)
    page_number = request.args.get("page", 1, type=int)
    page = db.paginate(base_fields, page=page_number, per_page=20)
    if not page.has_prev:
        return render_template(
            "fields.html", title="Fields", base_fields=base_fields, sidebar=sidebar, page=page
        )
    else:
        return render_template("_fields_base_fields.html", sidebar=sidebar, page=page)


@bp.route("/field/<id>", methods=["GET", "POST"])
@login_required
def field(id):
    if request.method == "GET":
        db_field = Field.query.filter_by(id=id).first_or_404()
        sidebar = current_user.get_fields(year=current_user.year)
        field = create_field(id)
        if field is not None:
            field.create_balances()
        form = YearForm()
        demand_form = DemandForm()
        return render_template(
            "field.html",
            title=db_field.base_field.name,
            db_field=db_field,
            sidebar=sidebar,
            form=form,
            demand_form=demand_form,
            field=field,
        )
    else:
        return jsonify("Invalid request."), 503


@bp.route("/field/<id>/data", methods=["GET"])
@login_required
def field_data(id):
    field = create_field(id)
    return asdict(field.total_balance())


@bp.route("/crop", methods=["GET", "POST"])
@login_required
def crop():
    crops = current_user.get_crops()
    return render_template("crops.html", title="Crops", crops=crops)


@bp.route("/fertilizer", methods=["GET", "POST"])
@login_required
def fertilizer():
    fertilizers = sorted(current_user.get_fertilizers(), key=lambda x: (x.year), reverse=True)
    return render_template("fertilizers.html", title="Fertilizers", fertilizers=fertilizers)


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


@bp.route("/fields/<id>", methods=["GET"])
@login_required
def get_field(id):
    if request.method == "GET":
        field = Field.query.get(id)
        return render_template("_fields_field.html", field=field)


@bp.route("/fields/<id>/create", methods=["GET", "POST", "DELETE"])
@login_required
def create_field_form(id):
    if request.method == "GET":
        form: FieldForm = FieldForm(id)
        return render_template("_fields_field_create.html", form=form)
    elif request.method == "POST":
        form: FieldForm = FieldForm(id)
        if form.validate_on_submit():
            field = form.save()
            return render_template("_fields_field.html", field=field)
        else:
            return render_template("_fields_field_create.html", form=form)
    elif request.method == "DELETE":
        return ""


@bp.route("/fields/<id>/edit", methods=["GET", "PUT"])
@login_required
def edit_field(id):
    form: EditFieldForm = EditFieldForm(id)
    if request.method == "GET":
        form.populate(id)
        return render_template("_fields_field_edit.html", form=form)
    elif request.method == "PUT":
        if form.validate_on_submit():
            form.save()
            field = form.model_data
            return render_template("_fields_field.html", field=field)
        else:
            return render_template("_fields_field_edit.html", form=form)


@bp.route("/fields/<id>/delete", methods=["DELETE"])
@login_required
def delete_field(id):
    if request.method == "DELETE":
        field = Field.query.get(id)
        db.session.delete(field)
        db.session.commit()
    return ""


@bp.route("/lists", methods=["GET", "POST"])
@login_required
def lists():
    form: ListForm = ListForm(current_user.id, year=current_user.year)
    form.update_choices()
    return render_template("lists.html", form=form)


@bp.route("/lists/datatable", methods=["POST"])
@login_required
def create_list():
    list = []
    form: ListForm = ListForm(current_user.id)
    form.update_choices()

    query = db.select(Fertilization)
    if form.fields.data:
        query = query.filter(Fertilization.field_id.in_(form.fields.data))
    if form.fertilizers.data:
        query = query.filter(Fertilization.fertilizer_id.in_(form.fertilizers.data))
    else:
        query = query.filter(
            Fertilization.fertilizer_id.in_([id for id, _ in form.fertilizers.choices])
        )
    if form.crops.data:
        query = query.join(Cultivation).filter(Cultivation.crop_id.in_(form.crops.data))
    else:
        query = query.join(Cultivation).filter(
            Cultivation.crop_id.in_([id for id, _ in form.crops.choices])
        )
    query = query.join(Field).filter(Field.year == form.year.data)
    list: list = db.session.execute(query).scalars().all()

    list.sort(key=lambda x: x.field.base_field.prefix)
    list.sort(key=lambda x: x.cultivation.crop.name)
    list.sort(key=lambda x: x.fertilizer.name)
    list.sort(key=cmp_to_key(MeasureType.sorting))
    unit = " | ".join(set(entry.fertilizer.unit.value for entry in list))
    return render_template("_lists_table.html", list=list, unit=unit)


@bp.route("/lists/form", methods=["POST"])
@login_required
def update_listform():
    form: ListForm = ListForm(current_user.id)
    form.update_choices()
    body = render_template("_lists_form.html", form=form)
    # rebuild multiselect dropdowns after htmx changes have settled
    response = make_response(body)
    response.headers["HX-Trigger-After-Settle"] = "reloadMultiSelectDropdown"
    return response


@bp.route("/sperrzeiten")
def sperrzeiten():
    return redirect(url_for("static", filename="/docs/Sperrzeiten.pdf"))


@bp.route("/hinweise")
def hinweise():
    return redirect(url_for("static", filename="/docs/Hinweise.pdf"))


@bp.route("/richtwerte")
def richtwerte():
    return redirect(url_for("static", filename="/docs/Richtwerte.pdf"))

from datetime import datetime

from flask import (
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from app.database.model import Field, User
from app.extensions import db, login
from app.main import bp
from app.main.forms import EditProfileForm, EmptyForm


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# @bp.before_app_request
# def before_request():
# if current_user.is_authenticated:
# current_user.last_seen = datetime.utcnow()
# db.session.commit()


@bp.route("/", methods=["GET", "POST"])
def home():
    if current_user.is_anonymous:
        return redirect(url_for("auth.login"))
    return redirect(url_for("main.index"))


@bp.route("/index", methods=["GET", "POST"])
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    fields = current_user.get_fields()  # .paginate(page, 10, False)
    # next_url = url_for("main.index", page=fields.next_num) if fields.has_next else None
    # prev_url = url_for("main.index", page=fields.prev_num) if fields.has_prev else None
    return render_template(
        "index.html",
        title="Home",
        fields=fields
        # next_url=next_url,
        # prev_url=prev_url,
    )


@bp.route("/user/<username>")
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template("user.html", title="Profile", user=user)


@bp.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username, current_user.email)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for("main.edit_profile"))
    if request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template("edit_profile.html", title="Edit Profile", form=form)


@bp.route("/user/<username>/popup")
@login_required
def user_popup(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template("user_popup.html", user=user)

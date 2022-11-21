from flask import flash, redirect, render_template, url_for

from app.errors import bp
from app.extensions import db


@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@bp.app_errorhandler(401)
def unauthorized(error):
    flash("Unauthorized access, you have to login to access that page.")
    return redirect(url_for("auth.login"))
    # return render_template("errors/401.html"), 401


@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template("errors/500.html"), 500

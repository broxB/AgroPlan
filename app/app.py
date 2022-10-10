"""The app module, containing the app factory function."""
import logging
import os
from logging.handlers import RotatingFileHandler, SMTPHandler

from flask import Flask

from app import auth, cli, errors, main
from app.database.model import Field, User
from app.extensions import bootstrap, db, login, migrate
from config import Config

# from app.extensions import mail, moment


def create_app(config_object=Config):
    """Create application factory, as explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object: The configuration object to use.
    """
    app = Flask(__name__)
    app.config.from_object(config_object)
    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    register_shellcontext(app)
    register_commands(app)
    configure_logger(app)
    return app


def register_extensions(app: Flask):
    """Register Flask extensions."""
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    login.init_app(app)
    # mail.init_app(app)
    bootstrap.init_app(app)
    # moment.init_app(app)


def register_blueprints(app: Flask):
    """Register Flask blueprints."""
    app.register_blueprint(auth.bp, url_prefix="/auth")
    app.register_blueprint(main.bp)


def register_errorhandlers(app: Flask):
    """Register error handlers."""
    app.register_blueprint(errors.bp)


def register_shellcontext(app: Flask):
    """Register shell context objects."""

    @app.shell_context_processor
    def make_shell_context():
        return {"db": db, "User": User, "Field": Field}


def register_commands(app: Flask):
    """Register Click commands."""
    cli.register(app)
    # app.cli.add_command(commands.test)
    # app.cli.add_command(commands.lint)


def configure_logger(app: Flask):
    """Configure loggers."""
    if not app.debug and not app.testing:
        if app.config["MAIL_SERVER"]:
            auth_creds = None
            if app.config["MAIL_USERNAME"] or app.config["MAIL_PASSWORD"]:
                auth_creds = (app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
            secure = None
            if app.config["MAIL_USE_TLS"]:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
                fromaddr="no-reply@" + app.config["MAIL_SERVER"],
                toaddrs=app.config["ADMINS"],
                subject="AgroPlan Failure",
                credentials=auth_creds,
                secure=secure,
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if not os.path.exists("logs"):
            os.mkdir("logs")
        file_handler = RotatingFileHandler("logs/agroplan.log", maxBytes=10240, backupCount=10)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s " + "[in %(pathname)s:%(lineno)d]"
            )
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info("AgroPlan startup")

    return app


if __name__ == "__main__":
    app = create_app()

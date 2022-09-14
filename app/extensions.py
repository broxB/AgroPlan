from flask_bootstrap import Bootstrap4
from flask_login import LoginManager
from flask_mailman import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy as SQLAlchemyBase

from app.database.base import Model, set_query_property


class SQLAlchemy(SQLAlchemyBase):
    """Flask extension that integrates alchy with Flask-SQLAlchemy."""

    def __init__(self, app=None, use_native_unicode=True, session_options=None, Model=None):
        self.Model = Model
        super(SQLAlchemy, self).__init__(app, use_native_unicode, session_options)

    def make_declarative_base(self, *args, **kwargs):
        """Creates or extends the declarative base."""
        if self.Model is None:
            self.Model = super(SQLAlchemyBase, self).make_declarative_base()
        else:
            set_query_property(self.Model, self.session)
        return self.Model


db = SQLAlchemy(None, Model=Model)
migrate = Migrate()
# login = LoginManager()
# login.login_view = "auth.login"
# login.login_message = "Please log in to access this page."
# mail = Mail()
# bootstrap = Bootstrap4()

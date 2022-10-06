# from flask_bootstrap import Bootstrap4
# from flask_login import LoginManager
# from flask_mailman import Mail
from flask_migrate import Migrate

from app.database.base import Model, SQLAlchemy

db = SQLAlchemy(None, Model=Model)
migrate = Migrate()
# login = LoginManager()
# login.login_view = "auth.login"
# login.login_message = "Please log in to access this page."
# mail = Mail()
# bootstrap = Bootstrap4()

from flask import Blueprint

from .edit_forms import create_edit_form
from .forms import Form, create_form

bp = Blueprint("api", __name__)

from app.api import routes

from flask import Blueprint

points_bp = Blueprint('points_bp', __name__, template_folder='templates')

from . import routes

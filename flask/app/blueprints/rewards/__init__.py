from flask import Blueprint

rewards_bp = Blueprint('rewards_bp', __name__, template_folder='templates')

from . import routes

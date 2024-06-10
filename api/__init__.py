from flask import Blueprint

calculate_tax_bp = Blueprint('calculate_tax', __name__, url_prefix='/api/v1/')

from api import routes
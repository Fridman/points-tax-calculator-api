from flask import (
    current_app,
    jsonify,
    request
)

from api import calculate_tax_bp
from api.controllers import calculate_tax
from api.exceptions import (
    CustomException,
)


@calculate_tax_bp.route('calculate-tax/<year>/', methods=['GET'])
def calculate_tax_view(year: int = 2022):

    if not year.isnumeric():
        raise CustomException(
            'year URL parameter is malformed or missing.',
            status_code=400
        )

    try:
        income = int(request.args.get('income'))
    except (TypeError, ValueError) as e:
        raise CustomException(
            'income URL parameter is malformed or missing.',
            status_code=400
        )

    return jsonify(
        calculate_tax(income, year)
    )

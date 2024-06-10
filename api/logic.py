import json
import requests

from flask import current_app as app

from api.exceptions import CustomException
from common.extensions import cache
from common.utils import convert_dollars_to_cents

# GLOBAL VARS∂


def prepare_tax_bracket_data(tax_brackets: list):
    '''
        Since we receive tax bracket data from the db service in a different
        format from our input, we want to modify our tax bracket data to be
        usable with our input data.
    '''
    for bracket in tax_brackets:
        if bracket.get("max") is not None:
            bracket["max"] = convert_dollars_to_cents(bracket.get("max"))
        if bracket.get("min") is not None:
            bracket["min"] = convert_dollars_to_cents(bracket.get("min"))
        else:
            raise CustomException(
                'Malformed data returned by remote tax API',
                status_code=500
            )
    return tax_brackets


@cache.memoize()
def fetch_tax_brackets(year: str):
    '''
        Query the db service for tax info, prepares it for use, and utilises
        caching to minimize service communication bottlenecks.
    '''
    app.logger.info(
        "Fetching fresh tax bracket data for: {year}".format(year=year)
    )

    request_url = '{API_URL}/tax-calculator/tax-year/{YEAR}'.format(
        API_URL=app.config.get("TAX_API_SERVER_URL"),
        YEAR=year
    )

    app.logger.debug(
        "Retrieving tax bracket data from: {url}".format(url=request_url)
    )

    request_content = json.loads(requests.get(request_url).content.decode())
    if request_content.get("errors") is not None:
        raise CustomException(
            'Malformed data returned by remote tax API',
            status_code=500
        )
    prepare_tax_bracket_data(request_content.get("tax_brackets"))
    return request_content


def calculate_tax_for_bracket(income: int, bracket: dict):
    '''
        Calculate the amount of taxes owed up to the maximum payable in this
        bracket.
    '''
    bracket_max, bracket_min = bracket.get("max"), bracket.get("min")
    if bracket_max is not None and bracket_max <= income:
        return (bracket_max - bracket_min) * bracket.get("rate")
    elif bracket_min <= income:
        return (income - bracket_min) * bracket.get("rate")
    return 0


def format_bracket_response(owed: int | float, bracket: dict):
    '''
        Prepare the bracket formatting to be converted to JSON.
    '''
    formatted_tax_info = {
        "min": bracket.get("min"),
        "max": bracket.get("max"),
        "rate": bracket.get("rate"),
        "owed": owed,
    }
    return formatted_tax_info

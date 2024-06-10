from flask import current_app as app

from api.logic import (
    calculate_tax_for_bracket,
    fetch_tax_brackets,
    format_bracket_response,
)


def calculate_tax(income: int, year: str):
    total_owed = 0
    response_list = []
    tax_brackets = fetch_tax_brackets(year)

    for bracket in tax_brackets.get("tax_brackets", []):
        bracket_owed = calculate_tax_for_bracket(income, bracket)
        total_owed += bracket_owed
        response_list.append(format_bracket_response(bracket_owed, bracket))

    response_dict = {
        "income": income,
        "total_owed": total_owed,
        "effective_rate": (total_owed / income),
        "tax_brackets": response_list,
    }
    return response_dict

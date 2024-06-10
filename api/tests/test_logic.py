from flask import Flask
import pytest
import requests
import unittest

from flask_caching import Cache
from unittest import mock

from api.logic import (
    prepare_tax_bracket_data,
    fetch_tax_brackets,
    calculate_tax_for_bracket,
    format_bracket_response,
)
from api.exceptions import CustomException

from app import create_app

from flask import current_app as app

'''
    prepare_tax_bracket_data(tax_brackets : list)
'''


class TestPrepareTaxBracketData(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.bracket_1_input = {
            "min": 0,
            "max": 18000,
            "rate": 0.1,
        }
        self.bracket_1_return = {
            "min": 0,
            "max": 1800000,
            "rate": 0.1,
        }

        self.bracket_2_input = {
            "min": 18000,
            "max": 25000,
            "rate": 0.1,
        }
        self.bracket_2_return = {
            "min": 1800000,
            "max": 2500000,
            "rate": 0.1,
        }
        self.api_response_mock = {
            "errors": None,
        }

    def tearDown(self):
        self.app_context.pop()

    def test_one_bracket(self):
        test_bracket_input = [self.bracket_1_input]
        test_bracket_return = [self.bracket_1_return]
        assert prepare_tax_bracket_data(
            test_bracket_input) == test_bracket_return

    def test_two_brackets(self):
        test_bracket_input = [
            self.bracket_1_input,
            self.bracket_2_input,
        ]
        test_bracket_return = [
            self.bracket_1_return,
            self.bracket_2_return,
        ]
        assert prepare_tax_bracket_data(
            test_bracket_input) == test_bracket_return

    def test_no_max(self):
        test_bracket_input = [
            self.bracket_1_input,
            self.bracket_2_input,
        ]
        test_bracket_return = [
            self.bracket_1_return,
            self.bracket_2_return,
        ]
        assert prepare_tax_bracket_data(
            test_bracket_input) == test_bracket_return

    def test_no_min(self):
        test_bracket_input = [
            {}
        ]
        with self.app_context:
            with pytest.raises(CustomException):
                prepare_tax_bracket_data(test_bracket_input)


'''
    fetch_tax_brackets(year: str)
'''


class TestFetchTaxBrackets(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.bracket_1_input = {
            "min": 0,
            "max": 18000,
            "rate": 0.1,
        }
        self.bracket_1_return = {
            "min": 0,
            "max": 1800000,
            "rate": 0.1,
        }

        self.bracket_2_input = {
            "min": 18000,
            "max": 25000,
            "rate": 0.1,
        }
        self.bracket_2_return = {
            "min": 1800000,
            "max": 2500000,
            "rate": 0.1,
        }
        self.api_response_mock = {
            "errors": None,
        }
        self.year = 2022
        self.request_response = requests.Response()

    def tearDown(self):
        self.app_context.pop()

    @mock.patch('api.logic.requests.get')
    def test_base(self, mocked_get):
        self.request_response._content = b'{"tax_brackets":\
            [\
                {\
                    "min": 0,\
                    "max": 18000,\
                    "rate": 0.1\
                }\
            ],\
            "errors": null\
            }'
        self.api_response_mock["tax_brackets"] = [self.bracket_1_return]
        fetch_tax_brackets_return = self.api_response_mock

        mocked_get.return_value = self.request_response
        assert fetch_tax_brackets.uncached(
            self.year) == fetch_tax_brackets_return

    @mock.patch('api.logic.requests.get')
    def test_cache(self, mocked_get):
        self.request_response._content = b'{"tax_brackets":\
            [\
                {\
                    "min": 0,\
                    "max": 18000,\
                    "rate": 0.1\
                }\
            ],\
            "errors": null\
            }'
        self.api_response_mock["tax_brackets"] = [self.bracket_1_return]
        fetch_tax_brackets_return = self.api_response_mock

        with self.app_context:
            mocked_get.return_value = self.request_response
            assert fetch_tax_brackets(self.year) == fetch_tax_brackets_return
            mocked_get.return_value = None
            assert fetch_tax_brackets(self.year) == fetch_tax_brackets_return
            with pytest.raises(AttributeError):
                fetch_tax_brackets.uncached(self.year)

    @mock.patch('api.logic.requests.get')
    def test_no_min(self, mocked_get):
        self.request_response._content = b'{\
            "tax_brackets":\
                [\
                    {\
                    "max": 18000,\
                    "rate": 0.1\
                    }\
                ]\
            ,"errors": null\
        }'

        mocked_get.return_value = self.request_response
        with pytest.raises(CustomException):
            fetch_tax_brackets.uncached(self.year)


'''
    calculate_tax_for_bracket(income: int, bracket: dict)
'''


class TestCalculateTaxForBracket(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.bracket_1 = {
            "min": 0,
            "max": 1800000,
            "rate": 0.1,
        }
        self.bracket_2 = {
            "min": 1800000,
            "max": 5500000,
            "rate": 0.1,
        }
        self.bracket_3 = {
            "min": 5500000,
            "rate": 0.1,
        }
        self.request_response = requests.Response()

    def tearDown(self):
        self.app_context.pop()

    def test_base(self):
        income = 5000000
        assert calculate_tax_for_bracket(income, self.bracket_1) == 180000

    def test_below_min(self):
        income = 1700000
        assert calculate_tax_for_bracket(income, self.bracket_2) == 0

    def test_partial(self):
        income = 5000000
        assert calculate_tax_for_bracket(income, self.bracket_2) == 320000

    def test_no_max(self):
        income = 10000000
        assert calculate_tax_for_bracket(income, self.bracket_3) == 450000


'''
    format_bracket_response(owed: int | float, bracket: dict)
'''


class TestFormatBracketResponse(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.owed = 180000

    def tearDown(self):
        self.app_context.pop()

    def test_base(self):
        self.bracket_base = {
            "min": 0,
            "max": 1800000,
            "rate": 0.1,
        }
        self.bracket_base_return = {
            "min": 0,
            "max": 1800000,
            "rate": 0.1,
            "owed": 180000,
        }
        assert format_bracket_response(
            self.owed, self.bracket_base) == self.bracket_base_return

    def test_no_max(self):
        self.bracket_no_max = {
            "min": 0,
            "rate": 0.1,
        }
        self.bracket_no_max_return = {
            "min": 0,
            "max": None,
            "rate": 0.1,
            "owed": 180000,
        }
        assert format_bracket_response(
            self.owed, self.bracket_no_max) == self.bracket_no_max_return

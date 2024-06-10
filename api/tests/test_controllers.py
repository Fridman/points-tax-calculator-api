from flask import Flask
import pytest
import requests
import unittest

from flask_caching import Cache
from unittest import mock

from api.controllers import (
    calculate_tax
)

from app import create_app

from flask import current_app as app

'''
    calculate_tax(income: int, year: str)
'''


class TestCalculateTax(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.bracket_1_return = {
            "min": 0,
            "max": 1800000,
            "rate": 0.1,
            "owed": 180000,
        }
        self.api_fetch_mock = {
            "errors": None,
        }
        self.income = 5000000
        self.year = 2022

    def tearDown(self):
        self.app_context.pop()

    @mock.patch('api.controllers.fetch_tax_brackets')
    def test_base(self, mocked_fetch):
        self.api_fetch_mock["tax_brackets"] = [self.bracket_1_return]

        mocked_fetch.return_value = self.api_fetch_mock
        expected = {
            "income": self.income,
            "total_owed": 180000,
            "effective_rate": (180000 / self.income),
            "tax_brackets": [self.bracket_1_return],
        }

        assert calculate_tax(self.income, self.year) == expected

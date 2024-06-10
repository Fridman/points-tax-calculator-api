import json
import pytest
import requests
import unittest

from app import create_app
from flask import Flask
from flask import current_app as app
from flask_caching import Cache
from unittest import mock

from api.routes import (
    calculate_tax_view
)

'''
    calculate_tax_view(year=2022 : int)
'''


class TestCalculateTaxView(unittest.TestCase):
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
        self.income = 5000000

    def tearDown(self):
        self.app_context.pop()

    @mock.patch('api.routes.calculate_tax')
    def test_base(self, mocked_call):

        expected = {
            "income": self.income,
            "total_owed": 180000,
            "effective_rate": (180000 / self.income),
            "tax_brackets": [self.bracket_1_return],
        }
        mocked_call.return_value = expected
        with self.app.test_client() as client:
            response = client.get("/api/v1/calculate-tax/2022/?income=5000000")

            assert response.status_code == 200
            assert json.loads(response.data) == expected

    @mock.patch('api.routes.calculate_tax')
    def test_malformed_year(self, mocked_fetch):
        with self.app.test_client() as client:
            response = client.get("/api/v1/calculate-tax/202a/?income=5000000")

            assert response.status_code == 400
            assert json.loads(response.data).get("detail") is not None

    @mock.patch('api.routes.calculate_tax')
    def test_malformed_income(self, mocked_fetch):
        with self.app.test_client() as client:
            response = client.get("/api/v1/calculate-tax/202a/?income=500000a")

            assert response.status_code == 400
            assert json.loads(response.data).get("detail") is not None

    @mock.patch('api.routes.calculate_tax')
    def test_missing_income(self, mocked_fetch):
        with self.app.test_client() as client:
            response = client.get("/api/v1/calculate-tax/202a/")

            assert response.status_code == 400
            assert json.loads(response.data).get("detail") is not None

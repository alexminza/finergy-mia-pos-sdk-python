"""Python SDK for Finergy MIA POS eComm API"""

import json
import logging
import hashlib
import base64

import requests

from .finergy_mia_pos_auth_client import FinergyMiaPosAuthClient
from .finergy_mia_pos_api_client import FinergyMiaPosApiClient

# Based on Finergy MIA POS PHP SDK https://github.com/finergy-tech/mia-pay-ecomm-php-sdk (https://packagist.org/packages/finergy/mia-pos-sdk)

class FinergyMiaPosSdk:
    __instance = None
    __api_client = None
    __auth_client = None

    def __init__(self, base_url: str, merchant_id: str, secret_key: str):
        self.__auth_client = FinergyMiaPosAuthClient(base_url=base_url, merchant_id=merchant_id, secret_key=secret_key)
        self.__api_client = FinergyMiaPosApiClient(base_url=base_url)

    @classmethod
    def get_instance(cls, base_url: str, merchant_id: str, secret_key: str):
        """Returns a singleton instance of FinergyMiaPosSdk"""

        if cls.__instance is None:
            cls.__instance = cls(base_url=base_url, merchant_id=merchant_id, secret_key=secret_key)

        return cls.__instance

    def create_payment(self, payment_data: dict):
        pass

    def get_payment_status(self, payment_id: str):
        pass

    def verify_signature(self, result_str: str, signature: str):
        pass

    def form_sign_string_by_result(self, result_data: dict):
        pass

    def __validate_parameters(self, data: dict, required_fields: list):
        pass

    def __get_access_token(self):
        return self.__auth_client.get_access_token()

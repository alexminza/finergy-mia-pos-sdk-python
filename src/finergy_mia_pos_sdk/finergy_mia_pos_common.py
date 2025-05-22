"""Python SDK for Finergy MIA POS eComm API"""

import logging

import requests

class FinergyMiaPosCommon:
    DEFAULT_TIMEOUT = 30

    @classmethod
    def send_request(cls, method: str, url: str, data: dict = None, params: dict = None, token: str = None):
        """Sends an HTTP request to the Mia POS API."""

        auth = BearerAuth(token) if token else None

        logging.debug('FinergyMiaPosSdk Request', extra={'method': method, 'url': url, 'data': data, 'params': params})
        with requests.request(method=method, url=url, params=params, json=data, auth=auth, timeout=cls.DEFAULT_TIMEOUT) as response:
            response_json = response.json()
            logging.debug('FinergyMiaPosSdk Response', extra={'response_json': response_json})
            #response.raise_for_status()
            return response_json

#region Requests
class BearerAuth(requests.auth.AuthBase):
    """Attaches HTTP Bearer Token Authentication to the given Request object."""
    #https://requests.readthedocs.io/en/latest/user/authentication/#new-forms-of-authentication

    token: str = None

    def __init__(self, token: str):
        self.token = token

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        request.headers["Authorization"] = f'Bearer {self.token}'
        return request
#endregion

#region Exceptions
class FinergyClientApiException(Exception):
    pass

class FinergyValidationException(Exception):
    pass
#endregion

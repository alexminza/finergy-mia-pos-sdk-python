"""Python SDK for Finergy MIA POS eComm API"""

import logging

import requests

class FinergyMiaPosCommon:
    DEFAULT_TIMEOUT = 30

    @classmethod
    def send_request(cls, method: str, url: str, data: dict = None, params: dict = None, token: str = None) -> dict:
        """
        Sends an HTTP request to the Mia POS API.

        Args:
            method (str): HTTP method (e.g., 'POST', 'GET').
            url (str): The API endpoint URL.
            data (dict): The request payload (for POST requests).
            params (dict): Request URL params.
            token: Access token for authorization (optional).

        Returns:
            dict: The decoded JSON response from the API.

        Raises:
            FinergyClientApiException: If a network error, HTTP error, or JSON decoding failure occurs.
        """

        try:
            auth = BearerAuth(token) if token else None

            logging.debug('FinergyMiaPosSdk Request', extra={'method': method, 'url': url, 'data': data, 'params': params})
            with requests.request(method=method, url=url, params=params, json=data, auth=auth, timeout=cls.DEFAULT_TIMEOUT) as response:
                #response.raise_for_status()
                if response.status_code >= 400:
                    raise FinergyClientApiException(f'Mia POS client url {url}, method {method} HTTP Error: {response.status_code}, Response: {response.text}')

                response_json = response.json()
                logging.debug('FinergyMiaPosSdk Response', extra={'response_json': response_json})
                return response_json
        except Exception as e:
            raise FinergyClientApiException(f'Mia POS client url {url}, method {method} error: {e}') from e

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
class FinergyMiaPosSdkException(Exception):
    """Base exception class for Mia POS SDK."""
    pass

class FinergyClientApiException(FinergyMiaPosSdkException):
    """Represents an exception thrown when an API request fails."""

    __http_status_code: int = None
    __error_code: str = None
    __error_message: str = None

    def __init__(self, message: str, http_status_code: int = None, error_code: str = None, error_message: str = None):
        """
        FinergyClientApiException constructor.

        Args:
            message (str): General error message.
            http_status_code (int): HTTP status code.
            error_code (str): Error code returned by the API.
            error_message (str): Error message returned by the API.
        """
        super().__init__(message)
        self.__http_status_code = http_status_code
        self.__error_code = error_code
        self.__error_message = error_message

    def get_http_status_code(self):
        """
        Get the HTTP status code.

        Returns:
            int: HTTP status code or None
        """

        return self.__http_status_code

    def get_error_code(self):
        """
        Get the error code returned by the API.

        Returns:
            str: Error code or None
        """

        return self.__error_code

    def get_error_message(self):
        """
        Get the error message returned by the API.

        Returns:
            str: Error message or None
        """

        return self.__error_message

class FinergyValidationException(FinergyMiaPosSdkException):
    """Represents an exception thrown when validation of input data fails."""

    __invalid_fields: list = None

    def __init__(self, message: str, invalid_fields: list = None):
        """
        ValidationException constructor.

        Args:
            message (str): Error message
            invalid_fields (list): List of invalid fields
        """

        super().__init__(message)
        self.__invalid_fields = invalid_fields or []

    def get_invalid_fields(self):
        """
        Get the invalid fields.

        Returns:
            list: List of invalid field names
        """

        return self.__invalid_fields
#endregion

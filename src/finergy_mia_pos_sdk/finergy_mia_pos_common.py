"""Python SDK for Finergy MIA POS eComm API"""

import logging
import httpx

logger = logging.getLogger(__name__)


class FinergyMiaPosCommon:
    DEFAULT_TIMEOUT = 30

    @classmethod
    def _process_response(cls, response: httpx.Response):
        if response.is_error:
            logger.error('%s Error: %d %s', cls.__qualname__, response.status_code, response.text, extra={'method': response.request.method, 'url': response.request.url, 'params': response.request.url.params, 'response_text': response.text, 'status_code': response.status_code})
            #response.raise_for_status()
            raise FinergyClientApiException(f'MIA POS client url {response.request.url}, method {response.request.method} HTTP Error: {response.status_code}, Response: {response.text}')

        response_json: dict = response.json()
        logger.debug('%s Response: %d', cls.__qualname__, response.status_code, extra={'response_json': response_json})
        return response_json

    @classmethod
    def send_request(cls, method: str, url: str, data: dict = None, params: dict = None, token: str = None):
        """
        Sends an HTTP request to the MIA POS API.

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

            logger.debug('%s Request: %s %s', cls.__qualname__, method, url, extra={'method': method, 'url': url, 'data': data, 'params': params, 'token': token})
            with httpx.Client() as client:
                response = client.request(method=method, url=url, params=params, json=data, auth=auth, timeout=cls.DEFAULT_TIMEOUT)
                return cls._process_response(response=response)

        except Exception as ex:
            logger.exception(cls.__qualname__)
            raise FinergyClientApiException(f'MIA POS client url {url}, method {method} error: {ex}') from ex

    @classmethod
    async def send_request_async(cls, method: str, url: str, data: dict = None, params: dict = None, token: str = None):
        """
        Sends an async HTTP request to the MIA POS API.

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

            logger.debug('%s Request: %s %s', cls.__qualname__, method, url, extra={'method': method, 'url': url, 'data': data, 'params': params, 'token': token})
            async with httpx.AsyncClient() as client:
                response = await client.request(method=method, url=url, params=params, json=data, auth=auth, timeout=cls.DEFAULT_TIMEOUT)
                return cls._process_response(response=response)

        except Exception as ex:
            logger.exception(cls.__qualname__)
            raise FinergyClientApiException(f'MIA POS client url {url}, method {method} error: {ex}') from ex

#region Auth
class BearerAuth(httpx.Auth):
    """Attaches HTTP Bearer Token Authentication to the given Request object."""
    # https://www.python-httpx.org/advanced/authentication/#custom-authentication-schemes

    token: str = None

    def __init__(self, token: str):
        self.token = token

    def auth_flow(self, request: httpx.Request):
        request.headers['Authorization'] = f'Bearer {self.token}'
        yield request
#endregion

#region Exceptions
class FinergyMiaPosSdkException(Exception):
    """Base exception class for MIA POS SDK."""
    pass

class FinergyClientApiException(FinergyMiaPosSdkException):
    """Represents an exception thrown when an API request fails."""

    _http_status_code: int = None
    _error_code: str = None
    _error_message: str = None

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
        self._http_status_code = http_status_code
        self._error_code = error_code
        self._error_message = error_message

    def get_http_status_code(self):
        """
        Get the HTTP status code.

        Returns:
            int: HTTP status code or None
        """

        return self._http_status_code

    def get_error_code(self):
        """
        Get the error code returned by the API.

        Returns:
            str: Error code or None
        """

        return self._error_code

    def get_error_message(self):
        """
        Get the error message returned by the API.

        Returns:
            str: Error message or None
        """

        return self._error_message

class FinergyValidationException(FinergyMiaPosSdkException):
    """Represents an exception thrown when validation of input data fails."""

    _invalid_fields: list = None

    def __init__(self, message: str, invalid_fields: list = None):
        """
        ValidationException constructor.

        Args:
            message (str): Error message
            invalid_fields (list): List of invalid fields
        """

        super().__init__(message)
        self._invalid_fields = invalid_fields or []

    def get_invalid_fields(self):
        """
        Get the invalid fields.

        Returns:
            list: List of invalid field names
        """

        return self._invalid_fields
#endregion

"""Python SDK for Finergy MIA POS eComm API"""

import time
import logging

from .finergy_mia_pos_common import FinergyMiaPosCommon, FinergyClientApiException

logger = logging.getLogger(__name__)

class FinergyMiaPosAuthClient:
    """
    Handles authentication with the Mia POS Ecomm API.
    Provides methods to generate, refresh, and retrieve access tokens.
    """

    __base_url: str = None
    __merchant_id: str = None
    __secret_key: str = None

    __access_token: str = None
    __refresh_token: str = None
    __access_expire_time: str = None

    def __init__(self, base_url: str, merchant_id: str, secret_key: str):
        self.__base_url = base_url.rstrip('/')
        self.__merchant_id = merchant_id
        self.__secret_key = secret_key

    def get_access_token(self):
        """
        Retrieves the current access token.

        If the current access token is valid, it will return the cached token.
        Otherwise, it will attempt to refresh the token or generate a new one.

        Returns:
            str: The valid access token.

        Raises:
            FinergyClientApiException: If the token cannot be generated or refreshed.
        """

        if self.__access_token and not self.__is_token_expired():
            return self.__access_token

        if self.__refresh_token:
            try:
                return self.__refresh_access_token()
            except Exception:
                logger.exception('Mia POS refresh token failed')

        return self.__generate_new_tokens()

    def __generate_new_tokens(self):
        """
        Generates a new access token using the merchant credentials.
        Sends a request to the Mia POS API to obtain a new access and refresh token pair.

        Returns:
            str: The newly generated access token.

        Raises:
            FinergyClientApiException: If the API request fails or no access token is returned.
        """

        url = self.__base_url + '/ecomm/api/v1/token'
        data = {
            'merchantId': self.__merchant_id,
            'secretKey': self.__secret_key,
        }

        response = FinergyMiaPosCommon.send_request(method='POST', url=url, data=data)
        self.__parse_response_token(response)

        if not self.__access_token:
            raise FinergyClientApiException(f'Failed to retrieve access token by merchantId {self.__merchant_id}. accessToken is missing from the response')

        return self.__access_token

    def __refresh_access_token(self):
        """
        Refreshes the current access token using the refresh token.
        Sends a request to the Mia POS API to refresh the access token.

        Returns:
            str: The refreshed access token.

        Raises:
            FinergyClientApiException: If the API request fails or no access token is returned.
        """

        url = self.__base_url + '/ecomm/api/v1/token/refresh'
        data = {
            'refreshToken': self.__refresh_token,
        }

        response = FinergyMiaPosCommon.send_request(method='POST', url=url, data=data)
        self.__parse_response_token(response)

        if not self.__access_token:
            raise FinergyClientApiException(f'Failed to refresh access token by merchantId {self.__merchant_id}. accessToken is missing from the response')

        return self.__access_token

    def __is_token_expired(self):
        """
        Checks whether the current access token has expired.

        Returns:
            bool: True if the token is expired; otherwise, False.
        """

        return not self.__access_expire_time or time.time() >= self.__access_expire_time

    def __parse_response_token(self, response: dict):
        """
        Parses the token response from the Mia POS API.
        Extracts the access token, refresh token, and token expiration time from the response.

        Args:
            response (dict): The decoded API response containing token details.
        """

        self.__access_token = response.get('accessToken')
        self.__refresh_token = response.get('refreshToken')
        expires_in = response.get('accessTokenExpiresIn', 0)
        self.__access_expire_time = time.time() + expires_in - 10

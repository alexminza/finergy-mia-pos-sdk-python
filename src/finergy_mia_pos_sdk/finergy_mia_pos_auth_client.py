"""Python SDK for Finergy MIA POS eComm API"""

import logging
import time

from .finergy_mia_pos_common import FinergyMiaPosCommon, FinergyClientApiException

logger = logging.getLogger(__name__)


class FinergyMiaPosAuthClient:
    """
    Handles authentication with the MIA POS Ecomm API.
    Provides methods to generate, refresh, and retrieve access tokens.
    """

    AUTH_TOKEN = '/ecomm/api/v1/token'
    AUTH_TOKEN_REFRESH = '/ecomm/api/v1/token/refresh'

    _base_url: str = None
    _merchant_id: str = None
    _secret_key: str = None

    _access_token: str = None
    _refresh_token: str = None
    _access_expire_time: str = None

    def __init__(self, base_url: str, merchant_id: str, secret_key: str):
        self._base_url = base_url.rstrip('/')
        self._merchant_id = merchant_id
        self._secret_key = secret_key

    #region Get access token
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

        if self._access_token and not self._is_token_expired():
            return self._access_token

        if self._refresh_token:
            try:
                return self._refresh_access_token()
            except Exception:
                logger.exception('MIA POS refresh token failed')

        return self._generate_new_tokens()

    async def get_access_token_async(self):
        """
        Retrieves the current access token.

        If the current access token is valid, it will return the cached token.
        Otherwise, it will attempt to refresh the token or generate a new one.

        Returns:
            str: The valid access token.

        Raises:
            FinergyClientApiException: If the token cannot be generated or refreshed.
        """

        if self._access_token and not self._is_token_expired():
            return self._access_token

        if self._refresh_token:
            try:
                return await self._refresh_access_token_async()
            except Exception:
                logger.exception('MIA POS refresh token failed')

        return await self._generate_new_tokens_async()
    #endregion

    #region Generate new auth tokens API
    def _generate_new_tokens(self):
        """
        Generates a new access token using the merchant credentials.
        Sends a request to the MIA POS API to obtain a new access and refresh token pair.

        Returns:
            str: The newly generated access token.

        Raises:
            FinergyClientApiException: If the API request fails or no access token is returned.
        """

        url = self._base_url + self.AUTH_TOKEN
        generate_tokens_data = self._build_generate_tokens_data()

        response = FinergyMiaPosCommon.send_request(method='POST', url=url, data=generate_tokens_data)
        self._parse_response_token(response)

        if not self._access_token:
            raise FinergyClientApiException(f'Failed to retrieve access token by merchantId {self._merchant_id}. accessToken is missing from the response')

        return self._access_token

    async def _generate_new_tokens_async(self):
        """
        Generates a new access token using the merchant credentials.
        Sends a request to the MIA POS API to obtain a new access and refresh token pair.

        Returns:
            str: The newly generated access token.

        Raises:
            FinergyClientApiException: If the API request fails or no access token is returned.
        """

        url = self._base_url + self.AUTH_TOKEN
        generate_tokens_data = self._build_generate_tokens_data()

        response = await FinergyMiaPosCommon.send_request_async(method='POST', url=url, data=generate_tokens_data)
        self._parse_response_token(response)

        if not self._access_token:
            raise FinergyClientApiException(f'Failed to retrieve access token by merchantId {self._merchant_id}. accessToken is missing from the response')

        return self._access_token

    def _build_generate_tokens_data(self):
        tokens_data = {
            'merchantId': self._merchant_id,
            'secretKey': self._secret_key,
        }

        return tokens_data
    #endregion

    #region Refresh auth tokens API
    def _refresh_access_token(self):
        """
        Refreshes the current access token using the refresh token.
        Sends a request to the MIA POS API to refresh the access token.

        Returns:
            str: The refreshed access token.

        Raises:
            FinergyClientApiException: If the API request fails or no access token is returned.
        """

        url = self._base_url + self.AUTH_TOKEN_REFRESH
        refresh_tokens_data = self._build_refresh_tokens_data()

        response = FinergyMiaPosCommon.send_request(method='POST', url=url, data=refresh_tokens_data)
        self._parse_response_token(response)

        if not self._access_token:
            raise FinergyClientApiException(f'Failed to refresh access token by merchantId {self._merchant_id}. accessToken is missing from the response')

        return self._access_token

    async def _refresh_access_token_async(self):
        """
        Refreshes the current access token using the refresh token.
        Sends a request to the MIA POS API to refresh the access token.

        Returns:
            str: The refreshed access token.

        Raises:
            FinergyClientApiException: If the API request fails or no access token is returned.
        """

        url = self._base_url + self.AUTH_TOKEN_REFRESH
        refresh_tokens_data = self._build_refresh_tokens_data()

        response = await FinergyMiaPosCommon.send_request_async(method='POST', url=url, data=refresh_tokens_data)
        self._parse_response_token(response)

        if not self._access_token:
            raise FinergyClientApiException(f'Failed to refresh access token by merchantId {self._merchant_id}. accessToken is missing from the response')

        return self._access_token

    def _build_refresh_tokens_data(self):
        tokens_data = {
            'refreshToken': self._refresh_token
        }

        return tokens_data
    #endregion

    def _is_token_expired(self):
        """
        Checks whether the current access token has expired.

        Returns:
            bool: True if the token is expired; otherwise, False.
        """

        return not self._access_expire_time or time.time() >= self._access_expire_time

    def _parse_response_token(self, response: dict):
        """
        Parses the token response from the MIA POS API.
        Extracts the access token, refresh token, and token expiration time from the response.

        Args:
            response (dict): The decoded API response containing token details.
        """

        self._access_token = response.get('accessToken')
        self._refresh_token = response.get('refreshToken')
        expires_in: int = response.get('accessTokenExpiresIn', 0)
        self._access_expire_time = time.time() + expires_in - 10

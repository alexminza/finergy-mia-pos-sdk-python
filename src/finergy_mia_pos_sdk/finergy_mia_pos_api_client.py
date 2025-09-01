"""Python SDK for Finergy MIA POS eComm API"""

from .finergy_mia_pos_common import FinergyMiaPosCommon, FinergyClientApiException


class FinergyMiaPosApiClient:
    """
    Handles API requests to the MIA POS Ecomm API.
    Provides methods for creating payments, checking payment status,
    and retrieving the public key.
    """

    API_PAY = '/ecomm/api/v1/pay'
    API_PAYMENT = '/ecomm/api/v1/payment'
    API_PUBLIC_KEY = '/ecomm/api/v1/public-key'

    _base_url: str = None

    def __init__(self, base_url: str):
        self._base_url = base_url.rstrip('/')

    #region Create payment
    def create_payment(self, token: str, payment_data: dict):
        """
        Creates a new payment.
        Sends a POST request to the MIA POS API to create a payment.

        Args:
            token (str): Access token for authorization.
            payment_data (dict): A dict containing payment details by miaEcomm protocol

        Returns:
            dict: Response from the API containing payment details.

        Raises:
            FinergyClientApiException: If the API request fails or returns an error.
        """

        url = self._base_url + self.API_PAY
        return FinergyMiaPosCommon.send_request(method='POST', url=url, data=payment_data, token=token)

    async def create_payment_async(self, token: str, payment_data: dict):
        """
        Creates a new payment.
        Sends a POST request to the MIA POS API to create a payment.

        Args:
            token (str): Access token for authorization.
            payment_data (dict): A dict containing payment details by miaEcomm protocol

        Returns:
            dict: Response from the API containing payment details.

        Raises:
            FinergyClientApiException: If the API request fails or returns an error.
        """

        url = self._base_url + self.API_PAY
        return await FinergyMiaPosCommon.send_request_async(method='POST', url=url, data=payment_data, token=token)
    #endregion

    #region Payment status
    def get_payment_status(self, token: str, payment_id: str):
        """
        Retrieves the status of a payment.
        Sends a GET request to the MIA POS API to retrieve the payment status by its ID.

        Args:
            token (str): Access token for authorization.
            payment_id (str): Unique identifier of the payment.

        Returns:
            dict: Response from the API containing the payment status.

        Raises:
            FinergyClientApiException: If the API request fails or returns an error.
        """

        url = self._base_url + f'{self.API_PAYMENT}/{payment_id}'
        return FinergyMiaPosCommon.send_request(method='GET', url=url, token=token)

    async def get_payment_status_async(self, token: str, payment_id: str):
        """
        Retrieves the status of a payment.
        Sends a GET request to the MIA POS API to retrieve the payment status by its ID.

        Args:
            token (str): Access token for authorization.
            payment_id (str): Unique identifier of the payment.

        Returns:
            dict: Response from the API containing the payment status.

        Raises:
            FinergyClientApiException: If the API request fails or returns an error.
        """

        url = self._base_url + f'{self.API_PAYMENT}/{payment_id}'
        return await FinergyMiaPosCommon.send_request_async(method='GET', url=url, token=token)
    #endregion

    #region Public key
    def get_public_key(self, token: str):
        """
        Retrieves the public key from the MIA POS API.
        Sends a GET request to retrieve the public key for signature verification.

        Args:
            token (str): Access token for authorization.

        Returns:
            str: The public key returned by the API.

        Raises:
            FinergyClientApiException: If the public key is not found or the API request fails.
        """

        url = self._base_url + self.API_PUBLIC_KEY
        response = FinergyMiaPosCommon.send_request(method='GET', url=url, token=token)

        public_key: str = response.get('publicKey') if response else None

        if not public_key:
            raise FinergyClientApiException('Public key not found in the response')

        return public_key

    async def get_public_key_async(self, token: str):
        """
        Retrieves the public key from the MIA POS API.
        Sends a GET request to retrieve the public key for signature verification.

        Args:
            token (str): Access token for authorization.

        Returns:
            str: The public key returned by the API.

        Raises:
            FinergyClientApiException: If the public key is not found or the API request fails.
        """

        url = self._base_url + self.API_PUBLIC_KEY
        response = await FinergyMiaPosCommon.send_request_async(method='GET', url=url, token=token)

        public_key: str = response.get('publicKey') if response else None

        if not public_key:
            raise FinergyClientApiException('Public key not found in the response')

        return public_key
    #endregion

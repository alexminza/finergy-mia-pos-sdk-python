"""Python SDK for Finergy MIA POS eComm API"""

from .finergy_mia_pos_common import FinergyMiaPosCommon, FinergyClientApiException

class FinergyMiaPosApiClient:
    """
    Handles API requests to the Mia POS Ecomm API.
    Provides methods for creating payments, checking payment status,
    and retrieving the public key.
    """

    __base_url: str = None

    def __init__(self, base_url: str):
        self.__base_url = base_url.rstrip('/')

    def create_payment(self, token: str, payment_data: dict):
        """
        Creates a new payment.
        Sends a POST request to the Mia POS API to create a payment.

        Args:
            token (str): Access token for authorization.
            payment_data (dict): A dict containing payment details by miaEcomm protocol

        Returns:
            dict: Response from the API containing payment details.

        Raises:
            FinergyClientApiException: If the API request fails or returns an error.
        """

        url = self.__base_url + '/ecomm/api/v1/pay'
        return FinergyMiaPosCommon.send_request(method='POST', url=url, data=payment_data, token=token)

    def get_payment_status(self, token: str, payment_id: str):
        """
        Retrieves the status of a payment.
        Sends a GET request to the Mia POS API to retrieve the payment status by its ID.

        Args:
            token (str): Access token for authorization.
            payment_id (str): Unique identifier of the payment.

        Returns:
            dict: Response from the API containing the payment status.

        Raises:
            FinergyClientApiException: If the API request fails or returns an error.
        """

        url = self.__base_url + f'/ecomm/api/v1/payment/{payment_id}'
        return FinergyMiaPosCommon.send_request(method='GET', url=url, token=token)

    def get_public_key(self, token: str):
        """
        Retrieves the public key from the Mia POS API.
        Sends a GET request to retrieve the public key for signature verification.

        Args:
            token (str): Access token for authorization.

        Returns:
            str: The public key returned by the API.

        Raises:
            FinergyClientApiException: If the public key is not found or the API request fails.
        """

        url = self.__base_url + '/ecomm/api/v1/public-key'
        response = FinergyMiaPosCommon.send_request(method='GET', url=url, token=token)

        public_key = response.get('publicKey') if response else None

        if not public_key:
            raise FinergyClientApiException('Public key not found in the response')

        return public_key

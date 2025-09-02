"""Python SDK for Finergy MIA POS eComm API"""

import logging
import base64

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature

from .finergy_mia_pos_auth_client import FinergyMiaPosAuthClient
from .finergy_mia_pos_api_client import FinergyMiaPosApiClient
from .finergy_mia_pos_common import FinergyValidationException

logger = logging.getLogger(__name__)


# Based on Finergy MIA POS PHP SDK https://github.com/finergy-tech/mia-pay-ecomm-php-sdk (https://packagist.org/packages/finergy/mia-pos-sdk)
# Integration with MIA POS eComm https://github.com/finergy-tech/mia-pay-ecomm-integration

class FinergyMiaPosSdk:
    TEST_BASE_URL = 'https://ecomm-test.miapos.md'

    _api_client = None
    _auth_client = None

    def __init__(self, base_url: str, merchant_id: str, secret_key: str):
        """
        Initializes the SDK with the base URL, Merchant ID, and Secret Key.

        Args:
            base_url (str): Base URL for the MIA POS API.
            merchant_id (str): Merchant ID provided by MIA POS.
            secret_key (str): Secret Key for authentication.

        Raises:
            FinergyValidationException: If any of the required parameters are missing.
        """

        if not base_url:
            raise FinergyValidationException('Base URL is required.')

        if not merchant_id:
            raise FinergyValidationException('Merchant ID is required.')

        if not secret_key:
            raise FinergyValidationException('Secret Key is required.')

        self._auth_client = FinergyMiaPosAuthClient(base_url=base_url, merchant_id=merchant_id, secret_key=secret_key)
        self._api_client = FinergyMiaPosApiClient(base_url=base_url)

    #region Create payment
    def create_payment(self, payment_data: dict):
        """
        Creates a new payment.

        Args:
            payment_data (dict): A dict containing payment details by miaEcomm protocol.
                Required keys: 'terminalId', 'orderId', 'amount', 'currency', 'payDescription'.

        Returns:
            dict: Response from the API.

        Raises:
            FinergyValidationException: If required parameters are missing.
            FinergyClientApiException: If there is an API error during the request.
        """

        required_fields = ['terminalId', 'orderId', 'amount', 'currency', 'payDescription']

        self._validate_parameters(data=payment_data, required_fields=required_fields)
        token = self._get_access_token()
        return self._api_client.create_payment(token=token, payment_data=payment_data)

    async def create_payment_async(self, payment_data: dict):
        """
        Creates a new payment.

        Args:
            payment_data (dict): A dict containing payment details by miaEcomm protocol.
                Required keys: 'terminalId', 'orderId', 'amount', 'currency', 'payDescription'.

        Returns:
            dict: Response from the API.

        Raises:
            FinergyValidationException: If required parameters are missing.
            FinergyClientApiException: If there is an API error during the request.
        """

        required_fields = ['terminalId', 'orderId', 'amount', 'currency', 'payDescription']

        self._validate_parameters(data=payment_data, required_fields=required_fields)
        token = await self._get_access_token_async()
        return await self._api_client.create_payment_async(token=token, payment_data=payment_data)
    #endregion

    #region Get payment status
    def get_payment_status(self, payment_id: str):
        """
        Retrieves the status of a payment by its ID.

        Args:
            payment_id (str): The unique payment ID.

        Returns:
            dict: Response from the API.

        Raises:
            FinergyValidationException: If the payment ID is empty.
            FinergyClientApiException: If there is an API error during the request.
        """

        if not payment_id:
            raise FinergyValidationException('Payment ID is required.')

        token = self._get_access_token()
        return self._api_client.get_payment_status(token=token, payment_id=payment_id)

    async def get_payment_status_async(self, payment_id: str):
        """
        Retrieves the status of a payment by its ID.

        Args:
            payment_id (str): The unique payment ID.

        Returns:
            dict: Response from the API.

        Raises:
            FinergyValidationException: If the payment ID is empty.
            FinergyClientApiException: If there is an API error during the request.
        """

        if not payment_id:
            raise FinergyValidationException('Payment ID is required.')

        token = await self._get_access_token_async()
        return await self._api_client.get_payment_status_async(token=token, payment_id=payment_id)
    #endregion

    #region Callback signature validation
    def validate_callback_signature(self, callback_data: dict):
        """
        Validates the callback data signature.

        Args:
            callback_data (dict): Callback payload data.

        Returns:
            bool: Callback data payload signature validation result.

        Raises:
            FinergyValidationException: If required parameters are missing or fails to verify callback signature.
            FinergyClientApiException: If there is an API error during the request.
        """

        # https://github.com/finergy-tech/mia-pay-ecomm-integration/blob/main/docs/en/signature-verification.md
        # https://github.com/finergy-tech/mia-pay-ecomm-php-sdk/blob/main/examples/process_callback.php
        callback_signature: str = callback_data.get('signature')
        callback_result: dict[str, any] = callback_data.get('result')

        if not callback_signature or not callback_result:
            raise FinergyValidationException('Missing result or signature in callback data.')

        sign_string = self.form_sign_string_by_result(result_data=callback_result)
        validation_result = self.verify_signature(result_str=sign_string, signature=callback_signature)

        return validation_result

    async def validate_callback_signature_async(self, callback_data: dict):
        """
        Validates the callback data signature.

        Args:
            callback_data (dict): Callback payload data.

        Returns:
            bool: Callback data payload signature validation result.

        Raises:
            FinergyValidationException: If required parameters are missing or fails to verify callback signature.
            FinergyClientApiException: If there is an API error during the request.
        """

        callback_signature: str = callback_data.get('signature')
        callback_result: dict[str, any] = callback_data.get('result')

        if not callback_signature or not callback_result:
            raise FinergyValidationException('Missing result or signature in callback data.')

        sign_string = self.form_sign_string_by_result(result_data=callback_result)
        validation_result = await self.verify_signature_async(result_str=sign_string, signature=callback_signature)

        return validation_result

    def verify_signature(self, result_str: str, signature: str):
        """
        Verifies the signature of a payment result.

        Args:
            result_str (str): The result string to verify.
            signature (str): The provided signature.

        Returns:
            bool: True if the signature is valid; otherwise, False.

        Raises:
            FinergyValidationException: If required parameters are missing.
            FinergyClientApiException: If there is an API error during the request.
        """

        if not result_str:
            raise FinergyValidationException('Result string is required.')

        if not signature:
            raise FinergyValidationException('Signature is required.')

        token = self._get_access_token()
        public_key_str = self._api_client.get_public_key(token=token)

        if not public_key_str:
            raise FinergyValidationException('Public key is missing in the response.')

        try:
            return self._verify_result_signature(
                result_str=result_str,
                signature=signature,
                public_key_str=public_key_str)

        except Exception as ex:
            logger.exception(FinergyMiaPosSdk.__qualname__)
            raise FinergyValidationException(f'Failed to verify signature: {ex}') from ex

    async def verify_signature_async(self, result_str: str, signature: str):
        """
        Verifies the signature of a payment result.

        Args:
            result_str (str): The result string to verify.
            signature (str): The provided signature.

        Returns:
            bool: True if the signature is valid; otherwise, False.

        Raises:
            FinergyValidationException: If required parameters are missing.
            FinergyClientApiException: If there is an API error during the request.
        """

        if not result_str:
            raise FinergyValidationException('Result string is required.')

        if not signature:
            raise FinergyValidationException('Signature is required.')

        token = await self._get_access_token_async()
        public_key_str = await self._api_client.get_public_key_async(token=token)

        if not public_key_str:
            raise FinergyValidationException('Public key is missing in the response.')

        try:
            return self._verify_result_signature(
                result_str=result_str,
                signature=signature,
                public_key_str=public_key_str)

        except Exception as ex:
            logger.exception(FinergyMiaPosSdk.__qualname__)
            raise FinergyValidationException(f'Failed to verify signature: {ex}') from ex

    @staticmethod
    def form_sign_string_by_result(result_data: dict[str, any]):
        """
        Forms a signature string based on result data.

        Args:
            result_data (dict): A set of data received when receiving the payment status or when receiving the payment result on callbackUrl.

        Returns:
            str: Generated string for the data set, for signature verification.

        Raises:
            FinergyValidationException: If the result data is invalid.
        """

        if not result_data:
            raise FinergyValidationException('Result data must be a non-empty dict.')

        sorted_items = sorted(result_data.items())

        formatted_values = []
        for key, value in sorted_items:
            if key == 'amount':
                formatted_values.append(f'{float(value):.2f}')
            else:
                formatted_values.append(str(value))

        return ';'.join(formatted_values)

    @classmethod
    def _verify_result_signature(cls, result_str: str, signature: str, public_key_str: str):
        public_key_pem = (
            '-----BEGIN PUBLIC KEY-----\n' +
            '\n'.join(public_key_str[i:i+64] for i in range(0, len(public_key_str), 64)) +
            '\n-----END PUBLIC KEY-----'
        )

        public_key = serialization.load_pem_public_key(public_key_pem.encode())
        decoded_signature = base64.b64decode(signature)

        try:
            public_key.verify(
                decoded_signature,
                result_str.encode(),
                padding.PKCS1v15(),
                hashes.SHA256())

            return True
        except InvalidSignature:
            return False
    #endregion

    #region Validation
    def _validate_parameters(self, data: dict, required_fields: list[str]):
        """
        Validate the required parameters.

        Args:
            data (dict): Input data to validate.
            required_fields (list): List of required fields.

        Raises:
            ValidationException: If a required field is missing.
        """

        missing_fields = []

        for field in required_fields:
            if field not in data or not data[field]:
                missing_fields.append(field)

        if missing_fields:
            raise FinergyValidationException(
                f'Missing required fields: {", ".join(missing_fields)}',
                invalid_fields=missing_fields)
    #endregion

    #region Access token
    def _get_access_token(self):
        return self._auth_client.get_access_token()

    async def _get_access_token_async(self):
        return await self._auth_client.get_access_token_async()
    #endregion

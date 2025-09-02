# Python SDK for Finergy MIA POS eComm API
* Finergy MIA POS eComm integration: https://github.com/finergy-tech/mia-pay-ecomm-integration
* GitHub project https://github.com/alexminza/finergy-mia-pos-sdk-python
* PyPI package https://pypi.org/project/finergy-mia-pos-sdk/

## Installation
To easily install or upgrade to the latest release, use `pip`:
```shell
pip install --upgrade finergy-mia-pos-sdk
```

## Getting started
Import SDK:

```python
from finergy_mia_pos_sdk import FinergyMiaPosSdk
```

Add project configuration:

```python
import os

FINERGY_MIA_POS_BASE_URL = os.getenv('FINERGY_MIA_POS_BASE_URL', FinergyMiaPosSdk.TEST_BASE_URL)
FINERGY_MIA_POS_MERCHANT_ID = os.getenv('FINERGY_MIA_POS_MERCHANT_ID')
FINERGY_MIA_POS_SECRET_KEY = os.getenv('FINERGY_MIA_POS_SECRET_KEY')
FINERGY_MIA_POS_TERMINAL_ID = os.getenv('FINERGY_MIA_POS_TERMINAL_ID')
```

## SDK usage examples
### Initialize SDK instance

```python
finergy_sdk = FinergyMiaPosSdk(
    base_url=FINERGY_MIA_POS_BASE_URL,
    merchant_id=FINERGY_MIA_POS_MERCHANT_ID,
    secret_key=FINERGY_MIA_POS_SECRET_KEY)
```

### Create order payment

```python
payment_data = {
    'terminalId': FINERGY_MIA_POS_TERMINAL_ID,
    'orderId': 'order12345',
    'amount': 150.75,
    'currency': 'MDL',
    'language': 'ro',
    'payDescription': 'Payment for order #12345',
    'paymentType': 'qr',
    'clientName': 'Test Client',
    'clientPhone': '00000000',
    'clientEmail': 'test@test.com',
    'callbackUrl': 'http://your_callback_url',
    'successUrl': 'http://your_success_url?orderId=order12345',
    'failUrl': 'http://your_failUrl_url?orderId=order12345'
}

create_payment_response = finergy_sdk.create_payment(payment_data=payment_data)

payment_id = create_payment_response['paymentId']
checkout_page = create_payment_response['checkoutPage']
```

### Validate callback signature

```python
callback_data = {
    'result': {
        'terminalId': 'TRMW0001',
        'orderId': '108',
        'paymentId': '2a663962-c954-4984-90e5-1d24c3305f7b',
        'status': 'EXPIRED',
        'amount': 1775.00,
        'currency': 'MDL',
        'paymentType': 'qr',
        'paymentDate': '2024-12-17T11:54:23'
    },
    'signature': 'gtWkQdF2X2oCwO/+a+DJxpDc5DhjC1PMVWrnCXsCX54qOo24siRTy4PAjHoYet1r0KERVEL65p7UZuHcaK+TOiJptlalMUVZWbGLPf05WpyKPOPSPI1P4ZoADzJpceYsKjjZImB/+ft6OAF+ahxazhHkiT1Ze05vwD2L1D6zRohcxZl9XRJMChZcVD9bdNy23ozwuq6FwlnneJJeCPNvqveg7f5e0CD1NXWdLJ3WryP0ypcGtQGZAY+PrhkdVG5SWhYr0FFniAZIrp9yOFn3vrsUP4rpZmeqIahSV6x12pyyRsm+bs/tjw/kPR34ygG7ksXsrpwhQbltAHWeWwnOmg=='
}

validate_result = finergy_sdk.validate_callback_signature(callback_data=callback_data)
```

### Get payment status

```python
payment_status_response = finergy_sdk.get_payment_status(payment_id=payment_id)
```

For more examples see [Finergy MIA POS PHP SDK](https://github.com/finergy-tech/mia-pay-ecomm-php-sdk)
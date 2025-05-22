"""Python SDK for Finergy MIA POS eComm API"""

class FinergyMiaPosApiClient:
    __base_url: str = None

    def __init__(self, base_url: str):
        self.__base_url = base_url.rstrip('/')

    def create_payment(self, token: str, payment_data: dict):
        pass

    def get_payment_status(self, token: str, payment_id: str):
        pass

    def get_public_key(self, token: str):
        pass

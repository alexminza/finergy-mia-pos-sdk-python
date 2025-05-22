"""Python SDK for Finergy MIA POS eComm API"""

class FinergyMiaPosAuthClient:
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
        pass

    def __generate_new_token(self):
        pass

    def __refresh_access_token(self):
        pass

    def __is_token_expired(self):
        pass

    def __parse_response_token(self):
        pass

    def send_request(self, method: str, url: str, data: dict = None, params: dict = None, token: str = None, entity_id: str = None):
        pass

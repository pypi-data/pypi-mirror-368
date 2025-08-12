from __future__ import absolute_import

import enum

from rapyuta_io.utils import RestClient
from rapyuta_io.utils.rest_client import HttpMethod
from rapyuta_io.utils.utils import get_api_response_data


class AuthTokenLevel(str, enum.Enum):
    def __str__(self):
        return str(self.value)

    LOW = "low"
    MED = "med"
    HIGH = "high"


class RIPClient:
    AUTH_TOKEN_PATH = '/user/login'

    def __init__(self, rip_host):
        self._rip_host = rip_host

    def get_auth_token(self, email, password, token_level=AuthTokenLevel.LOW):
        """
        Fetches an auth token.

        You can fetch a new auth token and also specify the token validity
        with the token_level argument. It takes one of the following values
        `low`, `med` and `high` which correspond to 24h, 7d and 90d of token
        validity respectively.
        """
        url = self._rip_host + self.AUTH_TOKEN_PATH
        payload = {'email': email, 'password': password}
        response = RestClient(url).method(HttpMethod.POST).query_param(
            {'type': token_level}).execute(payload)
        data = get_api_response_data(response, parse_full=True)
        return data['data']['token']

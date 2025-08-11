import getpass
import time
from datetime import datetime

import requests
from dask_gateway.auth import GatewayAuth
from eodc_connect import settings
from jwt import PyJWKClient, decode


class DaskOIDC(GatewayAuth):
    def __init__(self, username: str):
        self.username = username
        self.token_url = settings.KEYCLOAK_TOKEN_URL
        self.cert_url = settings.KEYCLOAK_CERT_URL
        self.token = self.get_token()
        self.access_token_decoded = self.decode_access_token()

    def get_token(self):
        payload = {
            "grant_type": "password",
            "client_id": "dedl-dask-gateway",
            "username": self.username,
            "password": getpass.getpass(prompt="Enter your password:"),
        }
        return requests.post(self.token_url, data=payload).json()

    def decode_access_token(self):
        time.sleep(1)
        jwks_client = PyJWKClient(self.cert_url)
        time.sleep(1)
        signing_key = jwks_client.get_signing_key_from_jwt(self.token["access_token"])
        time.sleep(1)
        return decode(self.token["access_token"], signing_key.key, algorithms=["RS256"])

    def is_token_expired(self):
        return datetime.now() > datetime.fromtimestamp(self.access_token_decoded["exp"])

    def refresh_token_exchange(self):
        payload = {
            "grant_type": "refresh_token",
            "client_id": "dedl-dask-gateway",
            "refresh_token": self.token["refresh_token"],
        }
        return requests.post(self.token_url, data=payload).json()

    def refresh(self):
        self.token = self.refresh_token_exchange()
        self.access_token_decoded = self.decode_access_token()

    def pre_request(self, _):
        if self.is_token_expired():
            self.refresh()
        headers = {"Authorization": "Bearer " + self.token["access_token"]}
        return headers, None


class EODCConnection:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.token_url = settings.SDK_KEYCLOAK_TOKEN_URL
        self.cert_url = settings.SDK_KEYCLOAK_CERT_URL
        self.token = self.get_token()
        self.access_token_decoded = self.decode_access_token()

    def get_token(self):
        payload = {
            "grant_type": "password",
            "client_id": "sdk-login",
            "username": self.username,
            "password": self.password,
        }
        return requests.post(self.token_url, data=payload).json()

    def decode_access_token(self):
        jwks_client = PyJWKClient(self.cert_url)
        signing_key = jwks_client.get_signing_key_from_jwt(self.token["access_token"])

        time.sleep(1)

        return decode(
            self.token["access_token"],
            signing_key.key,
            algorithms=["RS256"],
            audience="sdk-login",
        )

    def is_token_expired(self):
        return datetime.now() > datetime.fromtimestamp(self.access_token_decoded["exp"])

    def refresh_token_exchange(self):
        payload = {
            "grant_type": "refresh_token",
            "client_id": "sdk-login",
            "refresh_token": self.token["refresh_token"],
        }
        return requests.post(self.token_url, data=payload).json()

    def refresh(self):
        self.token = self.refresh_token_exchange()
        self.access_token_decoded = self.decode_access_token()

    def inplace_sign(self, url: str):
        endpoint = settings.DATA_ACCESS_URL_SIGNING_URL.format(url=url, duration="10m")

        signed_url = requests.post(
            endpoint, headers={"Authorization": f"Bearer {self.token['access_token']}"}
        )

        return signed_url.text.lstrip('["').rstrip('"]')

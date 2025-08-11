from enum import Enum
from typing import Optional

from pydantic import BaseModel, SecretStr, field_validator
from pydantic_settings import BaseSettings


class Env(Enum):
    DEVELOPMENT = "dev"
    PRODUCTION = "prod"


class UrlModel(BaseModel):
    url: str

    @field_validator("url", mode="before")
    def strip_trailing_slash(cls, v):
        return v.rstrip("/")

    def __str__(self):
        return self.url


class EODCSettings(BaseSettings):
    ENVIRONMENT: Env = Env.DEVELOPMENT
    BASE_URL: Optional[str] = None
    FAAS_URL: Optional[str] = None
    DASK_URL: Optional[str] = "http://dask.services.eodc.eu"
    DASK_URL_TCP: Optional[str] = "tcp://dask.services.eodc.eu:10000/"
    KEYCLOAK_TOKEN_URL: Optional[
        str
    ] = "https://bouncer.eodc.eu/auth/realms/EODC/protocol/openid-connect/token"

    SDK_KEYCLOAK_TOKEN_URL: Optional[
        str
    ] = "https://keycloak.dev.services.eodc.eu/auth/realms/eodc-dev/protocol/openid-connect/token/"

    SDK_KEYCLOAK_CERT_URL: Optional[
        str
    ] = "https://keycloak.dev.services.eodc.eu/auth/realms/eodc-dev/protocol/openid-connect/certs"

    KEYCLOAK_CERT_URL: Optional[
        str
    ] = "https://bouncer.eodc.eu/auth/realms/EODC/protocol/openid-connect/certs"

    DATA_ACCESS_URL_SIGNING_URL: Optional[
        str
    ] = "https://dev.data.eodc.eu/presign?url={url}&duration={duration}"

    ARGO_WORKFLOWS_TOKEN: Optional[str] = ""
    NAMESPACE: Optional[str] = "development"

    CHILLER_URL: Optional[UrlModel] = UrlModel(url="https://chiller.eodc.eu/")
    API_KEY: Optional[SecretStr] = None

    @field_validator("NAMESPACE", mode="before")
    def set_namespace(cls, v, values):
        if v == Env.DEVELOPMENT:
            return "development"
        elif v == Env.PRODUCTION:
            return "production"
        else:
            return v


settings = EODCSettings()

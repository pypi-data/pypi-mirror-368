from pydantic_settings import BaseSettings,SettingsConfigDict
from typing import Optional
import os

"""
contains the envinronment variables settings for the fastapi server 
"""

class Settings(BaseSettings):
    oidc_client_id: str = ""
    oidc_client_secret: Optional[str] = None
    oidc_issuer: str = "https://auth.cern.ch/auth/realms/cern"
    oidc_jwks_uri: str = "https://auth.cern.ch/auth/realms/cern/protocol/openid-connect/certs"
    oidc_auth_uri: str = "https://auth.cern.ch/auth/realms/cern/protocol/openid-connect/auth"
    oidc_logout_uri: str = "https://auth.cern.ch/auth/realms/cern/protocol/openid-connect/logout"
    oidc_token_uri: str = "https://auth.cern.ch/auth/realms/cern/protocol/openid-connect/token"
    oidc_session_auth_allowed: bool = False  # whether the server can request a token from the auth server if it doesn't have one
    oidc_session_lifetime: int = 28800  # 8 hours
    oidc_session_store_type: str = "memory"  # the type of session store to use
    oidc_session_store_host: str = "localhost"  # the host of the session store
    oidc_session_store_port: int = 6379  # the port of the session store
    oidc_auth_route_prefix: str = "/auth"
    #allows developers to put this into a different namespace 
    model_config = SettingsConfigDict(env_prefix=os.environ.get("TSGAUTH_OIDC_PREFIX", "")) 
settings = Settings()
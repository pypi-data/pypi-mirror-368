import tsgauth.oidcauth
import requests
import authlib
from tsgauth.fastapi.settings import settings
from fastapi import HTTPException,Request

from typing import Dict, Any, Optional

def _parse_token_fastapi(token: str, validate: bool=True, require_aud:bool=True, key: Optional[Any]=None) -> Dict[str, Any]:
    """
    token parsing function for fastapi
    :param token: the token to parse
    :param validate: validate the token
    :param require_aud: require a client id to be set to validate the audience if validate = True
    :returns: the claims
    :raises: HTTPException if the token client_id is not set but require_aud is 
    """
    if require_aud and validate and not settings.oidc_client_id:
        raise HTTPException(status_code=500, detail="OIDC_CLIENT_ID not set but audience validation is set to required")

    return tsgauth.oidcauth.parse_token(token=token, 
                                        jwks_url=settings.oidc_jwks_uri,
                                        issuer=settings.oidc_issuer,
                                        client_id=settings.oidc_client_id,
                                        validate=validate)

def exchange_code_for_token(code: str, request: Request) -> Dict[str, Any]:
    """Exchanges an authorization code for an access token."""
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": f"{request.url_for('auth_callback')}",
        "client_id": settings.oidc_client_id,
        "client_secret": settings.oidc_client_secret,
    }
    response = requests.post(settings.oidc_token_uri, data=data)
    response.raise_for_status()
    return response.json()

def get_validated_claims(token : str, validate: bool =True, require_aud: bool = True) -> Dict[str, Any]:
    """
    validates the token and returns the claims
    :param token: the token to validate
    :param validate: if True, the token will be validated
    :param require_aud: if True, the client id of the exected aud must be set if validate is True
    :returns: the claims
    :raises: HTTPException if the token is invalid
    """
    try:
        return _parse_token_fastapi(token, validate=validate, require_aud=require_aud)  
    except authlib.jose.errors.InvalidClaimError as e:
        # changed from "aud to 'aud' in authlib 1.6
        if e.description == 'Invalid claim "aud"' or e.description == "Invalid claim 'aud'":
            raise HTTPException(status_code=403, detail=f"Invalid token audience, expects {settings.oidc_client_id}")
        else:
            raise HTTPException(status_code=403, detail="Invalid token")
    except HTTPException as e:
        raise e
    except Exception as e:            
        raise HTTPException(status_code=403, detail="Invalid token or expired token")

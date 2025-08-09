import tsgauth.oidcauth as oidcauth
import os
import pytest
import authlib

def test_client():
    """
    checks we can get a token and then decode and validate it
    """
    client_id = os.environ["TSGAUTH_CLIENT_ID"]
    client_secret = os.environ["TSGAUTH_CLIENT_SECRET"]
    target_client_id = "cms-tsg-frontend-testclient"
    auth = oidcauth.ClientAuth(client_id,client_secret,target_client_id)
    token_claims = oidcauth.parse_token(auth.token(),client_id=target_client_id)
    assert(token_claims["aud"]==target_client_id)

def test_headers():
    """
    checks we can add extra headers correctly
    """
    client_id = os.environ["TSGAUTH_CLIENT_ID"]
    client_secret = os.environ["TSGAUTH_CLIENT_SECRET"]
    target_client_id = "cms-tsg-frontend-testclient"
    auth = oidcauth.ClientAuth(client_id,client_secret,target_client_id)
    headers_extra = {"header" : "example_header","header2": "example_header2"}
    headers = auth.headers(headers_extra)
    headers_no_extra = auth.headers()
    #check no modification of input header
    assert(headers_extra == {"header" : "example_header","header2": "example_header2"})
    for header in ["header","header2"]:
        assert(headers[header] == headers_extra[header])
    assert("Authorization" in headers)
    assert("Authorization" in headers_no_extra)
    assert(headers["Authorization"]==headers_no_extra["Authorization"])


def test_client_wrong_secret():
    """
    checks auth fails with wrong secret
    """
    client_id = os.environ["TSGAUTH_CLIENT_ID"]
    client_secret = "423r423kfewkl23h23r"
    target_client_id = "cms-tsg-frontend-testclient"
    auth = oidcauth.ClientAuth(client_id,client_secret,target_client_id)
    with pytest.raises(oidcauth.AuthError):
        auth.token()

def test_client_wrong_aud():
    """
    checks we validate the audience correctly
    """
    client_id = os.environ["TSGAUTH_CLIENT_ID"]
    client_secret = os.environ["TSGAUTH_CLIENT_SECRET"]
    target_client_id = "cms-tsg-frontend-testclient"
    wrong_client_id = "cmsoms-prod"
    auth = oidcauth.ClientAuth(client_id,client_secret,target_client_id)
    with pytest.raises(authlib.jose.errors.InvalidClaimError):
        oidcauth.parse_token(auth.token(),client_id=wrong_client_id)

def test_client_wrong_aud_novalidate():
    """
    checks we can remove validation
    """
    client_id = os.environ["TSGAUTH_CLIENT_ID"]
    client_secret = os.environ["TSGAUTH_CLIENT_SECRET"]
    target_client_id = "cms-tsg-frontend-testclient"
    wrong_client_id = "cmsoms-prod"
    auth = oidcauth.ClientAuth(client_id,client_secret,target_client_id)
    oidcauth.parse_token(auth.token(),client_id=wrong_client_id,validate=False)


def test_client_default():
    """
    checks we parse correctly with the defaults
    """
    client_id = os.environ["TSGAUTH_CLIENT_ID"]
    client_secret = os.environ["TSGAUTH_CLIENT_SECRET"]
    target_client_id = "cms-tsg-frontend-testclient"    
    auth = oidcauth.ClientAuth(client_id,client_secret,target_client_id)
    token_claims = oidcauth.parse_token(auth.token())
    assert(token_claims["aud"]==target_client_id)


def test_client_wrong_iss():
    """
    checks we validate the issuer correctly
    """
    client_id = os.environ["TSGAUTH_CLIENT_ID"]
    client_secret = os.environ["TSGAUTH_CLIENT_SECRET"]
    target_client_id = "cms-tsg-frontend-testclient"    
    wrong_iss = "https://example.com/"
    auth = oidcauth.ClientAuth(client_id,client_secret,target_client_id)
    with pytest.raises(authlib.jose.errors.InvalidClaimError):
        oidcauth.parse_token(auth.token(),issuer=wrong_iss,client_id=target_client_id)


import pytest
import tsgauth
from Crypto.PublicKey import RSA
from Crypto.Hash import HMAC, SHA256
from authlib.jose import jwt, JsonWebKey
import authlib
import time
import base64
import os

@pytest.fixture
def client_id():
    return "tsgauth-test"

@pytest.fixture
def base_claims(client_id):
    """
    mocks up some basic claims for testing
    """
    return {
        "iss": "https://auth.cern.ch/auth/realms/cern",
        "aud": client_id,
        "sub": "testuser",
        "name": "testuser",
        "preferred_username": "testuser",
        "exp" : int(time.time()) + 3600,
        "iat" : int(time.time()),
        "email": "test@example.com"
    }

@pytest.fixture
def private_key():
    """
    creates a private key
    """
    return RSA.generate(2048)   

@pytest.fixture
def private_pem(private_key):
    """
    converts the private key to a pem
    """
    return private_key.export_key(format='PEM')

@pytest.fixture
def public_pem(private_key):
    """
    creates a public key in pem format
    """
    return private_key.publickey().export_key(format='PEM')

@pytest.fixture
def token_rs256(base_claims,private_pem):
    """
    creates a token with RS256
    """
    return jwt.encode({"alg": "RS256"}, base_claims, private_pem)

@pytest.fixture
def hs_key():
    """
    creates a key for HS256
    """
    return base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')

@pytest.fixture
def token_hs256(base_claims,hs_key):
    """
    creates a token with HS256
    """
    return jwt.encode({"alg": "HS256"}, base_claims, hs_key)

def test_rs256(token_rs256,public_pem,base_claims):
    """
    checks we can get a token and then decode and validate it
    """
    claims = tsgauth.oidcauth.parse_token(token_rs256, jwks_key=public_pem)    
    assert claims == base_claims

def test_hs256_not_allowed(token_hs256,hs_key):
    """
    checks that hs256 is forbidden by default
    """

    with pytest.raises(authlib.jose.errors.UnsupportedAlgorithmError):
        tsgauth.oidcauth.parse_token(token_hs256, jwks_key=hs_key)

@pytest.mark.parametrize("algos",[
    ("HS256"),("all"),("ALL"),("RS256,HS256")
])
def test_hs256_allowed(monkeypatch,token_hs256,hs_key,base_claims,algos):
    """
    checks we can enable hs256 if we want
    """
    monkeypatch.setenv("TSGAUTH_ALLOWED_ALGS",algos)
    jwk_key = JsonWebKey.import_key(hs_key,{'kty': 'oct'})
    claims = tsgauth.oidcauth.parse_token(token_hs256, jwks_key=jwk_key.as_dict())
    assert claims == base_claims
    


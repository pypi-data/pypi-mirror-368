import tsgauth.oidcauth as oidcauth
import os
import pytest
import time
"""
this the ability to refresh a token, client and kerb represent the two types  (client can auth directly against another aud)
"""

@pytest.mark.parametrize("target_client_id, authclass",[
    (None,oidcauth.ClientAuth),
    ("cms-tsg-frontend-testclient",oidcauth.ClientAuth),
    (None,oidcauth.KerbAuth)    
])
def test_refresh(target_client_id,authclass):
    client_id = os.environ["TSGAUTH_CLIENT_ID"]
    client_secret = os.environ["TSGAUTH_CLIENT_SECRET"]
    auth = authclass(client_id=client_id,client_secret=client_secret,target_client_id=target_client_id)

    expected_aud = client_id if target_client_id is None else target_client_id
    token_claims = oidcauth.parse_token(auth.token(),client_id=expected_aud)
    expires_in = token_claims["exp"]
    assert(token_claims["aud"]==expected_aud)

    time.sleep(10)
    #this will force a refresh
    auth._token_required_remaining_time = 999999999
    token_refresh_claims = oidcauth.parse_token(auth.token(),client_id=expected_aud)
    assert(token_refresh_claims["aud"]==expected_aud)
    assert(token_refresh_claims["exp"]>expires_in)
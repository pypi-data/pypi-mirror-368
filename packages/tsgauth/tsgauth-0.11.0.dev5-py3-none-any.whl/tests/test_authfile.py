import tsgauth
import os
import pytest


def token_filename(client_id,target_client_id=None):
    return f"access_token_{client_id}_{target_client_id}.json" if target_client_id is not None else f"access_token_{client_id}.json"

@pytest.mark.parametrize("tsgauth_force_use_authfile,tsgauth_force_dont_use_authfile,use_auth_file,expected_file_written",[
    (None,None,False,False),
    (None,None,True,True),
    ("0","0",False,False),
    ("0","0",True,True),
    ("0","1",False,False),
    ("0","1",True,False),
    ("1","0",False,True),
    ("1","0",True,True),
])
def test_write_authfile(tmp_path,tsgauth_force_use_authfile,tsgauth_force_dont_use_authfile,use_auth_file,expected_file_written,monkeypatch):
    """
    checks the various combinations of writing the auth file
    """    
    monkeypatch.setenv("TSGAUTH_AUTHDIR",str(tmp_path))
    
    if tsgauth_force_use_authfile is not None:
        monkeypatch.setenv("TSGAUTH_FORCE_USE_AUTHFILE",tsgauth_force_use_authfile)        
    if tsgauth_force_dont_use_authfile is not None:
        monkeypatch.setenv("TSGAUTH_FORCE_DONT_USE_AUTHFILE",tsgauth_force_dont_use_authfile)
        
    client_id = os.environ["TSGAUTH_CLIENT_ID"]
    client_secret = os.environ["TSGAUTH_CLIENT_SECRET"]
    target_client_id = "cms-tsg-frontend-testclient"
    auth = tsgauth.oidcauth.ClientAuth(client_id,client_secret,target_client_id,use_auth_file=use_auth_file)
    token_claims = tsgauth.oidcauth.parse_token(auth.token(),client_id=target_client_id)
    assert(token_claims["aud"]==target_client_id)
   
    token_file = os.path.join(tmp_path,token_filename(client_id,target_client_id))
    assert os.path.exists(token_file)==expected_file_written, f"token file created {os.path.exists(token_file)} but expected file creation was {expected_file_written}"

def test_writefile(tmp_path,monkeypatch):
    """
    checks we can get read a token from the file
    first we write it to the file
    then we change our client secret to a wrong value so getting the token fails (just to prove that the test can fail)
    then we get the token from the file and check we decode it properly
    """
    
    monkeypatch.setenv("TSGAUTH_AUTHDIR",str(tmp_path))
    client_id = os.environ["TSGAUTH_CLIENT_ID"]
    client_secret = os.environ["TSGAUTH_CLIENT_SECRET"]
    target_client_id = "cms-tsg-frontend-testclient"
    auth = tsgauth.oidcauth.ClientAuth(client_id,client_secret,target_client_id,use_auth_file=True)
    token_claims = tsgauth.oidcauth.parse_token(auth.token(),client_id=target_client_id)
    assert(token_claims["aud"]==target_client_id)

    auth_readtoken_fail = tsgauth.oidcauth.ClientAuth(client_id,"badsecret",target_client_id,use_auth_file=False)
    with pytest.raises(tsgauth.oidcauth.AuthError):
        auth_readtoken_fail.token()
    
    auth_readtoken = tsgauth.oidcauth.ClientAuth(client_id,"badsecret",target_client_id,use_auth_file=True)
    token_claims = tsgauth.oidcauth.parse_token(auth_readtoken.token(),client_id=target_client_id)
    assert(token_claims["aud"]==target_client_id)


def test_permissions(tmp_path,monkeypatch):
    """
    checks the written file has the correct permssions
    """    
    monkeypatch.setenv("TSGAUTH_AUTHDIR",str(tmp_path))
    client_id = os.environ["TSGAUTH_CLIENT_ID"]
    client_secret = os.environ["TSGAUTH_CLIENT_SECRET"]    
    target_client_id = "cms-tsg-frontend-testclient"
    auth = tsgauth.oidcauth.ClientAuth(client_id,client_secret,target_client_id,use_auth_file=True)
    auth.token()
    token_file = os.path.join(tmp_path,token_filename(client_id,target_client_id))
    permissions = oct(os.stat(token_file).st_mode)[-3:]
    assert permissions == "600", f"token file permissions are {permissions} but expected 600"


def test_permissions_wrong(tmp_path,monkeypatch):
    """
    checks we detect a file with the wrong permssions
    also side tests our ability to gracefully handle a file of invalid format
    """
    client_id = os.environ["TSGAUTH_CLIENT_ID"]
    target_client_id = "cms-tsg-frontend-testclient"
    token_file = os.path.join(tmp_path,token_filename(client_id,target_client_id))
    with open(token_file,"w") as f:
        pass

    monkeypatch.setenv("TSGAUTH_AUTHDIR",str(tmp_path))
   
    client_secret = os.environ["TSGAUTH_CLIENT_SECRET"]
    
    auth = tsgauth.oidcauth.ClientAuth(client_id,client_secret,target_client_id,use_auth_file=True)
    with pytest.raises(tsgauth.oidcauth.FilePermissionsError):
        auth.token()
    
    
import tsgauth.oidcauth as oidcauth
import os
import pytest
import threading
import time
import bs4
import requests
import sys
"""
this is for testing with a user with kerberous authentication

"""

def test_kerblogin_public():
    """
    checks we can login with kerberos for a public client
    """
    client_id = "cms-tsg-frontend-testclient"
    auth = oidcauth.KerbAuth(client_id=client_id)
    token_claims = oidcauth.parse_token(auth.token(),client_id=client_id)
    assert(token_claims["aud"]=="cms-tsg-frontend-testclient")

def test_kerblogin_public_not_auth():
    """
    checks we cant login with kerberos to a public client dont have permissions
    also checks error logging
    """
    client_id = "cms-tsg-frontend-testclient-nousers"
    auth = oidcauth.KerbAuth(client_id=client_id)
    with pytest.raises(oidcauth.AuthError):
        auth.token()

def test_authssotoken():
    """
    checks that AuthGetSSOToken now throws a run time error after it was removed
    """
    client_id = "cms-tsg-frontend-testclient"
    with pytest.raises(RuntimeError):
        oidcauth.AuthGetSSOTokenAuth(client_id=client_id)
    

def test_kerblogin_private():
    """
    checks we can kerberos login to a private client
    """
    client_id = os.environ["TSGAUTH_CLIENT_ID"]
    client_secret = os.environ["TSGAUTH_CLIENT_SECRET"]
    auth = oidcauth.KerbAuth(client_id=client_id,client_secret=client_secret)
    token_claims = oidcauth.parse_token(auth.token(),client_id=client_id)
    assert(token_claims["aud"]==client_id)

def test_kerblogin_private_wrong_secret():
    """
    checks we cant login with kerberos to a private client with wrong secret
    """
    client_id = os.environ["TSGAUTH_CLIENT_ID"]
    client_secret = "tefwefewfewfewf2"
    auth = oidcauth.KerbAuth(client_id=client_id,client_secret=client_secret)
    with pytest.raises(oidcauth.AuthError):
        auth.token()


def test_device_login(capsys):
    """
    this checks we can do a device login. This also does a side test of our ability
    to session based auth as we need to access the cern device login page and click yes
    programtically (which normally you would never do of course!)

    its a little complicated as we keep a seperate thread going for the device login polling
    while we capture the output and parse it to get the url for the device login page
    """
        
    auth = oidcauth.DeviceAuth("cms-tsg-frontend-testclient",use_auth_file=False)
    expected_code_url = f"https://{auth.hostname}/auth/realms/{auth.realm}/device?user_code="
  
    thread = threading.Thread(target=auth.token)

    # Start the thread (non-blocking)
    thread.start()
    url = ""
    start_time = time.time()  
    while not url.startswith(expected_code_url) and time.time()-start_time<60:            
        captured = capsys.readouterr()
        try:
            url = captured.out.split("\n")[1]
            print(url,file=sys.stderr)
        except IndexError:
            print("url not found",captured.out,file=sys.stderr)
            pass                  
        time.sleep(10)

    if not url.startswith(expected_code_url):
        raise Exception("Could not get the url for the device login page")

    #now we need to "click the link" to authenticate
    auth_kerb = oidcauth.KerbSessionAuth()    
    r_test = requests.get("https://twiki.cern.ch/twiki/bin/view/CMS/HLTOnCallGuide",**auth_kerb.authparams())
    r_auth = requests.get(url,**auth_kerb.authparams())
    soup = bs4.BeautifulSoup(r_auth.text, features="html.parser")
    auth_form = soup.find("form")
    action = auth_form.attrs["action"]
    form_input = soup.find('input',{"name" : "code"})
    form_input_value = form_input.attrs["value"]
    form_input_name = form_input.attrs["name"]
    auth_url = f"https://{auth.hostname}{action}"

    r_auth = requests.post(auth_url,data={form_input_name : form_input_value},**auth_kerb.authparams())
    
    thread.join()
    assert oidcauth.parse_token(auth.token())["aud"] == "cms-tsg-frontend-testclient"
    
    

 

from fastapi import FastAPI,Depends
from fastapi.testclient import TestClient
from tsgauth.fastapi import JWTBearerClaims
from starlette.middleware.sessions import SessionMiddleware
import tsgauth
import pytest
import requests
import uvicorn
import asyncio

### test server setup
client_id = "cms-tsg-frontend-testclient"
client_id_wrong = "not_a_real_client"
auth = tsgauth.oidcauth.KerbAuth(client_id)

@pytest.fixture
def app(monkeypatch):
    monkeypatch.setenv("OIDC_CLIENT_ID",client_id)
    monkeypatch.setattr(tsgauth.fastapi.settings,"oidc_client_id",client_id)
    app = FastAPI()
    setup_app_endpoints(app)
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

def setup_app_endpoints(app):
    @app.get("/unsecure")
    async def unsecure():
        return {"msg": "unsecure endpoint"}

    @app.get("/secure")
    async def secure(claims = Depends(JWTBearerClaims())):
        return {"msg": f"welcome {claims['sub']}"}
    
    @app.get("/secure_noaud")
    async def secure(claims = Depends(JWTBearerClaims(require_aud=False))):
        return {"msg": f"welcome {claims['sub']}"}
    
    @app.get("/secure_noverify")
    async def secure(claims = Depends(JWTBearerClaims(validate_token=False))):
        return {"msg": f"welcome {claims['sub']}"}


### tests
def test_unsecure(client):
    """
    simple test to just check we started the fastapi server correctly
    """    
    resp = client.get('/unsecure')
    assert resp.status_code == 200
    assert resp.json()['msg'] == 'unsecure endpoint'

def test_secure_noauth(client):
    """
    test that we fail the auth when we dont pass in the correct authentication parameters
    """    
    resp = client.get('/secure')
    assert resp.status_code == 401

def test_secure_auth(client):
    """
    test that we can authenticate and get the username back
    """
    resp = client.get('/secure',**auth.authparams())
    subject = tsgauth.oidcauth.parse_token(auth.token())["sub"]
    assert resp.status_code == 200
    assert resp.json()['msg'] == f'welcome {subject}'

@pytest.mark.parametrize("client_id,require_aud,expected_status",[(None,True,500),("",True,500),(None,False,200),("",False,200)])
def test_secure_auth_no_client_id(client,monkeypatch,client_id,require_aud,expected_status):
    """
    tests that by default we require the client_id to be set
    """
    monkeypatch.setenv("OIDC_CLIENT_ID",client_id if client_id is not None else "")
    monkeypatch.setattr(tsgauth.fastapi.settings,"oidc_client_id",client_id)
    endpoint = "/secure" if require_aud else "/secure_noaud"
    resp = client.get(endpoint,**auth.authparams())
    assert resp.status_code == expected_status


def test_secure_wrong_aud(client,monkeypatch):
    """
    test that we reject tokens with the wrong auth
    """
    monkeypatch.setenv("OIDC_CLIENT_ID",client_id_wrong)
    monkeypatch.setattr(tsgauth.fastapi.settings,"oidc_client_id",client_id_wrong)
    resp = client.get('/secure',**auth.authparams())
    assert resp.status_code == 403
    assert resp.json()['detail'] == f'Invalid token audience, expects {client_id_wrong}'

@pytest.fixture
def server_with_session(monkeypatch):
    app = FastAPI()
    monkeypatch.setenv("OIDC_CLIENT_ID",client_id)
    monkeypatch.setattr(tsgauth.fastapi.settings,"oidc_client_id",client_id)
    monkeypatch.setattr(tsgauth.fastapi.settings,"oidc_session_auth_allowed",True)
    setup_app_endpoints(app)    
    tsgauth.fastapi.setup_app(app,secret_key="for-testing-purposes")
    config = uvicorn.Config(app, host="0.0.0.0", port=5000, log_level="info")
    server = uvicorn.Server(config)
    
    import threading

    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()
    
    yield
    
    server.should_exit = True
    server_thread.join()

def test_session_auth(server_with_session):
    """
    test that we can use a custom session auth

    I just could not get this to work with the test client so we just run it as normal    
    """
    
    auth = tsgauth.oidcauth.KerbSessionAuth()
    resp = requests.get("http://localhost:5000/secure",**auth.authparams())     
    assert resp.status_code == 200
    assert resp.json()['msg'].startswith('welcome')

def test_session_auth_customstore(client,monkeypatch):
    """
    test that we can override the session auth store with another one
    this one just removes the auth and injects fake auth data
    """

    monkeypatch.setattr(tsgauth.fastapi.settings,"oidc_session_auth_allowed",True)
    class CustomAuthStore(tsgauth.fastapi.SessionAuthBase):
        async def claims(cls,request):
            return {"sub" : "testuser"}
        async def store(cls,request,claims):
            pass
        async def clear(cls,request):
            pass
        async def token_request_allowed(cls, request):
            return await super().token_request_allowed(request)
        async def auth_attemp(cls):
            pass
    def custom_auth_store():   
        return CustomAuthStore() 
    
    
    client.app.dependency_overrides[tsgauth.fastapi.get_auth_store] = custom_auth_store    
    resp = client.get('/secure')
    assert resp.status_code == 200
    assert resp.json()['msg'] == 'welcome testuser'

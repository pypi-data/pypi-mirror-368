from flask import Flask, g, request
import tsgauth
import pytest
import multiprocessing
import requests

@pytest.fixture
def app():
    """
    creates our toy flask app to test with
    """
    app = Flask(__name__)

    app.config.update({           
        'OIDC_ISSUER' : "https://auth.cern.ch/auth/realms/cern",
        'OIDC_JWKS_URI' : "https://auth.cern.ch/auth/realms/cern/protocol/openid-connect/certs",
        'OIDC_CLIENT_ID' : "cms-tsg-frontend-testclient"        
    }) 
        
    @app.route('/unsecure')
    def unsecure():
        return {"msg" : "unsecure endpoint"}
    

    @app.route('/secure')
    @tsgauth.flaskoidc.accept_token()
    def secure():
        return {"msg" : f"welcome {g.oidc_token_info['sub']}"}
    return app

@pytest.fixture
def app_with_session(app):
    app.config['OIDC_SESSION_AUTH_ALLOWED'] = True
    app.config['OIDC_SESSION_STORE_TYPE'] = "simplemem"
    app.secret_key = "test key, change this in production"
    app.register_blueprint(tsgauth.flaskoidc.auth_blueprint)


    return app

@pytest.fixture
def server_with_session(app_with_session):
    server_thread = multiprocessing.Process(target=lambda: app_with_session.run(host='127.0.0.1', port=5000), daemon=True)
    server_thread.start()
    
    # Add a delay to ensure the server has time to start
    import time
    time.sleep(1)
    
    yield    
    server_thread.terminate()


def test_unsecure(app):
    """
    simple test to just check we started the flask server correctly
    """    
    with app.test_client() as c:
        resp = c.get('/unsecure')
        assert resp.status_code == 200
        assert resp.json['msg'] == 'unsecure endpoint'

def test_secure_noauth(app):
    """
    test that we fail the auth when we dont pass in the correct authentication parameters
    """
    with app.test_client() as c:
        resp = c.get('/secure')
        assert resp.status_code == 401

def test_secure_auth(app):
    """
    test that we can authenticate and get the username back
    """    
    auth = tsgauth.oidcauth.KerbAuth("cms-tsg-frontend-testclient")
    subject = tsgauth.oidcauth.parse_token(auth.token())["sub"]
    with app.test_client() as c:
        resp = c.get('/secure',**auth.authparams())
        assert resp.status_code == 200
        assert resp.json['msg'] == f'welcome {subject}'

def test_secure_session_auth(server_with_session):
    """
    test that we can authenticate and get the username back using session auth
    """    
    auth = tsgauth.oidcauth.KerbSessionAuth()
    resp = requests.get('http://localhost:5000/secure',**auth.authparams())    
    assert resp.status_code == 200
    assert resp.json()['msg'].startswith('welcome')
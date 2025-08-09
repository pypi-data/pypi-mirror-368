from flask import Flask, g, session, request, redirect, url_for
from urllib.parse import urlencode
import tsgauth

"""
to run do 

FLASK_APP=flask_server.py flask dev

by default session auth is enabled (OIDC_ALLOW_TOKEN_REQUEST = True)
if you setup a redis server you can set OIDC_AUTH_STORE to redis to store the session data persistently

a simple way to run a redis server is to use docker (note normally I use podman with docker aliased to podman)

docker pull registry.cern.ch/docker.io/library/redis
docker run -p 6379:6379 redis


"""

def create_app():
    """
    creates our toy flask app to test with
    """
    app = Flask(__name__)

    app.config.update({           
        'OIDC_ISSUER' : "https://auth.cern.ch/auth/realms/cern",
        'OIDC_JWKS_URI' : "https://auth.cern.ch/auth/realms/cern/protocol/openid-connect/certs",
        'OIDC_AUTH_URI' : "https://auth.cern.ch/auth/realms/cern/protocol/openid-connect/auth",
        'OIDC_LOGOUT_URI' : "https://auth.cern.ch/auth/realms/cern/protocol/openid-connect/logout",
        'OIDC_CLIENT_ID' : "cms-tsg-frontend-client",        
        'OIDC_TOKEN_URI' : "https://auth.cern.ch/auth/realms/cern/protocol/openid-connect/token",
        'OIDC_SESSION_AUTH_ALLOWED' : True, #if True, we can request a token from the auth server if no token is passed in
        'OIDC_SESSION_STORE_HOST' : "localhost", #change to your redis host if you are using redis as auth store
        'OIDC_SESSION_STORE_PORT' : 6379,
        'OIDC_SESSION_STORE_TYPE' : "redis", #change this to redis to store it persistently
        'OIDC_SESSION_LIFETIME' : 12*60*60, #12 hours 
        'OIDC_SESSION_MANAGE_COOKIE' : True,    
        'OIDC_SESSION_COOKIE_SAMESITE' : "Lax",          
        'OIDC_SESSION_COOKIE_PERMANENT' : True
        
        
    }) 
    app.secret_key = "test key, change this in production"
    app.register_blueprint(tsgauth.flaskoidc.auth_blueprint)
    return app 


app = create_app()

@app.route('/api/v0/unsecure')
def unsecure():
    return {"msg" : "unsecure endpoint"}
    

@app.route('/api/v0/secure')
@tsgauth.flaskoidc.accept_token()
def secure():
    return {"claims" : g.oidc_token_info}


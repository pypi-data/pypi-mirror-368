# tsgauth

A collection of python base CERN SSO based authentication and authorisation tools used by the TSG. It provides methods for both users trying to access SSO protected sites in python and for sites to add SSO protection to their endpoints. It is minimal and tries to stay out of the way of the user as much as possible.

The current version is 0.11.0

It is pip installable by 
```bash
pip3 install tsgauth==0.11.0
pip3 install tsgauth[flask]==0.11.0  #if you want flask modules
pip3 install tsgauth[fastapi]==0.11.0 #if you want fastapi modules
```

Version policy: The major version number will be incremented for any breaking changes. The minor version number will be incremented for any new features. The patch version number will be incremented for any bug fixes. The package is currently in development and will be so till it hits version 1.0.0, until then these rules will be a bit looser.

It is intended that users use keyword arguments when passing into the function as the order of the arguements may change in minor versions with the exception of client_id which is always first. Only public methods and members (ie do not start with _) are considered part of the API and thus subject to the version policy. Changes to the internals will not be considered breaking changes but will be considered enough to bump the minor version number.

Support requests can be raised on the [gitlab issue tracker](https://gitlab.cern.ch/cms-tsg-fog/tsgauth/-/issues) or by contacting Sam Harper on mattermost (prefered)

## Security Warning

To use this package securely there are two things you need to do:

1. if you use the option to persist sessions ensure that the resulting authentication files stored in ~/.tsgauth are not compromised. Whoever has these files has the privileges they represent. They are created to be only read/writable by the user but if you copy them about, you need to ensure they are protected. **this option is set by default for tokens** 
1. if you use pip, **always specify a version**, ie `pip3 install tsgauth==0.11.0` not `pip3 install tsgauth` to prevent a [supply chain attack](https://en.wikipedia.org/wiki/Supply_chain_attack). This is a good idea for packages in general but is critical here. Otherwise you are trusting that a malicious actor has not compromised my pypi account and uploaded a malicious version of the package which could either intercept OTPs or send the resulting authentication files to a remote server. It would not be possible for them to access your password, just the auth session cookie/ access token. Note, it is not possible for anybody to upload new code as an existing version to pypi, ie `pip3 install tsgauth==0.11.0` will always install the same code.


## Quick start

### How to Access SSO CERN sites in python using TSGAuth

This is a minimal explaination for the impatient who just want to access a SSO protected website using python. For a more detailed explaination, please see the rest of this guide. TSGAuth is designed assuming you are using the `requests` module but exposes methods which will work with any module which can make http requests assuming you can pass cookies and headers to it.


There are different ways to access SSO protected sites on the cmdline, there are a series of classes in tsgauth.oidcauth for various types of authorsization and authentication mechanisms. They are all designed such that

```python
auth = tsgauth.oidcauth.<AUTHCLASS>()
r = requests.get(url,**auth.authparams()) #note depending on the auth class, it may override your headers, thus you need to 
                                          #pass in any headers you want in the authparams call, eg
                                          #**auth.authparams(headers={"Accept":"application/json"})
```
will work for all of them.

The only thing the user needs to do is select the correct class. To do this you need to know if the website (aka protected resource) you which to access is using session/cookie or token based authorisation. 

If its cookie based, you will need to use a SessionAuth derived class of which the only one is `tsgauth.oidcauth.KerbSessionAuth()` which uses kerberos to authenticate. If it is token based, you need a TokenAuth class, of which there are three, `tsgauth.oidcauth.KerbAuth()`, `tsgauth.oidcauth.ClientAuth()` and `tsgauth.oidcauth.DeviceAuth()` depending on how you wish to authenticate.  You will also need to know the client id of the application you wish to access as well as its redirect_uri. If it is a confidential client, you will also need the client secret. 

Most users will want `tsgauth.oidcauth.KerbAuth()` which uses kerberos to authenticate. Unlike the CERN sso-get-cookie and sso-get-token, tsgauth supports accounts with 2FA enabled (the author of this package has 2FA enabled...)

examples using kerberos 

```python
auth = tsgauth.oidcauth.KerbAuth("cms-tsg-frontend-client")
r = requests.get("https://hltsupervisor.app.cern.ch/api/v0/thresholds",**auth.authparams())
```

```python
auth = tsgauth.oidcauth.KerbSessionAuth()
r = requests.get("https://twiki.cern.ch/twiki/bin/view/CMS/TriggerStudies?raw=text",**auth.authparams())
```

As a final heads up, the AuthClasses can persist cookies and tokens to disk so you dont need to reauthenticate every time. This is true by default for KerbSessionAuth, DeviceAuth classes. The directory should only be readable by the user and is `~/.tsgauth` by default but you can override it by setting the `TSGAUTH_AUTHDIR` environmental variable.  **These files should be protected as they grant access as you to the given application.** Note, it is not an error for the application to fail to read/write to this directory, it will continue as is but log a warning. The logging level is controled by the `TSGAUTH_LOGLEVEL` environmental variable and defaults to `ERROR`. The writing of the authentication files is controled by the parameter `use_auth_file` passed in the constructor of the auth class. For convenience you can also force enabling / disabling of this feature globally by setting the environmental variables `TSGAUTH_FORCE_USE_AUTHFILE` / `TSGAUTH_FORCE_DONT_USE_AUTHFILE` to 1. 

A summary of the enviromental variables is as follows:
 * TSGAUTH_LOGLEVEL : logging level ("NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
 * TSGAUTH_AUTHDIR : directory where the auth files are written if requested to be (default: ~/.tsgauth)) 
 * TSGAUTH_FORCE_USE_AUTHFILE : forces the authfile to be written/used (set to 1 to do this)
 * TSGAUTH_FORCE_DONT_USE_AUTHFILE : forces the authfile to not be written/used  (set to 1 do this)
 * TSGAUTH_ALLOWED_ALGS : the allowed algorithms for the token, unset defaults to RS256 (will be updated if CERN SSO changes), can be set to "ALL" to allow all algorithms or a comma separated list of allowed algorithms (the default avoids the risk of signature bypass described in CVE-2016-10555 which 'ALL' would be vulnerable to). Really only important for servers securing resources.

#### Determing if a resource expects Session or Cookie based authorisation

The easiest way to find out how to service expects you to authenticate is ask the owner or review their documenation. As this is not always possible, you can open it up in a webbrowser and see how the browser is making requests. 

If you see the the requests to the protected api  have a header {"Authorization", "Bearer <long string>}" it is token based. You should also see the browser requesting said token, with something like:

```
https://auth.cern.ch/auth/realms/cern/protocol/openid-connect/auth?client_id=cms-tsg-frontend-client&redirect_uri=https%3A%2F%2Fhltsupervisor.app.cern.ch%2F&state=8dbacbe6-e06e-4fb9-8699-eb87c136195a&response_mode=fragment&response_type=code&scope=openid&nonce=3d5ff976-fd51-43aa-8b0d-3a72c2782b20
```
this gives your client_id (cms-tsg-frontend-client) and a valid redirect_uri (https://hltsupervisor.app.cern.ch/) which you can use to request a token.

If you dont see anything like this, its session based (you'll probably see a cookie auth session or similar). Session Cookie auth is mainly done public services using confidential clients. The client (say an apache server which is interacting with the resource server on your behalf) handles the token exchange and the user never sees the token. It will instead issue you a cookie so identify you for the authentication session. 

### Securing APIs with TSGAuth

Currently we support FastAPI and Flask. If you have a choice, we would recommend you using FastAPI as it is a more modern framework. The FastAPI implimention has more features and is less error prone and is the primary development focus. However we still intend to support Flask for the forseeable future.

Examples of FastAPI and Flask implimentations can be found in the examples directory.

### Securing FastAPI sites

If you wish to secure an endpoint on your fast api system, you just need to make your endpoint depend on tsgauth.fastapi.JWTBearerClaims. This will validate the user claims (unless validate_token=False) and make them available to your endpoint. 

```python
from tsgauth.fastapi import JWTBearerClaims
@app.get("/api/v0/secure")
def secure_endpoint(claims = Depends(JWTBearerClaims())):
   return {"claims" : claims}
```
This will validate the user claims with an audience of the client id specified in the OIDC_CLIENT_ID environmental varaible and make the claims available to your endpoint. If you have no further need of the the claims info, you can put the depends in the decorator. 

However a better way to ensure you do not forget to add the claims dependency to secure an endpoint is to add it to the app as a global dependency. This will ensure that all endpoints are protected by default. Even better would be to add it to a router which you then include in your app so you can choose which endpoints are protected. In our opinion, best practice is to have all your secure endpoints in a router in a seperate file (s) which you then include in your app. This way you can not forget to add the dependency to your secure endpoints. When doing this rather than accessing the claims directly, you access them via the `request.state` object. 

An example

```python
#all routes declared on this router will be protected by default
#they will also have the tag "secure" for convenience
secure_route = APIRouter(dependencies=[Depends(JWTBearerClaims())],tags=["secure"])
@secure_route.get("/api/v0/secure")
def secure_endpoint(request: Request):
    return {"claims" : request.state.claims}
#adds the router to the file
app.include_router(secure_route)
```


You can see an example of this in the examples/fastapi_server.py file which is run as part of the unit tests

#### Session Auth

In the base setup, the fast api server relies on a client to pass in the token. However this is awkward when you 
wish the user to directly access the api endpoint in the browser. In this case, you can set the OIDC_SESSION_AUTH_ALLOWED environmental variable to True. This will cause the server to request a token on behalf of the client if one is not passed in and start an internal authentication session. 

Beyond setting ODIC_SESSION_AUTH_ALLOWED to True, you will also need add the following to your fastapi configuration

```python
import tsgauth.fastapi
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=your_secret_key, same_site="lax", https_only=True)
tsgauth.fastapi.setup_app(app)
```

Remember the secret key should be a long random string that is not shared with anybody. This is used to sign the session data and if anybody has this key, they can fake the session data and bypass the authentication.

This sets a session cookie to handle the auth session for the application. It then request a token from the CERN SSO and store in the auth information received. By default, it stores it in memory but it is possible to write your own auth session manager to store it how you wish.

Environmental variables for default Session Auth
* OIDC_SESSION_AUTH_ALLOWED : if set to True, the server will request a token on behalf of the client if one is not passed in. Defaults to False 
  * this is how you enable session auth, by default it is not enabled
* OIDC_SESSION_LIFETIME : the lifetime of the session claims in seconds (default 28800 seconds, 8 hours)
  * if you set this longer than 12 hours, this will start to request an offline token. The idle time of an offline token is currently 30 days but can be renewed indefinately. 
* OIDC_SESSION_STORE_TYPE: can be "memory" or "redis" (default "memory")
  * the type of store to use for the session data. We recommend redis for production as this will perist the session data across server restarts and also across multiple instances of the server
* OIDC_SESSION_STORE_HOST: the address of the redis server (default "localhost")
* OIDC_SESSION_STORE_PORT: the port of the redis server (default 6379)


#### Custom SessionAuth store

Currently the session auth is handled by SessionAuthMemoryStore which is a simple memory based store. A user is assigned a unique session id which is saved in the session cookie and used to look up the auth information in the store. 

Alterative stores are supported and can be implimented by creating a class which inherits from SessionAuthBase and impliments the following methods:

  * claims : returns the claims the user has. If it wishes to trigger an token request, it must raise a MissingAuthException which will start the process to request a token from the SSO
  * store  : stores the claims for the user, raises SessionAuthBase.AuthResponseException if the store fails. Additionally if
  it wants an offline token but the current token is not one, it should raise a SessionAuthBase.TokenNoOfflineException
  * clear  : clears all auth data from the store and cookie but does not log the user out of the SSO. A parameter "deep" is passed defaulting to False, what deep means is up to the implimentation. In the reference, its used to clear offline tokens
  * token_request_allowed : returns True if the application is allowed to request a token, False otherwise. This is mainly used to stop infinite loops of the application requesting a token from the SSO and the SSO redirecting the application to request a token from the SSO.
  * auth_attempt : registers that an auth attempt is occuring

In the SessionAuthMemoryStore, it uses a counter to determine how many auth attempts have happened for the request and stops it after 5 to stop infinite loops. auth_attempt is used to increment this counter.

Note nothing says your SessionAuth class actually requires a session cookie, you have complete freedom to impliment it how you wish. Nor does it have to request a token, you can even just always return the same claims if you wish which could be useful for testing.

In examples/fastapi_server.py there is an example of such a custom store.

To use your custom store, you need to override the dependency `get_auth_store` in the fastapi module. 
```python
# Register a custom auth_store
def custom_auth_store() -> tsgauth.fastapi.SessionAuthBase:
    return CustomSessionAuth()

app.dependency_overrides[tsgauth.fastapi.get_auth_store] = custom_auth_store
```


#### Configuration 

The auth settings are configured from environmental variables. The following are avalible:

   * OIDC_CLIENT_ID : the client id of the application you wish to access (required)
   * OIDC_CLIENT_SECRET: the client secret of the application you wish to access (only required for confidential clients, not set for public clients and only makes sense if ODIC_SESSION_AUTH_ALLOWED is set to True)
   * OIDC_SESSION_AUTH_ALLOWED : if set to True, if the token is not passed to a token requiring endpoint, the application will self request a token and mangages it itself.  Defaults to `False` when means a token will always have to be passed into a token requiring endpoint by the calling client. **Important If you set this to True, YOU MUST SET the secret key (SECRET_KEY) to a random long secure string that is not shared with anybody.** This is used to sign the session token / token info in the session data and if anybody has this key, they can fake this data and essentially bypass the authentication. 
   * ODIC_SESSION_LIFETIME : how long an auth session lasts in seconds
   * ODIC_SESSION_STORE_TYPE : the type of store to use for the session data. We recommend `redis` for production as this will perist the session data across server restarts and also across multiple instances of the server. Defaults to `memory`
   * ODIC_SESSION_STORE_HOST : the address of the redis server. Defaults to `localhost`
   * ODIC_SESSION_STORE_PORT : the port of the redis server. Defaults to `6379`

the following are variables depend on the OIDC provider you are using. The defaults are set up for the CERN SSO so for users of the CERN SSO (most if not all of our users) you do not need to set these. They are
   * OIDC_ISSUER : the OIDC issuer, defaults to "https://auth.cern.ch/auth/realms/cern"
   * OIDC_JWKS_URI : the OIDC JWKS URI, defaults to "https://auth.cern.ch/auth/realms/cern/protocol/openid-connect/certs"
   * OIDC_AUTH_URI : the OIDC auth URI, defaults to "https://auth.cern.ch/auth/realms/cern/protocol/openid-connect/auth"
   * OIDC_LOGOUT_URI : the OIDC logout URI, defaults to "https://auth.cern.ch/auth/realms/cern/protocol/openid-connect/logout"
   * OIDC_TOKEN_URI : the OIDC token URI, defaults to "https://auth.cern.ch/auth/realms/cern/protocol/openid-connect/token"
   
#### JWTBearerClaims options

The JWTBearerClaims class has the following options:
   * validate_token : if set to False, the token will not be validated. This is useful for testing. Obviously should be True if you want any security at all. Defaults to True.
   * use_state: if true, it also adds the claims to request.state. Useful for using it as a global dependency. Defaults to True
   * auto_error : you probably dont need to touch this but for completeness this is a pass through to the base BearerAuth class, if true it will raise an exception if the token is not present. However it is best to have this false as the exception returns a 403 code not a 401. If false JWTBearerClaims will raise an exception which will return a 401 code. Defaults to False. 

### Securing Flask sites

In python this was modeled after the flask-oidc package which is completely not recommended but when we started we ended up using due to very inadequate documenation. It requires the following variable to be set in your flask configuration

```python
app.config.update({
   'OIDC_CLIENT_ID' : <your client id>   
}) 
```

The application also allows you set the following parameters to configure it based on which OIDC server you are using. By default it is set up for the CERN SSO so for users of the CERN SSO (most if not all of our users) you do not need to set these. The defaults are:
```python
app.config.update({
   'OIDC_ISSUER' : "https://auth.cern.ch/auth/realms/cern",
   'OIDC_JWKS_URI' : "https://auth.cern.ch/auth/realms/cern/protocol/openid-connect/certs",
   'OIDC_AUTH_URI' : "https://auth.cern.ch/auth/realms/cern/protocol/openid-connect/auth",
   'OIDC_LOGOUT_URI' : "https://auth.cern.ch/auth/realms/cern/protocol/openid-connect/logout",
   'OIDC_TOKEN_URI' : "https://auth.cern.ch/auth/realms/cern/protocol/openid-connect/token",
})
```
If you use a different OIDC provider, you will need to set these to the correct values appropriate for your provider.


The following parameters are optional:
`OIDC_SESSION_AUTH_ALLOWED` : if set to True, if the token is not passed to a token requiring endpoint application will self request a token and pass it back to the client if public token or token_info if its a private token.  Defaults to `False` when means a token will always have to be passed into a token requiring endpoint by the calling client. **Important If you set this to True, YOU MUST SET the flask secret key (SECRET_KEY) to a random long secure string that is not shared with anybody.** 

`OIDC_CLIENT_SECRET`: required if the token is a private token and thus requires a secret to obtain. This is only needed if OIDC_SESSION_AUTH_ALLOWED is set to True. There is no default value.

`OIDC_SESSION_LIFETIME`: this is the max time in seconds that an auth session is valid. Defaults to 28800 seconds (8 hours). This only applies to private tokens, public tokens will be send to client and the expiry is managed in the normal way. OIDC_SESSION_AUTH_ALLOWED must be set to True for this to have any effect. Note the flask implimentation does not yet support offline tokens and thus the max possible lifetime is 12 hours which in practise will be shorter as it will expire when your CERN SSO session ends. Currently there are no plans to support longer sessions in flask but we can discuss if needed. The FastAPI implimentation does support offline tokens and thus can have a longer session lifetime and you may wish to consider using that instead. If OIDC_SESSION_MANAGE_COOKIE and OIDC_SESSION_COOKIE_PERMANENT are both set to True, this will also be the lifetime of the session cookie.

`OIDC_SESSION_STORE_TYPE`: the type of store to use for the session data. We recommend `redis` for production as this will perist the session data across server restarts and also across multiple instances of the server. Defaults to `simplemem`

`OIDC_SESSION_STORE_HOST`: the address of the redis server. Defaults to `service/redis`. Only used if using redis as the store.

`OIDC_SESSION_STORE_PORT`: the port of the redis server. Defaults to `6379`. Only used if using redis as the store.

`OIDC_SESSION_MANAGE_COOKIE` : where the tsgauth package manages the session cookie, setting the samesign, the lifetime etc.  Defaults to True. If False, you manage it yourself according to the normall flask way of doing it.

`OIDC_SESSION_COOKIE_SAMESITE` : sets tthe same site of the session cookie. Defaults to "Lax". Overrides SESSION_COOKIE_SAMESITE if OIDC_SESSION_MANAGE_COOKIE is True otherwise has no effect.

`OIDC_SESSION_COOKIE_PERMANENT`: sets the session cookie to permanent. Defaults to True. Only has an effect if OIDC_SESSION_MANAGE_COOKIE is True.

These other parameters are standard flask parmeters which are used to control the session cookie are `SESSION_COOKIE_HTTPONLY` and `SESSION_COOKIE_SECURE` even if OIDC_SESSION_MANAGE_COOKIE is set to True as it does not override them.




Then package can then be used as follows

```python
import tsgauth.flaskoidc as oidc
@application.route('/api/v0/secure', methods=['GET'])
@oidc.accept_token(require_token=True)
def secure_endpoint():
      return jsonify({"claims" : g.oidc_token_info})
```

You can see an example of this in the tests/test_flaskoidc.py file which is run as part of the unit tests

### Using the Token

In the above examples you get the a dictionary with the claims of the token. The two most common use cases are to uniquely identify the user and the roles they have in the application (ie who they are and what they can do). These are in the `sub` and `cern_roles` claims respectively.
  * sub : the subject of the token, ie the user id. This is the unique identifier of the user and typically the cern username but in the case of applications it is `service-account-<applicationname>`, eg for me it is sharper, but if I use the client id and secret of cms-tsg-client to log in it will be `service-account-cms-tsg-client`. 
  * cern_roles:  the roles the user has for this application (ie for the client_id of the token). See below for defining roles. Note this is a duplication of `["resource_access"]["<client_id>"]["roles"]` field. Given you have already validated that this token is for the client_id your application expects, its easier to just access "cern_roles" unless for some reason you are not using the CERN SSO provider

If you wish to know more about the user, you have the following additional claims. None of these are defined for applications (ie login with a client id/secret), only for users, so your application should be able to handle the case where they are not present unless you wish to restrict access to only users and not applications. 
  * name: the users full name
  * given_name: the users given name
  * family_name: the users family name
  * preferred_username: the users preferred username
  * email: the users email address
  * cern_mail_upn: the users cern email identifier
  * cern_upn : the users cern username, the same as sub 
  * cern_email : the users email address
  * cern_person_id : the users cern id number
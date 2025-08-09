from fastapi import HTTPException, Request, FastAPI, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from tsgauth.fastapi.settings import settings
from tsgauth.fastapi.authstores import SessionAuthBase, get_auth_store
from tsgauth.fastapi.exceptions import MissingAuthException
from tsgauth.fastapi.routes import router
from tsgauth.fastapi.tokenutil import get_validated_claims

"""
package to add authentication to a fastapi server

the file structure is internal to the package and can change without warning, 

please alway import from tsgauth.fastapi rather than tsgauth.fastapi.<submodule> as the internal structure may change
eg tsgauth.fastapi.SessionAuthBase rather than tsgauth.fastapi.authstores.SessionAuthBase

The only user things a user should need are 

   JWTBearerClaims
   setup_app
   setup_app_wo_session_middleware (if you want to use your own session middleware, use instead of setup_app)

and optionally SessionAuthBase if they want to override the default auth store

Everything else is internal to the package and can change without warning. If you do need to use something other than those three items please let me know so we can ensure we find a solution where
updates do not break your code

author Sam Harper (STFC-RAL, 2022)


"""


class JWTBearerClaims(HTTPBearer):
    def __init__(self, validate_token :bool = True, require_aud : bool = True, auto_error: bool = False ,use_state: bool = True):
        """
        gets the decoded claims from the request header

        :param validate_token: whether or not to validate the token, if false it'll just return the claims
        :param require_aud: if True, the client id must be set to validate the audience if validate_token is also True
                            no effect if validate_token is False
        :auto_error: this is for the base class BearerAuth, if true it'll raise an exception if the token is not present
                     I would use this but it returns a 403 code rather than a 401 in this case which is incorrect :(
        :use_state: if true, the claims will be stored in the request.state.claims
        """                
        super(JWTBearerClaims, self).__init__(auto_error=auto_error)
        self.validate_token = validate_token
        self.require_aud = require_aud
        self.use_state = use_state

    async def __call__(self, request: Request, auth_store: SessionAuthBase = Depends(get_auth_store)):           
        credentials: HTTPAuthorizationCredentials = await super(JWTBearerClaims, self).__call__(request)   
        claims = None        
        if credentials:
            if not credentials.scheme == "Bearer":
                #do we want to redirect for this?
                raise HTTPException(status_code=401, detail="Invalid authentication scheme.")
            claims = get_validated_claims(credentials.credentials, self.validate_token, self.require_aud)            
            
        elif await auth_store.token_request_allowed(request): 
            claims =  await auth_store.claims(request)  

        if claims is not None:               
            if self.use_state:
                request.state.claims = claims   
            return claims
        else:                        
            raise HTTPException(status_code=401, detail="No authentication credentials provided.")

    

def add_auth_exception_handler(app: FastAPI) -> None:
    @app.exception_handler(MissingAuthException)
    async def auth_exception_handler(request: Request, exc: MissingAuthException) -> RedirectResponse:
        extra_scopes = "&extra_scopes=offline_access" if exc.request_offline else ""
        redirect_uri = exc.redirect_uri if exc.redirect_uri is not None else request.url
        return RedirectResponse(f"{request.url_for('get_token_from_auth_server')}?redirect_uri={redirect_uri}{extra_scopes}")

def setup_app_wo_session_middleware(app: FastAPI) -> None:
    app.include_router(router)
    add_auth_exception_handler(app)

def setup_app(app: FastAPI,secret_key) -> None:
    app.add_middleware(SessionMiddleware, secret_key=secret_key, same_site="lax", max_age=settings.oidc_session_lifetime)
    setup_app_wo_session_middleware(app)
    
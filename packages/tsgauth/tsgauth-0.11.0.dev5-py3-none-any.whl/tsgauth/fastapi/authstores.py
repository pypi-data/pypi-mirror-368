from tsgauth.fastapi.tokenutil import _parse_token_fastapi
from tsgauth.fastapi.exceptions import MissingAuthException
from tsgauth.fastapi.settings import settings
from aiocache import Cache
from typing import Optional, Dict, Any
from fastapi import HTTPException, Request, APIRouter, FastAPI, Depends
import time
import uuid
import requests
import authlib
import abc



class SessionAuthBase(abc.ABC):
    """
    Base class for the session auth store

    Aims to handle user authentication when session based. So if a token is not passed in to the request,
    it will managed getting the claim the application wishes for the user.

    This is usually involves obtaining a token from the SSO server with session based on a session cookie but doesnt have to be

    Due to how its used, multiple instances of this class may be created per request so the state should be only set in the __init__ func
    
    Design notes:
    There was some debate about whether to have the methods as classmethods or instance methods given the limited ability for this
    class to have a state. Eventually instance methods were chosen as those can be overriden as classmethods safely but not the
    other way around. This also allows for a subclass to have a state set in the __init__ method if needed

    """
    class AuthResponseException(Exception):
        """
        when storing the auth info, raise this is the response from the auth server is invalid
        """
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

    class TokenNotOfflineException(Exception):
        """
        raise when you want an offline token but provided token is not offline
        """
        pass
    
    @abc.abstractmethod
    async def claims(self,request: Request) -> Dict[str, Any]:
        """
        gets the claims
        :param request: the request object
        :returns: the claims in a dictionary
        :raises: MissingAuthException if the token is missing or invalid
        """
        pass
    
    @abc.abstractmethod
    async def store(self,request: Request, auth_response_data : Dict[str, Any]) -> None:
        """
        stores the auth data in the session and any associated caches
        :param request: the request object
        :param auth_response_data: the response data from the auth server containing the auth info
        :raises: AuthResponseException if the response is invalid (ie doesnt contain a token or has an invalid token)
        :raises: TokenNotOfflineException if an offline token is required but the token provided is not offline
        """
        pass
    
    @abc.abstractmethod
    async def clear(self,request: Request,deep: bool = False) -> None:
        """
        clears any auth data from the session and associated caches
        :param request: the request object
        :param deep: if True does a deep clear, with what deep means up to the implimentation
        """
        pass

    async def token_request_allowed(self,request : Request) -> bool:
        """
        checks if the token request is allowed
        for example the classes may have an internal counter to limit the number of requests to stop an infinite loop of
        requests to the auth server

        :returns: True if allowed, False if not
        """       
        return settings.oidc_session_auth_allowed

    async def auth_attempt(self,request: Request) -> None:
        """
        registers an auth attempt, throwing a HTTPException if not allowed ideally with the reason
        """
        pass

class SessionAuthTokenStore(SessionAuthBase):
    """
    this stores the tokens in a cache and allows them to be used
    it has the ability to request an offline token if the session lifetime is over 12hrs (CERN SSO session length)
    it will only request a single offline token per user, multiple sessions of the user will share the same offline access token
    
    note the design that it only requests a single offline toke per user is the reason its a little complicated
    would have been simplier to just request one per session

    There are two places where the auth infomation is stored

    - the session cookie in the frontend (SessionAuthData)
        - this is mostly the session_id 
    - the backend cache (BackendAuthData)
        - this is the tokens and related info
    typically session_data is the info stored in the session cookie and 
    auth_data is the info stored in the backend cache
        
    """


    if settings.oidc_session_store_type == "memory":
        cache = Cache(Cache.MEMORY)        
    else:
        cache = Cache(Cache.REDIS,endpoint=settings.oidc_session_store_host,port=settings.oidc_session_store_port)
    min_access_token_lifetime = 30  # 30 seconds    
    min_time_to_request_offline = 12*60*60+1  # 12 hours and 1 second

    class SessionAuthData:
        """
        this defines the data stored in the session cookie in the frontend
        """
        def __init__(self, session_id : Optional[str] = None, auth_try_count : int = 0, **kwargs):
            self.session_id = session_id
            self.auth_try_count = auth_try_count
        def to_dict(self) -> Dict[str, Any]:
            return {"session_id": self.session_id, "auth_try_count": self.auth_try_count}
        def from_dict(self, data : Dict[str, Any]):
            self.session_id = data.get("session_id",None)
            self.auth_try_count = data.get("auth_try_count",0)

    class BackendAuthData:
        """
        this defines the stored in the backends auth cache (eg tokens and similar things)

        it defines
        - refresh_token: the refresh token used to get a new access token
        - access_token: the access token used to authenticate the user
        - key: the key used to validate the token
        - is_offline: whether the refresh token is an offline token
        - access_exp: the expiry time of the access token
        - sub: the subject of the token

        the access_exp and sub are simply stored for convenience to make it easier to know when the token has expired
        and who the token is for

        """
        def __init__(self, access_token : str, refresh_token : Optional[str],                      
                     key : Dict[str, Any],
                     is_offline : bool = False,
                     access_exp : Optional[int] = None, sub : Optional[str] = None
                     ):        
            """
            access_exp and sub can be obtained from access token if not provided
            however if they are provided, they will be used
            """    
            self.refresh_token = refresh_token
            self.is_offline = is_offline
            self.key = key #key to validate the token
            self.access_token = access_token
            if access_exp is None or sub is None:
                self._set_claims()
            if access_exp is not None:
                self.access_exp = access_exp
            if sub is not None:
                self.sub = sub
            
        def set_access_token(self,access_token,key=None):
            self.access_token = access_token
            self.key = key
            self._set_claims()
            
        def to_dict(self) -> Dict[str, Any]:
            return {"refresh_token": self.refresh_token, 
                    "is_offline" : self.is_offline,
                    "access_token": self.access_token, 
                    "key": self.key, 
                    "access_exp": self.access_exp, 
                    "sub": self.sub
                    }
        def _set_claims(self):
            claims = _parse_token_fastapi(self.access_token, key = self.key)
            self.access_exp = claims["exp"]
            self.sub = claims["sub"]
    
    """
    public methods overriden from the base class
    """
    @classmethod
    async def claims(cls,request: Request) -> Dict[str, Any]:
        auth_session_data = cls._get_session_data(request)
        
        if auth_session_data.session_id is None:
            auth_session_data.session_id = str(uuid.uuid4())
            cls._set_session_data(request, auth_session_data)
        if await cls.cache.exists(auth_session_data.session_id):
            #will raise MissingAuthExcepion if it fails
            token_data = await cls._cache_get(auth_session_data.session_id)            
            if token_data.access_exp - time.time() < cls.min_access_token_lifetime:
                #will raise MissingAuthExcepion if it fails
                await cls._renew_token(request)
                token_data = await cls._cache_get(auth_session_data.session_id)  
            try:          
                return _parse_token_fastapi(token_data.access_token,key = token_data.key)
            except authlib.jose.errors.InvalidClaimError as e:
                if e.claim_name=="aud":
                    raise MissingAuthException(status_code=401, detail="Invalid token audience")
            except Exception as e:
                raise MissingAuthException(status_code=401, detail="Invalid or expired token")
            
        raise MissingAuthException(status_code=401, detail="No authentication credentials provided.")
    
    @classmethod
    async def store(cls,request: Request, auth_response : Dict[str, Any]) -> None:
        try:
            access_token = auth_response["access_token"]
        except KeyError:
            raise cls.AuthResponseException("No access token in response")
        
        refresh_token = auth_response.get("refresh_token")
        is_offline_token = auth_response.get("refresh_expires_in") == 0
           

        try:
            #TODO: hmm key set over just key?
            key = requests.get(settings.oidc_jwks_uri).json()["keys"][0]
        except Exception as e:
            raise cls.AuthResponseException("Could not get key from jwks_uri")
        
        try:
            #really just to check the token is valid
            _parse_token_fastapi(access_token,key = key)
        except Exception as e:
            raise cls.AuthResponseException("Invalid or expired token in response") 
        
        session_data = cls._get_session_data(request)
        auth_data = cls.BackendAuthData(access_token,refresh_token,key,is_offline=is_offline_token)
        #raises a TokenNotOfflineException if we need to store an offline token 
        #but the token provided is not offline
        await cls._cache_set(session_data.session_id, auth_data, ttl=settings.oidc_session_lifetime)
        
        session_data.auth_try_count = 0
        cls._set_session_data(request, session_data)

    @classmethod
    async def token_request_allowed(cls,request: Request) -> bool:
        return  settings.oidc_session_auth_allowed and cls._get_session_data(request).auth_try_count < 5
    
    @classmethod
    async def auth_attempt(cls,request: Request) -> None:
        session_data = cls._get_session_data(request)
        session_data.auth_try_count += 1        
        cls._set_session_data(request, session_data)
        if not await cls.token_request_allowed(request):
            await cls.clear(request)
            raise HTTPException(status_code=401, detail="Too many token reqeusts")

    @classmethod
    async def clear(cls,request: Request, deep = False) -> None:        
        session_data = cls._get_session_data(request)
        if session_data.session_id:
            if deep: #delete the offline token if it exists
                sub = await cls._cache_get_sub(session_data.session_id)
                if sub is not None:
                    await cls.cache.delete(cls._offline_token_key(sub)) 
            await cls.cache.delete(session_data.session_id)            
        cls._del_session_data(request)
        
    """
    private methods for the implimentation
    """
    @classmethod
    def _get_session_data(cls,request:Request) -> SessionAuthData:
        if not hasattr(request, "session"):
            raise HTTPException(status_code=500, detail="Session middleware not configured correctly")
        return cls.SessionAuthData(**request.session.get("auth_data", {}))
    
    @classmethod
    def _set_session_data(cls,request:Request, session_data : SessionAuthData) -> None:
        if not hasattr(request, "session"):
            raise HTTPException(status_code=500, detail="Session middleware not configured correctly")
        request.session["auth_data"] = session_data.to_dict()

    @classmethod
    def _del_session_data(cls,request:Request) -> None:
        """
        deletes the session auth data (ie the stuff in the cookie)
        """
        if not hasattr(request, "session"):
            raise HTTPException(status_code=500, detail="Session middleware not configured correctly")
        if "auth_data" in request.session:
            del request.session["auth_data"]    

    @classmethod
    async def _renew_token(cls,request:Request) -> BackendAuthData:
        """
        renews the token, storing the new token in the cache
        :param request: the request object
        :returns: the new token data
        :raises: MissingAuthException if the token is missing or somehow it fails
        """
        auth_session_data = cls._get_session_data(request)
        token_data = await cls._cache_get(auth_session_data.session_id)
        
        refresh_token = token_data.refresh_token
        if refresh_token is None:
            raise MissingAuthException(status_code=401, detail="Token refresh required but no refresh token available")
        
        try:
            token_response = requests.post(settings.oidc_token_uri, data={"grant_type" : "refresh_token",
                                                                         "refresh_token" : refresh_token,
                                                                         "client_id" : settings.oidc_client_id})
            
            #TODO: remove debug            
            token_response.raise_for_status()
            token_data = token_response.json()            
            await cls.store(request,token_data)
        except Exception as e:            
            #if its an offline token, its no longer working and we need to destroy it
            if token_data.is_offline:
                await cls.cache.delete(cls._offline_token_key(token_data.sub))
            raise MissingAuthException(status_code=401,detail="Token renewal failed")
        
        return token_data
    
    @classmethod
    def _request_offline(cls) -> bool:
        """
        checks if an offline token should be requested

        :returns: True if an offline token should be requested
        """

        return settings.oidc_session_lifetime >= cls.min_time_to_request_offline
    
    @classmethod
    async def _cache_set(cls,id : str,payload: BackendAuthData,ttl :int):
        """
        passthrough to help with storing the data in the cache
        :param id: the session id
        :param payload: the BackendAuthData object
        :param ttl: the time to live of the cache
        :raises: TokenNotOfflineException if the token is not offline and an offline one was requested
        """
        if not cls._request_offline():
            await cls.cache.set(id, payload.to_dict(), ttl=ttl)
        else:
            await cls.cache.set(id,{"sub": payload.sub, "is_offline": True}, ttl=ttl)
            if payload.is_offline:
                await cls.cache.set(cls._offline_token_key(payload.sub),payload.to_dict(),ttl=ttl)
            elif await cls._get_offline_token(payload.sub) is None:                
                raise cls.TokenNotOfflineException()
                

    @classmethod
    async def _cache_get(cls,id : str) -> BackendAuthData:
        """
        passthrough to help with getting the data from the cache
        :param id: the session id
        :returns: the BackendAuthData object
        :raises: MissingAuthException if the the auth data is missing or its not an offline token and one was requested
        """
        raw_data = await cls.cache.get(id)
        if raw_data is None:
            raise MissingAuthException(status_code=401, detail="No token stored for auth session")                
        if not raw_data["is_offline"]:
            return cls.BackendAuthData(**raw_data)       
        else:
            offline_token = await cls._get_offline_token(raw_data["sub"])
            if offline_token is not None:
                return cls.BackendAuthData(**offline_token)
            else:
                raise MissingAuthException(status_code=401, detail="No offline token stored for auth session")                
        
    @classmethod
    async def _cache_get_sub(cls,id: str) -> Optional[str]:
        """
        gets the sub of user from the session id
        :returns: the sub of the user, None if the session id is not found
        """
        raw_data = await cls.cache.get(id)
        if raw_data is None:
            return None
        else:
            return raw_data["sub"]  

    @classmethod
    async def _get_offline_token(cls,sub : str):
        """
        gets the offline token for a given subject
        :param sub: the subject of the token
        :returns: the offline token, None if not found

        """
        return await cls.cache.get(cls._offline_token_key(sub))
    
    @classmethod
    def _offline_token_key(cls,sub : str):
        """
        gets the db key for the offline token
        :param sub: the subject of the token
        :returns: the key
        """
        return sub+"::"+settings.oidc_client_id
    
def get_auth_store() -> SessionAuthBase:
    return SessionAuthTokenStore
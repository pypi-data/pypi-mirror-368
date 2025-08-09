from fastapi import FastAPI, Depends, Request, APIRouter
import tsgauth.fastapi
from tsgauth.fastapi import JWTBearerClaims
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

client_id = tsgauth.fastapi.settings.oidc_client_id

"""
to run you must set a OIDC_CLIENT_ID environment variable to the client id you wish to use
you can do this by 

export OIDC_CLIENT_ID=<your  client id> 
fastapi dev examples/fastapi_server.py

or 
ODIC_CLIENT_ID=<your client id> fastapi dev examples/fastapi_server.py

To allow session auth you must also the same for OIDC_ALLOW_TOKEN_REQUEST and set it to True

"""

description = f"""

To access the secure endpoints, you need to either have a token with the audience of {client_id}
or have a valid CERN SSO session active. 

An example of how to do this with tsgauth using python is below. Please adjust http://localhost:5000 to the correct URL
for the instance you wish to use

```python

import tsgauth.oidcauth
import requests

auth = tsgauth.oidcauth.DeviceAuth("{client_id}")
r = requests.get("http://localhost:5000/api/v0/secure",**auth.authparams())

"""


app = FastAPI(title="TSG Auth Test Server",description=description)

#if you want to use a js client with it, you need to add to allow the origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
tsgauth.fastapi.setup_app(app,secret_key="some-random-string-please-change-this")

print("using client id",tsgauth.fastapi.settings.oidc_client_id)
@app.get("/")
async def root():
    return {"message": "Hello World"}

#we recommend you use the JWTBearerClaims as a global dependency on a router in a seperate file
#for all your secure endpoints as this means its impossible to forget to add it to a
#new endpoint
secure_route = APIRouter(dependencies=[Depends(JWTBearerClaims())],tags=["secure"])
@secure_route.get("/api/v0/secure")
def secure_endpoint(request: Request):
    return {"claims" : request.state.claims}


@app.get("/api/v0/unsecure")
def unsecure_endpoint(request: Request):
   return {"msg" : "unsecure endpoint"}

@secure_route.get("/api/v0/setvalue")
def setvalue(request: Request):
    print(request.state)
    request.state.value = 10
    request.session['value'] = 1
    return {"msg" : "value set","state" : request.state}

@secure_route.get("/api/v0/getvalue")
def getvalue(request: Request):
    return {"value" : request.session.get('value',0),"state" : request.state}
#now add the secure route to the app
app.include_router(secure_route)

#if you want to use it in a single endpoint you can do it like this
#however we recommend to use the global dependency on a router as above
#as you may forget to add it to a new endpoint
@app.get("/api/v0/secure_alt")
def secure_endpoint_alt(claims = Depends(JWTBearerClaims())):
    return {"claims" : claims}


"""
Now here is an example of how to override the default auth store
We just need to make a class which inherts from CustomAuthStore and define
the 5 methods that are required
This not even required that we actually do any auth, we can just return dummy claims
This is what we will demonstrate below
"""
class DummyAuthStore(tsgauth.fastapi.SessionAuthBase):
    
    async def claims(cls,request : Request):        
        return {"sub" : "testuser"}
    
    async def store(cls,request : Request,claims):
        pass
            
    async def clear(cls,request : Request,deep=False):
        pass
        
    async def token_request_allowed(cls, request):
        return await super().token_request_allowed(request)
        
    async def auth_attemp(cls):        
        pass

def custom_auth_store():    
    return DummyAuthStore()
"""
to activate it, simply uncomment the line below
"""
#app.dependency_overrides[tsgauth.fastapi.get_auth_store] = custom_auth_store

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
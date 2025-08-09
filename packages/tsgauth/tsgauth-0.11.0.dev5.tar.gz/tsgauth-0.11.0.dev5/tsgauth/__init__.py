import tsgauth.oidcauth

try:
    import fastapi 
except ModuleNotFoundError:    
    class FastAPIDummyClass:
        def __init__(self):
            pass
        def __getattr__(self,name):
            
            raise ImportError("fastapi is not installed, to you use this function you must install fastapi\n"
                          "pip install fastapi or "
                          "pip install tsgauth[fastapi]"
            )
    fastapi = FastAPIDummyClass()
else:
    import tsgauth.fastapi

try:
    import flask
except ModuleNotFoundError:
    print("no flask")
    class FlaskDummyClass:
        def __init__(self):
            pass
        def __getattr__(self,name):
            
            raise ImportError("flask is not installed, to you use this function you must install flask\n"
                          "pip install Flask or "
                          "pip install tsgauth[flask]"
            )
    flask = FlaskDummyClass()
else:
    import tsgauth.flaskoidc
   

from fastapi import HTTPException

"""
Defines all auth related exceptions
"""

class MissingAuthException(HTTPException):
    def __init__(self, request_offline=False,redirect_uri=None,*args, **kwargs):
        self.request_offline = request_offline
        self.redirect_uri = redirect_uri
        super().__init__(*args, **kwargs)
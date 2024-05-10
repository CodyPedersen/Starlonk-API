"""Authorization functionality"""
import os
from functools import wraps

from fastapi import HTTPException


def authorize(f):
    """Decorator to force API key authentication/authorization on API call"""
    @wraps(f)
    async def resolver(Authorization: str, *args, **kwargs):
        if Authorization != os.getenv('API_KEY'):
            raise HTTPException(status_code=401, detail="Authorization failed")
        return await f(*args, **kwargs)
    return resolver

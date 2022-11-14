from functools import wraps
import os

def authorize(f):
    """Decorator to force API key authentication/authorization on API call"""
    @wraps(f)
    async def resolver(Authorization, *args, **kwargs):
        print("Authorizing")
        if Authorization != os.getenv('API_KEY'):
            return {"status": "Invalid credentials"}

        return await f(*args, **kwargs)
    
    return resolver
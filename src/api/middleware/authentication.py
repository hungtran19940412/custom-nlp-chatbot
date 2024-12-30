from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from jose import JWTError, jwt
from datetime import datetime
from typing import Optional
import os

class AuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.security = HTTPBearer()
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key")  # In production, use env var
        self.algorithm = "HS256"
        self.public_paths = {"/health", "/auth/login", "/auth/register", "/docs", "/openapi.json"}

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.public_paths:
            return await call_next(request)

        try:
            token = await self._get_token(request)
            if not token:
                raise HTTPException(status_code=401, detail="Invalid authentication token")

            payload = self._verify_token(token)
            request.state.user = payload
            
            return await call_next(request)
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    async def _get_token(self, request: Request) -> Optional[str]:
        try:
            auth = await self.security(request)
            return auth.credentials if isinstance(auth, HTTPAuthorizationCredentials) else None
        except:
            return None

    def _verify_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("exp") and datetime.utcfromtimestamp(payload["exp"]) < datetime.utcnow():
                raise HTTPException(status_code=401, detail="Token has expired")
            return payload
        except JWTError:
            raise HTTPException(status_code=401, detail="Could not validate credentials")

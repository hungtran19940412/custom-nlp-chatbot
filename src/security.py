from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import os
import logging

logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")  # Change in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Error verifying password: {str(e)}")
        return False

def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)

def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a new JWT token."""
    try:
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        return encoded_jwt
        
    except Exception as e:
        logger.error(f"Error creating access token: {str(e)}")
        raise

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    """Get the current user from a JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
            
        # Here you would typically validate against your user database
        # For this example, we'll just return the username
        return {"username": username}
        
    except JWTError as e:
        logger.error(f"JWT error: {str(e)}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        raise credentials_exception

def create_api_key() -> str:
    """Generate a new API key."""
    try:
        # Generate a random API key
        api_key = os.urandom(32).hex()
        return api_key
    except Exception as e:
        logger.error(f"Error generating API key: {str(e)}")
        raise

def validate_api_key(api_key: str) -> bool:
    """Validate an API key."""
    try:
        # Here you would typically validate against your API key database
        # For this example, we'll just check if it's not empty
        return bool(api_key and len(api_key) == 64)
    except Exception as e:
        logger.error(f"Error validating API key: {str(e)}")
        return False

class SecurityConfig:
    """Security configuration settings."""
    
    def __init__(
        self,
        secret_key: Optional[str] = None,
        algorithm: str = ALGORITHM,
        token_expire_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES
    ):
        self.secret_key = secret_key or os.getenv("SECRET_KEY", SECRET_KEY)
        self.algorithm = algorithm
        self.token_expire_minutes = token_expire_minutes
        
        # Validate configuration
        if not self.secret_key:
            raise ValueError("SECRET_KEY must be set")
            
    def get_token_expire_delta(self) -> timedelta:
        """Get token expiration timedelta."""
        return timedelta(minutes=self.token_expire_minutes)
        
    def update_secret_key(self, new_secret_key: str):
        """Update the secret key."""
        if not new_secret_key:
            raise ValueError("New secret key cannot be empty")
        self.secret_key = new_secret_key
        
    def update_token_expire_minutes(self, minutes: int):
        """Update token expiration time."""
        if minutes <= 0:
            raise ValueError("Token expiration time must be positive")
        self.token_expire_minutes = minutes

# Initialize security configuration
security_config = SecurityConfig()

def get_security_config() -> SecurityConfig:
    """Get the current security configuration."""
    return security_config

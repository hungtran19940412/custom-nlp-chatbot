from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    username: str
    exp: datetime
    scopes: List[str] = []

class User(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    disabled: bool = False
    scopes: List[str] = []

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None

class FinancialQuery(BaseModel):
    query: str = Field(..., description="The financial analysis query")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context for the query")
    include_market_data: bool = Field(default=True, description="Whether to include real-time market data")

class SupportQuery(BaseModel):
    query: str = Field(..., description="The support query")
    category: Optional[str] = Field(default=None, description="Optional category for the query")
    priority: Optional[str] = Field(default="normal", description="Query priority (low, normal, high)")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context for the query")

class ChatResponse(BaseModel):
    response: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    context: Optional[Dict[str, Any]] = None
    sources: Optional[List[str]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

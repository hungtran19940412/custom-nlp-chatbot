from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn
import logging
from datetime import datetime, timedelta

from .chatbot import Chatbot
from .context_manager import ContextManager
from .security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Custom NLP Chatbot",
    description="A domain-specific chatbot for financial insights and customer support",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Initialize chatbot and context manager
chatbot = Chatbot()
context_manager = ContextManager()

class Message(BaseModel):
    text: str
    context_id: Optional[str] = None
    language: Optional[str] = "en"

class ChatResponse(BaseModel):
    response: str
    confidence: float
    context_id: str
    timestamp: datetime

class TrainingConfig(BaseModel):
    dataset_path: str
    model_type: str
    epochs: int
    batch_size: int

@app.post("/chat", response_model=ChatResponse)
async def chat(
    message: Message,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Get conversation context
        context = context_manager.get_context(message.context_id) if message.context_id else {}
        
        # Process message and generate response
        response, confidence = await chatbot.generate_response(
            message.text,
            context=context,
            language=message.language
        )
        
        # Update context
        context_id = context_manager.update_context(
            message.context_id,
            message.text,
            response
        )
        
        return ChatResponse(
            response=response,
            confidence=confidence,
            context_id=context_id,
            timestamp=datetime.now()
        )
    
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/train")
async def train_model(
    config: TrainingConfig,
    current_user: dict = Security(get_current_user, scopes=["admin"])
):
    try:
        # Start training process
        training_job = await chatbot.train(
            dataset_path=config.dataset_path,
            model_type=config.model_type,
            epochs=config.epochs,
            batch_size=config.batch_size
        )
        return {"message": "Training started", "job_id": training_job}
    
    except Exception as e:
        logger.error(f"Error starting training: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        # Authenticate user and create access token
        if not verify_password(form_data.password, get_password_hash(form_data.password)):
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = create_access_token(
            data={"sub": form_data.username}
        )
        return {"access_token": access_token, "token_type": "bearer"}
    
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": app.version
    }

@app.get("/metrics")
async def get_metrics(
    current_user: dict = Security(get_current_user, scopes=["admin"])
):
    try:
        metrics = await chatbot.get_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error fetching metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional, List
from datetime import datetime
from ..schemas.base import SupportQuery, ChatResponse
from ...chatbot import Chatbot
from ...context_manager import ContextManager

router = APIRouter()
chatbot = Chatbot()
context_manager = ContextManager()

@router.post("/query", response_model=ChatResponse)
async def handle_support_query(
    query: SupportQuery,
    background_tasks: BackgroundTasks
):
    """
    Handle a customer support query using the custom-trained LLM
    """
    try:
        # Prepare context with category and priority
        context = query.context or {}
        context.update({
            "category": query.category,
            "priority": query.priority
        })

        # Get response from chatbot
        response, confidence = chatbot.generate_response(
            query.query,
            context=context,
            domain="support"
        )

        # Store context for future reference
        context_manager.update_context(
            query.query,
            response,
            context
        )

        # If confidence is low, schedule for human review
        if confidence < 0.8:
            background_tasks.add_task(
                schedule_human_review,
                query=query.query,
                response=response,
                confidence=confidence
            )

        return ChatResponse(
            response=response,
            confidence=confidence,
            context=context,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback")
async def submit_feedback(
    query_id: str,
    feedback: str,
    helpful: bool,
    background_tasks: BackgroundTasks
):
    """
    Submit feedback for a support response
    """
    try:
        # Store feedback
        background_tasks.add_task(
            store_feedback,
            query_id=query_id,
            feedback=feedback,
            helpful=helpful
        )

        return {"status": "Feedback received", "timestamp": datetime.utcnow()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories")
async def get_support_categories() -> List[str]:
    """
    Get available support categories
    """
    return [
        "account",
        "billing",
        "technical",
        "product",
        "general"
    ]

async def schedule_human_review(
    query: str,
    response: str,
    confidence: float
):
    """
    Schedule a query for human review when confidence is low
    """
    # In production, implement logic to:
    # 1. Create a review ticket
    # 2. Notify support team
    # 3. Track review status
    pass

async def store_feedback(
    query_id: str,
    feedback: str,
    helpful: bool
):
    """
    Store user feedback for model improvement
    """
    # In production, implement logic to:
    # 1. Store feedback in database
    # 2. Use feedback for model retraining
    # 3. Track feedback metrics
    pass

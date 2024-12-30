from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime
import yfinance as yf
from ..schemas.base import FinancialQuery, ChatResponse
from ...chatbot import Chatbot
from ...context_manager import ContextManager

router = APIRouter()
chatbot = Chatbot()
context_manager = ContextManager()

@router.post("/analyze", response_model=ChatResponse)
async def analyze_financial_query(query: FinancialQuery):
    """
    Analyze a financial query using the custom-trained LLM
    """
    try:
        # Get real-time market data if requested
        context = query.context or {}
        if query.include_market_data:
            # Extract stock symbols from query and add market data
            symbols = extract_stock_symbols(query.query)
            market_data = get_market_data(symbols)
            context.update({"market_data": market_data})

        # Get response from chatbot
        response, confidence = chatbot.generate_response(
            query.query,
            context=context,
            domain="financial"
        )

        # Store context for future reference
        context_manager.update_context(
            query.query,
            response,
            context
        )

        return ChatResponse(
            response=response,
            confidence=confidence,
            context=context,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market-data/{symbol}")
async def get_stock_data(symbol: str):
    """
    Get real-time market data for a specific stock symbol
    """
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        return {
            "symbol": symbol,
            "price": info.get("regularMarketPrice"),
            "change": info.get("regularMarketChange"),
            "change_percent": info.get("regularMarketChangePercent"),
            "volume": info.get("regularMarketVolume"),
            "market_cap": info.get("marketCap"),
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Stock data not found for symbol: {symbol}")

def extract_stock_symbols(query: str) -> List[str]:
    """
    Extract stock symbols from the query using NLP
    This is a simplified version - in production, use more sophisticated NLP
    """
    # Simple implementation - look for uppercase words
    words = query.split()
    symbols = [
        word.strip(",.!?") 
        for word in words 
        if word.isupper() and len(word) >= 2
    ]
    return symbols

def get_market_data(symbols: List[str]) -> dict:
    """
    Get market data for multiple symbols
    """
    data = {}
    for symbol in symbols:
        try:
            stock = yf.Ticker(symbol)
            data[symbol] = {
                "price": stock.info.get("regularMarketPrice"),
                "change": stock.info.get("regularMarketChange"),
                "timestamp": datetime.utcnow()
            }
        except:
            continue
    return data

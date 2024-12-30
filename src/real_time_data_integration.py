import requests
import json
from datetime import datetime
from typing import Dict, Any
from .cache import CacheManager

class RealTimeDataIntegration:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cache = CacheManager(config)
        self.api_key = config['api_keys']['financial_data']
        self.base_url = config['financial_api']['base_url']
        
    def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """Get real-time stock price"""
        cache_key = f"stock_price_{symbol}"
        cached_data = self.cache.get(cache_key)
        
        if cached_data:
            return cached_data
            
        endpoint = f"{self.base_url}/stock/price"
        params = {
            'symbol': symbol,
            'apikey': self.api_key
        }
        
        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            data = response.json()
            self.cache.set(cache_key, data, ttl=60)  # Cache for 1 minute
            return data
        else:
            raise Exception(f"Failed to fetch stock price: {response.status_code}")

    def get_company_info(self, symbol: str) -> Dict[str, Any]:
        """Get company information"""
        cache_key = f"company_info_{symbol}"
        cached_data = self.cache.get(cache_key)
        
        if cached_data:
            return cached_data
            
        endpoint = f"{self.base_url}/company/profile"
        params = {
            'symbol': symbol,
            'apikey': self.api_key
        }
        
        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            data = response.json()
            self.cache.set(cache_key, data, ttl=3600)  # Cache for 1 hour
            return data
        else:
            raise Exception(f"Failed to fetch company info: {response.status_code}")

    def get_market_news(self) -> Dict[str, Any]:
        """Get latest market news"""
        cache_key = "market_news"
        cached_data = self.cache.get(cache_key)
        
        if cached_data:
            return cached_data
            
        endpoint = f"{self.base_url}/news/market"
        params = {
            'apikey': self.api_key
        }
        
        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            data = response.json()
            self.cache.set(cache_key, data, ttl=300)  # Cache for 5 minutes
            return data
        else:
            raise Exception(f"Failed to fetch market news: {response.status_code}")

"""AI utilities for OpenRouter API operations."""

import requests
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class AIManager:
    """Manages AI operations and OpenRouter API calls"""
    
    def __init__(self, config: dict):
        # Extract configuration from open_router config dict
        self.base_url = config.get('base_url', 'https://openrouter.ai/api/v1')
        self.api_key = config.get('api_key', '')
        self.model = config.get('model', 'google/gemini-2.0-flash-001')
        self.http_referer = config.get('http_referer', 'https://jumaworks.dev')
        self.x_title = config.get('x_title', 'Jumaworks AI Strategy')
        
        # Verify configuration
        if not self.api_key:
            logger.error("❌ OpenRouter API key not provided")
            self.client_available = False
        else:
            self.client_available = True
            logger.info(f"🤖 AI Manager initialized: Model={self.model}, "
                       f"Base URL={self.base_url}")
    
    def request(self, endpoint: str, payload: dict) -> Optional[dict]:
        """Make HTTP request to OpenRouter API"""
        if not self.client_available:
            logger.error("❌ AI Manager not available - API key missing")
            return None
        
        try:
            # Prepare headers
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': self.http_referer,
                'X-Title': self.x_title
            }
            
            # Make request
            url = f"{self.base_url}/{endpoint}"
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ AI API request failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ AI API request error: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ AI API unexpected error: {e}")
            return None

    def verify_connectivity(self) -> bool:
        """Verify AI service connectivity"""
        if not self.client_available:
            logger.error("❌ AI connectivity test failed: No API key")
            return False
        
        try:
            # Simple connectivity test with a basic API call
            test_payload = {
                'model': self.model,
                'messages': [
                    {
                        'role': 'user',
                        'content': 'Hello, this is a connectivity test. Please respond with "OK".'
                    }
                ],
                'max_tokens': 10
            }
            
            response = self.request('chat/completions', test_payload)
            
            if response is not None:
                logger.info("✅ AI service connection successful")
                return True
            else:
                logger.error("❌ AI connectivity test failed: No response")
                return False
                
        except Exception as e:
            logger.error(f"❌ AI connectivity test error: {e}")
            return False
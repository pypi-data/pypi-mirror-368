"""AI embedding utilities for OpenAI API operations."""

import logging
import time
import hashlib
import requests
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class AIEmbedManager:
    """Manages AI embedding operations using OpenAI API"""
    
    def __init__(self, config: dict):
        # Extract configuration from openai config dict
        self.api_key = config.get('api_key', '')
        self.model = config.get('model', 'text-embedding-3-small')
        self.base_url = config.get('base_url', 'https://api.openai.com/v1')
        self.cache_duration = config.get('cache_duration', 120)
        
        # Initialize cache and rate limiting
        self.cache = {}
        self.last_request_time = 0
        self.rate_limit_delay = 0.1  # 100ms between requests for OpenAI
        
        # Verify configuration
        if not self.api_key:
            logger.error("❌ OpenAI API key not provided")
            self.client_available = False
        else:
            self.client_available = True
            logger.info(f"🔤 AI Embed Manager initialized: Model={self.model}, "
                       f"Cache Duration={self.cache_duration}s, "
                       f"Base URL={self.base_url}")
    
    def _rate_limit_check(self) -> None:
        """Enforce rate limiting between API calls"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _generate_cache_key(self, text: str) -> str:
        """Generate cache key for text"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_entry: dict) -> bool:
        """Check if cache entry is still valid"""
        if not cache_entry:
            return False
        
        cache_time = cache_entry.get('timestamp', 0)
        current_time = time.time()
        
        return (current_time - cache_time) < self.cache_duration
    
    def request(self, endpoint: str, payload: dict) -> Optional[dict]:
        """Make HTTP request to OpenAI API"""
        if not self.client_available:
            logger.error("❌ AI Embed Manager not available - API key missing")
            return None
        
        try:
            # Rate limiting
            self._rate_limit_check()
            
            # Prepare headers
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Make request
            url = f"{self.base_url}/{endpoint}"
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ OpenAI API request failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ OpenAI API request error: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ OpenAI API unexpected error: {e}")
            return None
    
    def get_embedding(self, text: str, use_cache: bool = True) -> Optional[list]:
        """Get text embedding using OpenAI embedding model"""
        if not self.client_available:
            return None
        
        # Check cache first if enabled
        if use_cache:
            cache_key = self._generate_cache_key(text)
            cached_entry = self.cache.get(cache_key)
            
            if cached_entry and self._is_cache_valid(cached_entry):
                logger.debug(f"✅ Using cached embedding: {len(cached_entry['embedding'])} dimensions")
                return cached_entry['embedding']
        
        # Prepare payload for OpenAI API
        payload = {
            'model': self.model,
            'input': text,
            'encoding_format': 'float',
            'dimensions': 128
        }
        
        response = self.request('embeddings', payload)
        
        if response:
            try:
                embedding = response['data'][0]['embedding']
                
                # Cache the result if caching is enabled
                if use_cache:
                    cache_key = self._generate_cache_key(text)
                    self.cache[cache_key] = {
                        'embedding': embedding,
                        'timestamp': time.time(),
                        'model': self.model,
                        'text_length': len(text)
                    }
                
                logger.debug(f"✅ OpenAI embedding generated: {len(embedding)} dimensions")
                return embedding
                
            except (KeyError, IndexError) as e:
                logger.error(f"❌ Failed to extract OpenAI embedding: {e}")
                return None
        
        return None
    
    def get_embedding_batch(self, texts: list, use_cache: bool = True) -> Optional[list]:
        """Get embeddings for multiple texts in a single API call"""
        if not self.client_available:
            return None
        
        if not texts:
            return []
        
        # Check cache for all texts first
        if use_cache:
            cached_embeddings = []
            uncached_texts = []
            uncached_indices = []
            
            for i, text in enumerate(texts):
                cache_key = self._generate_cache_key(text)
                cached_entry = self.cache.get(cache_key)
                
                if cached_entry and self._is_cache_valid(cached_entry):
                    cached_embeddings.append((i, cached_entry['embedding']))
                else:
                    uncached_texts.append(text)
                    uncached_indices.append(i)
            
            # If all texts are cached, return cached results
            if not uncached_texts:
                # Sort by original index and return embeddings
                cached_embeddings.sort(key=lambda x: x[0])
                return [emb for _, emb in cached_embeddings]
            
            # Process uncached texts
            texts_to_process = uncached_texts
        else:
            texts_to_process = texts
            cached_embeddings = []
            uncached_indices = list(range(len(texts)))
        
        # Prepare payload for batch embedding
        payload = {
            'model': self.model,
            'input': texts_to_process,
            'encoding_format': 'float'
        }
        
        response = self.request('embeddings', payload)
        
        if response:
            try:
                new_embeddings = [item['embedding'] for item in response['data']]
                
                # Cache new embeddings if caching is enabled
                if use_cache:
                    for i, text in enumerate(texts_to_process):
                        cache_key = self._generate_cache_key(text)
                        self.cache[cache_key] = {
                            'embedding': new_embeddings[i],
                            'timestamp': time.time(),
                            'model': self.model,
                            'text_length': len(text)
                        }
                
                # Combine cached and new embeddings in correct order
                if use_cache and cached_embeddings:
                    all_embeddings = [None] * len(texts)
                    
                    # Place cached embeddings
                    for idx, embedding in cached_embeddings:
                        all_embeddings[idx] = embedding
                    
                    # Place new embeddings
                    for i, idx in enumerate(uncached_indices):
                        all_embeddings[idx] = new_embeddings[i]
                    
                    return all_embeddings
                else:
                    return new_embeddings
                
            except (KeyError, IndexError) as e:
                logger.error(f"❌ Failed to extract OpenAI batch embeddings: {e}")
                return None
        
        return None
    
    def clear_cache(self) -> None:
        """Clear the embedding cache"""
        self.cache.clear()
        logger.info("🧹 Embedding cache cleared")
    
    def get_cache_stats(self) -> dict:
        """Get cache statistics"""
        current_time = time.time()
        valid_entries = 0
        expired_entries = 0
        
        for entry in self.cache.values():
            if self._is_cache_valid(entry):
                valid_entries += 1
            else:
                expired_entries += 1
        
        return {
            'total_entries': len(self.cache),
            'valid_entries': valid_entries,
            'expired_entries': expired_entries,
            'cache_hit_potential': valid_entries / max(len(self.cache), 1),
            'cache_duration': self.cache_duration
        }
    
    def verify_connectivity(self) -> bool:
        """Verify OpenAI service connectivity"""
        if not self.client_available:
            logger.error("❌ OpenAI connectivity test failed: No API key")
            return False
        
        try:
            # Simple connectivity test with a basic embedding request
            test_text = "Hello, this is a connectivity test."
            embedding = self.get_embedding(test_text, use_cache=False)
            
            if embedding is not None:
                logger.info(f"✅ OpenAI embedding service connection successful ({len(embedding)} dimensions)")
                return True
            else:
                logger.error("❌ OpenAI connectivity test failed: No embedding returned")
                return False
                
        except Exception as e:
            logger.error(f"❌ OpenAI connectivity test error: {e}")
            return False
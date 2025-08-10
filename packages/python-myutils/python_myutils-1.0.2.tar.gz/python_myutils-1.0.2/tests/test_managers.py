"""Tests for manager classes (AI, Database, Sentry, Embed)."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from myutils.ai_manager_utils import AIManager
from myutils.database_manager_utils import DatabaseManager
from myutils.sentry_manager_utils import SentryManager
from myutils.ai_embed_manager_utils import AIEmbedManager


class TestAIManager:
    """Test AIManager functionality."""
    
    def test_init_with_api_key(self):
        """Test AIManager initialization with API key."""
        config = {
            'api_key': 'test-key',
            'model': 'test-model',
            'base_url': 'https://test.api.com'
        }
        
        ai = AIManager(config)
        
        assert ai.api_key == 'test-key'
        assert ai.model == 'test-model'
        assert ai.base_url == 'https://test.api.com'
        assert ai.client_available is True
    
    def test_init_without_api_key(self):
        """Test AIManager initialization without API key."""
        config = {}
        
        ai = AIManager(config)
        
        assert ai.api_key == ''
        assert ai.client_available is False
    
    @patch('myutils.ai_manager_utils.requests.post')
    def test_request_success(self, mock_post):
        """Test successful API request."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'result': 'success'}
        mock_post.return_value = mock_response
        
        config = {'api_key': 'test-key'}
        ai = AIManager(config)
        
        # Test
        payload = {'test': 'data'}
        result = ai.request('test-endpoint', payload)
        
        # Verify
        assert result == {'result': 'success'}
        mock_post.assert_called_once()
        
        # Check call arguments
        call_args = mock_post.call_args
        assert call_args[1]['json'] == payload
        assert 'Authorization' in call_args[1]['headers']
        assert call_args[1]['headers']['Authorization'] == 'Bearer test-key'
    
    @patch('myutils.ai_manager_utils.requests.post')
    def test_request_failure(self, mock_post):
        """Test failed API request."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = 'Unauthorized'
        mock_post.return_value = mock_response
        
        config = {'api_key': 'test-key'}
        ai = AIManager(config)
        
        # Test
        result = ai.request('test-endpoint', {'test': 'data'})
        
        # Verify
        assert result is None
    
    def test_request_no_client(self):
        """Test request without available client."""
        config = {}
        ai = AIManager(config)
        
        result = ai.request('test-endpoint', {'test': 'data'})
        
        assert result is None
    
    @patch('myutils.ai_manager_utils.requests.post')
    def test_verify_connectivity_success(self, mock_post):
        """Test successful connectivity verification."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'choices': [{'message': {'content': 'OK'}}]}
        mock_post.return_value = mock_response
        
        config = {'api_key': 'test-key'}
        ai = AIManager(config)
        
        result = ai.verify_connectivity()
        
        assert result is True
    
    def test_verify_connectivity_no_client(self):
        """Test connectivity verification without client."""
        config = {}
        ai = AIManager(config)
        
        result = ai.verify_connectivity()
        
        assert result is False


class TestDatabaseManager:
    """Test DatabaseManager functionality."""
    
    @patch('myutils.database_manager_utils.create_client')
    def test_init_success(self, mock_create_client):
        """Test DatabaseManager initialization success."""
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        config = {
            'url': 'https://test.supabase.co',
            'key': 'test-key'
        }
        
        db = DatabaseManager(config)
        
        assert db.url == 'https://test.supabase.co'
        assert db.key == 'test-key'
        assert db.client == mock_client
        mock_create_client.assert_called_once_with(
            'https://test.supabase.co', 'test-key'
        )
    
    @patch('myutils.database_manager_utils.create_client')
    def test_init_failure(self, mock_create_client):
        """Test DatabaseManager initialization failure."""
        mock_create_client.side_effect = Exception("Connection failed")
        
        config = {
            'url': 'https://test.supabase.co',
            'key': 'test-key'
        }
        
        db = DatabaseManager(config)
        
        assert db.client is None
    
    @patch('myutils.database_manager_utils.create_client')
    def test_insert_success(self, mock_create_client):
        """Test successful database insert."""
        # Setup mock chain
        mock_execute = Mock()
        mock_execute.execute.return_value.data = [{'id': 1, 'name': 'test'}]
        
        mock_insert = Mock()
        mock_insert.insert.return_value = mock_execute
        
        mock_table = Mock()
        mock_table.table.return_value = mock_insert
        
        mock_create_client.return_value = mock_table
        
        config = {'url': 'test', 'key': 'test'}
        db = DatabaseManager(config)
        
        # Test
        result = db.insert({'name': 'test'}, 'users')
        
        # Verify
        assert result == {'id': 1, 'name': 'test'}
        mock_table.table.assert_called_with('users')
        mock_insert.insert.assert_called_with({'name': 'test'})
    
    @patch('myutils.database_manager_utils.create_client')
    def test_select_with_filters(self, mock_create_client):
        """Test database select with query parameters."""
        # Setup mock chain
        mock_execute = Mock()
        mock_execute.execute.return_value.data = [{'id': 1, 'status': 'active'}]
        
        mock_eq = Mock()
        mock_eq.eq.return_value = mock_execute
        
        mock_select = Mock()
        mock_select.select.return_value = mock_eq
        
        mock_table = Mock()
        mock_table.table.return_value = mock_select
        
        mock_create_client.return_value = mock_table
        
        config = {'url': 'test', 'key': 'test'}
        db = DatabaseManager(config)
        
        # Test
        result = db.select('users', {'status': 'active'})
        
        # Verify
        assert result == [{'id': 1, 'status': 'active'}]
        mock_select.select.assert_called_with('*')
        mock_eq.eq.assert_called_with('status', 'active')
    
    def test_operations_no_client(self):
        """Test database operations without client."""
        with patch('myutils.database_manager_utils.create_client') as mock_create:
            mock_create.side_effect = Exception("No client")
            
            config = {'url': 'test', 'key': 'test'}
            db = DatabaseManager(config)
            
            # All operations should return None/False
            assert db.insert({}, 'table') is None
            assert db.select('table') is None
            assert db.update({}, {}, 'table') is None
            assert db.delete({}, 'table') is False


class TestSentryManager:
    """Test SentryManager functionality."""
    
    @patch('myutils.sentry_manager_utils.sentry_sdk')
    @patch('myutils.sentry_manager_utils.LoggingIntegration')
    def test_init_success(self, mock_logging_integration, mock_sentry):
        """Test SentryManager initialization success."""
        config = {
            'dsn': 'https://test-dsn@sentry.io/123',
            'environment': 'test',
            'version': '1.0.0'
        }
        
        sentry = SentryManager(config)
        
        assert sentry.dsn == 'https://test-dsn@sentry.io/123'
        assert sentry.environment == 'test'
        assert sentry.version == '1.0.0'
        
        # Verify Sentry SDK was initialized
        mock_sentry.init.assert_called_once()
        mock_sentry.set_tag.assert_called()
    
    @patch('myutils.sentry_manager_utils.sentry_sdk')
    def test_capture_success(self, mock_sentry):
        """Test successful event capture."""
        config = {'dsn': 'test-dsn'}
        sentry = SentryManager(config)
        
        context = {'message': 'test event', 'data': 'test'}
        result = sentry.capture(context, 'info')
        
        assert result is True
        mock_sentry.set_context.assert_called_with('context', context)
        mock_sentry.capture_message.assert_called()
    
    @patch('myutils.sentry_manager_utils.sentry_sdk')
    def test_capture_special_levels(self, mock_sentry):
        """Test capture with special level types."""
        config = {'dsn': 'test-dsn'}
        sentry = SentryManager(config)
        
        # Test special levels
        special_levels = ['performance', 'productive', 'connectivity', 'ai_request']
        
        for level in special_levels:
            context = {'message': f'test {level} event'}
            result = sentry.capture(context, level)
            
            assert result is True
            mock_sentry.set_tag.assert_called_with('metric_type', level)
    
    @patch('myutils.sentry_manager_utils.sentry_sdk')
    def test_verify_connectivity(self, mock_sentry):
        """Test Sentry connectivity verification."""
        config = {'dsn': 'test-dsn'}
        sentry = SentryManager(config)
        
        # Mock the capture method to return True
        with patch.object(sentry, 'capture', return_value=True):
            result = sentry.verify_connectivity()
            assert result is True


class TestAIEmbedManager:
    """Test AIEmbedManager functionality."""
    
    def test_init_with_config(self):
        """Test AIEmbedManager initialization."""
        config = {
            'api_key': 'test-key',
            'model': 'text-embedding-3-small',
            'cache_duration': 300
        }
        
        embedder = AIEmbedManager(config)
        
        assert embedder.api_key == 'test-key'
        assert embedder.model == 'text-embedding-3-small'
        assert embedder.cache_duration == 300
        assert embedder.client_available is True
    
    def test_init_no_api_key(self):
        """Test AIEmbedManager initialization without API key."""
        config = {}
        
        embedder = AIEmbedManager(config)
        
        assert embedder.client_available is False
    
    def test_generate_cache_key(self):
        """Test cache key generation."""
        config = {'api_key': 'test-key'}
        embedder = AIEmbedManager(config)
        
        key1 = embedder._generate_cache_key("test text")
        key2 = embedder._generate_cache_key("test text")
        key3 = embedder._generate_cache_key("different text")
        
        # Same text should generate same key
        assert key1 == key2
        # Different text should generate different key
        assert key1 != key3
        # Keys should be strings
        assert isinstance(key1, str)
    
    def test_cache_validation(self):
        """Test cache entry validation."""
        config = {'api_key': 'test-key', 'cache_duration': 60}
        embedder = AIEmbedManager(config)
        
        import time
        current_time = time.time()
        
        # Valid cache entry (recent)
        valid_entry = {
            'embedding': [1, 2, 3],
            'timestamp': current_time - 30  # 30 seconds ago
        }
        assert embedder._is_cache_valid(valid_entry) is True
        
        # Invalid cache entry (expired)
        invalid_entry = {
            'embedding': [1, 2, 3],
            'timestamp': current_time - 120  # 2 minutes ago
        }
        assert embedder._is_cache_valid(invalid_entry) is False
        
        # Invalid cache entry (no timestamp)
        no_timestamp = {'embedding': [1, 2, 3]}
        assert embedder._is_cache_valid(no_timestamp) is False
        
        # No entry
        assert embedder._is_cache_valid(None) is False
    
    @patch('myutils.ai_embed_manager_utils.time.sleep')
    @patch('myutils.ai_embed_manager_utils.time.time')
    def test_rate_limiting(self, mock_time, mock_sleep):
        """Test rate limiting functionality."""
        config = {'api_key': 'test-key'}
        embedder = AIEmbedManager(config)
        
        # Setup time mock
        mock_time.side_effect = [0, 0.05, 0.1]  # First call, check, update
        
        embedder.last_request_time = 0
        embedder._rate_limit_check()
        
        # Should sleep to enforce rate limit
        mock_sleep.assert_called_once()
        sleep_time = mock_sleep.call_args[0][0]
        assert sleep_time > 0
    
    @patch('myutils.ai_embed_manager_utils.requests.post')
    def test_get_embedding_success(self, mock_post):
        """Test successful embedding generation."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [{'embedding': [0.1, 0.2, 0.3]}]
        }
        mock_post.return_value = mock_response
        
        config = {'api_key': 'test-key'}
        embedder = AIEmbedManager(config)
        
        # Test
        result = embedder.get_embedding("test text", use_cache=False)
        
        # Verify
        assert result == [0.1, 0.2, 0.3]
        mock_post.assert_called_once()
    
    @patch('myutils.ai_embed_manager_utils.requests.post')
    def test_get_embedding_with_cache(self, mock_post):
        """Test embedding generation with caching."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [{'embedding': [0.1, 0.2, 0.3]}]
        }
        mock_post.return_value = mock_response
        
        config = {'api_key': 'test-key', 'cache_duration': 300}
        embedder = AIEmbedManager(config)
        
        # First call - should make API request
        result1 = embedder.get_embedding("test text")
        assert result1 == [0.1, 0.2, 0.3]
        assert mock_post.call_count == 1
        
        # Second call - should use cache
        result2 = embedder.get_embedding("test text")
        assert result2 == [0.1, 0.2, 0.3]
        assert mock_post.call_count == 1  # No additional API call
    
    def test_cache_management(self):
        """Test cache management functionality."""
        config = {'api_key': 'test-key'}
        embedder = AIEmbedManager(config)
        
        # Add some mock cache entries
        embedder.cache['key1'] = {
            'embedding': [1, 2, 3],
            'timestamp': embedder.last_request_time
        }
        
        # Test cache stats
        stats = embedder.get_cache_stats()
        assert stats['total_entries'] == 1
        assert 'valid_entries' in stats
        assert 'cache_duration' in stats
        
        # Test cache clearing
        embedder.clear_cache()
        assert len(embedder.cache) == 0
        
        stats_after_clear = embedder.get_cache_stats()
        assert stats_after_clear['total_entries'] == 0
    
    def test_operations_no_client(self):
        """Test operations without available client."""
        config = {}  # No API key
        embedder = AIEmbedManager(config)
        
        # All operations should return None
        assert embedder.get_embedding("test") is None
        assert embedder.get_embedding_batch(["test1", "test2"]) is None
        assert embedder.verify_connectivity() is False


class TestIntegrationScenarios:
    """Test integration scenarios across managers."""
    
    def test_manager_initialization_flow(self):
        """Test typical manager initialization flow."""
        # AI Manager
        ai_config = {'api_key': 'ai-key', 'model': 'test-model'}
        ai = AIManager(ai_config)
        assert ai.client_available is True
        
        # Embedding Manager
        embed_config = {'api_key': 'embed-key'}
        embedder = AIEmbedManager(embed_config)
        assert embedder.client_available is True
        
        # Sentry Manager
        with patch('myutils.sentry_manager_utils.sentry_sdk'):
            sentry_config = {'dsn': 'test-dsn'}
            sentry = SentryManager(sentry_config)
            assert sentry.dsn == 'test-dsn'
    
    @patch('myutils.database_manager_utils.create_client')
    @patch('myutils.ai_manager_utils.requests.post')
    def test_data_pipeline_simulation(self, mock_ai_post, mock_db_client):
        """Test simulated data processing pipeline."""
        # Setup AI Manager mock
        mock_ai_response = Mock()
        mock_ai_response.status_code = 200
        mock_ai_response.json.return_value = {'choices': [{'message': {'content': 'processed'}}]}
        mock_ai_post.return_value = mock_ai_response
        
        # Setup Database Manager mock
        mock_db_execute = Mock()
        mock_db_execute.execute.return_value.data = [{'id': 1}]
        mock_db_insert = Mock()
        mock_db_insert.insert.return_value = mock_db_execute
        mock_db_table = Mock()
        mock_db_table.table.return_value = mock_db_insert
        mock_db_client.return_value = mock_db_table
        
        # Initialize managers
        ai = AIManager({'api_key': 'test-key'})
        db = DatabaseManager({'url': 'test', 'key': 'test'})
        
        # Simulate pipeline: AI processing -> Database storage
        ai_result = ai.request('chat/completions', {'messages': [{'role': 'user', 'content': 'test'}]})
        assert ai_result is not None
        
        db_result = db.insert({'result': 'processed'}, 'results')
        assert db_result == {'id': 1}
    
    def test_error_handling_across_managers(self):
        """Test error handling consistency across managers."""
        # Managers without proper configuration
        managers = [
            AIManager({}),
            AIEmbedManager({}),
        ]
        
        # All should handle missing config gracefully
        for manager in managers:
            assert hasattr(manager, 'client_available')
            assert manager.client_available is False
        
        # Operations should return None/False safely
        ai = AIManager({})
        assert ai.request('test', {}) is None
        assert ai.verify_connectivity() is False
        
        embedder = AIEmbedManager({})
        assert embedder.get_embedding('test') is None
        assert embedder.verify_connectivity() is False
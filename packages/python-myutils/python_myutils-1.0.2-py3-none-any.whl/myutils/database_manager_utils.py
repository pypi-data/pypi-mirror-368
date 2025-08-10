"""Database utilities for Supabase database operations."""

import logging
from typing import Optional, Dict, List, Union
from supabase import create_client

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database operations"""
    
    def __init__(self, config: dict):
        self.url = config.get('url', '')
        self.key = config.get('key', '')
        self.client = None
        
        try:
            self.client = create_client(self.url, self.key)
            # Test connection by checking if we can access the client
            if self.client:
                logger.info(f"🗄️  Database SDK initialized with database: {self.url}")
            else:
                raise Exception("Failed to create database client")
        except Exception as e:
            logger.error(f"❌ Failed to connect to database SDK: {e}")
            self.client = None
    
    def insert(self, data: dict, table: str) -> Optional[dict]:
        """Insert data into database table"""
        if not self.client:
            return None
        
        try:
            response = self.client.table(table).insert(data).execute()
            
            if response.data:
                return response.data[0] if len(response.data) == 1 else response.data
            else:
                logger.error(f"❌ Database insert failed: {response.error}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Database insert error: {e}")
            return None

    def select(self, table: str, query_params: dict = None) -> Optional[list]:
        """Select data from database table"""
        if not self.client:
            return None
        
        try:
            query = self.client.table(table).select('*')
            
            # Apply filters if provided
            if query_params:
                for key, value in query_params.items():
                    if isinstance(value, (list, tuple)):
                        query = query.in_(key, value)
                    else:
                        query = query.eq(key, value)
            
            response = query.execute()
            
            if response.data is not None:
                return response.data
            else:
                logger.error(f"❌ Database select failed: {response.error}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Database select error: {e}")
            return None

    def update(self, data: dict, filters: dict, table: str) -> Optional[dict]:
        """Update data in database table"""
        if not self.client:
            return None
        
        try:
            query = self.client.table(table).update(data)
            
            # Apply filters
            for key, value in filters.items():
                query = query.eq(key, value)
            
            response = query.execute()
            
            if response.data:
                return response.data[0] if len(response.data) == 1 else response.data
            else:
                logger.error(f"❌ Database update failed: {response.error}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Database update error: {e}")
            return None

    def delete(self, filters: dict, table: str) -> bool:
        """Delete data from database table"""
        if not self.client:
            return False
        
        try:
            query = self.client.table(table).delete()
            
            # Apply filters
            for key, value in filters.items():
                query = query.eq(key, value)
            
            response = query.execute()
            
            if response.data is not None:
                return True
            else:
                logger.error(f"❌ Database delete failed: {response.error}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Database delete error: {e}")
            return False

    def execute_sql(self, sql: str, params: dict = None) -> Optional[list]:
        """Execute raw SQL query using Supabase RPC"""
        if not self.client:
            return None
        
        try:
            # Use RPC to execute raw SQL - function only takes 'query' parameter
            response = self.client.rpc('execute_sql', {'query': sql}).execute()
            
            if response.data is not None:
                return response.data
            else:
                logger.error(f"❌ Raw SQL query failed: {response}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Raw SQL query error: {e}")
            return None

    def verify_connectivity(self) -> bool:
        """Verify database connectivity"""
        if not self.client:
            logger.error("❌ Database test failed: No database client")
            return False
        
        try:
            # Test with a simple connectivity query
            sql_query = "SELECT 'Database connection successful' as message, NOW() as current_time"
            
            response = self.execute_sql(sql_query)
            
            if response is not None:
                logger.info(f"✅ Database connection successful: {response}")
                return True
            else:
                logger.error("❌ Database test failed: No response data")
                return False
                
        except Exception as e:
            logger.error(f"❌ Database test error: {e}")
            return False
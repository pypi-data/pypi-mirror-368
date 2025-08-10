"""Sentry error tracking and monitoring utilities."""

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

logger = logging.getLogger(__name__)


class SentryManager:
    """Manages Sentry error tracking and monitoring"""
    
    def __init__(self, config: dict):
        self.dsn = config.get('dsn', '')
        self.environment = config.get('environment', 'production')
        self.version = config.get('version', '1.0.0')
        
        try:
            # Configure Sentry SDK with logging integration
            sentry_logging = LoggingIntegration(
                level=logging.ERROR,  # Capture error level and above
                event_level=logging.ERROR  # Send errors as events
            )
            
            sentry_sdk.init(
                dsn=self.dsn,
                environment=self.environment,
                integrations=[sentry_logging],
                # Set a uniform sample rate between 0.0 and 1.0
                profiles_sample_rate=1.0,
                # Enable performance monitoring
                enable_tracing=True
            )
            
            # Set default tags after initialization
            sentry_sdk.set_tag("strategy", "AITradingStrategy")
            sentry_sdk.set_tag("version", self.version)
            
            logger.info(f"🔍 Sentry SDK initialized with logging integration: {self.environment}")
        except Exception as e:
            # Don't log to avoid potential infinite loop
            print(f"❌ Failed to initialize Sentry SDK: {e}")
    
    def capture(self, context: dict, level: str = "info") -> bool:
        """Send context to Sentry"""
        try:
            # Add context as extra data
            sentry_sdk.set_context("context", context)
            
            # Handle special levels
            if level in ['performance', 'productive', 'connectivity', 'debugging', 'ai_request']:
                sentry_sdk.set_tag("metric_type", level)
                actual_level = "info"
            else:
                # Map string levels to Sentry levels
                level_mapping = {
                    "debug": "debug",
                    "info": "info", 
                    "warning": "warning",
                    "error": "error",
                    "critical": "fatal"
                }
                actual_level = level_mapping.get(level.lower(), "info")
            
            # Capture the context as a message
            message = context.get('message', 'Trading event captured')
            sentry_sdk.capture_message(message, level=actual_level)
            logger.debug(f"🔍 Sentry context captured: {message} (level: {level})")
            return True
                
        except Exception as e:
            logger.error(f"❌ Failed to send to Sentry: {e}")
            return False

    def verify_connectivity(self) -> bool:
        """Verify Sentry connectivity"""
        try:
            self.capture({"message": "Sentry connection successful"}, level="connectivity")
            logger.info("✅ Sentry connection successful")
            return True
        except Exception as e:
            logger.error(f"❌ Sentry connection test failed: {e}")
            return False
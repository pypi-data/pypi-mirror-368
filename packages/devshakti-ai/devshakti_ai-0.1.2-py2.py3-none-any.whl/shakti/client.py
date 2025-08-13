from .chat import Completions
from typing import Optional
import logging

# Set up logging
logger = logging.getLogger(__name__)

class ChatShakti:
    """
    Client for interacting with the Shakti Chat API.
    
    Example:
        >>> # Using default URL
        >>> client = ChatShakti(api_key="your-api-key")
        >>> 
        >>> # Or specify custom URL
        >>> client = ChatShakti(
        ...     base_url="https://custom-api.com",
        ...     api_key="your-api-key"
        ... )
        >>> response = client.chat.completions.create(
        ...     messages=[{"role": "user", "content": "Hello"}]
        ... )
    """
    
    DEFAULT_BASE_URL = "https://devshakti.serveo.net"  # Default API endpoint
    DEFAULT_TIMEOUT = 30  # seconds
    DEFAULT_MAX_RETRIES = 3
    
    def __init__(
        self, 
        api_key: str,  # Required
        base_url: Optional[str] = None,  # Optional, uses default if not provided
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        verify_ssl: bool = True
    ):
        """
        Initialize the ChatShakti client.
        
        Args:
            api_key: API key for authentication (required)
            base_url: Base URL of the API (optional, uses DEFAULT_BASE_URL if not provided)
            timeout: Default timeout for requests in seconds
            max_retries: Maximum number of retry attempts
            verify_ssl: Whether to verify SSL certificates
            
        Raises:
            ValueError: If api_key is empty
        """
        if not api_key:
            raise ValueError("api_key cannot be empty")
        
        # Use provided base_url or fall back to default
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.verify_ssl = verify_ssl
        
        # Set up headers
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "User-Agent": "shakti-sdk/0.1.0"  # Add version tracking
        }
        
        # Initialize chat namespace
        self.chat = self._ChatNamespace(
            self.base_url, 
            self.headers, 
            self.timeout
        )
        
        logger.debug(f"ChatShakti client initialized with base_url: {self.base_url}")

    class _ChatNamespace:
        """Namespace for chat-related operations."""
        
        def __init__(self, base_url: str, headers: dict, timeout: int):
            self.completions = Completions(base_url, headers, timeout)
    
    def test_connection(self) -> bool:
        """
        Test if the API is reachable.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Make a minimal request to test connection
            response = self.chat.completions.create(
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return bool(response)
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def __repr__(self) -> str:
        """String representation of the client."""
        return f"ChatShakti(base_url='{self.base_url}')"
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # Could add cleanup here if needed
        pass
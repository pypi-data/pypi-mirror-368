"""Configuration module for ClasherJK library."""

import os
from typing import Optional


class Config:
    """Configuration class for ClasherJK library."""
    
    # Default proxy URL (can be changed without users knowing)
    DEFAULT_PROXY_URL = "https://clasherjk.vercel.app"
    
    @classmethod
    def get_proxy_url(cls, custom_url: Optional[str] = None) -> str:
        """
        Get the proxy URL to use for API requests.
        
        Priority:
        1. Custom URL provided by user
        2. Environment variable CLASHERJK_PROXY_URL
        3. Default proxy URL
        
        Args:
            custom_url: Custom proxy URL provided by user
            
        Returns:
            Proxy URL to use for API requests
        """
        if custom_url:
            return custom_url
            
        # Check environment variable (useful for advanced users or testing)
        env_url = os.getenv("CLASHERJK_PROXY_URL")
        if env_url:
            return env_url
            
        return cls.DEFAULT_PROXY_URL
    
    @classmethod
    def update_default_proxy_url(cls, new_url: str) -> None:
        """
        Update the default proxy URL.
        
        This allows you to change the proxy URL without updating
        the library code that users have installed.
        
        Args:
            new_url: New default proxy URL
        """
        cls.DEFAULT_PROXY_URL = new_url
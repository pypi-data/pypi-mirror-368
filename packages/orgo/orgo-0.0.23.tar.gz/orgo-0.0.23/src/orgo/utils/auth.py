# src/orgo/utils/auth.py
"""Authentication utilities for Orgo SDK"""

import os
from typing import Optional

def get_api_key(api_key: Optional[str] = None) -> str:
    """Get the Orgo API key from parameters or environment"""
    key = api_key or os.environ.get("ORGO_API_KEY")
    
    if not key:
        raise ValueError(
            "API key required. Set ORGO_API_KEY environment variable or pass api_key parameter. "
            "Get a key at https://www.orgo.ai/start"
        )
        
    return key
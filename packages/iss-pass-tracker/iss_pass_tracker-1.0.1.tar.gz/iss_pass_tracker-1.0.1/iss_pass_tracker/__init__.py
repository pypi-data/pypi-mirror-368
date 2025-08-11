# __init__.py
import os
from .api import get_passes, Pass, set_api_key

# Try to auto-load from environment variable
_env_key = os.getenv("N2YO_API_KEY")
if _env_key:
    set_api_key(_env_key)

__all__ = ["get_passes", "Pass", "set_api_key"]

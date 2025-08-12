"""
Utility functions for Airflow MCP
"""
import os
import requests
from typing import Any, Dict, Optional

def airflow_request(method: str, path: str, **kwargs) -> requests.Response:
    """
    Make a Basic Auth request to Airflow REST API.
    'path' should be relative to AIRFLOW_API_URL (e.g., '/dags', '/pools').
    """
    base_url = os.getenv("AIRFLOW_API_URL", "").rstrip("/")
    if not base_url:
        raise RuntimeError("AIRFLOW_API_URL environment variable is not set")
    
    # Ensure path starts with /
    if not path.startswith("/"):
        path = "/" + path
    
    # Construct full URL
    full_url = base_url + path
    
    # Get authentication
    username = os.getenv("AIRFLOW_API_USERNAME")
    password = os.getenv("AIRFLOW_API_PASSWORD")
    if not username or not password:
        raise RuntimeError("AIRFLOW_API_USERNAME or AIRFLOW_API_PASSWORD environment variable is not set")
    
    auth = (username, password)
    headers = kwargs.pop("headers", {})
    
    return requests.request(method, full_url, headers=headers, auth=auth, **kwargs)

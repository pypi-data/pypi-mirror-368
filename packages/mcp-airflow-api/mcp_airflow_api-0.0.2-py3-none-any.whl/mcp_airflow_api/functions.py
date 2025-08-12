"""
Airflow MCP auxiliary utility functions definition file
"""
import os
import requests

def airflow_request(method, url, **kwargs):
    user = os.getenv("AIRFLOW_API_USER")
    password = os.getenv("AIRFLOW_API_PASSWORD")
    headers = kwargs.pop("headers", {})
    auth = (user, password) if user and password else None
    return requests.request(method, url, headers=headers, auth=auth, **kwargs)

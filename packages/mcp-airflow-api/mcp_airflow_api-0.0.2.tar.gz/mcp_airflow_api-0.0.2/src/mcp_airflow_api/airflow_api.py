"""
Main feature definitions for Airflow MCP.
"""
import os
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
import requests
from .functions import airflow_request

load_dotenv(dotenv_path=os.getenv("MCP_CONFIG", "config"))

AIRFLOW_API_URL = os.getenv("AIRFLOW_API_URL")
AIRFLOW_API_TOKEN = os.getenv("AIRFLOW_API_TOKEN")

router = APIRouter()

# MCP tool: DAG 목록 조회
@router.get("/dags", tags=["airflow"])
def list_dags():
    resp = airflow_request("GET", f"{AIRFLOW_API_URL}/dags")
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()

# MCP tool: 실행 중인 DAG 조회
@router.get("/dags/running", tags=["airflow"])
def running_dags():
    resp = airflow_request("GET", f"{AIRFLOW_API_URL}/dags?state=running")
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()

# MCP tool: 최근 실패한 DAG 조회
@router.get("/dags/failed", tags=["airflow"])
def failed_dags():
    resp = airflow_request("GET", f"{AIRFLOW_API_URL}/dags?state=failed")
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()

# MCP tool: DAG 실행 트리거
@router.post("/dags/{dag_id}/trigger", tags=["airflow"])
def trigger_dag(dag_id: str):
    resp = airflow_request("POST", f"{AIRFLOW_API_URL}/dags/{dag_id}/dagRuns")
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()

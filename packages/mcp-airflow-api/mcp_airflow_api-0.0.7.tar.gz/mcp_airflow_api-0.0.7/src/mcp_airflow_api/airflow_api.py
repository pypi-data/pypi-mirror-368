"""
MCP tool definitions for Airflow REST API operations.
"""
import argparse
import logging
from typing import Any, Dict, List, Optional
import mcp
from mcp.server.fastmcp import FastMCP
from .functions import airflow_request

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# MCP server instance for registering tools
mcp = FastMCP("mcp-airflow-api")

@mcp.tool()
def list_dags() -> Dict[str, Any]:
    """
    [Tool Role]: Lists all DAGs registered in the Airflow cluster.

    Returns:
        List of DAGs with minimal info: dag_id, dag_display_name, is_active, is_paused, owners, tags
    """
    resp = airflow_request("GET", "/dags")
    resp.raise_for_status()
    dags = resp.json().get("dags", [])
    minimal = []
    for dag in dags:
        minimal.append({
            "dag_id": dag.get("dag_id"),
            "dag_display_name": dag.get("dag_display_name"),
            "is_active": dag.get("is_active"),
            "is_paused": dag.get("is_paused"),
            "owners": dag.get("owners"),
            "tags": [t.get("name") for t in dag.get("tags", [])]
        })
    return {"dags": minimal}

@mcp.tool()
def running_dags() -> Dict[str, Any]:
    """
    [Tool Role]: Lists all currently running DAG runs in the Airflow cluster.

    Returns:
        List of running DAG runs with minimal info: dag_id, run_id, state, execution_date, start_date, end_date
    """
    dags_resp = airflow_request("GET", "/dags")
    dags_resp.raise_for_status()
    dags = dags_resp.json().get("dags", [])
    running = []
    for dag in dags:
        dag_id = dag.get("dag_id")
        if not dag_id:
            continue
        runs_resp = airflow_request("GET", f"/dags/{dag_id}/dagRuns")
        runs_resp.raise_for_status()
        runs = runs_resp.json().get("dag_runs", [])
        for run in runs:
            if run.get("state") == "running":
                running.append({
                    "dag_id": dag_id,
                    "run_id": run.get("run_id"),
                    "state": run.get("state"),
                    "execution_date": run.get("execution_date"),
                    "start_date": run.get("start_date"),
                    "end_date": run.get("end_date")
                })
    return {"dag_runs": running}

@mcp.tool()
def failed_dags() -> Dict[str, Any]:
    """
    [Tool Role]: Lists all recently failed DAG runs in the Airflow cluster.

    Returns:
        List of failed DAG runs with minimal info: dag_id, run_id, state, execution_date, start_date, end_date
    """
    dags_resp = airflow_request("GET", "/dags")
    dags_resp.raise_for_status()
    dags = dags_resp.json().get("dags", [])
    failed = []
    for dag in dags:
        dag_id = dag.get("dag_id")
        if not dag_id:
            continue
        runs_resp = airflow_request("GET", f"/dags/{dag_id}/dagRuns")
        runs_resp.raise_for_status()
        runs = runs_resp.json().get("dag_runs", [])
        for run in runs:
            if run.get("state") == "failed":
                failed.append({
                    "dag_id": dag_id,
                    "run_id": run.get("run_id"),
                    "state": run.get("state"),
                    "execution_date": run.get("execution_date"),
                    "start_date": run.get("start_date"),
                    "end_date": run.get("end_date")
                })
    return {"dag_runs": failed}

@mcp.tool()
def trigger_dag(dag_id: str) -> Dict[str, Any]:
    """
    [Tool Role]: Triggers a new DAG run for a specified Airflow DAG.

    Args:
        dag_id: The DAG ID to trigger

    Returns:
        Minimal info about triggered DAG run: dag_id, run_id, state, execution_date, start_date, end_date
    """
    if not dag_id:
        raise ValueError("dag_id must not be empty")
    resp = airflow_request("POST", f"/dags/{dag_id}/dagRuns", json={"conf": {}})
    resp.raise_for_status()
    run = resp.json()
    return {
        "dag_id": dag_id,
        "run_id": run.get("run_id"),
        "state": run.get("state"),
        "execution_date": run.get("execution_date"),
        "start_date": run.get("start_date"),
        "end_date": run.get("end_date")
    }

#========================================================================================

def main(argv: Optional[List[str]] = None):
    """Entrypoint for MCP Airflow API server.

    Supports optional CLI arguments (e.g. --log-level DEBUG) while remaining
    backward-compatible with stdio launcher expectations.
    """
    parser = argparse.ArgumentParser(prog="mcp-airflow-api", description="MCP Airflow API Server")
    parser.add_argument(
        "--log-level", "-l",
        dest="log_level",
        help="Logging level override (DEBUG, INFO, WARNING, ERROR, CRITICAL). Overrides AIRFLOW_LOG_LEVEL env if provided.",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    # Allow future extension without breaking unknown args usage
    args = parser.parse_args(argv)

    if args.log_level:
        # Override root + specific logger level
        logging.getLogger().setLevel(args.log_level)
        logger.setLevel(args.log_level)
        logging.getLogger("requests.packages.urllib3").setLevel("WARNING")  # reduce noise at DEBUG
        logger.info("Log level set via CLI to %s", args.log_level)
    else:
        logger.debug("Log level from environment: %s", logging.getLogger().level)

    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()

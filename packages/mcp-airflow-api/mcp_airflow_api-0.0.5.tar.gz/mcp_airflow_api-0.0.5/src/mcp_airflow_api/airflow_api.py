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
    """List DAGs in the Airflow cluster."""
    resp = airflow_request("GET", "/dags")
    resp.raise_for_status()
    return resp.json()

@mcp.tool()
def running_dags() -> Dict[str, Any]:
    """List currently running DAGs."""
    resp = airflow_request("GET", "/dags?state=running")
    resp.raise_for_status()
    return resp.json()

@mcp.tool()
def failed_dags() -> Dict[str, Any]:
    """List recently failed DAGs."""
    resp = airflow_request("GET", "/dags?state=failed")
    resp.raise_for_status()
    return resp.json()

@mcp.tool()
def trigger_dag(dag_id: str) -> Dict[str, Any]:
    """Trigger a DAG run by dag_id."""
    resp = airflow_request("POST", f"/dags/{dag_id}/dagRuns")
    resp.raise_for_status()
    return resp.json()

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

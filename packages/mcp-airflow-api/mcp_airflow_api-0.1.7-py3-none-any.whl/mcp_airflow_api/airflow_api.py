"""
MCP tool definitions for Airflow REST API operations.
"""
import argparse
import logging
from typing import Any, Dict, List, Optional
import mcp
from mcp.server.fastmcp import FastMCP
import os
from .functions import airflow_request, read_prompt_template, parse_prompt_sections

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


# MCP server instance for registering tools
mcp = FastMCP("mcp-airflow-api")

PROMPT_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "prompt_template.md")



@mcp.tool()
def get_prompt_template(section: Optional[str] = None, mode: Optional[str] = None) -> str:
    """
    Returns the MCP prompt template (full, headings, or specific section).
    Args:
        section: Section number or keyword (optional)
        mode: 'full', 'headings', or None (optional)
    """
    template = read_prompt_template(PROMPT_TEMPLATE_PATH)
    
    if mode == "headings":
        headings, _ = parse_prompt_sections(template)
        lines = ["Section Headings:"]
        for idx, title in enumerate(headings, 1):
            lines.append(f"{idx}. {title}")
        return "\n".join(lines)
    
    if section:
        headings, sections = parse_prompt_sections(template)
        # Try by number
        try:
            idx = int(section) - 1
            if 0 <= idx < len(sections):
                return sections[idx]
        except Exception:
            pass
        # Try by keyword
        section_lower = section.strip().lower()
        for i, heading in enumerate(headings):
            if section_lower in heading.lower():
                return sections[i]
        return f"Section '{section}' not found."
    
    return template

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

@mcp.tool()
def pause_dag(dag_id: str) -> Dict[str, Any]:
    """
    [Tool Role]: Pauses the specified Airflow DAG (prevents scheduling new runs).

    Args:
        dag_id: The DAG ID to pause

    Returns:
        Minimal info about the paused DAG: dag_id, is_paused
    """
    if not dag_id:
        raise ValueError("dag_id must not be empty")
    resp = airflow_request("PATCH", f"/dags/{dag_id}", json={"is_paused": True})
    resp.raise_for_status()
    dag = resp.json()
    return {"dag_id": dag.get("dag_id", dag_id), "is_paused": dag.get("is_paused", True)}

@mcp.tool()
def unpause_dag(dag_id: str) -> Dict[str, Any]:
    """
    [Tool Role]: Unpauses the specified Airflow DAG (allows scheduling new runs).

    Args:
        dag_id: The DAG ID to unpause

    Returns:
        Minimal info about the unpaused DAG: dag_id, is_paused
    """
    if not dag_id:
        raise ValueError("dag_id must not be empty")
    resp = airflow_request("PATCH", f"/dags/{dag_id}", json={"is_paused": False})
    resp.raise_for_status()
    dag = resp.json()
    return {"dag_id": dag.get("dag_id", dag_id), "is_paused": dag.get("is_paused", False)}

#========================================================================================
# MCP Prompts (for prompts/list exposure)
#========================================================================================

@mcp.prompt("prompt_template_full")
def prompt_template_full_prompt() -> str:
    """Return the full canonical prompt template."""
    return read_prompt_template(PROMPT_TEMPLATE_PATH)

@mcp.prompt("prompt_template_headings")
def prompt_template_headings_prompt() -> str:
    """Return compact list of section headings."""
    template = read_prompt_template(PROMPT_TEMPLATE_PATH)
    headings, _ = parse_prompt_sections(template)
    lines = ["Section Headings:"]
    for idx, title in enumerate(headings, 1):
        lines.append(f"{idx}. {title}")
    return "\n".join(lines)

@mcp.prompt("prompt_template_section")
def prompt_template_section_prompt(section: Optional[str] = None) -> str:
    """Return a specific prompt template section by number or keyword."""
    if not section:
        headings_result = prompt_template_headings_prompt()
        return "\n".join([
            "[HELP] Missing 'section' argument.",
            "Specify a section number or keyword.",
            "Examples: 1 | overview | tool map | usage",
            headings_result.strip()
        ])
    return get_prompt_template(section=section)

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

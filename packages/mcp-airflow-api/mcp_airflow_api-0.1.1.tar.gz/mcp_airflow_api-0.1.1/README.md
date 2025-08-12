Model Context Protocol (MCP) server for Apache Airflow API integration.  
This project provides natural language MCP tools for essential Airflow cluster operations.

[![Deploy to PyPI with tag](https://github.com/call518/MCP-Airflow-API/actions/workflows/pypi-publish.yml/badge.svg)](https://github.com/call518/MCP-Airflow-API/actions/workflows/pypi-publish.yml)

[![smithery badge](https://smithery.ai/badge/@call518/mcp-airflow-api)](https://smithery.ai/server/@call518/mcp-airflow-api)

---


# MCP-Airflow-API

**Tested and supported Airflow version: 2.10.2**

## Features

- List all DAGs in the Airflow cluster
- Monitor running/failed DAG runs
- Trigger DAG runs on demand
- Minimal, LLM-friendly output for all tools
- Easy integration with MCP Inspector, OpenWebUI, Smithery, etc.

---

## Available MCP Tools

### DAG Management

- `list_dags`  
	Returns all DAGs registered in the Airflow cluster.  
	Output: `dag_id`, `dag_display_name`, `is_active`, `is_paused`, `owners`, `tags`

- `running_dags`  
	Returns all currently running DAG runs.  
	Output: `dag_id`, `run_id`, `state`, `execution_date`, `start_date`, `end_date`

- `failed_dags`  
	Returns all recently failed DAG runs.  
	Output: `dag_id`, `run_id`, `state`, `execution_date`, `start_date`, `end_date`

- `trigger_dag(dag_id)`  
	Immediately triggers the specified DAG.  
	Output: `dag_id`, `run_id`, `state`, `execution_date`, `start_date`, `end_date`

---

## Main Tool Files

- MCP tool definitions: `src/mcp_airflow_api/airflow_api.py`
- Utility functions: `src/mcp_airflow_api/functions.py`

---

## How To Use

1. In your MCP Tools environment, configure `mcp-config.json` as follows:

```json
{
	"mcpServers": {
		"airflow-api": {
			"command": "uvx",
			"args": ["--python", "3.11", "mcp-airflow-api"],
			"env": {
				"AIRFLOW_API_URL": "http://localhost:38080/api/v1",
				"AIRFLOW_API_USERNAME": "airflow",
				"AIRFLOW_API_PASSWORD": "airflow",
				"AIRFLOW_LOG_LEVEL": "INFO"
			}
		}
	}
}
```

2. Register the MCP server in MCP Inspector, OpenWebUI, Smithery, etc. and use the tools.

---

## QuickStart (Demo): Running MCP-Airflow-API with Docker

1. Prepare an Airflow cluster  
	 - See [Official Airflow Docker Install Guide](https://airflow.apache.org/docs/apache-airflow/stable/start/docker.html)

2. Prepare MCP Tools environment  
	 - Install Docker and Docker Compose
	 - Clone this project and run `docker-compose up -d` in the root directory

3. Register the MCP server in MCP Inspector/Smithery  
	 - Example address: `http://localhost:8000/airflow-api`

---

## Logging & Observability

- Structured logs for all tool invocations and HTTP requests
- Control log level via environment variable (`AIRFLOW_LOG_LEVEL`) or CLI flag (`--log-level`)
- Supported levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

---

## License

This project is licensed under the MIT License.

---

## Roadmap

This project starts with a minimal set of essential Airflow management tools. Many more useful features and tools for Airflow cluster operations will be added soon, including advanced monitoring, DAG/task analytics, scheduling controls, and more. Contributions and suggestions are welcome!

---

## Additional Links

- [Code](https://github.com/call518/MCP-Airflow-API)
- [Issues](https://github.com/call518/MCP-Airflow-API/issues)
- [Smithery Deployment](https://smithery.ai/server/@call518/mcp-airflow-api)


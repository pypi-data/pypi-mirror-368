# MCP Airflow API Prompt Template

## 1. Overview

This MCP server provides natural language tools for managing Apache Airflow clusters via REST API. All prompts and tool outputs are designed for minimal, LLM-friendly English responses.

## 2. Available MCP Tools

- `list_dags`: List all DAGs in the Airflow cluster.
- `running_dags`: List all currently running DAG runs.
- `failed_dags`: List all recently failed DAG runs.
- `trigger_dag(dag_id)`: Trigger a DAG run by ID.
- `pause_dag(dag_id)`: Pause a DAG (prevent scheduling).
- `unpause_dag(dag_id)`: Unpause a DAG (allow scheduling).

## 3. Tool Map

| Tool Name      | Role/Description                          | Input Args      | Output Fields                        |
|----------------|-------------------------------------------|-----------------|--------------------------------------|
| list_dags      | List all DAGs                             | None            | dag_id, dag_display_name, is_active, is_paused, owners, tags |
| running_dags   | List running DAG runs                     | None            | dag_id, run_id, state, execution_date, start_date, end_date |
| failed_dags    | List failed DAG runs                      | None            | dag_id, run_id, state, execution_date, start_date, end_date |
| trigger_dag    | Trigger a DAG run                         | dag_id (str)    | dag_id, run_id, state, execution_date, start_date, end_date |
| pause_dag      | Pause a DAG                               | dag_id (str)    | dag_id, is_paused                    |
| unpause_dag    | Unpause a DAG                             | dag_id (str)    | dag_id, is_paused                    |

## 4. Usage Guidelines

- Always use minimal, structured output.
- All tool invocations must use English for internal reasoning.
- For user-facing responses, translate to the user's language if needed.

## 5. Example Queries

- "List all DAGs."
- "Show running DAGs."
- "Trigger DAG 'example_dag'."
- "Pause DAG 'etl_job'."
- "Unpause DAG 'etl_job'."

## 6. Formatting Rules

- Output only the requested fields.
- No extra explanation unless explicitly requested.
- Use JSON objects for tool outputs.

## 7. Logging & Environment

- Control log level via AIRFLOW_LOG_LEVEL env or --log-level CLI flag.
- Supported levels: DEBUG, INFO, WARNING, ERROR, CRITICAL.

## 8. References

- Main MCP tool file: `src/mcp_airflow_api/airflow_api.py`
- Utility functions: `src/mcp_airflow_api/functions.py`
- See README.md for full usage and configuration.

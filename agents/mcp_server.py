"""
ORBIT Model Context Protocol (MCP) Server
Standardized tool interface exposing enterprise operations tools to LLMs and Agents.
Exposes: run_sql, get_lineage, rerun_task, quarantine_batch, get_metrics.
"""
from typing import Dict, Any, List
import json
from .tools import OrbitTools


class OrbitMCPServer:
    """Model Context Protocol server for autonomous data operations tools."""

    def __init__(self, db_path: str = None):
        self.tools = OrbitTools(db_path=db_path) if db_path else OrbitTools()

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Returns standard MCP tool schemas."""
        return [
            {
                "name": "run_sql",
                "description": "Execute a SQL query against the DuckDB analytical engine for investigation or remediation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The exact SQL statement to execute."
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_lineage",
                "description": "Fetch the complete 3D dependency lineage graph with node health scores, active faults, and throughput.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "rerun_task",
                "description": "Re-execute materialization and data transformations for a specific pipeline node.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "node_id": {
                            "type": "string",
                            "description": "Identifier of the pipeline node to rerun."
                        }
                    },
                    "required": ["node_id"]
                }
            },
            {
                "name": "quarantine_batch",
                "description": "Quarantine invalid, corrupted, or schema-breaking records to prevent downstream failure.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "The target table containing corrupted records."
                        },
                        "filter_condition": {
                            "type": "string",
                            "description": "SQL WHERE clause identifying corrupted records (e.g. 'amount IS NULL' or 'amount < 0')."
                        }
                    },
                    "required": ["table_name", "filter_condition"]
                }
            },
            {
                "name": "get_metrics",
                "description": "Get current throughput, error rate, p95 latency, and SLA compliance for an enterprise pipeline.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pipeline_id": {
                            "type": "string",
                            "description": "Domain pipeline identifier: 'banking', 'retail', 'supply_chain', or 'customer'."
                        }
                    },
                    "required": ["pipeline_id"]
                }
            }
        ]

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatches an MCP tool call and returns the execution result."""
        if tool_name == "run_sql":
            return self.tools.run_sql(arguments.get("query", ""))
        elif tool_name == "get_lineage":
            return self.tools.get_lineage()
        elif tool_name == "rerun_task":
            return self.tools.rerun_task(arguments.get("node_id", ""))
        elif tool_name == "quarantine_batch":
            return self.tools.quarantine_batch(
                arguments.get("table_name", ""),
                arguments.get("filter_condition", "")
            )
        elif tool_name == "get_metrics":
            return self.tools.get_metrics(arguments.get("pipeline_id", "banking"))
        else:
            return {
                "status": "error",
                "error": f"Tool '{tool_name}' not recognized by ORBIT MCP server."
            }

"""
Mode-based selection and filtering of MCP function-tools per server.
"""

from typing import List

from agents.mcp import MCPServer
from agents.mcp.util import MCPUtil
from agents.tool import Tool

from oai_coding_agent.runtime_config import RuntimeConfig


def _filter_tools_for_mode(
    server_name: str, tools: List[Tool], config: RuntimeConfig
) -> List[Tool]:
    """
    Apply mode-specific filtering rules for a given MCP server's tools.

    Note: The atlassian-mcp server is only started when in plan mode and atlassian flag is set.
    """
    mode = config.mode.value
    # File-system MCP: remove edit_file in plan mode
    if server_name == "file-system-mcp":
        if mode == "plan":
            return [t for t in tools if t.name != "edit_file"]

    # Git MCP server: restrict to a whitelist in plan mode (adjust as needed)
    if server_name == "mcp-server-git":
        if mode == "plan":
            allowed = {"clone_repo", "list_branches"}
            return [t for t in tools if t.name in allowed]

    # Atlassian MCP server: only allow when in plan mode and atlassian flag is set
    if server_name == "atlassian-mcp":
        if mode != "plan" or not config.atlassian:
            # Remove all tools if not in plan mode or atlassian flag not set
            return []
        # In plan mode with atlassian flag, allow all tools
        return tools

    # GitHub MCP server: restrict to a whitelist of allowed tools
    if server_name == "github-mcp-server":
        # Read-only commands only in plan mode
        if mode == "plan":
            readonly_allowed = {
                "get_issue",
                "get_issue_comments",
                "create_issue",
                "list_issues",
                "search_issues",
                "get_pull_request",
                "list_pull_requests",
                "get_pull_request_files",
                "get_pull_request_status",
                "get_pull_request_comments",
                "get_pull_request_reviews",
            }
            return [t for t in tools if t.name in readonly_allowed]
        # Full whitelist including create/update in non-plan modes
        allowed = {
            "get_issue",
            "get_issue_comments",
            "create_issue",
            "add_issue_comment",
            "list_issues",
            "update_issue",
            "search_issues",
            "get_pull_request",
            "list_pull_requests",
            "get_pull_request_files",
            "get_pull_request_status",
            "update_pull_request_branch",
            "get_pull_request_comments",
            "get_pull_request_reviews",
            "create_pull_request",
            "add_pull_request_review_comment",
            "update_pull_request",
        }
        return [t for t in tools if t.name in allowed]

    # No filtering by default
    return tools


async def get_filtered_function_tools(
    servers: list[MCPServer],
    config: RuntimeConfig,
    convert_schemas_to_strict: bool = False,
) -> List[Tool]:
    """
    Fetch all function tools from MCP servers, apply mode-specific filters, and return the combined list.

    Args:
        servers: List of connected MCPServer instances.
        config: The runtime configuration containing mode and atlassian flag.
        convert_schemas_to_strict: Whether to coerce input schemas to strict JSON schemas.
    Returns:
        A flattened list of filtered FunctionTool objects ready to attach to an Agent.
    """
    filtered_tools: List[Tool] = []
    for server in servers:
        server_tools = await MCPUtil.get_function_tools(
            server, convert_schemas_to_strict
        )
        server_tools = _filter_tools_for_mode(server.name, server_tools, config)
        filtered_tools.extend(server_tools)
    return filtered_tools

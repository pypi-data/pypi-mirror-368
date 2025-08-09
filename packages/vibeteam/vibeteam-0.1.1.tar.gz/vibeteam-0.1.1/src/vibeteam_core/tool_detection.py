"""
Runtime tool detection for adapting agent behavior to different coding environments.
"""

import os
import sys
from enum import Enum
from pathlib import Path
from typing import Any, Dict


class CodingTool(Enum):
    """Detected coding tools/environments."""

    CURSOR = "cursor"
    WINDSURF = "windsurf"
    VSCODE = "vscode"
    CLAUDE_DESKTOP = "claude_desktop"
    CLI = "cli"
    UNKNOWN = "unknown"


class ToolDetector:
    """Detects which coding tool is using the MCP server."""

    @staticmethod
    def detect_current_tool() -> CodingTool:
        """Detect the current tool based on environment variables and process context."""

        # Check environment variables that tools might set
        if os.getenv("CURSOR_SESSION") or os.getenv("CURSOR_USER_DATA_DIR"):
            return CodingTool.CURSOR

        if os.getenv("WINDSURF_SESSION") or os.getenv("WINDSURF_USER_DATA_DIR"):
            return CodingTool.WINDSURF

        if os.getenv("VSCODE_PID") or os.getenv("TERM_PROGRAM") == "vscode":
            return CodingTool.VSCODE

        if os.getenv("CLAUDE_DESKTOP"):
            return CodingTool.CLAUDE_DESKTOP

        # Check process ancestry (parent process names)
        try:
            import psutil

            current_process = psutil.Process()

            # Walk up the process tree
            for parent in current_process.parents():
                parent_name = parent.name().lower()

                if "cursor" in parent_name:
                    return CodingTool.CURSOR
                elif "windsurf" in parent_name:
                    return CodingTool.WINDSURF
                elif "code" in parent_name and "vscode" in parent_name:
                    return CodingTool.VSCODE
                elif "claude" in parent_name:
                    return CodingTool.CLAUDE_DESKTOP

        except (ImportError, Exception):
            # psutil not available or error accessing process info
            pass

        # Check if running via MCP (stdio mode indicates MCP usage)
        if not sys.stdin.isatty() and not sys.stdout.isatty():
            # Running via MCP, but can't determine specific tool
            # Check for tool-specific config files in parent directories
            cwd = Path.cwd()

            for parent in [cwd] + list(cwd.parents):
                if (parent / ".cursor").exists():
                    return CodingTool.CURSOR
                elif (parent / ".windsurf").exists():
                    return CodingTool.WINDSURF
                elif (parent / ".vscode").exists():
                    return CodingTool.VSCODE

            return CodingTool.CLAUDE_DESKTOP  # Default for MCP

        return CodingTool.CLI

    @staticmethod
    def get_tool_capabilities(tool: CodingTool) -> Dict[str, Any]:
        """Get capabilities specific to each tool."""
        capabilities = {
            CodingTool.CURSOR: {
                "real_time_editing": True,
                "multi_file_operations": True,
                "ide_integration": True,
                "git_integration": True,
                "terminal_access": True,
                "debugging": True,
                "code_completion": True,
                "refactoring_tools": True,
                "preferred_agents": ["backend", "frontend", "refactor", "analyzer"],
                "agent_style": "interactive",
                "response_format": "structured_suggestions",
            },
            CodingTool.WINDSURF: {
                "real_time_editing": True,
                "multi_file_operations": True,
                "ide_integration": True,
                "workflow_automation": True,
                "preferred_agents": ["fullstack", "analyzer", "tester"],
                "agent_style": "workflow_focused",
                "response_format": "step_by_step",
            },
            CodingTool.VSCODE: {
                "real_time_editing": True,
                "multi_file_operations": True,
                "ide_integration": True,
                "extension_ecosystem": True,
                "debugging": True,
                "preferred_agents": ["backend", "frontend", "tester"],
                "agent_style": "extension_compatible",
                "response_format": "actionable_items",
            },
            CodingTool.CLAUDE_DESKTOP: {
                "file_operations": True,
                "web_browsing": True,
                "research_capabilities": True,
                "preferred_agents": ["researcher", "analyzer", "documentation"],
                "agent_style": "conversational",
                "response_format": "detailed_explanation",
            },
            CodingTool.CLI: {
                "terminal_access": True,
                "file_operations": True,
                "git_integration": True,
                "preferred_agents": ["devops", "analyzer"],
                "agent_style": "command_focused",
                "response_format": "terminal_friendly",
            },
        }

        return capabilities.get(tool, {})

    @staticmethod
    def adapt_agent_response(tool: CodingTool, agent_result: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt agent response format based on the detected tool."""
        capabilities = ToolDetector.get_tool_capabilities(tool)
        response_format = capabilities.get("response_format", "default")

        if response_format == "structured_suggestions":
            # Cursor prefers structured suggestions with clear actions
            return {
                "suggestions": agent_result.get("recommendations", []),
                "actions": agent_result.get("next_actions", []),
                "context": agent_result.get("context", {}),
                "files_to_modify": agent_result.get("files", []),
                "reasoning": agent_result.get("reasoning", ""),
            }

        elif response_format == "step_by_step":
            # Windsurf prefers step-by-step workflows
            return {
                "workflow": {
                    "steps": agent_result.get("next_actions", []),
                    "context": agent_result.get("context", {}),
                    "dependencies": agent_result.get("dependencies", []),
                },
                "recommendations": agent_result.get("recommendations", []),
            }

        elif response_format == "actionable_items":
            # VS Code prefers clear actionable items
            return {
                "actions": [
                    {"type": "edit", "file": f, "description": desc}
                    for f, desc in zip(
                        agent_result.get("files", []), agent_result.get("descriptions", [])
                    )
                ],
                "insights": agent_result.get("recommendations", []),
            }

        elif response_format == "detailed_explanation":
            # Claude Desktop prefers detailed explanations
            return {
                "explanation": agent_result.get("reasoning", ""),
                "analysis": agent_result.get("analysis", {}),
                "recommendations": agent_result.get("recommendations", []),
                "next_steps": agent_result.get("next_actions", []),
            }

        elif response_format == "terminal_friendly":
            # CLI prefers concise, terminal-friendly output
            return {
                "summary": agent_result.get("summary", ""),
                "commands": agent_result.get("commands", []),
                "files": agent_result.get("files", []),
            }

        return agent_result

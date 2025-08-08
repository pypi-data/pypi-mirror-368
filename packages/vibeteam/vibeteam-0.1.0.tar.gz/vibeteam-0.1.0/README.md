# Vibeteam

An MCP (Model Context Protocol) server that intelligently orchestrates sub-agents based on query analysis and project context.

## Features

- **Query Analysis**: Understands user intent (build, debug, feature, refactor, research, etc.)
- **Project Detection**: Automatically identifies project type (backend, frontend, fullstack, library)
- **Smart Agent Orchestration**: Deploys specialized agents based on project context and query intent
- **Multi-Agent Support**:
  - Backend Specialist
  - Frontend Specialist
  - Web Researcher
  - Code Analyzer
  - Test Engineer
  - DevOps Specialist

## Installation

### Via uvx (Recommended)

Once published to PyPI, you can install and run directly with uvx:

```bash
uvx vibeteam
```

### Via pip

```bash
pip install vibeteam
```

### From Source

```bash
git clone https://github.com/XiaoConstantine/vibeteam.git
cd vibeteam
uv sync
uv run vibeteam
```

## MCP Configuration

Add to your Claude Desktop or MCP client configuration:

```json
{
  "servers": {
    "vibeteam": {
      "command": "uvx",
      "args": ["vibeteam"]
    }
  }
}
```

Or if installed via pip:

```json
{
  "servers": {
    "vibeteam": {
      "command": "vibeteam"
    }
  }
}
```

## Usage

### As MCP Server

The server runs as an MCP server and exposes tools for Claude or other MCP clients:

```bash
# Run with uvx
uvx vibeteam

# Or if installed
vibeteam
```

### Testing

```bash
uv run python test_server.py
```

## Tools Available

1. **analyze_and_orchestrate**: Main orchestration tool that analyzes query and deploys agents
2. **analyze_project**: Analyzes project structure and technology stack
3. **analyze_query**: Determines query intent and complexity

## How It Works

1. **Project Analysis**: Scans the current working directory to understand project structure
2. **Query Understanding**: Analyzes user query to determine intent and complexity
3. **Agent Planning**: Based on project type and query intent, plans appropriate agents
4. **Orchestration**: Executes agents in priority order and collects results
5. **Summary**: Provides consolidated output from all agents

## Architecture

The orchestrator uses a sophisticated analysis system to:
- Detect backend (Python, Go, Java, etc.) and frontend (React, Vue, Angular) technologies
- Understand query complexity and required expertise
- Deploy agents with appropriate priority levels
- Coordinate multi-agent workflows for complex tasks

#!/usr/bin/env python3
"""
Claude Code Sub-Agent Integration for MCP Server

This module shows how to format MCP responses to trigger Claude Code's Task tool
for creating sub-agents.
"""

from typing import Any, Dict, List


def format_for_claude_task_tool(agents: List[Dict[str, Any]]) -> str:
    """
    Format agent dispatch instructions for Claude Code's Task tool.

    Claude Code will recognize these patterns and can use its Task tool
    to create actual sub-agents.
    """

    instructions = []

    for agent in agents:
        agent_type = agent.get("agent_type", "general-purpose")
        task = agent.get("task", "")
        context = agent.get("dispatch_instruction", {}).get("context", {})

        # Create instruction that Claude will recognize
        instruction = f"""
[AGENT REQUEST: {agent_type}]
Task: {task}
Context: Working in {context.get("cwd", "current directory")}
Technologies: {", ".join(context.get("technologies", ["Not specified"]))}
Priority: {agent.get("priority", 5)}/10

Please use the Task tool with subagent_type='general-purpose' to handle this specialized task.
The agent should focus on {agent_type.replace("_", " ")} aspects.
"""
        instructions.append(instruction.strip())

    return "\n\n".join(instructions)


def create_agent_dispatch_response(result: Dict[str, Any]) -> str:
    """
    Create a response that will trigger Claude to use its Task tool.
    """

    agents = result.get("agent_results", [])

    if not agents:
        return "No agents needed for this task."

    response = f"""Based on my analysis, I need to deploy {len(agents)} specialized agents for this task.

{format_for_claude_task_tool(agents)}

## How Claude Code can execute these:

1. Use the Task tool with subagent_type='general-purpose' for each agent
2. Each agent gets a specialized prompt based on their role
3. Agents can work in parallel for efficiency

## Project Context:
- Type: {result.get("project_context", {}).get("type", "Unknown")}
- Technologies: {", ".join(result.get("project_context", {}).get("technologies", []))}
- Query Intent: {", ".join(result.get("query_analysis", {}).get("intents", []))}

Would you like me to execute these agents using the Task tool?"""

    return response


def create_task_tool_instructions(
    agent_type: str, task: str, context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create instructions that match Claude Code's Task tool parameters.

    Returns a dict with:
    - description: Short description for the task
    - prompt: Detailed prompt for the agent
    - subagent_type: Always 'general-purpose' for Claude Code
    """

    descriptions = {
        "backend_specialist": "Backend API implementation",
        "frontend_specialist": "Frontend UI development",
        "web_researcher": "Research best practices",
        "code_analyzer": "Analyze codebase",
        "test_engineer": "Create test suite",
        "devops_specialist": "Setup deployment",
    }

    prompts = {
        "backend_specialist": f"""You are a backend specialist working on: {task}
        
Analyze the requirements and:
1. Design RESTful API endpoints
2. Implement database schemas
3. Add authentication/authorization
4. Optimize performance
5. Ensure security best practices

Project context:
- Directory: {context.get("cwd")}
- Technologies: {", ".join(context.get("technologies", []))}
- Type: {context.get("type")}

Provide specific implementation details and code examples.""",
        "frontend_specialist": f"""You are a frontend specialist working on: {task}

Focus on:
1. Component architecture
2. State management
3. User experience
4. Performance optimization
5. Accessibility

Project context:
- Directory: {context.get("cwd")}
- Technologies: {", ".join(context.get("technologies", []))}
- Type: {context.get("type")}

Provide specific UI/UX solutions and component implementations.""",
        "web_researcher": f"""Research the following: {task}

Find:
1. Current best practices
2. Similar implementations
3. Documentation and tutorials
4. Performance benchmarks
5. Security considerations

Keywords to research: {", ".join(context.get("keywords", []))}

Provide links, examples, and actionable recommendations.""",
        "code_analyzer": f"""Analyze the codebase for: {task}

Review:
1. Code structure and organization
2. Potential bugs and issues
3. Performance bottlenecks
4. Security vulnerabilities
5. Refactoring opportunities

Codebase location: {context.get("cwd")}
Technologies: {", ".join(context.get("technologies", []))}

Provide specific findings and improvement suggestions.""",
        "test_engineer": f"""Create test strategy for: {task}

Develop:
1. Unit test cases
2. Integration tests
3. End-to-end test scenarios
4. Performance tests
5. Test coverage analysis

Project type: {context.get("type")}
Technologies: {", ".join(context.get("technologies", []))}

Provide test implementations and coverage reports.""",
        "devops_specialist": f"""Setup deployment for: {task}

Configure:
1. CI/CD pipelines
2. Container orchestration
3. Monitoring and logging
4. Security scanning
5. Infrastructure as code

Project: {context.get("cwd")}
Type: {context.get("type")}

Provide deployment configurations and automation scripts.""",
    }

    return {
        "description": descriptions.get(agent_type, "Execute specialized task"),
        "prompt": prompts.get(agent_type, f"Work on: {task}"),
        "subagent_type": "general-purpose",  # Claude Code's agent type
    }

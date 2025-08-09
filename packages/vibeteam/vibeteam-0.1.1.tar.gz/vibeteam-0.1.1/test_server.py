#!/usr/bin/env python3
import asyncio
import json
from pathlib import Path
from src import ProjectAnalyzer, QueryAnalyzer, AgentOrchestrator


async def test_orchestrator():
    print("Testing VibeteamHub Orchestrator\n")
    print("=" * 50)

    cwd = Path.cwd()
    print(f"Current directory: {cwd}\n")

    print("1. Project Analysis:")
    print("-" * 30)
    project_type = ProjectAnalyzer.detect_project_type(cwd)
    context = ProjectAnalyzer.get_project_context(cwd)
    print(f"Project Type: {project_type.value}")
    print(f"Technologies detected: {', '.join(context['technologies'])}")
    print(f"Files found: {len(context['files'])}")
    print(f"Directory structure: {json.dumps(context['structure'], indent=2)}\n")

    test_queries = [
        "Help me implement a new user authentication feature",
        "Debug the API endpoint that's returning 500 errors",
        "Research best practices for React performance optimization",
        "Refactor the database connection logic",
        "Deploy the application to production",
    ]

    print("2. Query Analysis & Orchestration:")
    print("-" * 30)

    orchestrator = AgentOrchestrator()

    for query in test_queries:
        print(f"\nQuery: '{query}'")
        analysis = QueryAnalyzer.analyze_query(query)
        print(f"  Intents: {', '.join(analysis['intents'])}")
        print(f"  Needs web research: {analysis['needs_web_research']}")
        print(f"  Complexity: {analysis['complexity']}/3")

        agents = orchestrator.plan_agents(query, cwd)
        print(f"  Agents planned: {len(agents)}")
        for agent in agents:
            print(f"    - {agent.type.value} (priority: {agent.priority})")

    print("\n3. Full Orchestration Test:")
    print("-" * 30)
    test_query = "Build a REST API with authentication and implement frontend dashboard"
    print(f"Executing full orchestration for: '{test_query}'")

    result = await orchestrator.orchestrate(test_query, cwd)
    print("\nOrchestration Results:")
    print(f"  Agents deployed: {result['agents_deployed']}")
    print(f"  Summary: {result['summary']}")

    print("\n" + "=" * 50)
    print("Test completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_orchestrator())

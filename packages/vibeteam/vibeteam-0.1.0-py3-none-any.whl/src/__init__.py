#!/usr/bin/env python3
import asyncio
import json
import os
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel, Field

from .claude_integration import (
    create_agent_dispatch_response,
)


class ProjectType(Enum):
    BACKEND = "backend"
    FRONTEND = "frontend"
    FULLSTACK = "fullstack"
    LIBRARY = "library"
    UNKNOWN = "unknown"


class QueryIntent(Enum):
    BUILD = "build"
    DEBUG = "debug"
    FEATURE = "feature"
    REFACTOR = "refactor"
    RESEARCH = "research"
    ANALYZE = "analyze"
    TEST = "test"
    DEPLOY = "deploy"


class AgentType(Enum):
    BACKEND = "backend_specialist"
    FRONTEND = "frontend_specialist"
    FULLSTACK = "fullstack_engineer"
    RESEARCHER = "web_researcher"
    ANALYZER = "code_analyzer"
    TESTER = "test_engineer"
    DEVOPS = "devops_specialist"


class SubAgent(BaseModel):
    type: AgentType
    task: str
    context: Dict[str, Any]
    priority: int = Field(default=0, ge=0, le=10)
    status: str = Field(default="pending")
    result: Optional[Dict[str, Any]] = None


class ProjectAnalyzer:
    @staticmethod
    def detect_project_type(cwd: Path) -> ProjectType:
        files = list(cwd.glob("*"))
        file_names = [f.name for f in files]

        indicators = {
            "backend": [
                "requirements.txt",
                "Pipfile",
                "go.mod",
                "pom.xml",
                "build.gradle",
                "Cargo.toml",
                "api/",
                "server/",
                "backend/",
            ],
            "frontend": [
                "package.json",
                "index.html",
                "src/App.js",
                "src/App.tsx",
                "angular.json",
                "vue.config.js",
                "frontend/",
                "client/",
            ],
            "fullstack": ["docker-compose.yml", "Dockerfile"],
        }

        backend_score = sum(
            1 for ind in indicators["backend"] if any(ind in str(f) for f in file_names)
        )
        frontend_score = sum(
            1 for ind in indicators["frontend"] if any(ind in str(f) for f in file_names)
        )
        fullstack_score = sum(
            1 for ind in indicators["fullstack"] if any(ind in str(f) for f in file_names)
        )

        if fullstack_score > 0 or (backend_score > 0 and frontend_score > 0):
            return ProjectType.FULLSTACK
        elif backend_score > frontend_score:
            return ProjectType.BACKEND
        elif frontend_score > backend_score:
            return ProjectType.FRONTEND
        elif any(f.suffix in [".py", ".js", ".ts", ".go", ".rs", ".java"] for f in files):
            return ProjectType.LIBRARY
        else:
            return ProjectType.UNKNOWN

    @staticmethod
    def get_project_context(cwd: Path) -> Dict[str, Any]:
        context = {
            "cwd": str(cwd),
            "type": ProjectAnalyzer.detect_project_type(cwd).value,
            "files": [],
            "technologies": [],
            "structure": {},
        }

        tech_indicators = {
            "Python": ["*.py", "requirements.txt", "setup.py", "pyproject.toml"],
            "JavaScript": ["*.js", "*.jsx", "package.json"],
            "TypeScript": ["*.ts", "*.tsx", "tsconfig.json"],
            "Go": ["*.go", "go.mod"],
            "Rust": ["*.rs", "Cargo.toml"],
            "Java": ["*.java", "pom.xml", "build.gradle"],
            "React": ["package.json", "src/App.js", "src/App.tsx"],
            "Vue": ["vue.config.js", "*.vue"],
            "Angular": ["angular.json"],
            "Django": ["manage.py", "settings.py"],
            "Flask": ["app.py", "application.py"],
            "Express": ["server.js", "app.js"],
        }

        for tech, patterns in tech_indicators.items():
            for pattern in patterns:
                if list(cwd.glob(pattern)) or list(cwd.rglob(pattern)):
                    context["technologies"].append(tech)
                    break

        for item in cwd.iterdir():
            if item.is_file():
                context["files"].append(item.name)
            elif item.is_dir() and not item.name.startswith("."):
                context["structure"][item.name] = len(list(item.glob("*")))

        return context


class QueryAnalyzer:
    intent_keywords = {
        QueryIntent.BUILD: ["build", "create", "implement", "develop", "add feature"],
        QueryIntent.DEBUG: ["debug", "fix", "error", "bug", "issue", "problem"],
        QueryIntent.FEATURE: ["feature", "functionality", "capability", "add", "new"],
        QueryIntent.REFACTOR: [
            "refactor",
            "improve",
            "optimize",
            "clean",
            "restructure",
        ],
        QueryIntent.RESEARCH: ["research", "find", "search", "explore", "investigate"],
        QueryIntent.ANALYZE: ["analyze", "understand", "explain", "review", "audit"],
        QueryIntent.TEST: ["test", "testing", "unit test", "integration", "coverage"],
        QueryIntent.DEPLOY: [
            "deploy",
            "deployment",
            "production",
            "release",
            "publish",
        ],
    }

    @staticmethod
    def analyze_query(query: str) -> Dict[str, Any]:
        query_lower = query.lower()
        intents = []

        for intent, keywords in QueryAnalyzer.intent_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                intents.append(intent)

        if not intents:
            intents = [QueryIntent.ANALYZE]

        needs_web_research = any(
            word in query_lower
            for word in [
                "best practice",
                "how to",
                "tutorial",
                "example",
                "documentation",
                "latest",
                "trend",
                "comparison",
            ]
        )

        complexity = QueryAnalyzer._estimate_complexity(query)

        return {
            "original_query": query,
            "intents": [i.value for i in intents],
            "needs_web_research": needs_web_research,
            "complexity": complexity,
            "keywords": QueryAnalyzer._extract_keywords(query),
        }

    @staticmethod
    def _estimate_complexity(query: str) -> int:
        complexity_indicators = {
            "simple": ["what", "show", "list", "get"],
            "medium": ["create", "implement", "fix", "update"],
            "complex": ["refactor", "optimize", "integrate", "architecture", "system"],
        }

        query_lower = query.lower()
        if any(ind in query_lower for ind in complexity_indicators["complex"]):
            return 3
        elif any(ind in query_lower for ind in complexity_indicators["medium"]):
            return 2
        else:
            return 1

    @staticmethod
    def _extract_keywords(query: str) -> List[str]:
        stop_words = {
            "the",
            "is",
            "at",
            "which",
            "on",
            "a",
            "an",
            "as",
            "are",
            "was",
            "were",
            "been",
            "be",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "can",
            "could",
            "need",
            "needs",
        }
        words = query.lower().split()
        return [w for w in words if w not in stop_words and len(w) > 2]


class AgentOrchestrator:
    def __init__(self):
        self.agents: List[SubAgent] = []
        self.project_context: Optional[Dict[str, Any]] = None
        self.query_analysis: Optional[Dict[str, Any]] = None

    def plan_agents(self, query: str, cwd: Path) -> List[SubAgent]:
        self.project_context = ProjectAnalyzer.get_project_context(cwd)
        self.query_analysis = QueryAnalyzer.analyze_query(query)

        agents = []
        project_type = ProjectType(self.project_context["type"])
        intents = [QueryIntent(i) for i in self.query_analysis["intents"]]

        if project_type == ProjectType.FULLSTACK:
            if QueryIntent.BUILD in intents or QueryIntent.FEATURE in intents:
                agents.append(
                    SubAgent(
                        type=AgentType.BACKEND,
                        task=f"Handle backend aspects of: {query}",
                        context={"focus": "backend", **self.project_context},
                        priority=8,
                    )
                )
                agents.append(
                    SubAgent(
                        type=AgentType.FRONTEND,
                        task=f"Handle frontend aspects of: {query}",
                        context={"focus": "frontend", **self.project_context},
                        priority=8,
                    )
                )
        elif project_type == ProjectType.BACKEND:
            agents.append(
                SubAgent(
                    type=AgentType.BACKEND,
                    task=query,
                    context=self.project_context,
                    priority=9,
                )
            )
        elif project_type == ProjectType.FRONTEND:
            agents.append(
                SubAgent(
                    type=AgentType.FRONTEND,
                    task=query,
                    context=self.project_context,
                    priority=9,
                )
            )

        if QueryIntent.ANALYZE in intents or self.query_analysis["complexity"] >= 2:
            agents.append(
                SubAgent(
                    type=AgentType.ANALYZER,
                    task=f"Analyze codebase for: {query}",
                    context=self.project_context,
                    priority=10,
                )
            )

        if self.query_analysis["needs_web_research"]:
            agents.append(
                SubAgent(
                    type=AgentType.RESEARCHER,
                    task=f"Research best practices and solutions for: {query}",
                    context={
                        "keywords": self.query_analysis["keywords"],
                        **self.project_context,
                    },
                    priority=7,
                )
            )

        if QueryIntent.TEST in intents:
            agents.append(
                SubAgent(
                    type=AgentType.TESTER,
                    task=f"Create or update tests for: {query}",
                    context=self.project_context,
                    priority=6,
                )
            )

        if QueryIntent.DEPLOY in intents:
            agents.append(
                SubAgent(
                    type=AgentType.DEVOPS,
                    task=f"Handle deployment aspects of: {query}",
                    context=self.project_context,
                    priority=5,
                )
            )

        self.agents = sorted(agents, key=lambda x: x.priority, reverse=True)
        return self.agents

    async def execute_agent(self, agent: SubAgent) -> Dict[str, Any]:
        agent.status = "running"

        # Create agent dispatch instruction for Claude Code
        agent_prompt = self._create_agent_prompt(agent)

        result = {
            "agent_type": agent.type.value,
            "task": agent.task,
            "status": "dispatched",
            "dispatch_instruction": {
                "type": "claude_subagent",
                "agent_type": agent.type.value,
                "prompt": agent_prompt,
                "context": agent.context,
            },
        }

        agent.status = "dispatched"
        agent.result = result
        return result

    def _create_agent_prompt(self, agent: SubAgent) -> str:
        """Create specialized prompt for each agent type"""

        prompts = {
            AgentType.BACKEND: f"""You are a backend specialist. Task: {agent.task}
Project type: {agent.context.get("type")}
Technologies: {agent.context.get("technologies")}
Focus on: API design, database architecture, server logic, performance.""",
            AgentType.FRONTEND: f"""You are a frontend specialist. Task: {agent.task}
Project type: {agent.context.get("type")}
Technologies: {agent.context.get("technologies")}
Focus on: UI/UX, components, state management, user experience.""",
            AgentType.RESEARCHER: f"""You are a web researcher. Task: {agent.task}
Keywords: {agent.context.get("keywords")}
Find: best practices, documentation, similar implementations, current trends.""",
            AgentType.ANALYZER: f"""You are a code analyzer. Task: {agent.task}
Codebase at: {agent.context.get("cwd")}
Analyze: structure, issues, refactoring opportunities, improvements.""",
            AgentType.TESTER: f"""You are a test engineer. Task: {agent.task}
Project: {agent.context.get("type")}
Create: test strategies, unit tests, integration tests, coverage plans.""",
            AgentType.DEVOPS: f"""You are a DevOps specialist. Task: {agent.task}
Handle: deployment, CI/CD, infrastructure, monitoring, security.""",
        }

        return prompts.get(agent.type, f"Task: {agent.task}")

    async def orchestrate(self, query: str, cwd: Path) -> Dict[str, Any]:
        agents = self.plan_agents(query, cwd)
        results = []

        for agent in agents:
            result = await self.execute_agent(agent)
            results.append(result)

        return {
            "query": query,
            "project_context": self.project_context,
            "query_analysis": self.query_analysis,
            "agents_deployed": len(agents),
            "agent_results": results,
            "summary": self._generate_summary(results),
        }

    def _generate_summary(self, results: List[Dict[str, Any]]) -> str:
        summary_parts = [f"Orchestrated {len(results)} agents successfully."]

        for result in results:
            if "recommendations" in result and result["recommendations"]:
                summary_parts.append(
                    f"{result['agent_type']}: {len(result['recommendations'])} recommendations"
                )
            if "research_findings" in result:
                summary_parts.append(
                    f"{result['agent_type']}: {len(result['research_findings'])} findings"
                )

        return " ".join(summary_parts)


app = Server("vibeteam")
orchestrator = AgentOrchestrator()


@app.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="analyze_and_orchestrate",
            description="Analyzes query and current project, then orchestrates appropriate sub-agents",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user's query or task description",
                    },
                    "cwd": {
                        "type": "string",
                        "description": "Current working directory path (optional, defaults to current directory)",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="analyze_project",
            description="Analyzes the current project structure and returns context information",
            inputSchema={
                "type": "object",
                "properties": {
                    "cwd": {
                        "type": "string",
                        "description": "Directory path to analyze (optional, defaults to current directory)",
                    }
                },
                "required": [],
            },
        ),
        Tool(
            name="analyze_query",
            description="Analyzes a query to determine intent and requirements",
            inputSchema={
                "type": "object",
                "properties": {"query": {"type": "string", "description": "The query to analyze"}},
                "required": ["query"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    if name == "analyze_and_orchestrate":
        query = arguments["query"]
        cwd = Path(arguments.get("cwd", os.getcwd()))

        result = await orchestrator.orchestrate(query, cwd)

        # Format response to trigger Claude Code's sub-agents
        response = create_agent_dispatch_response(result)

        return [TextContent(type="text", text=response)]

    elif name == "analyze_project":
        cwd = Path(arguments.get("cwd", os.getcwd()))
        context = ProjectAnalyzer.get_project_context(cwd)

        return [TextContent(type="text", text=json.dumps(context, indent=2))]

    elif name == "analyze_query":
        query = arguments["query"]
        analysis = QueryAnalyzer.analyze_query(query)

        return [TextContent(type="text", text=json.dumps(analysis, indent=2))]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())

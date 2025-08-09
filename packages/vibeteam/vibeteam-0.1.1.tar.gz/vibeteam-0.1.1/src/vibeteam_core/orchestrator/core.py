"""
Core orchestration logic for managing agents across different tools.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from ..adapters import ToolAdapter
from ..agents import AgentRegistry, AgentResult, BaseAgent, get_global_registry
from .project_analyzer import ProjectAnalyzer
from .query_analyzer import QueryAnalyzer


class OrchestratorConfig(BaseModel):
    """Configuration for the core orchestrator."""

    max_concurrent_agents: int = Field(default=3, ge=1, le=10)
    agent_timeout: float = Field(default=300.0, gt=0)  # seconds
    enable_cross_agent_communication: bool = True
    default_tool: Optional[str] = None
    agent_selection_strategy: str = Field(
        default="priority", pattern="^(priority|round_robin|random)$"
    )


class AgentTask(BaseModel):
    """A task assigned to an agent."""

    model_config = {"arbitrary_types_allowed": True}

    agent: BaseAgent
    task: str
    context: Dict[str, Any]
    priority: int = 5
    status: str = "pending"  # pending, running, completed, failed


class CoreOrchestrator:
    """Core orchestrator that manages agent execution across different tools."""

    def __init__(
        self,
        config: OrchestratorConfig = None,
        registry: AgentRegistry = None,
        tool_adapter: ToolAdapter = None,
    ):
        self.config = config or OrchestratorConfig()
        self.registry = registry or get_global_registry()
        self.tool_adapter = tool_adapter

        self.query_analyzer = QueryAnalyzer()
        self.project_analyzer = ProjectAnalyzer()

        self._active_tasks: List[AgentTask] = []
        self._completed_tasks: List[AgentTask] = []

    async def orchestrate(self, query: str, cwd: Optional[Path] = None) -> Dict[str, Any]:
        """Main orchestration method - analyze query and execute appropriate agents."""
        if cwd is None:
            cwd = Path.cwd()

        # Analyze the query and project context
        query_analysis = self.query_analyzer.analyze_query(query)
        project_context = self.project_analyzer.get_project_context(cwd)

        # Plan which agents to use
        agent_plan = await self._plan_agents(query, query_analysis, project_context)

        # Execute agents
        results = await self._execute_agents(agent_plan)

        # Generate summary
        summary = self._generate_summary(results)

        return {
            "query": query,
            "project_context": project_context,
            "query_analysis": query_analysis,
            "agents_deployed": len(agent_plan),
            "agent_results": results,
            "summary": summary,
            "execution_stats": self._get_execution_stats(),
        }

    async def _plan_agents(
        self, query: str, query_analysis: Dict[str, Any], project_context: Dict[str, Any]
    ) -> List[AgentTask]:
        """Plan which agents should be used for this query."""
        tasks = []

        # Get compatible agents from registry
        tool_name = self.tool_adapter.tool_name if self.tool_adapter else None
        compatible_agents = self.registry.get_compatible_agents(query, project_context, tool_name)

        # Plan agents based on project type and query intent
        for agent_class, metadata in compatible_agents[: self.config.max_concurrent_agents]:
            agent_instance = agent_class(metadata.agent_type, metadata.capabilities)

            # Check if agent can handle this specific task
            if await agent_instance.can_handle(query, project_context):
                priority = agent_instance.get_priority(query, project_context)

                task = AgentTask(
                    agent=agent_instance,
                    task=query,
                    context={**project_context, "query_analysis": query_analysis},
                    priority=priority,
                )
                tasks.append(task)

        # Sort by priority
        tasks.sort(key=lambda x: x.priority, reverse=True)

        return tasks

    async def _execute_agents(self, agent_plan: List[AgentTask]) -> List[AgentResult]:
        """Execute the planned agents."""
        results = []

        for task in agent_plan:
            task.status = "running"
            self._active_tasks.append(task)

            try:
                # Execute the agent
                result = await task.agent.execute(task.task, task.context)
                results.append(result)

                # Update registry usage
                self.registry.update_usage(task.agent.agent_type, task.agent.__class__.__name__)

                task.status = "completed"

            except Exception as e:
                # Handle agent execution failure
                error_result = AgentResult(
                    agent_type=task.agent.agent_type, status="failed", result={}, errors=[str(e)]
                )
                results.append(error_result)
                task.status = "failed"

            # Move to completed tasks
            self._active_tasks.remove(task)
            self._completed_tasks.append(task)

        return results

    def _generate_summary(self, results: List[AgentResult]) -> str:
        """Generate a summary of the orchestration results."""
        if not results:
            return "No agents were executed."

        successful = len([r for r in results if r.status == "success"])
        failed = len([r for r in results if r.status == "failed"])

        summary_parts = [
            f"Executed {len(results)} agents: {successful} successful, {failed} failed."
        ]

        # Add agent-specific summaries
        for result in results:
            if result.recommendations:
                summary_parts.append(
                    f"{result.agent_type.value}: {len(result.recommendations)} recommendations"
                )

        return " ".join(summary_parts)

    def _get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        return {
            "active_tasks": len(self._active_tasks),
            "completed_tasks": len(self._completed_tasks),
            "total_agents_available": len(self.registry.get_all_metadata()),
        }

    def get_active_tasks(self) -> List[AgentTask]:
        """Get currently active tasks."""
        return self._active_tasks.copy()

    def get_completed_tasks(self) -> List[AgentTask]:
        """Get completed tasks."""
        return self._completed_tasks.copy()

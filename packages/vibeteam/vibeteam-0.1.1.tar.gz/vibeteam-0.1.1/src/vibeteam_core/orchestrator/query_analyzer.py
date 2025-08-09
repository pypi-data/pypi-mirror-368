"""
Query analysis for understanding user intent and requirements.
"""

from enum import Enum
from typing import Any, Dict, List


class QueryIntent(Enum):
    """Different types of query intents."""

    BUILD = "build"
    DEBUG = "debug"
    FEATURE = "feature"
    REFACTOR = "refactor"
    RESEARCH = "research"
    ANALYZE = "analyze"
    TEST = "test"
    DEPLOY = "deploy"
    SECURITY = "security"
    PERFORMANCE = "performance"
    DOCUMENTATION = "documentation"


class QueryAnalyzer:
    """Analyzes queries to understand intent and requirements."""

    intent_keywords = {
        QueryIntent.BUILD: ["build", "create", "implement", "develop", "add feature", "make"],
        QueryIntent.DEBUG: ["debug", "fix", "error", "bug", "issue", "problem", "broken"],
        QueryIntent.FEATURE: ["feature", "functionality", "capability", "add", "new"],
        QueryIntent.REFACTOR: [
            "refactor",
            "improve",
            "optimize",
            "clean",
            "restructure",
            "reorganize",
        ],
        QueryIntent.RESEARCH: ["research", "find", "search", "explore", "investigate", "learn"],
        QueryIntent.ANALYZE: ["analyze", "understand", "explain", "review", "audit", "examine"],
        QueryIntent.TEST: ["test", "testing", "unit test", "integration", "coverage", "verify"],
        QueryIntent.DEPLOY: ["deploy", "deployment", "production", "release", "publish"],
        QueryIntent.SECURITY: [
            "security",
            "secure",
            "vulnerability",
            "auth",
            "permission",
            "encrypt",
        ],
        QueryIntent.PERFORMANCE: [
            "performance",
            "optimize",
            "speed",
            "memory",
            "benchmark",
            "profile",
        ],
        QueryIntent.DOCUMENTATION: ["document", "docs", "readme", "guide", "example", "tutorial"],
    }

    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze a query to determine intent, complexity, and requirements."""
        query_lower = query.lower()
        intents = []

        # Identify intents based on keywords
        for intent, keywords in self.intent_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                intents.append(intent)

        # Default to analyze if no specific intent found
        if not intents:
            intents = [QueryIntent.ANALYZE]

        # Determine if web research is needed
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
                "learn",
                "guide",
                "standard",
            ]
        )

        # Estimate complexity
        complexity = self._estimate_complexity(query)

        # Extract keywords
        keywords = self._extract_keywords(query)

        return {
            "original_query": query,
            "intents": [i.value for i in intents],
            "needs_web_research": needs_web_research,
            "complexity": complexity,
            "keywords": keywords,
            "estimated_agents": self._estimate_agents_needed(intents, complexity),
            "priority_score": self._calculate_priority_score(intents, complexity),
        }

    def _estimate_complexity(self, query: str) -> int:
        """Estimate query complexity on a scale of 1-5."""
        complexity_indicators = {
            "simple": ["what", "show", "list", "get", "find", "display"],
            "medium": ["create", "implement", "fix", "update", "modify", "change"],
            "complex": ["refactor", "optimize", "integrate", "architecture", "system", "migrate"],
            "advanced": ["performance", "scale", "security", "enterprise", "distributed"],
        }

        query_lower = query.lower()

        if any(ind in query_lower for ind in complexity_indicators["advanced"]):
            return 5
        elif any(ind in query_lower for ind in complexity_indicators["complex"]):
            return 4
        elif any(ind in query_lower for ind in complexity_indicators["medium"]):
            return 3
        elif any(ind in query_lower for ind in complexity_indicators["simple"]):
            return 2
        else:
            return 2  # Default complexity

    def _extract_keywords(self, query: str) -> List[str]:
        """Extract meaningful keywords from the query."""
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
            "need",
            "needs",
            "want",
            "wants",
            "i",
            "me",
            "my",
            "you",
            "your",
            "he",
            "she",
            "it",
            "we",
            "they",
            "this",
            "that",
            "these",
            "those",
        }

        words = query.lower().split()
        return [w for w in words if w not in stop_words and len(w) > 2]

    def _estimate_agents_needed(self, intents: List[QueryIntent], complexity: int) -> int:
        """Estimate how many agents might be needed."""
        base_agents = len(intents)

        # Add more agents for complex tasks
        if complexity >= 4:
            base_agents += 2
        elif complexity >= 3:
            base_agents += 1

        return min(base_agents, 5)  # Cap at 5 agents

    def _calculate_priority_score(self, intents: List[QueryIntent], complexity: int) -> int:
        """Calculate priority score (1-10)."""
        priority_weights = {
            QueryIntent.DEBUG: 9,  # High priority
            QueryIntent.SECURITY: 9,  # High priority
            QueryIntent.BUILD: 7,  # Medium-high priority
            QueryIntent.FEATURE: 6,  # Medium priority
            QueryIntent.PERFORMANCE: 6,
            QueryIntent.REFACTOR: 5,  # Medium priority
            QueryIntent.TEST: 5,
            QueryIntent.ANALYZE: 4,  # Lower priority
            QueryIntent.RESEARCH: 3,  # Lower priority
            QueryIntent.DOCUMENTATION: 3,
            QueryIntent.DEPLOY: 8,  # High priority
        }

        if not intents:
            return 5

        # Take highest priority intent and adjust for complexity
        max_priority = max(priority_weights.get(intent, 5) for intent in intents)

        # Adjust for complexity
        if complexity >= 4:
            max_priority = min(max_priority + 1, 10)
        elif complexity <= 2:
            max_priority = max(max_priority - 1, 1)

        return max_priority

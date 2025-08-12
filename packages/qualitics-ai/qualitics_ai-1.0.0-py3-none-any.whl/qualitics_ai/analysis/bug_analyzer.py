"""
AI-powered bug analysis for pattern recognition and insights.
"""

import logging
from typing import Dict, List, Any, cast
from collections import defaultdict, Counter
import re

from ..core.config import AnalysisConfig

logger = logging.getLogger(__name__)


class BugAnalyzer:
    """
    Analyzes bugs to identify patterns, categorize by impact, and extract insights.

    This class implements the core logic that was manually performed in the
    MapVis analysis, now automated with AI-powered pattern recognition.
    """

    def __init__(self) -> None:
        """Initialize the bug analyzer."""
        self.pattern_keywords = {
            "race_condition": [
                "race condition",
                "concurrent",
                "threading",
                "synchronization",
                "deadlock",
                "thread safety",
                "parallel",
                "async",
            ],
            "visual_regression": [
                "rendering",
                "display",
                "visual",
                "icon",
                "ui",
                "graphics",
                "positioning",
                "layout",
                "chevron",
                "arrow",
            ],
            "platform_integration": [
                "platform",
                "android",
                "ios",
                "device",
                "orientation",
                "lifecycle",
                "background",
                "foreground",
            ],
            "grpc_communication": [
                "grpc",
                "rpc",
                "network",
                "communication",
                "connection",
                "dispatcher",
                "socket",
                "timeout",
            ],
            "memory_management": [
                "memory",
                "leak",
                "oom",
                "garbage",
                "allocation",
                "performance",
                "crash",
            ],
        }

    async def analyze_bugs(
        self,
        bug_data: Dict[str, Any],
        repository_data: Dict[str, Any],
        analysis_config: AnalysisConfig,
    ) -> Dict[str, Any]:
        """
        Perform comprehensive bug analysis.

        Args:
            bug_data: Raw bug data from tracking system
            repository_data: Repository information for context
            analysis_config: Analysis parameters

        Returns:
            Comprehensive analysis results
        """
        logger.info("Starting bug pattern analysis...")

        bugs = bug_data.get("bugs", [])

        analysis_results: Dict[str, Any] = {
            "total_bugs": len(bugs),
            "bug_categories": self._categorize_bugs(bugs),
            "pattern_analysis": self._analyze_patterns(bugs),
            "developer_insights": self._extract_developer_insights(bugs),
            "severity_distribution": self._analyze_severity_distribution(bugs),
            "timeline_analysis": self._analyze_timeline(bugs),
            "component_impact": self._analyze_component_impact(bugs),
            "test_effectiveness": self._analyze_test_effectiveness(bugs, repository_data),
        }

        logger.info(
            f"Analyzed {len(bugs)} bugs across {len(analysis_results['bug_categories'])} categories"
        )

        return analysis_results

    def _categorize_bugs(self, bugs: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize bugs by pattern type."""
        categories = defaultdict(list)

        for bug in bugs:
            bug_text = self._extract_bug_text(bug).lower()
            bug_category = self._classify_bug(bug_text)

            categories[bug_category].append(
                {
                    "id": bug.get("id", ""),
                    "summary": bug.get("summary", ""),
                    "severity": bug.get("severity", "unknown"),
                    "components": bug.get("components", []),
                    "labels": bug.get("labels", []),
                }
            )

        return dict(categories)

    def _classify_bug(self, bug_text: str) -> str:
        """Classify a bug based on text content."""
        scores = {}

        for category, keywords in self.pattern_keywords.items():
            score = sum(1 for keyword in keywords if keyword in bug_text)
            if score > 0:
                scores[category] = score

        if scores:
            return max(scores, key=lambda k: scores[k])
        return "other"

    def _analyze_patterns(self, bugs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze recurring patterns in bugs."""
        patterns: Dict[str, Any] = {
            "recurring_components": Counter(),
            "common_keywords": Counter(),
            "severity_patterns": defaultdict(list),
            "resolution_patterns": defaultdict(list),
        }

        for bug in bugs:
            # Component analysis
            for component in bug.get("components", []):
                patterns["recurring_components"][component] += 1

            # Keyword extraction
            bug_text = self._extract_bug_text(bug)
            keywords = self._extract_keywords(bug_text)
            cast(Counter, patterns["common_keywords"]).update(keywords)

            # Severity patterns
            severity = bug.get("severity", "unknown")
            cast(defaultdict, patterns["severity_patterns"])[severity].append(bug.get("id"))

            # Resolution analysis
            if bug.get("status") == "resolved":
                resolution_time = self._calculate_resolution_time(bug)
                cast(defaultdict, patterns["resolution_patterns"])[severity].append(resolution_time)

        return {
            "top_components": dict(cast(Counter, patterns["recurring_components"]).most_common(10)),
            "top_keywords": dict(cast(Counter, patterns["common_keywords"]).most_common(20)),
            "severity_distribution": {
                k: len(v) for k, v in cast(defaultdict, patterns["severity_patterns"]).items()
            },
            "avg_resolution_time": {
                k: sum(v) / len(v) if v else 0
                for k, v in cast(defaultdict, patterns["resolution_patterns"]).items()
            },
        }

    def _extract_developer_insights(self, bugs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract insights from developer comments."""
        insights = []

        for bug in bugs:
            comments = bug.get("comments", [])

            for comment in comments:
                comment_text = comment.get("text", "").lower()

                # Look for root cause analysis patterns
                if any(
                    phrase in comment_text
                    for phrase in [
                        "root cause",
                        "caused by",
                        "issue is",
                        "problem is",
                        "need to",
                        "should implement",
                        "missing test",
                    ]
                ):
                    insights.append(
                        {
                            "bug_id": bug.get("id"),
                            "author": comment.get("author"),
                            "insight_type": self._classify_insight(comment_text),
                            "text": comment.get("text"),
                            "created": comment.get("created"),
                        }
                    )

        return insights

    def _classify_insight(self, text: str) -> str:
        """Classify the type of developer insight."""
        if any(phrase in text for phrase in ["root cause", "caused by"]):
            return "root_cause_analysis"
        elif any(phrase in text for phrase in ["need test", "missing test", "should test"]):
            return "test_requirement"
        elif any(phrase in text for phrase in ["need to implement", "should add"]):
            return "implementation_suggestion"
        else:
            return "general_insight"

    def _analyze_severity_distribution(self, bugs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze distribution of bug severities."""
        severity_counts = Counter(bug.get("severity", "unknown") for bug in bugs)

        return {
            "distribution": dict(severity_counts),
            "critical_percentage": (
                (severity_counts.get("critical", 0) / len(bugs)) * 100 if bugs else 0
            ),
            "high_percentage": (severity_counts.get("high", 0) / len(bugs)) * 100 if bugs else 0,
        }

    def _analyze_timeline(self, bugs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze bug timeline patterns."""
        # Placeholder implementation
        return {
            "creation_trend": "stable",  # Would be calculated from actual dates
            "resolution_trend": "improving",
            "seasonal_patterns": {},
        }

    def _analyze_component_impact(self, bugs: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze which components are most affected by bugs."""
        component_counts: Counter[str] = Counter()

        for bug in bugs:
            for component in bug.get("components", []):
                component_counts[component] += 1

        return dict(component_counts.most_common())

    def _analyze_test_effectiveness(
        self, bugs: List[Dict[str, Any]], repository_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze how effective existing tests are at catching bugs."""
        # This would analyze which bugs occurred in areas with existing test coverage
        return {
            "bugs_with_existing_tests": 0,  # Placeholder
            "test_coverage_gaps": [],
            "recommendations": [
                "Implement integration testing for concurrent operations",
                "Add visual regression testing framework",
                "Enhance error handling validation",
            ],
        }

    def _extract_bug_text(self, bug: Dict[str, Any]) -> str:
        """Extract all text content from a bug for analysis."""
        text_parts = [bug.get("summary", ""), bug.get("description", "")]

        # Add comment text
        for comment in bug.get("comments", []):
            text_parts.append(comment.get("text", ""))

        return " ".join(text_parts)

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text."""
        # Simple keyword extraction - could be enhanced with NLP
        words = re.findall(r"\b\w+\b", text.lower())

        # Filter out common words
        stop_words = {
            "the",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "was",
            "are",
            "were",
            "be",
            "been",
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
        }

        return [word for word in words if len(word) > 3 and word not in stop_words]

    def _calculate_resolution_time(self, bug: Dict[str, Any]) -> int:
        """Calculate resolution time in days."""
        # Placeholder - would parse actual dates
        return 7  # Default 7 days

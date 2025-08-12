"""
Core analyzer for Qualitics AI - Main orchestration logic.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from pathlib import Path
from datetime import datetime

from .config import QualiticsConfig
from ..integrations.repository_factory import RepositoryFactory
from ..integrations.bug_tracking_factory import BugTrackingFactory
from ..analysis.bug_analyzer import BugAnalyzer
from ..analysis.test_gap_analyzer import TestGapAnalyzer
from ..reports.report_generator import ReportGenerator

if TYPE_CHECKING:
    from ..integrations.repository_factory import RepositoryClient
    from ..integrations.bug_tracking_factory import BugTrackingClient

logger = logging.getLogger(__name__)


class QualiticsAnalyzer:
    """
    Main analyzer class that orchestrates the complete analysis workflow.

    This is the primary entry point for Qualitics AI analysis, coordinating:
    - Data collection from repositories and bug tracking systems
    - AI-powered analysis of bugs and test gaps
    - Report generation in multiple formats
    """

    def __init__(self, config: QualiticsConfig) -> None:
        """Initialize the analyzer with configuration."""
        self.config = config
        self.repository_client: Optional["RepositoryClient"] = None
        self.bug_tracking_client: Optional["BugTrackingClient"] = None
        self.bug_analyzer = BugAnalyzer()
        self.test_gap_analyzer = TestGapAnalyzer()
        self.report_generator = ReportGenerator(config.reports)

    async def initialize(self) -> None:
        """Initialize all clients and connections."""
        logger.info("Initializing Qualitics AI analyzer...")

        # Initialize repository client
        repo_factory = RepositoryFactory()
        self.repository_client = await repo_factory.create_client(self.config.repository)

        # Initialize bug tracking client
        bug_factory = BugTrackingFactory()
        self.bug_tracking_client = await bug_factory.create_client(self.config.bug_tracking)

        logger.info("All clients initialized successfully")

    async def run_analysis(self) -> Dict[str, Any]:
        """
        Run the complete analysis workflow.

        Returns:
            Dict containing all analysis results
        """
        logger.info("Starting comprehensive quality analysis...")

        analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "config": self.config.dict(),
            "repository_data": None,
            "bug_data": None,
            "bug_analysis": None,
            "test_gap_analysis": None,
            "recommendations": None,
        }

        try:
            # Step 1: Collect repository data
            logger.info("Collecting repository data...")
            repository_data = await self._collect_repository_data()
            analysis_results["repository_data"] = repository_data

            # Step 2: Collect bug data
            logger.info("Collecting bug tracking data...")
            bug_data = await self._collect_bug_data()
            analysis_results["bug_data"] = bug_data

            # Step 3: Analyze bugs
            logger.info("Analyzing bug patterns...")
            bug_analysis = await self.bug_analyzer.analyze_bugs(
                bug_data, repository_data, self.config.analysis
            )
            analysis_results["bug_analysis"] = bug_analysis

            # Step 4: Identify test gaps
            logger.info("Identifying test coverage gaps...")
            test_gap_analysis = await self.test_gap_analyzer.analyze_test_gaps(
                bug_analysis, repository_data, self.config.analysis
            )
            analysis_results["test_gap_analysis"] = test_gap_analysis

            # Step 5: Generate recommendations
            logger.info("Generating actionable recommendations...")
            recommendations = await self._generate_recommendations(bug_analysis, test_gap_analysis)
            analysis_results["recommendations"] = recommendations

            logger.info("Analysis completed successfully")
            return analysis_results

        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            raise

    async def generate_reports(self, analysis_results: Dict[str, Any]) -> List[str]:
        """
        Generate reports in all configured formats.

        Args:
            analysis_results: Results from run_analysis()

        Returns:
            List of generated report file paths
        """
        logger.info("Generating reports...")

        report_paths = []

        for format_type in self.config.reports.formats:
            try:
                report_path = await self.report_generator.generate_report(
                    analysis_results, format_type
                )
                report_paths.append(report_path)
                logger.info(f"Generated {format_type} report: {report_path}")

            except Exception as e:
                logger.error(f"Failed to generate {format_type} report: {str(e)}")

        return report_paths

    async def _collect_repository_data(self) -> Dict[str, Any]:
        """Collect data from the repository."""
        if not self.repository_client:
            raise RuntimeError("Repository client not initialized")

        return await self.repository_client.collect_data(self.config.analysis)

    async def _collect_bug_data(self) -> Dict[str, Any]:
        """Collect data from bug tracking system."""
        if not self.bug_tracking_client:
            raise RuntimeError("Bug tracking client not initialized")

        return await self.bug_tracking_client.collect_bugs(self.config.analysis)

    async def _generate_recommendations(
        self, bug_analysis: Dict[str, Any], test_gap_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate actionable recommendations based on analysis."""

        recommendations: Dict[str, Any] = {
            "priority_scenarios": [],
            "implementation_plan": {},
            "success_metrics": {},
            "timeline_estimate": {},
        }

        # Extract high-priority test scenarios
        if "missing_scenarios" in test_gap_analysis:
            for scenario in test_gap_analysis["missing_scenarios"]:
                if scenario.get("priority", "").lower() in ["critical", "high"]:
                    recommendations["priority_scenarios"].append(
                        {
                            "name": scenario["name"],
                            "description": scenario["description"],
                            "implementation_guidance": scenario.get("automation_guidance", ""),
                            "expected_impact": scenario.get("production_impact", ""),
                            "related_bugs": scenario.get("related_bugs", []),
                        }
                    )

        # Generate implementation timeline
        scenario_count = len(recommendations["priority_scenarios"])
        recommendations["timeline_estimate"] = {
            "total_scenarios": scenario_count,
            "estimated_weeks": max(2, scenario_count // 3),
            "phases": [
                {"phase": "Setup", "weeks": 1, "description": "Framework setup and CI integration"},
                {
                    "phase": "Critical Tests",
                    "weeks": scenario_count // 5 or 1,
                    "description": "Implement high-priority scenarios",
                },
                {"phase": "Validation", "weeks": 1, "description": "Verify effectiveness and tune"},
            ],
        }

        return recommendations

    async def close(self) -> None:
        """Clean up resources."""
        if self.repository_client:
            await self.repository_client.close()
        if self.bug_tracking_client:
            await self.bug_tracking_client.close()
        logger.info("Analyzer resources cleaned up")

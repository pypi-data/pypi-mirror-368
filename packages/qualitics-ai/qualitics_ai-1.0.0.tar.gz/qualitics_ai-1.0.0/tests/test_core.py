"""
Test suite for Qualitics AI core functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

from qualitics_ai.core.config import QualiticsConfig, RepositoryConfig, BugTrackingConfig
from qualitics_ai.core.analyzer import QualiticsAnalyzer


class TestQualiticsConfig:
    """Test configuration management."""

    def test_repository_config_validation(self):
        """Test repository configuration validation."""
        config = RepositoryConfig(
            type="github", url="https://github.com/test/repo", access_token="token123"
        )
        assert config.type == "github"
        assert config.default_branch == "main"

    def test_invalid_repository_type(self):
        """Test validation of invalid repository type."""
        with pytest.raises(ValueError):
            RepositoryConfig(
                type="invalid", url="https://github.com/test/repo", access_token="token123"
            )

    def test_bug_tracking_config_validation(self):
        """Test bug tracking configuration validation."""
        config = BugTrackingConfig(
            type="jira",
            base_url="https://company.atlassian.net",
            access_token="token123",
            projects=["PROJ1", "PROJ2"],
        )
        assert config.type == "jira"
        assert len(config.projects) == 2


class TestQualiticsAnalyzer:
    """Test main analyzer functionality."""

    @pytest.fixture
    def sample_config(self):
        """Create sample configuration for testing."""
        return {
            "customer": {"name": "Test Company", "contact_email": "test@example.com"},
            "repository": {
                "type": "github",
                "url": "https://github.com/test/repo",
                "access_token": "token123",
            },
            "bug_tracking": {
                "type": "jira",
                "base_url": "https://test.atlassian.net",
                "access_token": "token123",
                "projects": ["TEST"],
            },
        }

    @pytest.fixture
    def analyzer(self, sample_config):
        """Create analyzer instance for testing."""
        config = QualiticsConfig(**sample_config)
        return QualiticsAnalyzer(config)

    @pytest.mark.asyncio
    async def test_analyzer_initialization(self, analyzer):
        """Test analyzer initialization."""
        with patch(
            "qualitics_ai.integrations.repository_factory.RepositoryFactory"
        ) as mock_repo_factory, patch(
            "qualitics_ai.integrations.bug_tracking_factory.BugTrackingFactory"
        ) as mock_bug_factory:

            mock_repo_client = AsyncMock()
            mock_bug_client = AsyncMock()

            mock_repo_factory.return_value.create_client.return_value = mock_repo_client
            mock_bug_factory.return_value.create_client.return_value = mock_bug_client

            await analyzer.initialize()

            assert analyzer.repository_client == mock_repo_client
            assert analyzer.bug_tracking_client == mock_bug_client

    @pytest.mark.asyncio
    async def test_run_analysis_workflow(self, analyzer):
        """Test complete analysis workflow."""
        # Mock dependencies
        analyzer.repository_client = AsyncMock()
        analyzer.bug_tracking_client = AsyncMock()
        analyzer.bug_analyzer = AsyncMock()
        analyzer.test_gap_analyzer = AsyncMock()

        # Setup mock data
        mock_repo_data = {"test_files": [], "commits": []}
        mock_bug_data = {"bugs": [], "total_count": 0}
        mock_bug_analysis = {"total_bugs": 0, "bug_categories": {}}
        mock_gap_analysis = {"missing_scenarios": [], "gap_summary": {}}

        analyzer.repository_client.collect_data.return_value = mock_repo_data
        analyzer.bug_tracking_client.collect_bugs.return_value = mock_bug_data
        analyzer.bug_analyzer.analyze_bugs.return_value = mock_bug_analysis
        analyzer.test_gap_analyzer.analyze_test_gaps.return_value = mock_gap_analysis

        # Run analysis
        results = await analyzer.run_analysis()

        # Verify results structure
        assert "timestamp" in results
        assert "repository_data" in results
        assert "bug_data" in results
        assert "bug_analysis" in results
        assert "test_gap_analysis" in results
        assert "recommendations" in results

        # Verify mock calls
        analyzer.repository_client.collect_data.assert_called_once()
        analyzer.bug_tracking_client.collect_bugs.assert_called_once()
        analyzer.bug_analyzer.analyze_bugs.assert_called_once()
        analyzer.test_gap_analyzer.analyze_test_gaps.assert_called_once()


class TestIntegrations:
    """Test integration factories."""

    @pytest.mark.asyncio
    async def test_repository_factory_github(self):
        """Test GitHub repository client creation."""
        from qualitics_ai.integrations.repository_factory import RepositoryFactory

        config = RepositoryConfig(
            type="github", url="https://github.com/test/repo", access_token="token123"
        )

        factory = RepositoryFactory()
        client = await factory.create_client(config)

        assert client is not None
        assert hasattr(client, "collect_data")

    @pytest.mark.asyncio
    async def test_bug_tracking_factory_jira(self):
        """Test JIRA bug tracking client creation."""
        from qualitics_ai.integrations.bug_tracking_factory import BugTrackingFactory

        config = BugTrackingConfig(
            type="jira",
            base_url="https://test.atlassian.net",
            access_token="token123",
            projects=["TEST"],
        )

        factory = BugTrackingFactory()
        client = await factory.create_client(config)

        assert client is not None
        assert hasattr(client, "collect_bugs")


class TestAnalysis:
    """Test analysis modules."""

    @pytest.mark.asyncio
    async def test_bug_analyzer_categorization(self):
        """Test bug categorization logic."""
        from qualitics_ai.analysis.bug_analyzer import BugAnalyzer

        analyzer = BugAnalyzer()

        sample_bugs = [
            {
                "id": "BUG-1",
                "summary": "Race condition in navigation component",
                "description": "Concurrent operations cause threading issues",
                "severity": "high",
                "components": ["Navigation"],
            },
            {
                "id": "BUG-2",
                "summary": "Visual rendering problem with icons",
                "description": "Icons not displaying correctly after theme switch",
                "severity": "medium",
                "components": ["UI"],
            },
        ]

        bug_data = {"bugs": sample_bugs}
        repo_data = {"test_files": []}
        config = Mock()

        results = await analyzer.analyze_bugs(bug_data, repo_data, config)

        assert "bug_categories" in results
        assert "pattern_analysis" in results
        assert results["total_bugs"] == 2

    @pytest.mark.asyncio
    async def test_test_gap_analyzer_scenario_generation(self):
        """Test test gap scenario generation."""
        from qualitics_ai.analysis.test_gap_analyzer import TestGapAnalyzer

        analyzer = TestGapAnalyzer()

        bug_analysis = {
            "bug_categories": {
                "race_condition": [
                    {"id": "BUG-1", "severity": "high"},
                    {"id": "BUG-2", "severity": "critical"},
                ]
            }
        }
        repo_data = {"test_files": []}
        config = Mock()

        results = await analyzer.analyze_test_gaps(bug_analysis, repo_data, config)

        assert "missing_scenarios" in results
        assert "gap_summary" in results
        assert len(results["missing_scenarios"]) > 0


if __name__ == "__main__":
    pytest.main([__file__])

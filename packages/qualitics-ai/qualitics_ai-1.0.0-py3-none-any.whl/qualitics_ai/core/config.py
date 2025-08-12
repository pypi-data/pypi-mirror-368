"""
Core configuration management for Qualitics AI.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml
from pydantic import BaseModel, validator


class RepositoryConfig(BaseModel):
    """Configuration for repository integration."""

    type: str  # github, azure-repos, gitlab, bitbucket
    url: str
    access_token: str
    organization: Optional[str] = None
    default_branch: str = "main"

    @validator("type")
    def validate_repo_type(cls, v: str) -> str:
        allowed_types = ["github", "azure-repos", "gitlab", "bitbucket"]
        if v not in allowed_types:
            raise ValueError(f"Repository type must be one of {allowed_types}")
        return v


class BugTrackingConfig(BaseModel):
    """Configuration for bug tracking system integration."""

    type: str  # jira, azure-devops, github-issues, servicenow
    base_url: str
    access_token: str
    projects: List[str]
    username: Optional[str] = None

    @validator("type")
    def validate_bug_tracking_type(cls, v: str) -> str:
        allowed_types = ["jira", "azure-devops", "github-issues", "servicenow"]
        if v not in allowed_types:
            raise ValueError(f"Bug tracking type must be one of {allowed_types}")
        return v


class AnalysisConfig(BaseModel):
    """Configuration for analysis parameters."""

    time_range: str = "6_months"  # 1_month, 3_months, 6_months, 1_year, all
    severity_filter: List[str] = ["critical", "high", "medium"]
    components: Optional[List[str]] = None
    exclude_labels: List[str] = field(default_factory=list)
    include_resolved: bool = True
    min_bug_count: int = 5

    @validator("time_range")
    def validate_time_range(cls, v: str) -> str:
        allowed_ranges = ["1_month", "3_months", "6_months", "1_year", "all"]
        if v not in allowed_ranges:
            raise ValueError(f"Time range must be one of {allowed_ranges}")
        return v


class ReportConfig(BaseModel):
    """Configuration for report generation."""

    formats: List[str] = ["pdf", "markdown"]
    output_directory: str = "reports"
    include_charts: bool = True
    include_code_examples: bool = True
    confluence_space: Optional[str] = None
    confluence_parent_page: Optional[str] = None

    @validator("formats")
    def validate_formats(cls, v: List[str]) -> List[str]:
        allowed_formats = ["pdf", "markdown", "json", "confluence", "html"]
        invalid_formats = [f for f in v if f not in allowed_formats]
        if invalid_formats:
            raise ValueError(f"Invalid formats: {invalid_formats}. Allowed: {allowed_formats}")
        return v


class CustomerConfig(BaseModel):
    """Customer-specific configuration."""

    name: str
    contact_email: str
    logo_path: Optional[str] = None
    custom_templates_path: Optional[str] = None


class QualiticsConfig(BaseModel):
    """Main configuration class for Qualitics AI."""

    customer: CustomerConfig
    repository: RepositoryConfig
    bug_tracking: BugTrackingConfig
    analysis: AnalysisConfig = AnalysisConfig()
    reports: ReportConfig = ReportConfig()

    @classmethod
    def from_yaml(cls, config_path: Path) -> "QualiticsConfig":
        """Load configuration from YAML file."""
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)
        return cls(**config_data)

    def to_yaml(self, config_path: Path) -> None:
        """Save configuration to YAML file."""
        with open(config_path, "w") as f:
            yaml.dump(self.dict(), f, default_flow_style=False, indent=2)

    def validate_access(self) -> Dict[str, bool]:
        """Validate access to configured systems."""
        # This will be implemented with actual API calls
        return {
            "repository": True,  # Placeholder
            "bug_tracking": True,  # Placeholder
        }

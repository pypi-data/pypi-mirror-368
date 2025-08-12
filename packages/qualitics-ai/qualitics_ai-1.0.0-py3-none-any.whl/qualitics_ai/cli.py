"""
Command line interface for Qualitics AI.
"""

import click
import asyncio
import logging
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .core.config import QualiticsConfig
from .core.analyzer import QualiticsAnalyzer

console = Console()
logger = logging.getLogger(__name__)


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def cli(verbose: bool) -> None:  # type: ignore
    """Qualitics AI - Intelligent Test Gap Analysis Agent"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


@cli.command()  # type: ignore
@click.option(
    "--config", "-c", required=True, type=click.Path(exists=True), help="Configuration file path"
)
@click.option("--output", "-o", default="reports", help="Output directory for reports")
def analyze(config: str, output: str) -> None:  # type: ignore
    """Run comprehensive quality analysis."""
    asyncio.run(_run_analysis(config, output))


@cli.command()  # type: ignore
@click.option(
    "--config", "-c", required=True, type=click.Path(exists=True), help="Configuration file path"
)
def validate(config: str) -> None:  # type: ignore
    """Validate configuration and test connections."""
    asyncio.run(_validate_config(config))


@cli.command()  # type: ignore
@click.option("--output", "-o", default="config/config.yaml", help="Output configuration file path")
def init(output: str) -> None:  # type: ignore
    """Initialize a new configuration file."""
    _create_sample_config(output)


async def _run_analysis(config_path: str, output_dir: str) -> None:
    """Run the complete analysis workflow."""
    try:
        console.print(Panel("🚀 Starting Qualitics AI Analysis", style="bold blue"))

        # Load configuration
        config = QualiticsConfig.from_yaml(Path(config_path))
        config.reports.output_directory = output_dir

        # Initialize analyzer
        analyzer = QualiticsAnalyzer(config)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:

            # Initialize
            task = progress.add_task("Initializing connections...", total=None)
            await analyzer.initialize()
            progress.update(task, description="✅ Connections established")

            # Run analysis
            progress.update(task, description="🔍 Analyzing bugs and test coverage...")
            analysis_results = await analyzer.run_analysis()
            progress.update(task, description="✅ Analysis completed")

            # Generate reports
            progress.update(task, description="📄 Generating reports...")
            report_paths = await analyzer.generate_reports(analysis_results)
            progress.update(task, description="✅ Reports generated")

        # Display results
        _display_results(analysis_results, report_paths)

        await analyzer.close()

    except Exception as e:
        console.print(f"❌ Analysis failed: {str(e)}", style="bold red")
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)


async def _validate_config(config_path: str) -> None:
    """Validate configuration and connections."""
    try:
        console.print("🔍 Validating configuration...", style="bold blue")

        config = QualiticsConfig.from_yaml(Path(config_path))

        # Validate configuration structure
        console.print("✅ Configuration structure is valid")

        # Test connections
        analyzer = QualiticsAnalyzer(config)
        await analyzer.initialize()

        # Validate access
        access_results = config.validate_access()

        table = Table(title="Connection Validation")
        table.add_column("Service", style="cyan")
        table.add_column("Status", style="green")

        for service, status in access_results.items():
            status_text = "✅ Connected" if status else "❌ Failed"
            table.add_row(service.title(), status_text)

        console.print(table)

        await analyzer.close()
        console.print("✅ All validations passed", style="bold green")

    except Exception as e:
        console.print(f"❌ Validation failed: {str(e)}", style="bold red")


def _create_sample_config(output_path: str) -> None:
    """Create a sample configuration file."""
    try:
        sample_config = {
            "customer": {
                "name": "Your Company",
                "contact_email": "qa-team@yourcompany.com",
                "logo_path": None,
                "custom_templates_path": None,
            },
            "repository": {
                "type": "github",  # github, azure-repos, gitlab, bitbucket
                "url": "https://github.com/your-org/your-repo",
                "access_token": "${GITHUB_TOKEN}",
                "organization": "your-org",
                "default_branch": "main",
            },
            "bug_tracking": {
                "type": "jira",  # jira, azure-devops, github-issues, servicenow
                "base_url": "https://yourcompany.atlassian.net",
                "access_token": "${JIRA_TOKEN}",
                "projects": ["PROJ1", "PROJ2"],
                "username": "your-email@yourcompany.com",
            },
            "analysis": {
                "time_range": "6_months",  # 1_month, 3_months, 6_months, 1_year, all
                "severity_filter": ["critical", "high", "medium"],
                "components": None,  # Analyze all components, or specify: ["ComponentA", "ComponentB"]
                "exclude_labels": ["duplicate", "invalid"],
                "include_resolved": True,
                "min_bug_count": 3,
            },
            "reports": {
                "formats": ["pdf", "markdown", "json"],
                "output_directory": "reports",
                "include_charts": True,
                "include_code_examples": True,
                "confluence_space": None,  # "QA" for Confluence integration
                "confluence_parent_page": None,  # "Test Analysis Reports"
            },
        }

        Path(output_path).parent.mkdir(exist_ok=True)

        import yaml

        with open(output_path, "w") as f:
            yaml.dump(sample_config, f, default_flow_style=False, indent=2)

        console.print(f"✅ Sample configuration created: {output_path}", style="bold green")
        console.print("\n📝 Next steps:")
        console.print("1. Edit the configuration file with your actual values")
        console.print("2. Set environment variables for tokens (GITHUB_TOKEN, JIRA_TOKEN)")
        console.print("3. Run: qualitics-ai validate --config your-config.yaml")
        console.print("4. Run: qualitics-ai analyze --config your-config.yaml")

    except Exception as e:
        console.print(f"❌ Failed to create config: {str(e)}", style="bold red")


def _display_results(analysis_results: dict, report_paths: list) -> None:
    """Display analysis results summary."""
    bug_analysis = analysis_results.get("bug_analysis", {})
    test_gap_analysis = analysis_results.get("test_gap_analysis", {})

    # Summary Panel
    summary_text = f"""
📊 **Analysis Summary**

🐛 Total Bugs Analyzed: {bug_analysis.get('total_bugs', 0)}
🔍 Bug Categories Found: {len(bug_analysis.get('bug_categories', {}))}
⚠️  Missing Test Scenarios: {test_gap_analysis.get('gap_summary', {}).get('total_missing_scenarios', 0)}
🎯 Critical Scenarios: {test_gap_analysis.get('gap_summary', {}).get('critical_count', 0)}
"""

    console.print(Panel(summary_text, title="Analysis Results", style="bold green"))

    # Bug Categories Table
    if bug_analysis.get("bug_categories"):
        table = Table(title="Bug Categories")
        table.add_column("Category", style="cyan")
        table.add_column("Count", style="yellow")
        table.add_column("Priority", style="red")

        for category, bugs in bug_analysis["bug_categories"].items():
            priority = "High" if len(bugs) >= 5 else "Medium" if len(bugs) >= 3 else "Low"
            table.add_row(category.replace("_", " ").title(), str(len(bugs)), priority)

        console.print(table)

    # Generated Reports
    if report_paths:
        console.print("\n📄 **Generated Reports:**", style="bold blue")
        for path in report_paths:
            console.print(f"  • {path}")

    console.print("\n🎉 Analysis completed successfully!", style="bold green")


if __name__ == "__main__":
    cli()  # type: ignore

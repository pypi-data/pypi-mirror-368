# Qualitics AI

An intelligent AI agent for automated test gap analysis and quality intelligence.

## Requirements

- **Python 3.10+** (Recommended: Python 3.11 or 3.12)
- Modern operating systems (Linux, macOS, Windows)
- Git access to target repositories
- API access to bug tracking systems

## Overview

Qualitics AI automates the comprehensive analysis of software quality by:
- Analyzing production bugs from multiple tracking systems (JIRA, Azure DevOps, GitHub Issues)
- Examining repository test infrastructure across platforms (GitHub, Azure Repos, GitLab)
- Identifying critical test coverage gaps using AI-powered pattern recognition
- Generating actionable test scenarios with developer-specific recommendations
- Producing professional reports for stakeholders and technical teams

## Key Features

- **Multi-Platform Integration**: GitHub, Azure Repos, GitLab, Bitbucket
- **Bug Tracking Systems**: JIRA, Azure DevOps, GitHub Issues, ServiceNow
- **AI-Powered Analysis**: Pattern recognition, natural language processing
- **Automated Report Generation**: PDF, Confluence, Markdown, JSON formats
- **Configurable Analysis**: Customer-specific repository and bug tracking setups
- **Developer-Centric Insights**: Extract technical root causes from developer discussions

## 🚀 Quick Start

### Installation

#### Option 1: PyPI Package (Recommended)
```bash
# Install from PyPI
pip install qualitics-ai

# Initialize configuration
qualitics init --output config/my_config.yaml

# Run analysis
qualitics analyze --config config/my_config.yaml
```

#### Option 2: Docker Container
```bash
# Create configuration directory
mkdir -p ./config ./reports

# Initialize configuration
docker run --rm -v $(pwd):/workspace ghcr.io/arpitkothari-hub/qualitics-ai:latest 
  qualitics init --output /workspace/config/my_config.yaml

# Run analysis
docker run --rm -v $(pwd):/workspace ghcr.io/arpitkothari-hub/qualitics-ai:latest 
  qualitics analyze --config /workspace/config/my_config.yaml
```

#### Option 3: Development Installation
```bash
# Clone the repository
git clone https://github.com/arpitkothari-hub/qualitics-ai.git
cd qualitics-ai

# Install in development mode
pip install -e .

# Run the analysis
qualitics-ai init --output config/my_config.yaml
qualitics-ai analyze --config config/my_config.yaml
```

## Configuration

Qualitics AI is designed to be customer-configurable for different:
- Repository systems (GitHub, Azure Repos, GitLab)
- Bug tracking tools (JIRA, Azure DevOps, GitHub Issues)
- Analysis scope (time ranges, severity filters, component focus)
- Report formats and delivery methods

## Architecture

- **Core Engine**: `qualitics_ai/core/` - Main analysis logic
- **Integrations**: `qualitics_ai/integrations/` - Repository and bug tracking connectors
- **Analysis**: `qualitics_ai/analysis/` - AI-powered pattern recognition
- **Reports**: `qualitics_ai/reports/` - Multi-format report generation
- **Config**: `config/` - Customer configuration management

## Development

```bash
# Setup development environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-dev.txt

# Run tests
pytest

# Run linting
flake8 qualitics_ai/
black qualitics_ai/

# Type checking
mypy qualitics_ai/
```

## License

Commercial software - All rights reserved.

## Support

For enterprise support and custom configurations, contact: support@qualitics.ai

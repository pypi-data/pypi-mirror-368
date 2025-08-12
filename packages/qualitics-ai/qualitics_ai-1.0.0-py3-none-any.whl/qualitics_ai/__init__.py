"""
Qualitics AI - Intelligent Test Gap Analysis Agent

An AI-powered system for automated quality intelligence, test gap analysis,
and actionable recommendations for software development teams.
"""

__version__ = "1.0.0"
__author__ = "Qualitics AI Team"
__email__ = "info@qualitics.ai"

from .core.analyzer import QualiticsAnalyzer
from .core.config import QualiticsConfig

__all__ = ["QualiticsAnalyzer", "QualiticsConfig"]

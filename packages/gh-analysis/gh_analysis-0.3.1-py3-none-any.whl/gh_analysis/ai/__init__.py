"""AI processing module for GitHub issue analysis."""

from .agents import product_labeling_agent
from .analysis import analyze_issue, format_issue_prompt, prepare_issue_for_analysis
from .models import (
    IssueClassificationResponse,
    LabelAssessment,
    ProductLabel,
    ProductLabelingResponse,
    RecommendedLabel,
)
from .prompts import PRODUCT_LABELING_PROMPT

__all__ = [
    # Models
    "ProductLabel",
    "RecommendedLabel",
    "LabelAssessment",
    "ProductLabelingResponse",
    "IssueClassificationResponse",
    # Agents
    "product_labeling_agent",
    # Analysis functions
    "analyze_issue",
    "prepare_issue_for_analysis",
    "format_issue_prompt",
    # Prompts
    "PRODUCT_LABELING_PROMPT",
]

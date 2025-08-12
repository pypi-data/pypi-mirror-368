"""
Scorers module for bench evaluation framework.

This module provides various scoring functions for evaluating model outputs
across different types of tasks including mathematical problems, code generation,
and multiple choice questions.

Note: Eval-specific scorers (like those for MMLU and HumanEval) are not exported
from this module intentionally, as they are tailored to specific evaluation tasks
and should be imported directly from their respective modules when needed.
"""

from .score_last_number import score_last_integer, score_last_number
from .score_boxed import score_boxed
from .fallback_scorer import fallback_scorer

__all__ = [
    # Number scoring functions
    "score_last_integer",
    "score_last_number",
    # Boxed answer scoring
    "score_boxed",
    # Meta-scoring
    "fallback_scorer",
]

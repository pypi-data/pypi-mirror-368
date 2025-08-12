"""
Utility functions shared across CLI commands.
"""

from types import SimpleNamespace
from openbench.config import BenchmarkMetadata


def get_category_display_name(category: str) -> str:
    """Generate display name for category."""
    display = category.replace("_", " ").replace("-", " ").title()
    if "benchmark" not in display.lower():
        display += " Benchmarks"
    return display


def benchmark_to_eval_config(meta: BenchmarkMetadata):
    """Convert BenchmarkMetadata to a simple eval config for display."""
    return SimpleNamespace(
        name=meta.name,
        description=meta.description,
        category=meta.category,
        tags=meta.tags,
    )


def matches_search(eval_config, query: str) -> bool:
    """Check if an evaluation matches the search query."""
    query = query.lower()
    return (
        query in eval_config.name.lower()
        or query in eval_config.description.lower()
        or any(query in tag.lower() for tag in eval_config.tags)
    )

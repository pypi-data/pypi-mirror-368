"""
Minimal configuration for benchmarks.
Only contains human-written metadata that cannot be extracted from code.
Everything else (epochs, temperature, etc.) comes from the actual task definitions.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class BenchmarkMetadata:
    """Minimal metadata for a benchmark - only what can't be extracted."""

    name: str  # Human-readable display name
    description: str  # Human-written description
    category: str  # Category for grouping
    tags: List[str]  # Tags for searchability

    # Registry info - still needed
    module_path: str
    function_name: str


# Benchmark metadata - minimal, no duplication
BENCHMARKS = {
    # Core benchmarks
    "mmlu": BenchmarkMetadata(
        name="MMLU (cais/mmlu)",
        description="Massive Multitask Language Understanding - 57 academic subjects from the cais/mmlu dataset",
        category="core",
        tags=["multiple-choice", "knowledge", "reasoning", "multitask"],
        module_path="openbench.evals.mmlu",
        function_name="mmlu",
    ),
    "openai_mrcr": BenchmarkMetadata(
        name="OpenAI MRCR (Full)",
        description="Memory-Recall with Contextual Retrieval - long-context evaluation that measures recall of 2, 4, and 8 needles across million-token contexts",
        category="core",
        tags=["long-context", "retrieval", "needle", "sequence-matching"],
        module_path="openbench.evals.mrcr",
        function_name="openai_mrcr",
    ),
    "openai_mrcr_2n": BenchmarkMetadata(
        name="OpenAI MRCR (2 Needles)",
        description="Memory-Recall with Contextual Retrieval - long-context evaluation that measures recall of 2 needles across million-token contexts",
        category="core",
        tags=["long-context", "retrieval", "needle", "sequence-matching"],
        module_path="openbench.evals.mrcr",
        function_name="openai_mrcr_2n",
    ),
    "openai_mrcr_4n": BenchmarkMetadata(
        name="OpenAI MRCR (4 Needles)",
        description="Memory-Recall with Contextual Retrieval - long-context evaluation that measures recall of 4 needles across million-token contexts",
        category="core",
        tags=["long-context", "retrieval", "needle", "sequence-matching"],
        module_path="openbench.evals.mrcr",
        function_name="openai_mrcr_4n",
    ),
    "openai_mrcr_8n": BenchmarkMetadata(
        name="OpenAI MRCR (8 Needles)",
        description="Memory-Recall with Contextual Retrieval - long-context evaluation that measures recall of 8 needles across million-token contexts",
        category="core",
        tags=["long-context", "retrieval", "needle", "sequence-matching"],
        module_path="openbench.evals.mrcr",
        function_name="openai_mrcr_8n",
    ),
    "gpqa_diamond": BenchmarkMetadata(
        name="GPQA Diamond",
        description="Graduate-level Google-Proof Q&A in biology, chemistry, and physics",
        category="core",
        tags=["multiple-choice", "science", "graduate-level"],
        module_path="openbench.evals.gpqa_diamond",
        function_name="gpqa_diamond",
    ),
    "humaneval": BenchmarkMetadata(
        name="HumanEval",
        description="Code generation benchmark with 164 programming problems",
        category="core",
        tags=["coding", "generation", "execution"],
        module_path="openbench.evals.humaneval",
        function_name="humaneval",
    ),
    "openbookqa": BenchmarkMetadata(
        name="OpenBookQA",
        description="Elementary-level science questions probing understanding of core facts",
        category="core",
        tags=["multiple-choice", "science", "elementary", "open-book"],
        module_path="openbench.evals.openbookqa",
        function_name="openbookqa",
    ),
    "musr": BenchmarkMetadata(
        name="MuSR",
        description="Testing the Limits of Chain-of-thought with Multistep Soft Reasoning - includes murder mysteries, object placements, and team allocation tasks",
        category="core",
        tags=["multiple-choice", "reasoning", "commonsense", "chain-of-thought"],
        module_path="openbench.evals.musr",
        function_name="musr",
    ),
    "supergpqa": BenchmarkMetadata(
        name="SuperGPQA",
        description="Scaling LLM Evaluation across 285 Graduate Disciplines - 26,529 multiple-choice questions across science, engineering, medicine, economics, and philosophy",
        category="core",
        tags=["multiple-choice", "knowledge", "graduate-level", "multidisciplinary"],
        module_path="openbench.evals.supergpqa",
        function_name="supergpqa",
    ),
    "simpleqa": BenchmarkMetadata(
        name="SimpleQA",
        description="Measuring short-form factuality in large language models with simple Q&A pairs",
        category="core",
        tags=["factuality", "question-answering", "graded"],
        module_path="openbench.evals.simpleqa",
        function_name="simpleqa",
    ),
    "hle": BenchmarkMetadata(
        name="Humanity's Last Exam",
        description="Multi-modal benchmark at the frontier of human knowledge - 2,500 questions across mathematics, humanities, and natural sciences designed by subject-matter experts globally",
        category="core",
        tags=["knowledge", "reasoning", "multi-modal", "graded", "frontier"],
        module_path="openbench.evals.hle",
        function_name="hle",
    ),
    "hle_text": BenchmarkMetadata(
        name="Humanity's Last Exam (Text-Only)",
        description="Text-only variant of HLE with multi-modal questions filtered out - evaluates models without vision capabilities on text-based questions from the frontier of human knowledge",
        category="core",
        tags=["knowledge", "reasoning", "text-only", "graded", "frontier"],
        module_path="openbench.evals.hle",
        function_name="hle_text",
    ),
    "healthbench": BenchmarkMetadata(
        name="HealthBench",
        description="Medical dialogue evaluation using physician-created rubrics for assessing healthcare conversations",
        category="core",
        tags=["medical", "dialogue", "graded", "rubric-based"],
        module_path="openbench.evals.healthbench",
        function_name="healthbench",
    ),
    "healthbench_hard": BenchmarkMetadata(
        name="HealthBench Hard",
        description="Most challenging medical dialogue cases from HealthBench requiring nuanced medical knowledge",
        category="core",
        tags=["medical", "dialogue", "graded", "rubric-based", "hard"],
        module_path="openbench.evals.healthbench",
        function_name="healthbench_hard",
    ),
    "healthbench_consensus": BenchmarkMetadata(
        name="HealthBench Consensus",
        description="Medical dialogue cases with strong physician consensus on appropriate responses",
        category="core",
        tags=["medical", "dialogue", "graded", "rubric-based", "consensus"],
        module_path="openbench.evals.healthbench",
        function_name="healthbench_consensus",
    ),
    "mgsm": BenchmarkMetadata(
        name="MGSM",
        description="Multilingual Grade School Math benchmark across 11 languages for testing mathematical reasoning",
        category="core",
        tags=["math", "multilingual", "reasoning", "chain-of-thought"],
        module_path="openbench.evals.mgsm",
        function_name="mgsm",
    ),
    "mgsm_en": BenchmarkMetadata(
        name="MGSM English",
        description="Grade school math problems in English for testing mathematical reasoning",
        category="core",
        tags=["math", "english", "reasoning", "chain-of-thought"],
        module_path="openbench.evals.mgsm",
        function_name="mgsm_en",
    ),
    "mgsm_latin": BenchmarkMetadata(
        name="MGSM Latin Script",
        description="Grade school math problems in Latin script languages (German, English, Spanish, French, Swahili)",
        category="core",
        tags=["math", "multilingual", "latin-script", "reasoning", "chain-of-thought"],
        module_path="openbench.evals.mgsm",
        function_name="mgsm_latin",
    ),
    "mgsm_non_latin": BenchmarkMetadata(
        name="MGSM Non-Latin Script",
        description="Grade school math problems in non-Latin script languages (Bengali, Japanese, Russian, Telugu, Thai, Chinese)",
        category="core",
        tags=[
            "math",
            "multilingual",
            "non-latin-script",
            "reasoning",
            "chain-of-thought",
        ],
        module_path="openbench.evals.mgsm",
        function_name="mgsm_non_latin",
    ),
    "drop": BenchmarkMetadata(
        name="DROP",
        description="Reading comprehension benchmark requiring discrete reasoning over paragraphs (arithmetic, counting, sorting)",
        category="core",
        tags=[
            "reading-comprehension",
            "reasoning",
            "arithmetic",
            "counting",
            "sorting",
        ],
        module_path="openbench.evals.drop",
        function_name="drop",
    ),
    "math": BenchmarkMetadata(
        name="MATH",
        description="Measuring Mathematical Problem Solving - 5000 competition math problems across 7 subjects and 5 difficulty levels",
        category="core",
        tags=["math", "problem-solving", "reasoning", "competition", "graded"],
        module_path="openbench.evals.math",
        function_name="math",
    ),
    "math_500": BenchmarkMetadata(
        name="MATH-500",
        description="500-problem subset of MATH dataset for faster evaluation of mathematical problem solving",
        category="core",
        tags=[
            "math",
            "problem-solving",
            "reasoning",
            "competition",
            "graded",
            "subset",
        ],
        module_path="openbench.evals.math",
        function_name="math_500",
    ),
    # Math competitions
    "aime_2023_I": BenchmarkMetadata(
        name="AIME 2023 I",
        description="American Invitational Mathematics Examination 2023 (First)",
        category="math",
        tags=["math", "competition", "aime", "2023"],
        module_path="openbench.evals.matharena.aime_2023_I.aime_2023_I",
        function_name="aime_2023_I",
    ),
    "aime_2023_II": BenchmarkMetadata(
        name="AIME 2023 II",
        description="American Invitational Mathematics Examination 2023 (Second)",
        category="math",
        tags=["math", "competition", "aime", "2023"],
        module_path="openbench.evals.matharena.aime_2023_II.aime_2023_II",
        function_name="aime_2023_II",
    ),
    "aime_2024": BenchmarkMetadata(
        name="AIME 2024",
        description="American Invitational Mathematics Examination 2024 (Combined I & II)",
        category="math",
        tags=["math", "competition", "aime", "2024", "combined"],
        module_path="openbench.evals.matharena.aime_2024.aime_2024",
        function_name="aime_2024",
    ),
    "aime_2024_I": BenchmarkMetadata(
        name="AIME 2024 I",
        description="American Invitational Mathematics Examination 2024 (First)",
        category="math",
        tags=["math", "competition", "aime", "2024"],
        module_path="openbench.evals.matharena.aime_2024_I.aime_2024_I",
        function_name="aime_2024_I",
    ),
    "aime_2024_II": BenchmarkMetadata(
        name="AIME 2024 II",
        description="American Invitational Mathematics Examination 2024 (Second)",
        category="math",
        tags=["math", "competition", "aime", "2024"],
        module_path="openbench.evals.matharena.aime_2024_II.aime_2024_II",
        function_name="aime_2024_II",
    ),
    "aime_2025": BenchmarkMetadata(
        name="AIME 2025",
        description="American Invitational Mathematics Examination 2025",
        category="math",
        tags=["math", "competition", "aime", "2025"],
        module_path="openbench.evals.matharena.aime_2025.aime_2025",
        function_name="aime_2025",
    ),
    "aime_2025_II": BenchmarkMetadata(
        name="AIME 2025 II",
        description="American Invitational Mathematics Examination 2025 (Second)",
        category="math",
        tags=["math", "competition", "aime", "2025"],
        module_path="openbench.evals.matharena.aime_2025_II.aime_2025_II",
        function_name="aime_2025_II",
    ),
    "brumo_2025": BenchmarkMetadata(
        name="BRUMO 2025",
        description="Bruno Mathematical Olympiad 2025",
        category="math",
        tags=["math", "competition", "olympiad", "2025"],
        module_path="openbench.evals.matharena.brumo_2025.brumo_2025",
        function_name="brumo_2025",
    ),
    "hmmt_feb_2023": BenchmarkMetadata(
        name="HMMT Feb 2023",
        description="Harvard-MIT Mathematics Tournament February 2023",
        category="math",
        tags=["math", "competition", "hmmt", "2023"],
        module_path="openbench.evals.matharena.hmmt_feb_2023.hmmt_feb_2023",
        function_name="hmmt_feb_2023",
    ),
    "hmmt_feb_2024": BenchmarkMetadata(
        name="HMMT Feb 2024",
        description="Harvard-MIT Mathematics Tournament February 2024",
        category="math",
        tags=["math", "competition", "hmmt", "2024"],
        module_path="openbench.evals.matharena.hmmt_feb_2024.hmmt_feb_2024",
        function_name="hmmt_feb_2024",
    ),
    "hmmt_feb_2025": BenchmarkMetadata(
        name="HMMT Feb 2025",
        description="Harvard-MIT Mathematics Tournament February 2025",
        category="math",
        tags=["math", "competition", "hmmt", "2025"],
        module_path="openbench.evals.matharena.hmmt_feb_2025.hmmt_feb_2025",
        function_name="hmmt_feb_2025",
    ),
}


def get_benchmark_metadata(name: str) -> Optional[BenchmarkMetadata]:
    """Get benchmark metadata by name."""
    return BENCHMARKS.get(name)


def get_all_benchmarks() -> dict[str, BenchmarkMetadata]:
    """Get all benchmark metadata."""
    return BENCHMARKS


def get_benchmarks_by_category(category: str) -> dict[str, BenchmarkMetadata]:
    """Get all benchmarks in a category."""
    return {
        name: meta for name, meta in BENCHMARKS.items() if meta.category == category
    }


def get_categories() -> List[str]:
    """Get all available categories."""
    return sorted(list(set(meta.category for meta in BENCHMARKS.values())))


def search_benchmarks(query: str) -> dict[str, BenchmarkMetadata]:
    """Search benchmarks by name, description, or tags."""
    query = query.lower()
    results = {}

    for name, meta in BENCHMARKS.items():
        if (
            query in meta.name.lower()
            or query in meta.description.lower()
            or any(query in tag.lower() for tag in meta.tags)
        ):
            results[name] = meta

    return results

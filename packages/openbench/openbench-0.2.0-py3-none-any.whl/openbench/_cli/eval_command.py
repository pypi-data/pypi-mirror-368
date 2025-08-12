from typing import Optional, List, Dict, Annotated, Tuple, Union
from enum import Enum
import typer
from inspect_ai import eval
from inspect_ai.model import Model

from openbench._registry import load_task
from openbench.monkeypatch.display_results_patch import patch_display_results


class SandboxType(str, Enum):
    """Type of environment to run evaluations in."""

    LOCAL = "local"
    DOCKER = "docker"


class DisplayType(str, Enum):
    """Display type for evaluation progress."""

    FULL = "full"
    CONVERSATION = "conversation"
    RICH = "rich"
    PLAIN = "plain"
    NONE = "none"


class ReasoningEffortLevel(str, Enum):
    """Reasoning effort level."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


def parse_limit(value: Optional[str]) -> Optional[Union[int, Tuple[int, int]]]:
    """Parse the limit parameter which can be an int or a tuple of ints.

    Args:
        value: The value passed to the --limit option.

    Returns:
        Parsed limit value: int, tuple of (start, end), or None.

    Raises:
        typer.BadParameter: If the input format is incorrect.
    """
    if value is None:
        return None

    try:
        if "," in value:
            start, end = map(int, value.split(","))
            return (start, end)
        return int(value)
    except ValueError:
        raise typer.BadParameter(
            "Limit must be an integer or two integers separated by a comma"
        )


def validate_model_name(model: str, context: str = "") -> None:
    """Validate a model name format.

    Args:
        model: Model name to validate
        context: Additional context for error message

    Raises:
        typer.BadParameter: If model name format is invalid
    """
    if not model or "/" not in model:
        raise typer.BadParameter(
            f"Invalid model name format{context}: {model}. Expected format: provider/model-name"
        )


def validate_model_role(model_role: Optional[str]) -> Dict[str, str | Model]:
    """Validate and parse model role string.

    Args:
        model_role: Optional string in format 'role=model'

    Returns:
        Dictionary mapping role to model name

    Raises:
        typer.BadParameter: If model_role format is invalid
    """
    if not model_role:
        return {}

    try:
        role, model = model_role.split("=")
        if not role or not model:
            raise ValueError("Model role must be in format 'role=model'")
        validate_model_name(model, f" for role '{role}'")
        return {role: model}
    except ValueError as e:
        raise typer.BadParameter(str(e))


def run_eval(
    benchmarks: Annotated[
        List[str],
        typer.Argument(
            help="Benchmark(s) to run. Can be a built-in name (e.g. mmlu) or a path to a local eval directory/file containing __metadata__",
            envvar="BENCH_BENCHMARKS",
        ),
    ],
    model: Annotated[
        List[str],
        typer.Option(
            help="Model(s) to evaluate. Equivalent to --model-role candidate=<model>",
            envvar="BENCH_MODEL",
        ),
    ] = ["groq/meta-llama/llama-4-scout-17b-16e-instruct"],
    max_connections: Annotated[
        Optional[int],
        typer.Option(
            help="Maximum number of parallel requests to the model",
            envvar="BENCH_MAX_CONNECTIONS",
        ),
    ] = 10,
    model_base_url: Annotated[
        Optional[str],
        typer.Option(help="Base URL for model(s)", envvar="BENCH_MODEL_BASE_URL"),
    ] = None,
    model_role: Annotated[
        List[str],
        typer.Option(
            help="Model role(s). For example, --model-role grader=groq/meta-llama/llama-4-scout-17b-16e-instruct. Can be specified multiple times.",
            envvar="BENCH_MODEL_ROLE",
        ),
    ] = [],
    logfile: Annotated[
        Optional[str],
        typer.Option(help="Output file for results", envvar="BENCH_OUTPUT"),
    ] = None,
    sandbox: Annotated[
        Optional[SandboxType],
        typer.Option(
            help="Environment to run the evaluation in (local or docker)",
            case_sensitive=False,
            envvar="BENCH_SANDBOX",
        ),
    ] = None,
    epochs: Annotated[
        int,
        typer.Option(
            help="Number of epochs to run each evaluation", envvar="BENCH_EPOCHS"
        ),
    ] = 1,
    limit: Annotated[
        Optional[str],
        typer.Option(
            help="Limit evaluated samples (single number or start,end)",
            envvar="BENCH_LIMIT",
        ),
    ] = None,
    fail_on_error: Annotated[
        Optional[float],
        typer.Option(
            help="Failure threshold for sample errors. If between 0 and 1, it is interpreted as a percentage of samples that can fail. If greater than 1, it is interpreted as a fixed number of samples that can fail",
            envvar="BENCH_FAIL_ON_ERROR",
        ),
    ] = None,
    message_limit: Annotated[
        Optional[int],
        typer.Option(
            help="Maximum number of messages one sample can run",
            envvar="BENCH_MESSAGE_LIMIT",
        ),
    ] = None,
    max_subprocesses: Annotated[
        Optional[int],
        typer.Option(
            help="Maximum number of parallel subprocesses",
            envvar="BENCH_MAX_SUBPROCESSES",
        ),
    ] = None,
    log_samples: Annotated[
        Optional[bool],
        typer.Option(
            help="Log detailed samples and scores",
            envvar="BENCH_LOG_SAMPLES",
        ),
    ] = None,
    log_images: Annotated[
        Optional[bool],
        typer.Option(
            help="Log base64 encoded images",
            envvar="BENCH_LOG_IMAGES",
        ),
    ] = None,
    log_buffer: Annotated[
        Optional[int],
        typer.Option(
            help="Number of samples to buffer before writing to log",
            envvar="BENCH_LOG_BUFFER",
        ),
    ] = 10,
    score: Annotated[
        bool,
        typer.Option(
            help="Grade the benchmark, or leave unscored",
            envvar="BENCH_SCORE",
        ),
    ] = True,
    temperature: Annotated[
        float,
        typer.Option(
            help="Model temperature",
            envvar="BENCH_TEMPERATURE",
        ),
    ] = 0.6,
    top_p: Annotated[
        float,
        typer.Option(
            help="Model top-p",
            envvar="BENCH_TOP_P",
        ),
    ] = 1.0,
    max_tokens: Annotated[
        Optional[int],
        typer.Option(
            help="Maximum tokens for model response",
            envvar="BENCH_MAX_TOKENS",
        ),
    ] = None,
    seed: Annotated[
        Optional[int],
        typer.Option(
            help="Seed for deterministic generation",
            envvar="BENCH_SEED",
        ),
    ] = None,
    display: Annotated[
        Optional[DisplayType],
        typer.Option(
            help="Display type for evaluation progress",
            envvar="BENCH_DISPLAY",
            case_sensitive=False,
        ),
    ] = None,
    timeout: Annotated[
        Optional[int],
        typer.Option(
            help="Timeout for each request to the model API in seconds",
            envvar="BENCH_TIMEOUT",
        ),
    ] = 10000,
    reasoning_effort: Annotated[
        Optional[ReasoningEffortLevel],
        typer.Option(
            help="Reasoning effort level. used for reasoning models like openai/o3",
            envvar="BENCH_REASONING_EFFORT",
            case_sensitive=False,
        ),
    ] = None,
) -> None:
    """
    Run a benchmark on a model.
    """
    # Validate and aggregate model_role(s) into a dict
    role_models = {}
    for mr in model_role:
        parsed = validate_model_role(mr)
        for k, v in parsed.items():
            if k in role_models:
                raise typer.BadParameter(f"Duplicate model role: {k}")
            role_models[k] = v

    # Check for mutual exclusivity between --model and --model-role candidate
    if model and "candidate" in role_models:
        raise typer.BadParameter(
            "Cannot specify both --model and --model-role candidate=<model>"
        )

    # Validate model names
    for m in model:
        validate_model_name(m)

    # Load tasks from registry
    tasks = []
    for benchmark in benchmarks:
        try:
            task = load_task(benchmark)
            tasks.append(task)
        except (ValueError, ImportError, AttributeError) as e:
            raise typer.BadParameter(str(e))

    # Monkey patch FileRecorder log file name if logfile is provided
    if logfile:
        from openbench.monkeypatch.file_recorder_logfile_patch import (
            patch_file_recorder_logfile,
        )

        patch_file_recorder_logfile(logfile)

    # Parse limit string to int or tuple
    parsed_limit = parse_limit(limit)

    # Apply display patch
    patch_display_results()

    eval(
        tasks=tasks,
        model=model,
        max_connections=max_connections,
        model_base_url=model_base_url,
        model_roles=role_models if role_models else None,
        epochs=epochs,
        limit=parsed_limit,
        fail_on_error=fail_on_error,
        message_limit=message_limit,
        max_subprocesses=max_subprocesses,
        log_samples=log_samples,
        log_images=log_images,
        log_buffer=log_buffer,
        score=score,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        seed=seed,
        display=display.value if display else None,
        timeout=timeout,
        reasoning_effort=reasoning_effort.value if reasoning_effort else None,
        sandbox=sandbox,
    )

    # Placeholder - actual implementation would run the evaluation
    typer.echo("Evaluation complete!")

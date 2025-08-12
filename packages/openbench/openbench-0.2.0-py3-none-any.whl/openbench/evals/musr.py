"""OpenBench implementation of MuSR (Testing the Limits of Chain-of-thought with Multistep Soft Reasoning).
MuSR is a dataset that tests chain-of-thought reasoning with three types of tasks:
- Murder mysteries: Who is the most likely murderer?
- Object placements: Where would someone look for an object?
- Team allocation: How to allocate people to tasks efficiently?

Implemented by Aarush Sah
"""

import ast
from inspect_ai import Task, task
from inspect_ai.dataset import Sample, hf_dataset
from inspect_ai.scorer import choice
from inspect_ai.solver import multiple_choice


def record_to_sample(record: dict) -> Sample:
    # Parse the choices string representation into an actual list
    choices_list = ast.literal_eval(record["choices"])

    return Sample(
        input=f"{record['narrative']}\n\n{record['question']}",
        choices=choices_list,
        target=chr(ord("A") + int(record["answer_index"])),
        metadata={
            "narrative": record["narrative"],
            "question": record["question"],
            "answer_choice": record["answer_choice"],
            "answer_index": record["answer_index"],
        },
    )


@task
def musr(subset: str = "murder_mysteries") -> Task:
    """
    MuSR (Multistep Soft Reasoning) evaluation task.

    Args:
        subset: The subset of the dataset to use. Options are:
                - "murder_mysteries": Murder mystery scenarios
                - "object_placements": Object placement reasoning
                - "team_allocation": Team allocation problems
    """
    if subset not in ["murder_mysteries", "object_placements", "team_allocation"]:
        raise ValueError(
            f"Invalid subset '{subset}'. Must be one of: murder_mysteries, object_placements, team_allocation"
        )

    return Task(
        dataset=hf_dataset(
            path="TAUR-Lab/MuSR",
            split=subset,
            sample_fields=record_to_sample,
        ),
        solver=multiple_choice(),
        scorer=choice(),
    )

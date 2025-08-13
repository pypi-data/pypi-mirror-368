"""(Hierarchical) Task Plan."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from pprint import pformat
from types import SimpleNamespace

import yaml

from dana.contrib.knows.core.fs import PathOrStr

__all__ = ["TaskPlan"]

class HTP(SimpleNamespace):
    """Brief name for Hierarchical Task Plan."""

@dataclass
class TaskPlan:
    """Representation of hierarchical tasks."""

    task: str
    subs: list[TaskPlan] = field(default_factory=list)
    parameters: list[str] = field(default_factory=list, repr=False)

    @property
    def pformat(self) -> str:
        """Format the task plan as a pretty string.

        Args:
            indent: Current indentation level (default: 0)

        Returns:
            Formatted string showing task plan

        Example:
            >>> print(hierarchy.pformat)
            HTP(
                task="Calculate Cash Conversion Cycle for {COMPANY}",
                subs=[
                    HTP(task="Get financial data",
                        subs=[HTP(task="Fetch inventory data"),
                              HTP(task="Fetch receivables data")]),
                    HTP(task="Calculate DIO"),
                    HTP(task="Calculate final CCC")
                ]
            )
        """
        def _to_namespace(htp: TaskPlan) -> HTP:
            # Create base namespace with task
            ns_dict: dict[str, str | list[HTP]] = {'task': htp.task}

            # Only add subs if non-empty
            if htp.subs:
                ns_dict['subs'] = [_to_namespace(sub) for sub in htp.subs]

            return HTP(**ns_dict)

        # Format with pprint, strip quotes for better readability
        return pformat(object=_to_namespace(self),
                       indent=1,
                       width=102,
                       depth=None,
                       compact=False,
                       sort_dicts=False,
                       underscore_numbers=False).replace('\\n', '')

    def __repr__(self) -> str:
        """Get string representation showing task plan."""
        return self.pformat

    @classmethod
    def from_dict(cls, htp_dict: dict[str, str | dict]) -> TaskPlan:
        """Create task plan from dictionary specification.

        Args:
            task_hierarchy_dict: Dictionary containing task specification with:
                - task: Main task description
                - subs: List of subtask dictionaries (optional)

        Returns:
            TaskPlan instance with main task and subtasks

        Example:
            >>> hierarchy = TaskPlan.from_dict({
            ...     'task': 'Calculate CCC for {COMPANY}',
            ...     'subs': [
            ...         {'task': 'Get inventory data'},
            ...         {'task': 'Calculate DIO'}
            ...     ]
            ... })
        """
        return cls(task=(task := htp_dict.get('task', '')),
                   subs=[cls.from_dict(sub_dict) for sub_dict in htp_dict.get('subs', [])],
                   parameters=cls._extract_parameters(task))

    @classmethod
    def from_yaml(cls, yaml_src: PathOrStr, /) -> dict[str, TaskPlan]:
        """Load task hierarchies from YAML pattern file.

        Handles two YAML formats:
        1. Multiple named hierarchies:
            hierarchy1:
                task: "Task 1"
                subs: [...]
            hierarchy2:
                task: "Task 2"
                subs: [...]

        Args:
            yaml_path: Path to YAML file

        Returns:
            Either a Dict[str, TaskPlan]
        """
        if isinstance(yaml_src, Path | str):
            with Path(yaml_src).open('r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

        else:  # if yaml_src is already a stream
            data = yaml.safe_load(yaml_src)

        return {name: cls.from_dict(spec) for name, spec in data.items()}

    @staticmethod
    def _extract_parameters(text: str) -> list[str]:
        """Extract parameter names from text like {COMPANY}, {PERIOD}."""
        return re.findall(r'\{([^}]+)\}', text)

    @staticmethod
    def _substitute_params(text: str, values: dict[str, str]) -> str:
        """Replace parameter placeholders with values."""
        result = text
        for param, value in values.items():
            result = result.replace(f"{{{param}}}", value)
        return result

    def parameterize(self, param_values: dict[str, str]) -> TaskPlan:
        """Create new instance with parameter values substituted.

        Args:
            param_values: Dictionary mapping parameter names to values

        Returns:
            New TaskPlan with parameters replaced by values

        Example:
            >>> task = TaskPlan.from_dict({'task': 'Analyze {COMPANY}'})
            >>> parameterized = task.parameterize({'COMPANY': 'AAPL'})
        """
        return TaskPlan(task=self._substitute_params(self.task, param_values),
                        subs=[sub_task.parameterize(param_values) for sub_task in self.subs],
                        parameters=self.parameters.copy())

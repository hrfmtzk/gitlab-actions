from typing import Any, Dict, List, TextIO

import yaml
from gitlab.v4.objects import Project

from . import actions as act
from .actions import BaseAction
from .targets import BaseTarget, IssueTarget, MergeRequestTarget, TargetType


class JobRunner:
    def __init__(
        self,
        name: str,
        target_type: TargetType,
        conditions: Dict[str, Any],
        actions: List[BaseAction],
    ) -> None:
        self.name: str = name
        self.target_type: TargetType = target_type
        self.conditions: Dict[str, Any] = conditions
        self.actions: List[BaseAction] = actions

    def _get_filtered_targets(self, project: Project) -> List[BaseTarget]:
        target_manager = {
            TargetType.ISSUE: project.issues,
            TargetType.MERGE_REQUEST: project.mergerequests,
        }[self.target_type]
        native_targets = target_manager.list(all=True, **self.conditions)

        target_class = {
            TargetType.ISSUE: IssueTarget,
            TargetType.MERGE_REQUEST: MergeRequestTarget,
        }[self.target_type]
        targets = [
            target_class(native_target) for native_target in native_targets
        ]

        return targets

    def run(self, project: Project) -> List[BaseTarget]:
        targets: List[BaseTarget] = self._get_filtered_targets(project)

        for action in self.actions:
            for target in targets:
                action.run(target)

        return targets


class JobParser:
    def __init__(self, job_file: TextIO) -> None:
        self.raw_data: Dict[str, Any] = yaml.safe_load(job_file)
        self.jobs: List[JobRunner] = []

    def _action_mapper(self, action: Dict[str, Any]) -> BaseAction:
        action_type = action["type"]
        try:
            action_class = getattr(act, action_type.title() + "Action")
        except AttributeError:
            raise ValueError(f'action type "{action_type}" is not supported')
        return action_class(**action["property"])

    def _parse(self, job: Dict[str, Any]) -> JobRunner:
        return JobRunner(
            name=job["name"],
            target_type=TargetType(job["target"]),
            conditions=job["filters"],
            actions=[self._action_mapper(action) for action in job["actions"]],
        )

    def parse(self) -> None:
        for job in self.raw_data["jobs"]:
            self.jobs.append(self._parse(job))

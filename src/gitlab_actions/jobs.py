from typing import Any, Dict, List

from gitlab.v4.objects import Project

from .actions import BaseAction
from .targets import BaseTarget, IssueTarget, MergeRequestTarget, TargetType


class JobRunner:
    def __init__(
        self,
        project: Project,
        target_type: TargetType,
        conditions: Dict[str, Any],
        actions: List[BaseAction],
    ) -> None:
        self.project: Project = project
        self.target_type: TargetType = target_type
        self.conditions: Dict[str, Any] = conditions
        self.actions: List[BaseAction] = actions

    def _get_filtered_targets(self) -> List[BaseTarget]:
        target_manager = {
            TargetType.ISSUE: self.project.issues,
            TargetType.MERGE_REQUEST: self.project.mergerequests,
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

    def run(self) -> None:
        targets: List[BaseTarget] = self._get_filtered_targets()

        for action in self.actions:
            for target in targets:
                action.run(target)

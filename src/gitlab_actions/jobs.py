from typing import List

from gitlab.v4.objects import Project

from .actions import BaseAction
from .filters import BaseFilter
from .targets import BaseTarget, IssueTarget, MergeRequestTarget, TargetType


class JobRunner:
    def __init__(
        self,
        project: Project,
        target_type: TargetType,
        filters: List[BaseFilter],
        actions: List[BaseAction],
    ) -> None:
        self.project: Project = project
        self.target_type: TargetType = target_type
        self.filters: List[BaseFilter] = filters
        self.actions: List[BaseAction] = actions

    def _get_filtered_targets(self) -> List[BaseTarget]:
        list_conditions = {
            filter.list_condition_key: filter.list_condition_value
            for filter in self.filters
            if filter.support_list_condition
        }
        target_manager = {
            TargetType.ISSUE: self.project.issues,
            TargetType.MERGE_REQUEST: self.project.mergerequests,
        }[self.target_type]
        native_targets = target_manager.list(**list_conditions)

        target_class = {
            TargetType.ISSUE: IssueTarget,
            TargetType.MERGE_REQUEST: MergeRequestTarget,
        }[self.target_type]
        targets = [
            target_class(native_target) for native_target in native_targets
        ]

        for filter in self.filters:
            if filter.support_list_condition:
                continue
            targets = filter.filter(targets)

        return targets

    def run(self) -> None:
        targets: List[BaseTarget] = self._get_filtered_targets()

        for action in self.actions:
            for target in targets:
                action.run(target)

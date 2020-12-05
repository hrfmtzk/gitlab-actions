from typing import Dict, List, Optional

from gitlab.v4.objects import Project

from .targets import BaseTarget


class BaseAction:
    def run(self, target: BaseTarget) -> None:
        raise NotImplementedError


class StateAction(BaseAction):
    CLOSE = "close"
    REOPEN = "reopen"

    def __init__(self, state: str) -> None:
        self.state = state

    def run(self, target: BaseTarget) -> None:
        target._native_target.state_event = self.state
        target._native_target.save()


class LabelAction(BaseAction):
    def __init__(
        self,
        labels: Optional[List[str]] = None,
        add_labels: Optional[List[str]] = None,
        remove_labels: Optional[List[str]] = None,
    ) -> None:
        if labels and (add_labels or remove_labels):
            raise ValueError("can't accept labels and add/remove labels")
        self.labels = labels
        self.add_labels = add_labels
        self.remove_labels = remove_labels

    def run(self, target: BaseTarget) -> None:
        if self.labels:
            target._native_target.labels = self.labels
        else:
            target._native_target.add_labels = self.add_labels
            target._native_target.remove_labels = self.remove_labels
        target._native_target.save()


class AssigneeAction(BaseAction):
    _member_cache: Dict[str, int] = {}

    def __init__(
        self, project: Project, username: Optional[str] = None
    ) -> None:
        if username and username not in self._member_cache:
            members = project.members.list(username=username)
            if not members:
                raise ValueError(f"{username} is not a project member")
            self._member_cache[username] = members[0].id
        self.username = username

    def run(self, target: BaseTarget) -> None:
        if self.username:
            target._native_target.assignee_ids = [
                self._member_cache[self.username]
            ]
        else:
            target._native_target.assignee_ids = []
        target._native_target.save()


class MilestoneAction(BaseAction):
    _milestone_cache: Dict[str, int] = {}

    def __init__(
        self, project: Project, milestone: Optional[str] = None
    ) -> None:
        if milestone and milestone not in self._milestone_cache:
            milestones = project.milestones.list(title=milestone)
            if not milestones:
                raise ValueError(f"{milestone} does not exist")
            self._milestone_cache[milestone] = milestones[0].id
        self.milestone = milestone

    def run(self, target: BaseTarget) -> None:
        if self.milestone:
            target._native_target.milestone_id = [
                self._milestone_cache[self.milestone]
            ]
        else:
            target._native_target.milestone_id = None
        target._native_target.save()


class NoteAction(BaseAction):
    def __init__(self, body: str) -> None:
        self.body = body

    def run(self, target: BaseTarget) -> None:
        target._native_target.notes.create({"body": self.body})

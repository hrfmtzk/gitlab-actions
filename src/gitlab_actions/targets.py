from enum import Enum


class TargetType(Enum):
    ISSUE = "issue"
    MERGE_REQUEST = "merge_request"


class BaseTarget:
    type: TargetType = TargetType.ISSUE

    def __init__(self, native_target) -> None:
        self._native_target = native_target


class IssueTarget(BaseTarget):
    type: TargetType = TargetType.ISSUE


class MergeRequestTarget(BaseTarget):
    type: TargetType = TargetType.MERGE_REQUEST

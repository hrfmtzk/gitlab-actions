from .targets import BaseTarget


class BaseAction:
    def __init__(self, target) -> None:
        self.target = target

    def run(self, target: BaseTarget) -> None:
        raise NotImplementedError

from typing import Any

from amberflow.primitives.primitives import DirHandle

__all__ = [
    "FlowAnalysisABFE",
    "FlowABFE",
]


class FlowAnalysisABFE:
    name: str
    root_dir: DirHandle

    def __init__(self, *args, **kwargs) -> None:
        pass

    def run_wait(self, *args, **kwargs) -> Any:
        pass


class FlowABFE:
    name: str
    root_dir: DirHandle

    def __init__(self, *args, **kwargs) -> None:
        pass

    def run_wait(self, *args, **kwargs) -> Any:
        pass

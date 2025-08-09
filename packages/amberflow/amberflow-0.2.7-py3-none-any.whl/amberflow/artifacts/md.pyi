from typing import List, Type, Any
from amberflow.primitives import filepath_t
from amberflow.artifacts import BaseArtifactFile, BaseArtifactDir

__all__ = (
    "MdoutMD",
    "BoreschRestraints",
    "CpptrajData",
    "Groupfile",
    "LambdaScheduleFile",
    "Remlog",
)

class MdoutMD(BaseArtifactFile):
    prefix: str
    suffix: str
    tags: tuple[str]

    def __init__(self, filepath: filepath_t, *args: Any, **kwargs: Any) -> None: ...

class BoreschRestraints(BaseArtifactFile):
    prefix: str
    suffix: str
    tags: tuple[str]

    def __init__(
        self,
        filepath: filepath_t,
        *args: Any,
        **kwargs: Any,
    ) -> None: ...

class CpptrajData(BaseArtifactFile):
    prefix: str
    suffix: str
    tags: tuple[str]

    def __init__(self, filepath: filepath_t, *args: Any, **kwargs: Any) -> None: ...

class Groupfile(BaseArtifactFile):
    prefix: str
    suffix: str
    tags: tuple[str]

    def __init__(self, filepath: filepath_t, *args: Any, **kwargs: Any) -> None: ...
    @classmethod
    def from_lines(cls: Type["Groupfile"], filepath: filepath_t, lines: List[str]) -> "Groupfile": ...

class LambdaScheduleFile(BaseArtifactFile):
    prefix: str
    suffix: str
    tags: tuple[str]

    def __init__(self, filepath: filepath_t, *args: Any, **kwargs: Any) -> None: ...

class Remlog(BaseArtifactFile):
    prefix: str
    suffix: str
    tags: tuple[str]

    def __init__(self, filepath: filepath_t, *args, **kwargs) -> None: ...

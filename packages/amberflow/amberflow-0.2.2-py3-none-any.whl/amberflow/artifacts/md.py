from amberflow.artifacts import fileartifact
from amberflow.artifacts import BaseArtifactFile
from amberflow.primitives import filepath_t

__all__ = (
    "MdoutMD",
    "BoreschRestraints",
    "CpptrajData",
    "Groupfile",
    "LambdaScheduleFile",
    "Remlog",
)


@fileartifact
class MdoutMD(BaseArtifactFile):
    prefix: str = ""
    suffix: str = ".mdout"
    tags: tuple[str] = tuple()

    def __init__(self, filepath: filepath_t, *args, **kwargs) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, **kwargs)


@fileartifact
class BoreschRestraints(BaseArtifactFile):
    prefix: str = "rest"
    suffix: str = ".in"
    tags: tuple = ("alchemical",)

    def __init__(
            self,
            filepath: filepath_t,
            *args,
            **kwargs,
    ) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, **kwargs)


@fileartifact
class CpptrajData(BaseArtifactFile):
    prefix: str = ""
    suffix: str = ".dat"
    tags: tuple[str] = ("cpptraj",)

    def __init__(self, filepath: filepath_t, *args, **kwargs) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, **kwargs)


@fileartifact
class Groupfile(BaseArtifactFile):
    prefix: str = ""
    suffix: str = ".groupfile"
    tags: tuple[str] = ("",)

    def __init__(self, filepath: filepath_t, *args, **kwargs) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, **kwargs)

    @classmethod
    def from_lines(cls, filepath: filepath_t, lines: list[str]) -> "Groupfile":
        """Create a Groupfile from a list of lines."""
        with open(filepath, "w") as f:
            f.write("\n".join(lines))
            f.write("\n")
        return cls(filepath)


@fileartifact
class LambdaScheduleFile(BaseArtifactFile):
    prefix: str = "lambda"
    suffix: str = ".sch"
    tags: tuple[str] = ("",)

    def __init__(self, filepath: filepath_t, *args, **kwargs) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, **kwargs)


@fileartifact
class Remlog(BaseArtifactFile):
    prefix: str = "remd"
    suffix: str = ".log"
    tags: tuple[str] = ("",)

    def __init__(self, filepath: filepath_t, *args, **kwargs) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, **kwargs)

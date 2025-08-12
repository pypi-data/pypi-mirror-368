import logging
import os
import pickle
import re
import subprocess as sp
from copy import deepcopy
from pathlib import Path

import networkx as nx
from attr import Converter, Factory
from attrs import define, field

from amberflow.artifacts import (
    TargetProteinPDB,
    ArtifactRegistry,
    BinderLigandPDB,
    BinderLigandSmiles,
    BaseComplexStructureFile,
    BatchArtifacts,
    BaseArtifact,
    ArtifactContainer,
)
from amberflow.primitives import (
    InvalidPipeline,
    UnknownFileType,
    DirHandle,
    conv_build_resnames_set,
    set_logger,
    UnknownArtifactError,
    dirpath_t, filepath_t, BaseCommand, DefaultCommand, Executor, RemoteExecutor,
)
from amberflow.schedulers import BaseScheduler
from amberflow.worknodes import BaseWorkNode, WorkNodeDummy, WorkNodeStatus

__all__ = ["Pipeline"]


@define
class Pipeline:
    """
    The main orchestrator for an amberflow simulation workflow.

    This class discovers input data, builds a computational graph of work nodes,
    and uses a scheduler to execute the defined pipeline. It handles checkpointing
    to allow for resuming interrupted workflows.

    Attributes
    ----------
    name : str
        The name of the pipeline.
    cwd : dirpath_t
        The current working directory where systems are located and outputs will be generated.
    target : str
        The name assigned to the target molecule type, typically 'protein' or 'na'.
    binder : str
        The name assigned to the binder molecule type, typically 'ligand'.
    scheduler : BaseScheduler
        The scheduler instance responsible for executing the work nodes.
    command : BaseCommand
        The command execution object, which can be local or remote.
    new_run : bool
        Flag indicating if this is a new run (True) or a resumed run (False).
    force_restart : bool
        If True, ignores checkpoint validation errors and starts fresh.
    checkpoint_filename : str
        The name of the checkpoint file.
    checkpoint_path : Path
        The full path to the checkpoint file.
    logger : logging.Logger
        The logger for the pipeline.
    logging_level : int
        The logging level.
    systems : dict[str, dirpath_t]
        A dictionary mapping system names to their respective directory paths.
    root : WorkNodeDummy
        The root node of the workflow graph.
    free_md : bool
        If True, allows running simulations without a complex structure.
    user_accepted_resnames : set
        A set of user-provided residue names to be accepted.
    flow : nx.DiGraph
        The NetworkX directed graph representing the workflow.
    flow_ids : list[str]
        A list of all work node IDs in the flow.
    artifacts : dict[str, BatchArtifacts]
        A dictionary storing all artifacts generated during the pipeline execution.
    rootid : str
        The identifier for the root node.
    """
    name: str = field(converter=str)
    cwd: dirpath_t = field(kw_only=True, converter=lambda value: Path(value))
    target: str = field(kw_only=True, converter=str, default="protein")
    binder: str = field(kw_only=True, converter=str, default="ligand")
    scheduler: BaseScheduler = field(kw_only=True)
    command: BaseCommand = field(kw_only=True, default=Factory(DefaultCommand))
    new_run: bool = field(default=True)
    force_start: bool = field(default=False)
    force_restart: bool = field(default=False)
    checkpoint_filename: str = field(kw_only=True, converter=str, default="checkpoint.pkl")
    checkpoint_path: Path = field(init=False, default=Factory(
        lambda self: Path(self.cwd, self.checkpoint_filename),
        takes_self=True)
                                  )
    logger: logging.Logger = field(init=False, default=None)
    logging_level: int = field(kw_only=True, default=logging.INFO)
    systems: dict[str, dirpath_t] = field(init=False, default=Factory(dict))
    root: WorkNodeDummy = field(init=False)
    free_md: bool = field(init=True, default=True)
    user_accepted_resnames: set = field(kw_only=True, converter=Converter(conv_build_resnames_set), default=None)
    flow: nx.DiGraph = field(init=False, default=Factory(nx.DiGraph))
    flow_ids: list[str] = field(init=False, default=Factory(list))
    artifacts: dict[str, BatchArtifacts] = field(init=False, default=Factory(dict))
    rootid = "Root"
    RUNNER_SCRIPT_NAME: str = "run_pipeline.py"

    # noinspection PyUnresolvedReferences
    @force_restart.validator
    def _check_force_start(self, _, value):
        if value is True and self.force_start is True:
            raise ValueError("Cannot set `force_restart=True` and `force_start=True` simultaneously.")

    def __attrs_post_init__(self):
        """
        Initializes the pipeline after attribute setup.

        This method handles the core setup logic, either by starting a new run
        or by resuming from a checkpoint.
        """
        # If user sets `force_start` to True, we will always start a new run.
        self.new_run = not self.checkpoint_path.is_file() or self.force_start
        self.logger = set_logger(Path(self.cwd, f"{self.name}.log"), logging_level=self.logging_level,
                                 filemode="w" if self.new_run else "a")
        # Get the root dir system and the starting artifacts to pipe them through the root node.
        starting_artifacts, self.systems = self._walk_main_dir()
        root_artifacts = dict()
        self.root = WorkNodeDummy(wnid=self.rootid, root_dir=self.cwd)
        for sysname, syspath in self.systems.items():
            self.logger.debug(f"Loading system {sysname}")
            self.root.run(starting_artifacts[sysname], sysname=sysname, cwd=syspath)
            root_artifacts[sysname] = self.root.output_artifacts
        # load them into the artifact tree's root.
        self.artifacts[self.rootid] = BatchArtifacts(self.rootid, root_artifacts)
        self.flow_ids.append(self.rootid)

        if not self.command.initialized:
            # If the command is not initialized, we need to initialize it with the root_dir
            self.command = self.command.replace(local_base_dir=self.cwd)

        if self.new_run:
            self.flow = nx.DiGraph(name="workflow")
            self.flow.add_node(self.root)
        else:
            # TODO: add hashing to the checkpoint file.
            self._read_checkpoint(self.checkpoint_path, self.force_restart)

    def _read_checkpoint(self, checkpoint_path: filepath_t, force_restart: bool) -> None:
        """
        Reads the workflow from a checkpoint file.

        It also validates the state of a resumed pipeline from a checkpoint.
        It checks for missing files from completed nodes and resets failed nodes.

        Parameters
        ----------
        force_restart : bool
            If True, ignores validation errors.
        checkpoint_path : filepath_t
            The path to the checkpoint file.

        Returns
        -------

        Raises
        ------
        InvalidPipeline
            If the checkpoint is invalid and `force_restart` is False.
        """
        old_systems: dict[str, DirHandle] | None = None
        try:
            with open(checkpoint_path, "rb") as f:
                self.flow, self.artifacts, old_systems = pickle.load(f)
            self.new_run = False
        except FileNotFoundError:
            self.new_run = True
            return

        # Now, check if the systems in the checkpoint match the current systems.
        assert old_systems is not None, f"Expected old_systems to be not None when validating checkpoint."
        set_old_systems = set(old_systems.keys())

        valid = True
        err_msg = ""
        is_root = True
        for node in nx.topological_sort(self.flow):
            if is_root:
                if node.id != self.rootid:
                    err_msg += f"Pipeline's root node id is {self.rootid}, but found {node.id}.\n"
                    valid = force_restart
                    break
                is_root = False
            if node.status in (WorkNodeStatus.FAILED, WorkNodeStatus.CANCELLED):
                node.status = WorkNodeStatus.PENDING
                continue
            elif node.status == WorkNodeStatus.COMPLETED:
                if wd:= getattr(node, "work_dir", False):
                    if not wd.is_dir():
                        valid = force_restart
                        err_msg += f"WorkNode {node.id} has no work directory ({node.work_dir}).\n"
                        break
                    else:
                        valid = False
                        err_msg += f"WorkNode {node.id} has no work directory but is marked as completed?. Corrupted checkpoint file?"
                        break
                for _, art_list in node.output_artifacts.items():
                    for art in art_list:
                        if hasattr(node, "filepath"):
                            # artifact is file-based
                            if not art.filepath.is_file():
                                valid = False
                                err_msg += f"WorkNode {node.id} has no output artifact {art}.\n"
                                break

        for sysname in self.artifacts[self.rootid].keys():
            if sysname not in set_old_systems:
                self.logger.warning(f"Missing system in the current root dir: {sysname}")

        if not valid:
            err_msg += "Invalid Pipeline. Cannot continue from the checkpoint. Either set `force_restart=True`, or fix the project files."
            self.logger.error(err_msg)
            raise InvalidPipeline(err_msg)

        return

    def _walk_main_dir(self) -> tuple[BatchArtifacts, dict[str, DirHandle]]:
        """
        Walk through the main directory and collect initial artifacts for each system.

        This method iterates over the subdirectories in `cwd`, treating each as a
        system and collecting the initial set of artifacts.

        Returns
        -------
        BatchArtifacts
            A batch of artifacts found, organized by system name.
        """
        artifacts: dict[str, ArtifactContainer] = {}
        systems: dict[str, DirHandle] = {}
        for path_object in Path(self.cwd).iterdir():
            if path_object.is_dir():
                if path_object.name.startswith("allow_"):
                    continue
                sys_artifacts: ArtifactContainer = self._add_system_dir(path_object)
                artifacts[sys_artifacts.id] = sys_artifacts
                systems[sys_artifacts.id] = DirHandle(path_object)

        return BatchArtifacts("Root", artifacts), systems

    def _add_system_dir(self, system_path: Path) -> ArtifactContainer:
        """
        Identifies and collects artifacts from a single system directory.

        This method checks for specific file patterns (e.g., 'target_*', 'binder_*')
        to create and register the initial artifacts for a given system.

        Parameters
        ----------
        system_path : Path
            The path to the system directory.

        Returns
        -------
        ArtifactContainer
            A container with the artifacts found in the system directory.

        Raises
        ------
        InvalidPipeline
            If the directory contains unrecognized files or an invalid combination of inputs.
        """
        has_complex: bool = False
        has_target: bool = False
        has_binder: bool = False
        artifacts: list[BaseArtifact] = []
        # The folder name is the system name.
        sysname = str(system_path.name)

        for file in Path(system_path).iterdir():
            if file.is_file():
                try:
                    # TODO: hacky. Can do better.
                    if file.name.startswith("target_"):
                        file_artifact = ArtifactRegistry.create_instance_by_filename(file, tags=(self.target,))
                    elif file.name.startswith("binder_"):
                        file_artifact = ArtifactRegistry.create_instance_by_filename(file, tags=(self.binder,))
                    elif file.name.startswith("complex_"):
                        file_artifact = ArtifactRegistry.create_instance_by_filename(
                            file, tags=(self.target, self.binder)
                        )
                    else:
                        file_artifact = ArtifactRegistry.create_instance_by_filename(file)

                    artifacts.append(file_artifact)
                    artifact_type = type(file_artifact)

                    if issubclass(artifact_type, BaseComplexStructureFile):
                        if has_complex:
                            raise InvalidPipeline(f"System dir {system_path} has multiple complexes.")
                        has_complex = True
                    if issubclass(artifact_type, TargetProteinPDB):
                        if has_target:
                            raise InvalidPipeline(f"System dir {system_path} has multiple targets.")
                        has_target = True
                    if issubclass(artifact_type, BinderLigandPDB) or issubclass(artifact_type, BinderLigandSmiles):
                        if has_binder:
                            raise InvalidPipeline(f"System dir {system_path} has multiple binders.")
                        has_binder = True
                except UnknownFileType:
                    raise InvalidPipeline(f"System dir {system_path} has an unrecognized file ({file}).")
                except UnknownArtifactError as e:
                    self.logger.debug(f"System dir {system_path} has an unrecognized file: {file} which caused {e}.")

        if self.free_md or has_complex or (has_target and has_binder):
            self.systems[sysname] = DirHandle(system_path)
            return ArtifactContainer(sysname, artifacts)
        else:
            raise InvalidPipeline(
                f"Invalid dir: {system_path}. "
                "Structures of target and binder (together or separate) are a prerequisite."
            )

    def run(self) -> None:
        """
        Launches the pipeline execution by pickling itself and executing via a runner script.

        This method prepares the pipeline for execution, pickles it, and then uses the
        configured command (local or remote) to run a script that unpickles and
        executes the pipeline.
        """
        other_pipeline = self.setup_new_pipeline(self.command.executor)
        # Pickle the modified pipeline
        with open(Path(self.cwd, "pipeline.pkl"), "wb") as f:
            # noinspection PyTypeChecker
            pickle.dump(other_pipeline, f)

        # Create a runner script
        runner_script_content = f"""import pickle
from pathlib import Path

try:
    import amberflow
except ModuleNotFoundError:
    raise ModuleNotFoundError("Install amberflow: pip install amberflow")
except Exception as e:
    raise ModuleNotFoundError("Unknown error when trying to import amberflow") from e

if __name__ == "__main__":
    with open("pipeline.pkl", "rb") as f:
        pipeline = pickle.load(f)
    pipeline.launch()
"""
        runner_script_path = Path(self.cwd, self.RUNNER_SCRIPT_NAME)
        with open(runner_script_path, "w") as f:
            f.write(runner_script_content)

        # Execute the runner script using the pipeline's command
        self.logger.info(
            f"Executing pipeline using {self.command.__class__.__name__} with {self.command.executor.__class__.__name__}")
        self.command.run(
            ["python", self.RUNNER_SCRIPT_NAME],
            cwd=self.cwd,
            logger=self.logger,
            force=self.force_restart,
            download=True
        )
        self.logger.info("Done Pipeline.run().")

    def launch(self) -> None:
        """
        Executes the pipeline directly in the current process
        """
        self.scheduler.launch(
            self.flow,
            self.root,
            systems=self.systems,
            cwd=Path(self.cwd),
            pipeline_artifacts=self.artifacts,
            logger=self.logger,
            checkpoint_path=self.checkpoint_path,
        )

    def setup_new_pipeline(self, executor: Executor) -> "Pipeline":
        """Prepares a deep copy of the pipeline for execution.

        This method creates a standalone copy of the pipeline instance that is
        safe to be pickled and run in a separate process. It ensures the new
        pipeline will execute locally by setting its command to `DefaultCommand`.

        For remote execution, it also adjusts the `cwd` and artifact file paths
        within the new pipeline to point to their expected locations on the
        remote server.

        Parameters
        ----------
        executor : Executor
            The executor from the original pipeline, used to determine if
            the execution is remote and to get the remote base directory.

        Returns
        -------
        Pipeline
            A new, deep-copied pipeline instance configured for execution.
        """
        other_pipeline = deepcopy(self)
        other_pipeline.command = DefaultCommand()

        # Now, all paths need fixing
        if isinstance(executor, RemoteExecutor):
            # Set the current working directory for the local pipeline to the remote base directory, bypassing
            other_pipeline.cwd = executor.remote_base_dir

            #
            other_pipeline.checkpoint_path = Path(other_pipeline.cwd, self.checkpoint_path.relative_to(self.cwd))

            # If the pipeline is being run remotely, we need to ensure that the all the absolute paths are within the
            # remote base directory.
            other_pipeline.systems = {
                sysname: Path(
                    other_pipeline.cwd,
                    Path(sysdir).relative_to(self.cwd)
                )
                for sysname, sysdir in self.systems.items()
            }
            # If we're starting from a checkpoint, we need to ensure that the artifacts are also set to the remote base directory.
            for batch_artifacts in other_pipeline.artifacts.values():
                for artifact_container in batch_artifacts.values():
                    for artifacts in artifact_container.values():
                        for art in artifacts:
                            if hasattr(art, "filepath"):
                                art.change_base_dir(self.cwd, other_pipeline.cwd)

        return other_pipeline

    def append_node(self, left_worknode: BaseWorkNode, right_worknode: BaseWorkNode) -> BaseWorkNode:
        """
        Appends a new work node to an existing node in the workflow, and sets up the new node to work within the
        pipeline.

        Parameters
        ----------
        left_worknode : BaseWorkNode
            The existing node in the graph to connect from.
        right_worknode : BaseWorkNode
            The new node to add and connect to the graph.

        Returns
        -------
        BaseWorkNode
            The newly added work node.

        Raises
        ------
        RuntimeError
            If the `right_worknode` ID already exists or if `left_worknode` is not in the flow.
        """
        if left_worknode.id == right_worknode.id:
            err_msg = "Cannot append a WorkNode to itself."
            self.logger.error(err_msg)
            raise RuntimeError(err_msg)
        if right_worknode.id in self.flow_ids:
            if not self.new_run:
                self.logger.debug(f"Right Worknode, {right_worknode.id}, already present in the flow. Doing nothing.")
                return right_worknode
            err_msg = "Right WorkNode already present. Pipeline can't hold WorkNodes with duplicated ids."
            self.logger.error(err_msg)
            raise RuntimeError(err_msg)
        if left_worknode not in self.flow.nodes:
            err_msg = f"{left_worknode=} not found in the Pipeline's flow. Cannot have disjoint graphs."
            self.logger.error(err_msg)
            raise RuntimeError(err_msg)

        right_worknode.set_systems(tuple(self.systems.keys()))
        right_worknode.root_dir = self.cwd
        right_worknode.logging_level = self.logging_level
        self.flow.add_edge(left_worknode, right_worknode)
        self.flow_ids.append(right_worknode.id)

        return right_worknode

    def add_edge(self, left_worknode: BaseWorkNode, right_worknode: BaseWorkNode) -> BaseWorkNode:
        """
        Adds a directed edge between two existing nodes in the workflow.

        Parameters
        ----------
        left_worknode : BaseWorkNode
            The source node for the edge.
        right_worknode : BaseWorkNode
            The destination node for the edge.

        Returns
        -------
        BaseWorkNode
            The destination work node.

        Raises
        ------
        RuntimeError
            If either of the nodes is not already in the flow.
        """
        if left_worknode.id in self.flow_ids and right_worknode.id in self.flow_ids:
            self.flow.add_edge(left_worknode, right_worknode)
        else:
            err_msg = (
                f"Both {left_worknode=} and {right_worknode=} have to be present in the Pipeline's flow to add an edge."
                " Use `append_node()` instead to add a new node to the flow."
            )
            self.logger.error(err_msg)
            raise RuntimeError(err_msg)

        return right_worknode

    @staticmethod
    def _write_checkpoint(dag: nx.DiGraph, checkpoint_path: filepath_t, logger: logging.Logger) -> None:
        with open(checkpoint_path, "wb") as f:
            # noinspection PyTypeChecker
            pickle.dump(dag, f)
        logger.info(f"Checkpoint written to {checkpoint_path}.")

    @staticmethod
    def clean(checkpoint_path) -> None:
        """Removes the checkpoint file."""
        checkpoint_path.unlink()

    # noinspection PyUnresolvedReferences
    @target.validator
    def _prot_or_rdname(self, attribute, value: str):
        """Validates that the 'target' attribute is either 'protein' or 'na'."""
        if value != "protein" and value != "na":
            raise RuntimeError(f"{attribute} must be 'protein' or 'na'")

    @staticmethod
    def get_amber_version(logger: logging.Logger) -> None:
        """
        Get the pmemd version.

        This function checks for the AMBERHOME environment variable, which is
        standard in AmberTools installations. It then attempts to read the
        AmberTools.version file within that directory to get the version number.

        Returns:
            A string containing the AmberTools version, or "unknown" if it
            cannot be determined.

        Raises:
            EnvironmentError: If the AMBERHOME environment variable is not set.
        """
        amber_home = os.environ.get("AMBERHOME")
        if not amber_home:
            raise EnvironmentError(
                "The AMBERHOME environment variable is not set. "
                "Please ensure AmberTools is installed and configured correctly."
            )
        for engine in ("pmemd ", "pmemd.cuda", "pmemd.cuda.MPI"):
            p = sp.run(f"{engine} --version", stdout=sp.PIPE, stderr=sp.PIPE, text=True, shell=True)
            try:
                match = re.search(r"\d+\.\d+", p.stdout.strip())
                version = float(match.group(0))
                logger.info(f"Found {engine=} with {version=}")
            except ValueError:
                logger.warning(f"Could not find a version number for '{engine}'")

    def __getstate__(self) -> dict:
        """
        Pipeline's custom pickling method.

        Excludes the unpicklable 'logger' attribute. The rest of the attributes are handled automatically by attrs.
        """
        # Remove the logger and `__weakref__`  from the state to avoid pickling issues
        # noinspection PyUnresolvedReferences
        state = {
            slot: getattr(self, slot)
            for slot in self.__class__.__slots__
            if slot not in ("logger", "__weakref__")
        }
        return state

    def __setstate__(self, state: dict):
        """
        Pipeline's custom pickling method.

        Re-initializes the logger after all other attributes have been restored.
        """
        # Manually set the attributes from the state dictionary
        for key, value in state.items():
            super().__setattr__(key, value)

        # Re-create the logger instance, ensuring it appends to the existing log file
        self.logger = set_logger(
            Path(self.cwd, f"{self.name}.log"),
            logging_level=self.logging_level,
            filemode="a"  # Always append ('a') to the log file from a pickled instance
        )

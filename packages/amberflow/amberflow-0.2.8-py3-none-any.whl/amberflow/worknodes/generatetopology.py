import logging
from pathlib import Path
from typing import Any, Optional, Sequence, Union

from amberflow.artifacts import (
    ArtifactContainer,
    BaseBinderStructureFile,
    BaseComplexTopologyFile,
    BaseBinderTopologyFile,
    ArtifactRegistry,
)
from amberflow.artifacts.structure import BaseComplexStructureFile
from amberflow.artifacts.topology import LigandLib, LigandFrcmod
from amberflow.primitives import (
    filepath_t,
    dirpath_t,
    DEFAULT_RESOURCES_PATH,
    BaseCommand,
)
from amberflow.worknodes import noderesource, worknodehelper, BaseSingleWorkNode, TleapMixin, check_leap_log

__all__ = ("GenerateTopologyComplex", "GenerateTopologyBinder")


# noinspection DuplicatedCode
@noderesource(DEFAULT_RESOURCES_PATH / "tleap")
@worknodehelper(
    file_exists=True,
    input_artifact_types=(BaseComplexStructureFile, LigandLib, LigandFrcmod),
    output_artifact_types=(BaseComplexStructureFile, BaseComplexTopologyFile),
)
class GenerateTopologyComplex(BaseSingleWorkNode, TleapMixin):
    # noinspection PyUnusedLocal
    def __init__(
        self,
        wnid: str,
        *args,
        boxshape: str = "truncated_octahedron",
        solvent: str = "opc",
        force_field: str = "19SB",
        atom_type: str = "gaff2",
        **kwargs,
    ) -> None:
        super().__init__(
            wnid=wnid,
            *args,
            **kwargs,
        )
        super().check_supported(solvent, "water")
        self.solvent = solvent

        super().check_supported(force_field, "force_field")
        self.force_field = force_field

        super().check_supported(atom_type, "atom_type")
        self.atom_type = atom_type

        super().check_supported(boxshape, "boxshape")
        self.boxshape = boxshape

    def _run(
        self,
        *,
        cwd: dirpath_t,
        sysname: str,
        binpath: Optional[filepath_t] = None,
        **kwargs,
    ) -> Any:
        if self._try_and_skip(sysname):
            return self.output_artifacts

        in_pdb = Path(self.input_artifacts["ComplexProteinLigandPDB"])
        tleap_script = self.write_tleap(
            self.leaprc,
            self.load_nonstandard,
            self.load_pdb,
            self.neutralize,
            self.save_amberparm,
            cwd=self.work_dir,
            in_pdb=in_pdb,
            lig_lib=Path(self.input_artifacts["LigandLib"]),
            lig_frcmod=Path(self.input_artifacts["LigandFrcmod"]),
        )
        self.run_tleap(self.work_dir, tleap_script, sysname)
        self.output_artifacts = self.fill_output_artifacts(self.work_dir, sysname)

        return self.output_artifacts

    def run_tleap(self, output_dir: dirpath_t, tleap_script: filepath_t, sysname: str) -> None:
        logleap = "logleap"
        self.command.run(
            ["tleap", "-f", str(tleap_script), ">", logleap],
            cwd=output_dir,
            logger=self.node_logger,
            expected=(output_dir / f"complex_{sysname}.parm7", output_dir / f"complex_{sysname}.rst7"),
        )
        check_leap_log(output_dir / logleap, node_logger=self.node_logger)

    def fill_output_artifacts(self, output_dir: dirpath_t, sysname: str) -> ArtifactContainer:
        return ArtifactContainer(
            sysname,
            (
                ArtifactRegistry.create_instance_by_filename(
                    output_dir / f"complex_{sysname}.parm7",
                    tags=self.tags[self.artifact_map["BaseComplexStructureFile"]],
                ),
                ArtifactRegistry.create_instance_by_filename(
                    output_dir / f"complex_{sysname}.rst7",
                    tags=self.tags[self.artifact_map["BaseComplexStructureFile"]],
                ),
            ),
        )

    def write_tleap(
        self,
        template_leaprc: str,
        template_load_nonstandard: str,
        template_load_pdb: str,
        template_neutralize: str,
        template_save_amberparm: str,
        *,
        cwd: dirpath_t,
        in_pdb: Path,
        lig_lib: Path,
        lig_frcmod: Path,
    ) -> Path:
        """
        Generates a tleap input script based on a template and writes it to a file sitting right next to the input PDB.
        """

        leaprc = super().load_file(
            template_leaprc, {"SOLVENT_MODEL": self.solvent, "SBFF": self.force_field, "ATOM_TYPE": self.atom_type}
        )
        load_nonstandard = super().load_file(template_load_nonstandard, {"LIB": lig_lib, "FRCMOD": lig_frcmod})
        load_pdb = super().load_file(template_load_pdb, {"PDB": in_pdb})
        neutralize = super().load_file(template_neutralize)
        if self.boxshape == "truncated_octahedron":
            setbox = super().load_file(
                "solvateoct",
                {
                    "SOLVENT_BOX_TYPE": super().SOLVENT_TO_BOX[self.solvent],
                    "BOX_BUFFER_SIZE": "0",
                    "CLOSENESS": "999.9",
                },
            )
        else:
            setbox = super().load_file(
                "solvatebox",
                {
                    "SOLVENT_BOX_TYPE": super().SOLVENT_TO_BOX[self.solvent],
                    "BOX_BUFFER_SIZE": "0",
                    "CLOSENESS": "999.9",
                },
            )
        save_amberparm = super().load_file(template_save_amberparm, {"TOPOLOGY": in_pdb.stem, "RESTART": in_pdb.stem})

        # Join all sections
        tleap_script = "".join([leaprc, load_nonstandard, load_pdb, neutralize, setbox, save_amberparm, "quit\n"])

        # Write away
        output_path = cwd / f"tleap_{self.__class__.__name__}_{in_pdb.stem}.in"
        with open(output_path, "w") as outfile:
            outfile.write(tleap_script)

        return output_path

    def _try_and_skip(self, sysname: str) -> bool:
        if self.skippable:
            try:
                self.output_artifacts = self.fill_output_artifacts(self.work_dir, sysname)
                self.node_logger.info(f"Skipped {self.id} WorkNode.")
                return True
            except FileNotFoundError as e:
                self.node_logger.info(f"Can't skip {self.id}. Could not find file: {e}")
        return False


# noinspection DuplicatedCode
@noderesource(DEFAULT_RESOURCES_PATH / "tleap")
@worknodehelper(
    file_exists=True,
    input_artifact_types=(BaseBinderStructureFile, LigandLib, LigandFrcmod),
    output_artifact_types=(BaseBinderStructureFile, BaseBinderTopologyFile),
)
class GenerateTopologyBinder(BaseSingleWorkNode, TleapMixin):
    def __init__(
        self,
        wnid: str,
        *args,
        boxshape: str = "truncated_octahedron",
        solvent: str = "opc",
        force_field: str = "19SB",
        atom_type: str = "gaff2",
        debug: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(
            wnid=wnid,
            *args,
            **kwargs,
        )
        super().check_supported(solvent, "water")
        self.solvent = solvent

        super().check_supported(force_field, "force_field")
        self.force_field = force_field

        super().check_supported(atom_type, "atom_type")
        self.atom_type = atom_type

        super().check_supported(boxshape, "boxshape")
        self.boxshape = boxshape

        # self.solvent_selection = f"(resname {watname} or resname HOH or name Na+ Cl-)"
        self.debug = debug
        self.tleap = None

        self.out_dirs: list[Path] = []
        self.binders = []
        self.complexes = []

    def _run(
        self,
        *,
        cwd: dirpath_t,
        sysname: str,
        binpath: Optional[filepath_t] = None,
        **kwargs,
    ) -> Any:
        if self._try_and_skip(sysname):
            return self.output_artifacts

        in_pdb = Path(self.input_artifacts["BinderLigandPDB"])
        tleap_script = self.write_tleap(
            self.leaprc,
            self.load_nonstandard,
            self.load_pdb,
            self.neutralize,
            self.save_amberparm,
            cwd=self.work_dir,
            in_pdb=in_pdb,
            lig_lib=Path(self.input_artifacts["LigandLib"]),
            lig_frcmod=Path(self.input_artifacts["LigandFrcmod"]),
        )
        self.run_tleap(self.work_dir, tleap_script, sysname)
        self.output_artifacts = self.fill_output_artifacts(self.work_dir, sysname)

        return self.output_artifacts

    def run_tleap(self, output_dir: dirpath_t, tleap_script: filepath_t, sysname: str) -> None:
        logleap = "logleap"
        self.command.run(
            ["tleap", "-f", str(tleap_script), ">", logleap],
            cwd=output_dir,
            logger=self.node_logger,
            expected=(output_dir / f"binder_{sysname}.parm7", output_dir / f"binder_{sysname}.rst7"),
        )
        check_leap_log(output_dir / logleap, node_logger=self.node_logger)

    def fill_output_artifacts(self, output_dir: dirpath_t, sysname: str) -> ArtifactContainer:
        return ArtifactContainer(
            sysname,
            (
                ArtifactRegistry.create_instance_by_filename(
                    output_dir / f"binder_{sysname}.parm7", tags=self.tags[self.artifact_map["BaseBinderStructureFile"]]
                ),
                ArtifactRegistry.create_instance_by_filename(
                    output_dir / f"binder_{sysname}.rst7", tags=self.tags[self.artifact_map["BaseBinderStructureFile"]]
                ),
            ),
        )

    def write_tleap(
        self,
        template_leaprc: str,
        template_load_nonstandard: str,
        template_load_pdb: str,
        template_neutralize: str,
        template_save_amberparm: str,
        *,
        cwd: dirpath_t,
        in_pdb: Path,
        lig_lib: Path,
        lig_frcmod: Path,
    ) -> Path:
        """
        Generates a tleap input script based on a template and writes it to a file sitting right next to the input PDB.
        """

        leaprc = super().load_file(
            template_leaprc, {"SOLVENT_MODEL": self.solvent, "SBFF": self.force_field, "ATOM_TYPE": self.atom_type}
        )
        load_nonstandard = super().load_file(template_load_nonstandard, {"LIB": lig_lib, "FRCMOD": lig_frcmod})
        load_pdb = super().load_file(template_load_pdb, {"PDB": in_pdb})
        neutralize = super().load_file(template_neutralize)
        if self.boxshape == "truncated_octahedron":
            setbox = super().load_file(
                "solvateoct",
                {
                    "SOLVENT_BOX_TYPE": super().SOLVENT_TO_BOX[self.solvent],
                    "BOX_BUFFER_SIZE": "0",
                    "CLOSENESS": "999.9",
                },
            )
        else:
            setbox = super().load_file(
                "solvatebox",
                {
                    "SOLVENT_BOX_TYPE": super().SOLVENT_TO_BOX[self.solvent],
                    "BOX_BUFFER_SIZE": "0",
                    "CLOSENESS": "999.9",
                },
            )
        save_amberparm = super().load_file(template_save_amberparm, {"TOPOLOGY": in_pdb.stem, "RESTART": in_pdb.stem})

        # Join all sections
        tleap_script = "".join([leaprc, load_nonstandard, load_pdb, neutralize, setbox, save_amberparm, "quit\n"])

        # Write away
        output_path = cwd / f"tleap_{self.__class__.__name__}_{in_pdb.stem}.in"
        with open(output_path, "w") as outfile:
            outfile.write(tleap_script)

        return output_path

    def _try_and_skip(self, sysname: str) -> bool:
        if self.skippable:
            try:
                self.output_artifacts = self.fill_output_artifacts(self.work_dir, sysname)
                self.node_logger.info(f"Skipped {self.id} WorkNode.")
                return True
            except FileNotFoundError as e:
                self.node_logger.info(f"Can't skip {self.id}. Could not find file: {e}")
        return False

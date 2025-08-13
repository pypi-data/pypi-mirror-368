"""
This module contains the built-in artifact kinds representing Selene artifacts,
and steps between them.

These include the executable, representing the final output of a typical build,
and the "selene object file", which is an object file ready to be linked with
the selene core library to create the final executable.

Call register_selene_builtins(planner) to register these types to a build planner.
It is called automatically on the default planner, so manual invocation is only
necessary if you are using a fresh custom planner.
"""

import platform
import sys
from pathlib import Path
from typing import Any

from ..planner import BuildPlanner
from ..types import ArtifactKind, Step, BuildCtx, Artifact
from ..utils import get_undefined_symbols_from_object, invoke_zig


class SeleneExecutableKind(ArtifactKind[Path]):
    @classmethod
    def matches(cls, resource: Any) -> bool:
        expected_suffix = ".exe" if platform.system() == "Windows" else ".x"
        return isinstance(resource, Path) and resource.suffix == expected_suffix


class SeleneObjectFileKind(ArtifactKind[Path]):
    @classmethod
    def matches(cls, resource: Any) -> bool:
        if not isinstance(resource, Path):
            return False
        if not resource.is_file():
            return False
        if resource.suffix not in [".o", ".obj"]:
            return False
        undefined_symbols = get_undefined_symbols_from_object(resource)
        return "selene_load_config" in undefined_symbols


class SeleneObjectToSeleneExecutable(Step):
    """
    Link selene object with selene core library to create the final executable.
    """

    input_kind = SeleneObjectFileKind
    output_kind = SeleneExecutableKind

    @classmethod
    def apply(cls, build_ctx: BuildCtx, input_artifact: Artifact) -> Artifact:
        try:
            from selene_sim import dist_dir as selene_dist
        except ImportError:
            raise ImportError(
                "Selene simulation library not found. Please install selene_sim."
            )

        out_path = build_ctx.artifact_dir / "program.selene.x"
        selene_lib_dir = selene_dist / "lib"
        selene_lib = selene_lib_dir
        match platform.system():
            case "Darwin":
                selene_lib /= "libselene.dylib"
            case "Linux":
                selene_lib /= "libselene.so"
            case "Windows":
                selene_lib /= "selene.lib"
            case _:
                raise RuntimeError(f"Unsupported OS {sys.platform}")
        link_flags = []
        library_search_dirs = [selene_lib_dir]
        for dep in build_ctx.deps:
            link_flags.extend(dep.link_flags)
            library_search_dirs.extend(dep.library_search_dirs)

        if build_ctx.verbose:
            print("Linking selene object file with selene core library")
        invoke_zig(
            "cc", "-o", out_path, input_artifact.resource, selene_lib, *link_flags
        )
        return cls._make_artifact(
            out_path,
            metadata={"library_search_dirs": library_search_dirs},
        )


def register_selene_builtins(planner: BuildPlanner) -> None:
    """
    Register the default kinds with the provided planner.
    """
    planner.add_kind(SeleneExecutableKind)
    planner.add_kind(SeleneObjectFileKind)
    planner.add_step(SeleneObjectToSeleneExecutable)

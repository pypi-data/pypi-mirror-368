from pathlib import Path
import platform
from typing import Any
from ..types import (
    ArtifactKind,
    BuildCtx,
    Artifact,
    Step,
)
from ..utils import (
    get_undefined_symbols_from_object,
    get_undefined_symbols_from_llvm_ir_file,
    get_undefined_symbols_from_llvm_ir_string,
    invoke_zig,
)
from ..planner import BuildPlanner

from .selene import SeleneObjectFileKind, SeleneExecutableKind

# Artifact Kinds:


class HeliosLLVMIRStringKind(ArtifactKind):
    @classmethod
    def matches(cls, resource: Any) -> bool:
        if not isinstance(resource, str):
            return False
        undefined_symbols = get_undefined_symbols_from_llvm_ir_string(resource)
        return "teardown" in undefined_symbols


class HeliosLLVMIRFileKind(ArtifactKind):
    @classmethod
    def matches(cls, resource: Any) -> bool:
        if not isinstance(resource, Path):
            return False
        if not resource.is_file():
            return False
        if resource.suffix != ".ll":
            return False
        undefined_symbols = get_undefined_symbols_from_llvm_ir_file(resource)
        return "teardown" in undefined_symbols


class HeliosLLVMBitcodeStringKind(ArtifactKind):
    @classmethod
    def matches(cls, resource: Any) -> bool:
        if hasattr(resource, "bitcode"):
            resource = resource.bitcode
        return isinstance(resource, bytes) and b"teardown" in resource


class HeliosLLVMBitcodeFileKind(ArtifactKind):
    @classmethod
    def matches(cls, resource: Any) -> bool:
        if not isinstance(resource, Path):
            return False
        if not resource.is_file():
            return False
        if resource.suffix != ".bc":
            return False
        return b"teardown" in resource.read_bytes()


class HeliosObjectFileKind(ArtifactKind):
    @classmethod
    def matches(cls, resource: Any) -> bool:
        if not isinstance(resource, Path):
            return False
        if resource.suffix not in [".o", ".obj"]:
            return False
        undefined_symbols = get_undefined_symbols_from_object(resource)
        return any(f in undefined_symbols for f in ["get_tc", "teardown"])


# Steps


class LLVMBitcodeStringToLLVMBitcodeFileStep(Step):
    """
    Convert a bitcode string to a file (by writing the bytes)
    """

    input_kind = HeliosLLVMBitcodeStringKind
    output_kind = HeliosLLVMBitcodeFileKind

    @classmethod
    def get_cost(cls, build_ctx: BuildCtx) -> float:
        return 100

    @classmethod
    def apply(cls, build_ctx: BuildCtx, input_artifact: Artifact) -> Artifact:
        out_path = build_ctx.artifact_dir / "program.helios.bc"
        if build_ctx.verbose:
            print(f"Writing LLVM bitcode file: {out_path}")
        bitcode = input_artifact.resource
        if hasattr(bitcode, "bitcode"):  # handle wrapper types
            bitcode = bitcode.bitcode
        out_path.write_bytes(bitcode)
        return cls._make_artifact(out_path)


class LLVMIRStringToLLVMIRFileStep(Step):
    """
    Convert a LLVM IR string to a file (by writing the text)
    """

    input_kind = HeliosLLVMIRStringKind
    output_kind = HeliosLLVMIRFileKind

    @classmethod
    def get_cost(cls, build_ctx: BuildCtx) -> float:
        return 100

    @classmethod
    def apply(cls, build_ctx: BuildCtx, input_artifact: Artifact) -> Artifact:
        out_path = build_ctx.artifact_dir / "program.helios.ll"
        if build_ctx.verbose:
            print(f"Writing LLVM IR file: {out_path}")
        out_path.write_text(input_artifact.resource)
        return cls._make_artifact(out_path)


class HeliosLLVMIRFileToHeliosObjectFileStep(Step):
    """
    Convert LLVM IR text (.ll) to a Helios object file (.o)
    """

    input_kind = HeliosLLVMIRFileKind
    output_kind = HeliosObjectFileKind

    @classmethod
    def apply(cls, build_ctx: BuildCtx, input_artifact: Artifact) -> Artifact:
        out_path = build_ctx.artifact_dir / "program.helios.o"
        if build_ctx.verbose:
            print(f"Compiling LLVM IR to Helios-QIS object: {out_path}")
        invoke_zig(
            "cc",
            "-c",
            input_artifact.resource,
            "-o",
            out_path,
            verbose=build_ctx.verbose,
        )
        return cls._make_artifact(out_path)


class HeliosLLVMBitcodeFileToHeliosObjectFileStep(Step):
    """
    Convert LLVM Bitcode (.bc) to a Helios object file (.o)
    """

    input_kind = HeliosLLVMBitcodeFileKind
    output_kind = HeliosObjectFileKind

    @classmethod
    def apply(cls, build_ctx: BuildCtx, input_artifact: Artifact) -> Artifact:
        out_path = build_ctx.artifact_dir / "program.helios.o"
        if build_ctx.verbose:
            print(f"Compiling LLVM Bitcode to Helios-QIS object: {out_path}")
        invoke_zig("cc", "-c", input_artifact.resource, "-o", out_path)
        return cls._make_artifact(out_path)


class HeliosObjectFileToSeleneObjectFileStep_Linux(Step):
    """
    Link helios object with interface + utility shared libs to rebind
    to the selene interface and fill in any missing libraries.
    """

    input_kind = HeliosObjectFileKind
    output_kind = SeleneObjectFileKind

    @classmethod
    def get_cost(cls, build_ctx: BuildCtx) -> float:
        """
        Rule out this step for non-linux platforms.
        """
        if platform.system() == "Linux":
            return 100
        else:
            return float("inf")

    @classmethod
    def apply(cls, build_ctx: BuildCtx, input_artifact: Artifact) -> Artifact:
        out_path = build_ctx.artifact_dir / "program.selene.o"
        lib_paths = [d.path for d in build_ctx.deps]
        if build_ctx.verbose:
            print("Linking helios object file with dependencies")
        invoke_zig(
            "cc",
            "-r",
            input_artifact.resource,
            *lib_paths,
            "-o",
            out_path,
            verbose=build_ctx.verbose,
        )
        return cls._make_artifact(out_path)


class HeliosObjectFileToSeleneExecutableStep_Windows(Step):
    """
    Link helios object with the interface shim, utilities, and selene core library to create the final executable.
    """

    input_kind = HeliosObjectFileKind
    output_kind = SeleneExecutableKind

    @classmethod
    def get_cost(cls, build_ctx: BuildCtx) -> float:
        """
        Rule out this step for non-windows platforms.
        """
        if platform.system() == "Windows":
            return 100
        else:
            return float("inf")

    @classmethod
    def apply(cls, build_ctx: BuildCtx, input_artifact: Artifact) -> Artifact:
        out_path = build_ctx.artifact_dir / "program.selene.exe"
        if build_ctx.verbose:
            print("Linking helios object file with dependencies")

        try:
            from selene_sim import dist_dir as selene_dist
        except ImportError:
            raise ImportError(
                "Selene simulation library not found. Please install selene_sim."
            )

        selene_lib_dir = selene_dist / "lib"
        selene_lib = selene_lib_dir / "selene.dll.lib"
        link_flags = ["-lc"]
        libraries = [selene_lib]
        library_search_dirs = [selene_lib_dir]
        for dep in build_ctx.deps:
            link_flags.extend(dep.link_flags)
            library_search_dirs.extend(dep.library_search_dirs)
            libraries.append(dep.path)

        if build_ctx.verbose:
            print("Linking selene object file with selene core library")
        invoke_zig(
            "build-exe",
            f"-femit-bin={out_path}",
            input_artifact.resource,
            *libraries,
            *link_flags,
        )
        return cls._make_artifact(
            out_path,
            metadata={"library_search_dirs": library_search_dirs},
        )


class HeliosObjectFileToSeleneExecutableStep_Darwin(Step):
    """
    Link helios object with the interface shim, utilities, and selene core library to create the final executable.
    """

    input_kind = HeliosObjectFileKind
    output_kind = SeleneExecutableKind

    @classmethod
    def get_cost(cls, build_ctx: BuildCtx) -> float:
        """
        Rule out this step for non-Darwin platforms.
        """
        if platform.system() == "Darwin":
            return 100
        else:
            return float("inf")

    @classmethod
    def apply(cls, build_ctx: BuildCtx, input_artifact: Artifact) -> Artifact:
        out_path = build_ctx.artifact_dir / "program.selene.x"
        if build_ctx.verbose:
            print("Linking helios object file with dependencies")
        try:
            from selene_sim import dist_dir as selene_dist
        except ImportError:
            raise ImportError(
                "Selene simulation library not found. Please install selene_sim."
            )
        selene_lib_dir = selene_dist / "lib"
        selene_lib = selene_lib_dir / "libselene.dylib"
        link_flags = ["-lc"]
        libraries = [selene_lib]
        library_search_dirs = [selene_lib_dir]
        for dep in build_ctx.deps:
            link_flags.extend(dep.link_flags)
            library_search_dirs.extend(dep.library_search_dirs)
            libraries.append(dep.path)

        if build_ctx.verbose:
            print("Linking selene object file with selene core library")
        invoke_zig(
            "build-exe",
            f"-femit-bin={out_path}",
            input_artifact.resource,
            *libraries,
            *link_flags,
        )
        return cls._make_artifact(
            out_path,
            metadata={"library_search_dirs": library_search_dirs},
        )


def register_helios_builtins(planner: BuildPlanner) -> None:
    planner.add_kind(HeliosLLVMIRStringKind)
    planner.add_kind(HeliosLLVMIRFileKind)
    planner.add_kind(HeliosLLVMBitcodeStringKind)
    planner.add_kind(HeliosLLVMBitcodeFileKind)
    planner.add_kind(HeliosObjectFileKind)
    planner.add_step(LLVMBitcodeStringToLLVMBitcodeFileStep)
    planner.add_step(LLVMIRStringToLLVMIRFileStep)
    planner.add_step(HeliosLLVMIRFileToHeliosObjectFileStep)
    planner.add_step(HeliosLLVMBitcodeFileToHeliosObjectFileStep)
    planner.add_step(HeliosObjectFileToSeleneObjectFileStep_Linux)
    planner.add_step(HeliosObjectFileToSeleneExecutableStep_Windows)
    planner.add_step(HeliosObjectFileToSeleneExecutableStep_Darwin)

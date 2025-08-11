from __future__ import annotations

import collections
import logging
import os
import pathlib
import shutil
import subprocess
import sys
import typing
from abc import abstractmethod

if typing.TYPE_CHECKING:
    from collections.abc import MutableMapping, Sequence

from typing_extensions import override

_PYTHON_BIN = sys.executable

logger = logging.getLogger(__name__)


def _is_windows() -> bool:
    return os.name == "nt"


def _bin_dir(venv_path: pathlib.Path) -> pathlib.Path:
    return pathlib.Path(venv_path) / ("Scripts" if _is_windows() else "bin")


def _pip_executable(venv_path: pathlib.Path) -> pathlib.Path:
    name = "pip.exe" if _is_windows() else "pip"
    return _bin_dir(venv_path) / name


def _venv_python(venv_path: pathlib.Path) -> pathlib.Path:
    name = "python.exe" if _is_windows() else "python"
    return _bin_dir(venv_path) / name


class VenvBackend:
    """Abstract base class for virtual environment backends."""

    _path: pathlib.Path
    _NAME: typing.ClassVar[str]
    _PRIORITY: typing.ClassVar[int]

    def __init__(self, path: str | pathlib.Path):
        if isinstance(path, str):
            path = pathlib.Path(path)
        if not path.is_absolute():
            raise ValueError(f"Path must be absolute: {path}")
        self._path = path.resolve()

    @property
    def name(self) -> str:
        return self._NAME

    @abstractmethod
    def create(self, *, clear: bool = False) -> None: ...

    @abstractmethod
    def install(
        self, *packages: str, extra_args: Sequence[str] | None = None
    ) -> None: ...

    @classmethod
    @abstractmethod
    def is_supported(cls) -> bool:
        """Check if the backend is supported on the current system."""

    def _run_command(self, cmd: list[str]) -> None:  # noqa: PLR6301
        """Run a command in the virtual environment."""
        logger.debug("Running command: %s", " ".join(cmd))
        try:
            subprocess.check_call(cmd, stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            logger.exception(
                "Command failed with exit code %d: %s", e.returncode, " ".join(cmd)
            )
            raise RuntimeError(
                f"Command failed with exit code {e.returncode}: {' '.join(cmd)}"
            ) from e


class VenvBackendRegistry:
    """Registry of virtual environment backends."""

    _registry: typing.ClassVar[MutableMapping[str, type[VenvBackend]]] = {}

    @classmethod
    def register_backend(cls, backend_cls: type[VenvBackend]) -> None:
        cls._registry[backend_cls._NAME] = backend_cls  # pyright: ignore[reportPrivateUsage]

    @classmethod
    def get_backend(cls, name: str) -> type[VenvBackend] | None:
        return cls._registry.get(name)

    @classmethod
    def has_backend(cls, name: str) -> bool:
        return name in cls._registry

    @classmethod
    def get_backends(cls) -> MutableMapping[str, type[VenvBackend]]:
        result: MutableMapping[str, type[VenvBackend]] = collections.OrderedDict()
        for name in sorted(cls._registry, key=lambda x: cls._registry[x]._PRIORITY):  # pyright: ignore[reportPrivateUsage]
            result[name] = cls._registry[name]
        return result

    @classmethod
    def get_supported_backends(cls) -> dict[str, type[VenvBackend]]:
        return {
            name: backend_cls
            for name, backend_cls in cls._registry.items()
            if backend_cls.is_supported()
        }


class VenvBackendVenv(VenvBackend):
    """Virtual environment backend using the venv module."""

    _path: pathlib.Path
    _NAME: typing.ClassVar[str] = "venv"
    _PRIORITY: typing.ClassVar[int] = 1

    @override
    @classmethod
    def is_supported(cls) -> bool:
        return True

    @override
    def create(self, *, clear: bool = False) -> None:
        clear_opt = ["--clear"] if clear else []
        venv_args = [_PYTHON_BIN, "-m", "venv"] + clear_opt + [str(self._path)]
        self._run_command(venv_args)

    @override
    def install(self, *packages: str, extra_args: Sequence[str] | None = None) -> None:
        if not self._path.exists():
            raise FileNotFoundError(f"Virtual environment not found: {self._path}")

        pip_executable = _pip_executable(self._path)
        if not pip_executable.exists():
            raise FileNotFoundError(f"pip executable not found: {pip_executable}")

        pip_args = [
            str(pip_executable),
            "install",
            "--quiet",
            "--no-python-version-warning",
            "--disable-pip-version-check",
            "--upgrade",
            *(list(extra_args) if extra_args else []),
            *packages,
        ]
        self._run_command(pip_args)


class VenvBackendUV(VenvBackend):
    """Virtual environment backend using the uv tool."""

    _path: pathlib.Path
    _NAME: typing.ClassVar[str] = "uv"
    _PRIORITY: typing.ClassVar[int] = 0
    _CMD = "uv"

    @override
    @classmethod
    def is_supported(cls) -> bool:
        return bool(shutil.which(cls._CMD))

    @override
    def create(self, *, clear: bool = False) -> None:
        venv_py = _venv_python(self._path)
        if venv_py.exists() and not clear:
            return
        # uv removes existing virtual environment automatically.
        cmd = [
            f"{self._CMD}",
            "venv",
            "--quiet",
            "--python",
            _PYTHON_BIN,
            self._path.as_posix(),
        ]
        self._run_command(cmd)

    @override
    def install(self, *packages: str, extra_args: Sequence[str] | None = None) -> None:
        if not self._path.exists():
            raise FileNotFoundError(f"Virtual environment not found: {self._path}")
        pip_args = [
            f"{self._CMD}",
            "pip",
            "install",
            "--python",
            _venv_python(self._path).as_posix(),
            "--quiet",
            "--upgrade",
            *(list(extra_args) if extra_args else []),
            *packages,
        ]
        self._run_command(pip_args)


# Register backends
VenvBackendRegistry.register_backend(VenvBackendVenv)
VenvBackendRegistry.register_backend(VenvBackendUV)

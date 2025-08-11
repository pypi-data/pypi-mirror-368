from __future__ import annotations

import datetime
import functools
import hashlib
import json
import logging
import os
import pathlib
import pkgutil
import shutil
import sys
import tempfile
import typing

if typing.TYPE_CHECKING:
    from collections.abc import Callable
    from types import TracebackType
    from .backends import VenvBackend

from .backends import VenvBackendRegistry

P = typing.ParamSpec("P")
R = typing.TypeVar("R")

VERSION = "0.0.3dev0"
__version__ = VERSION

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# fmt: off
VENV_ROOT = pathlib.Path(
    os.environ.get("PYDEPINJECT_VENV_ROOT", None)
    or pathlib.Path(tempfile.gettempdir()) / __name__.split(".", maxsplit=1)[0] / "venvs"
)
# fmt: on
logger.debug("VENV_ROOT: %s", VENV_ROOT)

VENV_BACKENDS = "|".join(VenvBackendRegistry.get_backends())
logger.debug("VENV_BACKENDS: %s", VENV_BACKENDS)


def _is_windows() -> bool:
    return os.name == "nt"


def _bin_dir(venv_path: pathlib.Path) -> pathlib.Path:
    return pathlib.Path(venv_path) / ("Scripts" if _is_windows() else "bin")


def _site_packages_dir(venv_path: pathlib.Path) -> pathlib.Path:
    if _is_windows():
        return pathlib.Path(venv_path) / "Lib" / "site-packages"
    return pathlib.Path(venv_path).joinpath(
        "lib",
        f"python{sys.version_info.major}.{sys.version_info.minor}",
        "site-packages",
    )


def _normalize_req_token(pkg_spec: str) -> str:
    """Produce a stable, comparable token for a package requirement string.

    Return a canonical representation of a requirement's logical intent
    (name, extras, version specifiers and markers) so that equivalent
    requirement expressions compare equal. If normalization cannot be
    performed the function falls back to a trimmed, lowercased input.
    """
    pkg_spec = pkg_spec.strip().lower()
    try:
        from packaging.requirements import InvalidRequirement, Requirement
        from packaging.utils import canonicalize_name
    except ImportError:
        return pkg_spec

    try:
        req = Requirement(pkg_spec)
    except InvalidRequirement:
        return pkg_spec

    name = canonicalize_name(req.name)
    spec = str(req.specifier)
    extras = f"[{','.join(sorted(req.extras))}]" if req.extras else ""
    markers = f";{req.marker}" if req.marker else ""
    return f"{name}{extras}{spec}{markers}".lower()


def _normalized_requirements_key(packages: tuple[str, ...]) -> str:
    """Return a stable, deterministic string representing a set of requirement expressions."""
    return ",".join(sorted(_normalize_req_token(pkg_spec) for pkg_spec in packages))


def is_requirements_satisfied(*packages: str) -> bool | None:
    """Check if the requirements are already satisfied. Return None if it cannot be determined."""
    try:
        from importlib.metadata import PackageNotFoundError, distribution

        from packaging.requirements import InvalidRequirement, Requirement
    except ImportError:
        logger.warning(
            "importlib.metadata and packaging not found. Cannot check if requirements are satisfied."
        )
        return None

    for package in packages:
        logger.debug("Checking package: %s", package)
        try:
            req = Requirement(package)
        except InvalidRequirement:
            logger.warning("Invalid requirement: %s", package)
            return None

        try:
            dist = distribution(req.name)
        except PackageNotFoundError:
            logger.debug(
                "Requirement %s is not satisfied. Distribution not found.", package
            )
            return False

        if req.specifier and dist.version not in req.specifier:
            logger.debug("Requirement %s is not satisfied. Version conflict.", package)
            return False

        logger.debug("Requirement %s is satisfied", package)

    return True


class RequirementManager:
    """A decorator and context manager to manage Python package requirements."""

    def __init__(
        self,
        *packages: str,
        venv_name: str | None = None,
        venv_root: pathlib.Path = VENV_ROOT,
        venv_backend: str | None = None,
        recreate: bool = False,
        ephemeral: bool = False,
        install_args: tuple[str, ...] = (),
    ):
        """Initialize the RequirementManager.

        Args:
            *packages: A list of package requirements.
            venv_name: The name of the virtual environment. If not provided,
                a unique name will be generated based on the package requirements.
            venv_root: The root directory for virtual environments.
            venv_backend: The virtual environment backend to use. Defaults to $PYDEPINJECT_VENV_BACKEND or "uv|venv".
            recreate: If True, the virtual environment will be recreated if it exists.
            ephemeral: If True, the virtual environment will be deleted after use.
            install_args: Additional installer arguments forwarded to the backend (e.g., pip/uv flags).
        """
        self.packages = packages
        self.venv_name = venv_name or os.environ.get("PYDEPINJECT_VENV_NAME", "")
        self.original_pythonpath = os.environ.get("PYTHONPATH", "")
        self.original_path = os.environ.get("PATH", "")
        self.original_syspath = sys.path.copy()
        self._venv_path = venv_root / self.venv_name if self.venv_name else None
        self._venv_root = venv_root
        self._install_args = tuple(install_args)

        venv_backend = (
            venv_backend
            or os.environ.get("PYDEPINJECT_VENV_BACKEND", None)
            or VENV_BACKENDS
        )
        self._venv_backends = [item.strip() for item in venv_backend.split("|")]
        invalid_backends = set(self._venv_backends) - set(VENV_BACKENDS.split("|"))
        if invalid_backends:
            raise ValueError(f"Invalid venv_backend: {','.join(invalid_backends)}")

        self.ephemeral = ephemeral
        self.recreate = recreate
        self._activated = False

    @property
    def venv_backend_cls(self) -> type[VenvBackend]:
        """Returns the virtual environment backend class."""
        supported_backends = VenvBackendRegistry.get_supported_backends()
        for backend in self._venv_backends:
            if backend not in supported_backends:
                continue
            return supported_backends[backend]
        raise ValueError("No supported venv backend found")

    @property
    def venv_path(self):
        # pylint: disable=too-many-locals
        """Returns a path to the virtual environment. If not set, a unique path is generated."""
        if self._venv_path:
            return self._venv_path

        norm_key = _normalized_requirements_key(self.packages)
        key = "|".join((
            getattr(self.venv_backend_cls, "_NAME", self.venv_backend_cls.__name__),
            f"py{sys.version_info.major}.{sys.version_info.minor}",
            hashlib.sha256(sys.executable.encode()).hexdigest()[:8],
            norm_key,
        ))
        # Non-cryptographic hash to key the venv path (safe for identity, not security).
        self._venv_path = self._venv_root / hashlib.md5(key.encode()).hexdigest()  # noqa: S324
        return self._venv_path

    def _create_virtualenv(self):
        """Create a virtual environment if it does not exist."""
        if self.venv_path.exists() and not self.recreate:
            return
        logger.debug("Creating virtualenv: %s", self.venv_path)
        self.venv_backend_cls(self.venv_path).create(clear=self.recreate)

    def _install_packages(self):
        if not self.packages:
            logger.debug("No packages to install. Skipping installation.")
            return
        logger.info("Installing packages: %s", self.packages)
        self.venv_backend_cls(self.venv_path).install(
            *self.packages,
            extra_args=list(self._install_args) if self._install_args else None,
        )
        # Write metadata file for traceability
        timestamp = int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp())
        meta_filepath = self.venv_path / f".pydepinject-{timestamp}.json"
        try:
            meta = {
                "version": VERSION,
                "backend": getattr(
                    self.venv_backend_cls, "_NAME", self.venv_backend_cls.__name__
                ),
                "python": sys.version,
                "sys_executable": sys.executable,
                "platform": sys.platform,
                "packages": list(self.packages),
                "install_args": list(self._install_args),
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }
            meta_filepath.write_text(json.dumps(meta, indent=2))
            logger.debug("Wrote venv metadata to: %s", meta_filepath)
        except (OSError, ValueError, TypeError) as e:
            logger.debug("Failed to write venv metadata: %s", e)

    def _purge_venv_modules(self) -> set[str]:
        """Remove all modules that conflict with packages from the virtual environment."""
        purged_modules: set[str] = set()
        venv_site_packages = _site_packages_dir(self.venv_path)
        # get all modules from the new venv
        venv_packages = pkgutil.walk_packages(
            [str(venv_site_packages)], prefix="", onerror=lambda _x: None
        )
        venv_modules = {
            name for _, name, _ in venv_packages if name not in sys.builtin_module_names
        }
        # Add existing modules from sys.modules that are in the venv.
        for name, module in sys.modules.items():
            module_path = getattr(module, "__file__", None)
            if module_path and pathlib.Path(module_path).is_relative_to(
                venv_site_packages
            ):
                venv_modules.add(name)

        # delete them from sys.modules to avoid conflicts
        for name in set(sys.modules).intersection(venv_modules):
            del sys.modules[name]
            purged_modules.add(name)
        return purged_modules

    def _activate_venv(self):
        if is_requirements_satisfied(*self.packages):
            logger.debug(
                "Requirements %s already satisfied. No need to create venv",
                self.packages,
            )
            return self

        self.original_pythonpath = os.environ.get("PYTHONPATH", "")
        self.original_path = os.environ.get("PATH", "")
        self.original_syspath = sys.path.copy()

        self._create_virtualenv()

        bin_dir = _bin_dir(self.venv_path)
        venv_site_packages = _site_packages_dir(self.venv_path)
        os.environ["PYTHONPATH"] = str(venv_site_packages) + (
            os.pathsep + self.original_pythonpath if self.original_pythonpath else ""
        )
        os.environ["PATH"] = str(bin_dir) + os.pathsep + self.original_path
        sys.path.insert(0, str(venv_site_packages))
        self._activated = True
        if is_requirements_satisfied(*self.packages):
            logger.debug(
                "Requirements %s already satisfied within %s",
                self.packages,
                self.venv_path,
            )
            return self
        self._install_packages()
        purged_modules = sorted(self._purge_venv_modules())
        if purged_modules:
            logger.debug(
                "Purged modules from venv %s: %s", self.venv_path, purged_modules
            )

    def _deactivate_venv(self):
        if not self._activated:
            return
        os.environ["PATH"] = self.original_path
        os.environ["PYTHONPATH"] = self.original_pythonpath
        sys.path = self.original_syspath
        # Cleanup imported cached modules from the temporary venv.
        self._purge_venv_modules()
        self._activated = False
        if self.ephemeral:
            logger.debug("Deleting ephemeral venv: %s", self.venv_path)
            shutil.rmtree(self.venv_path)

    def __enter__(self):
        try:
            self._activate_venv()
        except RuntimeError:
            logger.exception("Failed to activate venv: %s")
            if self.ephemeral:
                self._deactivate_venv()
            raise
        return self

    def __exit__(
        self,
        exctype: type[BaseException] | None,
        excinst: BaseException | None,
        exctb: TracebackType | None,
    ) -> None:
        del exctype, excinst, exctb
        self._deactivate_venv()

    def __call__(self, func: Callable[P, R] | None = None) -> Callable[P, R] | None:
        if func is None:
            try:
                self._activate_venv()
            except RuntimeError:
                logger.exception("Failed to activate venv: %s")
                if self.ephemeral:
                    self._deactivate_venv()
                raise
            return None

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            with self:
                return func(*args, **kwargs)

        return wrapper


requires = RequirementManager

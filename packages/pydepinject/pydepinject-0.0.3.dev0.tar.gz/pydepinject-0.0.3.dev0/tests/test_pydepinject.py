from __future__ import annotations

import functools

import pytest

from pydepinject import requires


def _is_packaging_installed():
    """Returns whether the packaging library is installed or not."""
    try:
        import packaging
    except ImportError:
        return False
    return True


@pytest.mark.parametrize("backend", ["uv", "venv"], ids=["uv", "venv"])
@pytest.mark.parametrize("ephemeral", [True, False], ids=["ephemeral", "non-ephemeral"])
def test_decorator(venv_root, ephemeral, backend):
    assert not list(venv_root.iterdir())

    with pytest.raises(ImportError):
        import attrs

    requires_ = functools.partial(
        requires, venv_root=venv_root, ephemeral=ephemeral, venv_backend=backend
    )

    @requires_("attrs")
    def examplefn():
        print("examplefn")
        import attrs

        assert attrs.__version__

    examplefn()
    with pytest.raises(ImportError):
        import attrs

    if ephemeral:
        assert not list(venv_root.iterdir())
    else:
        assert len(list(venv_root.iterdir())) == 1


@pytest.mark.parametrize("backend", ["uv", "venv"], ids=["uv", "venv"])
@pytest.mark.parametrize("ephemeral", [True, False], ids=["ephemeral", "non-ephemeral"])
def test_venv_name_predefined(venv_root, ephemeral, backend):
    assert not list(venv_root.iterdir())

    venv_name = "test_venv_name_predefined"
    with pytest.raises(ImportError):
        import attrs

    requires_ = functools.partial(
        requires,
        venv_root=venv_root,
        venv_name=venv_name,
        ephemeral=ephemeral,
        venv_backend=backend,
    )

    @requires_("attrs")
    def examplefn():
        print("examplefn")
        import attrs

        assert attrs.__version__
        assert (venv_root / venv_name).exists()

    examplefn()
    with pytest.raises(ImportError):
        import attrs

    assert (venv_root / venv_name).exists() is (not ephemeral)
    assert len(list(venv_root.iterdir())) == (1 if not ephemeral else 0)

    with requires_("attrs"):
        import attrs

        assert attrs.__version__
        assert (venv_root / venv_name).exists()

    with pytest.raises(ImportError):
        import attrs

    assert (venv_root / venv_name).exists() is (not ephemeral)
    assert len(list(venv_root.iterdir())) == (1 if not ephemeral else 0)


@pytest.mark.parametrize("backend", ["uv", "venv"], ids=["uv", "venv"])
@pytest.mark.parametrize("ephemeral", [True, False], ids=["ephemeral", "non-ephemeral"])
def test_venv_name_predefined_env(venv_root, monkeypatch, ephemeral, backend):
    assert not list(venv_root.iterdir())

    venv_name = "test_venv_name_predefined_env"
    monkeypatch.setenv("PYDEPINJECT_VENV_NAME", venv_name)

    with pytest.raises(ImportError):
        import attrs

    requires_ = functools.partial(
        requires, venv_root=venv_root, ephemeral=ephemeral, venv_backend=backend
    )

    @requires_("attrs")
    def examplefn():
        print("examplefn")
        import attrs

        assert attrs.__version__
        assert (venv_root / venv_name).exists()

    examplefn()
    with pytest.raises(ImportError):
        import attrs

    assert (venv_root / venv_name).exists() is (not ephemeral)
    assert len(list(venv_root.iterdir())) == (1 if not ephemeral else 0)

    with requires_("attrs"):
        import attrs

        assert attrs.__version__
        assert (venv_root / venv_name).exists()

    with pytest.raises(ImportError):
        import attrs

    assert (venv_root / venv_name).exists() is (not ephemeral)
    assert len(list(venv_root.iterdir())) == (1 if not ephemeral else 0)


@pytest.mark.parametrize("backend", ["uv", "venv"], ids=["uv", "venv"])
@pytest.mark.parametrize("ephemeral", [True, False], ids=["ephemeral", "non-ephemeral"])
def test_context_manager(venv_root, ephemeral, backend):
    assert not list(venv_root.iterdir())

    with pytest.raises(ImportError):
        import attrs

    requires_ = functools.partial(
        requires, venv_root=venv_root, ephemeral=ephemeral, venv_backend=backend
    )
    with requires_("attrs"):
        import attrs

        assert attrs.__version__

    with pytest.raises(ImportError):
        import attrs

    if ephemeral:
        assert not list(venv_root.iterdir())
    else:
        assert len(list(venv_root.iterdir())) == 1


@pytest.mark.parametrize("backend", ["uv", "venv"], ids=["uv", "venv"])
def test_function_call(venv_root, backend):
    assert not list(venv_root.iterdir())

    with pytest.raises(ImportError):
        import attrs

    requires_instance = requires("attrs", venv_root=venv_root, venv_backend=backend)
    requires_instance()
    import attrs

    assert attrs.__version__
    assert len(list(venv_root.iterdir())) == 1

    requires_instance._deactivate_venv()
    with pytest.raises(ImportError):
        import attrs
    assert len(list(venv_root.iterdir())) == 1


@pytest.mark.parametrize("backend", ["uv", "venv"], ids=["uv", "venv"])
def test_no_installs(venv_root, backend):
    assert not list(venv_root.iterdir())

    @requires("pytest", venv_root=venv_root, ephemeral=False, venv_backend=backend)
    def examplefn():
        print("examplefn")

    examplefn()
    assert len(list(venv_root.iterdir())) == 0 if _is_packaging_installed() else 1


@pytest.mark.parametrize("backend", ["uv", "venv"], ids=["uv", "venv"])
def test_reuse_venv(venv_root, backend):
    assert not list(venv_root.iterdir())

    requires_ = functools.partial(
        requires, venv_root=venv_root, ephemeral=False, venv_backend=backend
    )

    @requires_("attrs")
    def examplea():
        import attrs

        assert attrs.__version__
        examplea.called = True

    @requires_("attrs")
    def exampleb():
        import attrs

        assert attrs.__version__
        exampleb.called = True

    examplea()
    with pytest.raises(ImportError):
        import attrs

    exampleb()
    with pytest.raises(ImportError):
        import attrs

    assert examplea.called is exampleb.called is True
    assert len(list(venv_root.iterdir())) == 1


@pytest.mark.parametrize("backend", ["uv", "venv"], ids=["uv", "venv"])
def test_one_venv_multiple_packages(venv_root, backend):
    assert not list(venv_root.iterdir())

    venv_name = "test_one_venv_multiple_packages"

    requires_ = functools.partial(
        requires,
        venv_root=venv_root,
        venv_name=venv_name,
        ephemeral=False,
        venv_backend=backend,
    )

    @requires_("attrs")
    def examplefn():
        import attrs

        assert attrs.__version__
        assert (venv_root / venv_name).exists()

    @requires_("pyparsing")
    def examplefn2():
        import pyparsing

        assert pyparsing.__version__

        import attrs

        assert attrs.__version__
        assert (venv_root / venv_name).exists()

    examplefn()
    examplefn2()

    # Still exists as ephemeral is False.
    assert (venv_root / venv_name).exists()

    with pytest.raises(ImportError):
        import attrs
    with pytest.raises(ImportError):
        import pyparsing

    assert len(list(venv_root.iterdir())) == 1


@pytest.mark.parametrize("backend", ["uv", "venv"], ids=["uv", "venv"])
def test_empty_requires_noop(venv_root, backend):
    """No packages requested should not create a venv and should be a no-op."""
    assert not list(venv_root.iterdir())
    mgr = requires(venv_root=venv_root, ephemeral=False, venv_backend=backend)
    # Activate via __call__ path (no function)
    mgr()
    assert not list(venv_root.iterdir())


def test_default_backend_prefers_uv(monkeypatch, venv_root):
    """When uv is available, it should be preferred by default (uv|venv)."""
    # Make uv available, venv is always supported
    from pydepinject import backends

    def fake_which(cmd: str):
        return "/usr/bin/uv" if cmd == "uv" else None

    monkeypatch.setattr(backends.shutil, "which", fake_which, raising=True)

    mgr = requires(
        "pytest", venv_root=venv_root
    )  # no explicit backend: use default order
    assert getattr(mgr.venv_backend_cls, "_NAME", None) == "uv"


@pytest.mark.parametrize("backend", ["uv", "venv"], ids=["uv", "venv"])
def test_venv_identity_same_across_calls(venv_root, backend):
    """Same inputs should hash to the same venv path."""
    a = requires("attrs", venv_root=venv_root, venv_backend=backend)
    b = requires("attrs", venv_root=venv_root, venv_backend=backend)
    assert a.venv_path == b.venv_path


def test_venv_identity_diff_by_backend(venv_root):
    """Different backends should produce different venv identities for the same requirements."""
    a = requires("attrs", venv_root=venv_root, venv_backend="venv")
    b = requires("attrs", venv_root=venv_root, venv_backend="uv")
    assert a.venv_path != b.venv_path


@pytest.mark.parametrize("backend", ["uv", "venv"], ids=["uv", "venv"])
@pytest.mark.parametrize("ephemeral", [True, False], ids=["ephemeral", "non-ephemeral"])
def test_invalid_requirements_install_raises_error(venv_root, backend, ephemeral):
    with pytest.raises(ImportError):
        import attrs

    # Invalid requirement spec (packaging and pip both treat this as invalid)
    invalid_req = "attrs=1.0"

    mgr = requires(
        invalid_req, venv_root=venv_root, ephemeral=ephemeral, venv_backend=backend
    )
    venv_path = mgr.venv_path
    assert not venv_path.exists()

    with pytest.raises(RuntimeError):
        mgr()

    # The import should still fail in the current interpreter
    with pytest.raises(ImportError):
        import attrs

    # The venv is created before install and remains on disk since __enter__ failed
    if ephemeral:
        assert not venv_path.exists()
    else:
        assert venv_path.exists()
        assert len(list(venv_root.iterdir())) == 1


@pytest.mark.parametrize("backend", ["uv", "venv"], ids=["uv", "venv"])
@pytest.mark.parametrize("ephemeral", [True, False], ids=["ephemeral", "non-ephemeral"])
def test_invalid_requirements_install_raises_error_decorator(
    venv_root, backend, ephemeral
):
    assert not list(venv_root.iterdir())

    with pytest.raises(ImportError):
        import attrs

    # Invalid requirement spec (packaging and pip both treat this as invalid)
    invalid_req = "attrs=1.0"

    @requires(
        invalid_req, venv_root=venv_root, ephemeral=ephemeral, venv_backend=backend
    )
    def fn():
        import attrs

        assert attrs.__version__

    with pytest.raises(RuntimeError):
        fn()

    # The import should still fail in the current interpreter
    with pytest.raises(ImportError):
        import attrs

    # The venv is created before install and remains on disk since __enter__ failed
    if ephemeral:
        assert not list(venv_root.iterdir())
    else:
        assert len(list(venv_root.iterdir())) == 1


def test_invalid_backend_value_raises_valueerror(venv_root):
    # Supplying an unknown backend should raise ValueError during initialization
    with pytest.raises(ValueError, match="Invalid venv_backend: invalid"):
        requires("attrs", venv_root=venv_root, venv_backend="invalid")


def test_invalid_backend_value_from_env_raises_valueerror(venv_root, monkeypatch):
    # Unknown backend coming from environment variable should also raise
    monkeypatch.setenv("PYDEPINJECT_VENV_BACKEND", "invalid")

    with pytest.raises(ValueError, match="Invalid venv_backend: invalid"):
        requires("attrs", venv_root=venv_root)


def test_no_supported_backends_found(monkeypatch, venv_root):
    """If no supported backend is available from the configured list, raise ValueError."""
    from pydepinject import backends

    # Force all registered backends to report unsupported by iterating over the registry
    for backend_cls in backends.VenvBackendRegistry.get_backends().values():
        monkeypatch.setattr(backend_cls, "is_supported", lambda: False, raising=True)
    mgr = requires("pytest", venv_root=venv_root)
    with pytest.raises(ValueError, match="No supported venv backend found"):
        _ = mgr.venv_backend_cls

    # No environment should be created
    assert not list(venv_root.iterdir())


@pytest.mark.parametrize("backend", ["uv", "venv"], ids=["uv", "venv"])
@pytest.mark.parametrize("ephemeral", [True, False], ids=["ephemeral", "non-ephemeral"])
def test_same_package_different_versions(venv_root, backend, ephemeral):
    """Installing the same package with two different versions uses distinct venvs and resolves the correct version in each context."""
    assert not list(venv_root.iterdir())

    # Ensure the package is not available in the base interpreter
    with pytest.raises(ImportError):
        import attrs

    ver_a = "24.2.0"
    ver_b = "25.3.0"
    req_a = f"attrs=={ver_a}"
    req_b = f"attrs=={ver_b}"

    with requires(
        req_a, venv_root=venv_root, ephemeral=ephemeral, venv_backend=backend
    ) as mgr_a:
        import attrs as attrs_a
        from attrs import define, field, frozen

        assert attrs_a.__version__ == ver_a

        @define
        class Empty:
            pass

        assert Empty() == Empty()

        with requires(
            req_b, venv_root=venv_root, ephemeral=ephemeral, venv_backend=backend
        ) as mgr_b:
            import attrs as attrs_b

            assert attrs_b.__version__ == ver_b

            assert mgr_a.venv_path != mgr_b.venv_path, (
                "Different venvs should be created for different versions"
            )

        assert attrs_a.__version__ == ver_a, (
            "Version should remain unchanged after second requirement"
        )
        assert Empty() == Empty(), (
            "Class defined in first venv should still work after second requirement"
        )

        @frozen
        class FrozenInt:
            x: int = field()

            @x.validator
            def check(self, attribute, value):
                del attribute  # Unused.
                if value < 0:
                    raise ValueError("x must be non-negative")

        assert FrozenInt(1) == FrozenInt(1)
        with pytest.raises(ValueError, match="x must be non-negative"):
            FrozenInt(-1)
        with pytest.raises(attrs_a.exceptions.FrozenInstanceError):
            FrozenInt(1).x = 2

    with pytest.raises(ImportError):
        import attrs

    # Ephemeral mode cleans up, non-ephemeral leaves two distinct environments
    if ephemeral:
        assert not list(venv_root.iterdir())
    else:
        assert len(list(venv_root.iterdir())) == 2  # noqa: PLR2004

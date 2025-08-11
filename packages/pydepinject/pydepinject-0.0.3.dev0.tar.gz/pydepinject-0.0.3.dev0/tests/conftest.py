from __future__ import annotations

import pathlib

import pytest

PROJECT_DIR = pathlib.Path(__file__).parent.parent


@pytest.fixture(autouse=True)
def _check_test_leftovers():
    """Checks if the test left any files in the project directory."""
    items_before = list(PROJECT_DIR.iterdir())
    yield
    items_after = list(PROJECT_DIR.iterdir())
    new_items = set(items_after) - set(items_before)

    def _ignore_new_item(item: pathlib.Path) -> bool:
        return item.name.startswith((".coverage", ".pytest_cache", "pytest-cache"))

    new_items = {item for item in new_items if not _ignore_new_item(item)}
    if new_items:
        pytest.fail(f"New items in the project directory: {new_items}")


@pytest.fixture
def venv_root(tmp_path):
    """Return the root directory for virtual environments."""
    path = tmp_path / "venvs"
    path.mkdir()
    return path

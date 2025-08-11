# Requirement Manager

This project provides a `RequirementManager` (`requires` is an alias) class to manage Python package requirements using virtual environments. It can be used as a decorator or context manager to ensure specific packages are installed and available during the execution of a function or code block.

## Features

- Automatically creates and manages virtual environments.
- Checks if the required packages are already installed.
- Installs packages if they are not already available.
- Supports ephemeral virtual environments that are deleted after use.
- Can be used as a decorator or context manager.

## Installation

`pip install pydepinject`

To use the `uv` backend for faster environment and package management, ensure `uv` is installed separately. You can find installation instructions at [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv).


## Usage

### Decorator

To use the `requires` as a decorator, simply decorate your function with the required packages:

```python
from pydepinject import requires


@requires("requests", "numpy")
def my_function():
    import requests
    import numpy as np
    print(requests.__version__)
    print(np.__version__)

my_function()
```

### Context Manager

You can also use the `requires` as a context manager:

```python
from pydepinject import requires


with requires("requests", "numpy"):
    import requests
    import numpy as np
    print(requests.__version__)
    print(np.__version__)
```

### Virtual Environment with specific name

The `requires` can create a virtual environment with a specific name:

```python
@requires("requests", venv_name="myenv")
def my_function():
    import requests
    print(requests.__version__)


with requires("pylint", "requests", venv_name="myenv"):
    import pylint
    print(pylint.__version__)
    import requests  # This is also available here because it was installed in the same virtual environment
    print(requests.__version__)


# The virtual environment name can also be set as PYDEPINJECT_VENV_NAME environment variable
import os
os.environ["PYDEPINJECT_VENV_NAME"] = "myenv"

@requires("requests")
def my_function():
    import requests
    print(requests.__version__)


with requires("pylint", "requests"):
    import pylint
    print(pylint.__version__)
    import requests  # This is also available here because it was installed in the same virtual environment
    print(requests.__version__)
```



### Reusable Virtual Environments

The `requires` can create named virtual environments and reuse them across multiple functions or code blocks:

```python
@requires("requests", venv_name="myenv", ephemeral=False)
def my_function():
    import requests
    print(requests.__version__)


with requires("pylint", "requests", venv_name="myenv", ephemeral=False):
    import pylint
    print(pylint.__version__)
    import requests  # This is also available here because it was installed in the same virtual environment
    print(requests.__version__)
```

### Managing Virtual Environments

The `requires` can automatically delete ephemeral virtual environments after use. This is useful when you want to ensure that the virtual environment is clean and does not persist after the function or code block completes:

```python
@requires("requests", venv_name="myenv", ephemeral=True)
def my_function():
    import requests
    print(requests.__version__)

my_function()
```

### Forcing Virtual Environment Recreation

If you need to ensure a completely clean environment, you can force its recreation using the `recreate=True` parameter. This will delete and rebuild the virtual environment even if it already exists.

```python
from pydepinject import requires

# This will delete the "my-clean-env" venv if it exists and create it from scratch
@requires("requests", venv_name="my-clean-env", recreate=True)
def my_function():
    import requests
    print(requests.__version__)

my_function()
```

## Logging

This library uses Python's standard logging but does not configure handlers or levels by default. Configure logging in your application to see debug output:

```python
import logging

logging.basicConfig(level=logging.INFO)  # or DEBUG for verbose output
logging.getLogger("pydepinject").setLevel(logging.DEBUG)
```

You can also integrate with your application's logging setup (structlog, rich logging, etc.) by attaching handlers as you normally would.
## Backend selection

By default, backends are tried in priority order "uv|venv". If uv is installed on your system, it will be preferred for faster environment creation and installs; otherwise the standard library venv backend is used.

You can control backend selection:
- Environment variable: set PYDEPINJECT_VENV_BACKEND, e.g. `PYDEPINJECT_VENV_BACKEND=venv` or `PYDEPINJECT_VENV_BACKEND=uv|venv`.
- API param: pass `venv_backend="uv"`, `"venv"`, or a pipe-separated list like `"uv|venv"` to requires/RequirementManager.

On Windows, paths (Scripts, Lib/site-packages) are handled automatically.

## Advanced options

### Additional installer arguments
You can forward extra arguments to the underlying installer (pip or uv pip) via `install_args`. This is useful for custom indexes, constraints files, proxies, etc.

```python
from pydepinject import requires

@requires(
    "requests",
    install_args=(
        "--index-url", "https://pypi.myorg/simple",
        "--upgrade-strategy", "eager",
    ),
    venv_backend="venv",
)
def my_function():
    import requests
    print(requests.__version__)
```

These arguments are appended to the installer command.

### Virtual environment identity
For unnamed environments, a unique directory is generated based on a stable identity key. This key is derived from:
- The set of requirements, which are normalized, canonicalized (e.g., `PyYAML` becomes `pyyaml`), and sorted alphabetically to ensure a consistent order.
- The active Python version tag (e.g., `py3.11`).
- The selected backend (`uv` or `venv`).
- A short hash of the current Python interpreter's path to distinguish between different Python installations.

This process guarantees that identical dependency sets produce the same virtual environment, while any change in requirements, Python version, or backend results in a new, distinct environment. Named environments (created using the `venv_name` parameter) are not affected by this hashing mechanism.

### Venv metadata
After successful installs, a metadata file `.pydepinject-{timestamp}.json` is written into the venv directory. It records:
- pydepinject version, backend, Python version, interpreter path
- Target platform, requested packages, forwarded install args
- An ISO 8601 timestamp (UTC)

There might be multiple metadata files if the venv is reused across different runs with different requirements or install args. Each file is timestamped to avoid collisions.

This helps with debugging and reproducibility.

## Configuration with Environment Variables

`pydepinject` can be configured using the following environment variables:

- **`PYDEPINJECT_VENV_ROOT`**: Specifies the root directory where virtual environments are stored. If not set, a default temporary directory is used.
- **`PYDEPINJECT_VENV_NAME`**: Sets a default name for the virtual environment, which can be useful for creating persistent, reusable environments across different runs.
- **`PYDEPINJECT_VENV_BACKEND`**: Defines the virtual environment backend to use. Supported values are `uv` and `venv`. `uv` is preferred for its speed.

These variables provide a convenient way to standardize behavior in CI/CD pipelines or development environments.

## Unit Tests

Unit tests are provided to verify the functionality of the `requires`. The tests use `pytest` and cover various scenarios including decorator usage, context manager usage, ephemeral environments, and more.

### Running Tests

To run the unit tests, ensure you have `pytest` installed, and then execute the following command:

```bash
pytest
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

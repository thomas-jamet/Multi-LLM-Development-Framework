"""Core package exports."""

# Re-export from core module (core.py)
import sys
from pathlib import Path

# Add parent to path to allow importing sibling modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import and re-export from the core.py file (not the package)
# We need to be careful here - "core" is a package, but core.py is a module
# Python will import the package by default, so we use importlib
import importlib.util
spec = importlib.util.spec_from_file_location("core_module", Path(__file__).parent.parent / "core.py")
core_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core_module)

# Re-export everything from core.py
validate_project_name = core_module.validate_project_name
success = core_module.success
error = core_module.error
warning = core_module.warning
info = core_module.info
header = core_module.header
dim = core_module.dim
_c = core_module._c
Colors = core_module.Colors
CreationError = core_module.CreationError
ValidationError = core_module.ValidationError
ConfigurationError = core_module.ConfigurationError
UpgradeError = core_module.UpgradeError
RollbackError = core_module.RollbackError
VERSION = core_module.VERSION
DEFAULT_PYTHON_VERSION = core_module.DEFAULT_PYTHON_VERSION

__all__ = [
    'validate_project_name',
    'success',
    'error',
    'warning',
    'info',
    'header',
    'dim',
    '_c',
    'Colors',
    'CreationError',
    'ValidationError',
    'ConfigurationError',
    'UpgradeError',
    'RollbackError',
    'VERSION',
    'DEFAULT_PYTHON_VERSION',
]

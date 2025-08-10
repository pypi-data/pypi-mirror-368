"""Lackey - Task chain management engine for AI agents."""

import logging

from .core import LackeyCore
from .dependencies import (
    CircularDependencyError,
    DependencyError,
    DependencyValidator,
    dependency_validator,
)
from .file_ops import (
    FileOperationError,
    IntegrityError,
    TransactionError,
    TransactionManager,
    atomic_write,
)
from .models import (
    Complexity,
    LackeyConfig,
    Project,
    ProjectIndex,
    ProjectStatus,
    Task,
    TaskStatus,
)
from .storage import (
    LackeyStorage,
    ProjectNotFoundError,
    StorageError,
    TaskNotFoundError,
)
from .validation import InputValidator, SecurityError, ValidationError, validator

__version__ = "2.0.0"
__api_version__ = "2.0.0"  # MCP API compatibility version (semantic versioning)
__schema_version__ = "1.0.0"  # File format version
__data_version__ = "1.0.0"  # Individual file version
__author__ = "Lackey Contributors"
__email__ = "contact@lackey.dev"

# API Compatibility Matrix
# Maps package versions to supported API versions
API_COMPATIBILITY_MATRIX = {
    "0.8.0": ["1.0.0"],
    "0.8.1": ["1.0.0"],
    "0.8.2": ["1.0.0"],
    "0.8.3": ["1.0.0"],
    "0.8.4": ["1.0.0"],
    "0.8.5": ["1.0.0"],
    "0.8.6": ["1.0.0"],
    "0.8.7": ["1.0.0"],  # Current baseline
    # Future versions will support multiple API versions for backward compatibility
    # "0.9.0": ["1.0.0", "1.1.0"],  # Example: backward compatible addition
    # "1.0.0": ["2.0.0"],           # Example: breaking change
    "1.0.0": ["2.0.0"],
}

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

__all__ = [
    # Version info
    "__version__",
    "__api_version__",
    "__schema_version__",
    "__data_version__",
    "API_COMPATIBILITY_MATRIX",
    # Core classes
    "LackeyCore",
    "LackeyStorage",
    # Models
    "Task",
    "Project",
    "ProjectIndex",
    "LackeyConfig",
    "TaskStatus",
    "Complexity",
    "ProjectStatus",
    # Validators
    "dependency_validator",
    "DependencyValidator",
    "validator",
    "InputValidator",
    # File operations
    "atomic_write",
    "TransactionManager",
    # Exceptions
    "ValidationError",
    "SecurityError",
    "FileOperationError",
    "IntegrityError",
    "TransactionError",
    "DependencyError",
    "CircularDependencyError",
    "StorageError",
    "TaskNotFoundError",
    "ProjectNotFoundError",
]

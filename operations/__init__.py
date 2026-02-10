"""Operations module public API.

This module provides the main operations for workspace management:
- create_workspace: Create a new workspace
- validate_workspace: Validate an existing workspace
- upgrade_workspace: Upgrade workspace to next tier
- rollback_workspace: Rollback workspace from backup
- get_enterprise_domain: Get enterprise domain configuration
- OutputFormatter: Format operation results
- CreationResult: Data class for creation results
- ValidationResult: Data class for validation results
"""

from operations.creation import create_workspace
from operations.validation import validate_workspace
from operations.upgrade import upgrade_workspace
from operations.rollback import rollback_workspace
from operations.enterprise import get_enterprise_domain
from operations.output import OutputFormatter, CreationResult, ValidationResult

__all__ = [
    "create_workspace",
    "validate_workspace",
    "upgrade_workspace",
    "rollback_workspace",
    "get_enterprise_domain",
    "OutputFormatter",
    "CreationResult",
    "ValidationResult",
]

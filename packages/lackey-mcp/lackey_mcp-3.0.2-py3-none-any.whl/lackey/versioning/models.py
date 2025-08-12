"""Version information models for Lackey."""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Optional


@dataclass
class VersionInfo:
    """Complete version information for Lackey components.

    This follows the multi-level versioning strategy documented in
    docs/api-versioning-implementation.md
    """

    package_version: str  # "0.8.7" - Overall Lackey version
    api_version: str  # "1.0.0" - MCP API compatibility
    schema_version: str  # "1.0.0" - File format version
    data_version: str  # "1.0.0" - Individual file version
    created_by: str  # "lackey-0.8.7" - Creating package version
    created_at: str  # ISO timestamp
    migrated_from: Optional[str] = None  # Previous version if migrated
    migrated_at: Optional[str] = None  # Migration timestamp

    @classmethod
    def current(cls) -> "VersionInfo":
        """Get current version information."""
        from lackey import (
            __api_version__,
            __data_version__,
            __schema_version__,
            __version__,
        )

        return cls(
            package_version=__version__,
            api_version=__api_version__,
            schema_version=__schema_version__,
            data_version=__data_version__,
            created_by=f"lackey-{__version__}",
            created_at=datetime.now(UTC).isoformat() + "Z",
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        result = {
            "package_version": self.package_version,
            "api_version": self.api_version,
            "schema_version": self.schema_version,
            "data_version": self.data_version,
            "created_by": self.created_by,
            "created_at": self.created_at,
        }

        if self.migrated_from:
            result["migrated_from"] = self.migrated_from
        if self.migrated_at:
            result["migrated_at"] = self.migrated_at

        return result

    @classmethod
    def from_dict(cls, data: dict) -> "VersionInfo":
        """Create from dictionary."""
        return cls(
            package_version=data["package_version"],
            api_version=data["api_version"],
            schema_version=data["schema_version"],
            data_version=data["data_version"],
            created_by=data["created_by"],
            created_at=data["created_at"],
            migrated_from=data.get("migrated_from"),
            migrated_at=data.get("migrated_at"),
        )

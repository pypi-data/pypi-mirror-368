"""Template versioning and update management system.

This module provides functionality for managing template versions,
updates, migrations, and compatibility checking.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .templates import Template, TemplateManager
from .validation import ValidationError


class VersionChangeType(Enum):
    """Types of version changes."""

    MAJOR = "major"  # Breaking changes
    MINOR = "minor"  # New features, backward compatible
    PATCH = "patch"  # Bug fixes, backward compatible


class UpdateStatus(Enum):
    """Update status enumeration."""

    AVAILABLE = "available"
    REQUIRED = "required"  # Security or critical updates
    OPTIONAL = "optional"
    NOT_AVAILABLE = "not_available"


@dataclass
class VersionInfo:
    """Version information with semantic versioning support."""

    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None
    build: Optional[str] = None

    @classmethod
    def parse(cls, version_string: str) -> VersionInfo:
        """Parse a semantic version string."""
        # Regex for semantic versioning: major.minor.patch[-prerelease][+build]
        pattern = (
            r"^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9\-\.]+))?(?:\+([a-zA-Z0-9\-\.]+))?$"
        )
        match = re.match(pattern, version_string)

        if not match:
            raise ValidationError(f"Invalid version format: {version_string}")

        major, minor, patch, prerelease, build = match.groups()

        return cls(
            major=int(major),
            minor=int(minor),
            patch=int(patch),
            prerelease=prerelease,
            build=build,
        )

    def __str__(self) -> str:
        """Return string representation of version."""
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            version += f"-{self.prerelease}"
        if self.build:
            version += f"+{self.build}"
        return version

    def __eq__(self, other: object) -> bool:
        """Check version equality."""
        if not isinstance(other, VersionInfo):
            return False
        return (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
            and self.prerelease == other.prerelease
        )

    def __lt__(self, other: VersionInfo) -> bool:
        """Check if this version is less than another."""
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        if self.patch != other.patch:
            return self.patch < other.patch

        # Handle prerelease versions
        if self.prerelease is None and other.prerelease is not None:
            return False  # 1.0.0 > 1.0.0-alpha
        if self.prerelease is not None and other.prerelease is None:
            return True  # 1.0.0-alpha < 1.0.0
        if self.prerelease is not None and other.prerelease is not None:
            return self.prerelease < other.prerelease

        return False

    def __le__(self, other: VersionInfo) -> bool:
        """Check if this version is less than or equal to another."""
        return self < other or self == other

    def __gt__(self, other: VersionInfo) -> bool:
        """Check if this version is greater than another."""
        return not self <= other

    def __ge__(self, other: VersionInfo) -> bool:
        """Check if this version is greater than or equal to another."""
        return not self < other

    def is_compatible_with(self, other: VersionInfo) -> bool:
        """Check if this version is compatible with another (same major version)."""
        return self.major == other.major

    def bump(self, change_type: VersionChangeType) -> VersionInfo:
        """Create a new version with the specified bump."""
        if change_type == VersionChangeType.MAJOR:
            return VersionInfo(self.major + 1, 0, 0)
        elif change_type == VersionChangeType.MINOR:
            return VersionInfo(self.major, self.minor + 1, 0)
        elif change_type == VersionChangeType.PATCH:
            return VersionInfo(self.major, self.minor, self.patch + 1)
        else:
            raise ValidationError(f"Unknown change type: {change_type}")


@dataclass
class TemplateUpdate:
    """Information about a template update."""

    template_name: str
    current_version: VersionInfo
    available_version: VersionInfo
    change_type: VersionChangeType
    status: UpdateStatus
    changelog: str
    migration_required: bool = False
    migration_guide: Optional[str] = None
    security_update: bool = False
    release_date: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "template_name": self.template_name,
            "current_version": str(self.current_version),
            "available_version": str(self.available_version),
            "change_type": self.change_type.value,
            "status": self.status.value,
            "changelog": self.changelog,
            "migration_required": self.migration_required,
            "migration_guide": self.migration_guide,
            "security_update": self.security_update,
            "release_date": (
                self.release_date.isoformat() if self.release_date else None
            ),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TemplateUpdate:
        """Create from dictionary."""
        return cls(
            template_name=data["template_name"],
            current_version=VersionInfo.parse(data["current_version"]),
            available_version=VersionInfo.parse(data["available_version"]),
            change_type=VersionChangeType(data["change_type"]),
            status=UpdateStatus(data["status"]),
            changelog=data["changelog"],
            migration_required=data.get("migration_required", False),
            migration_guide=data.get("migration_guide"),
            security_update=data.get("security_update", False),
            release_date=(
                datetime.fromisoformat(data["release_date"])
                if data.get("release_date")
                else None
            ),
        )


@dataclass
class MigrationStep:
    """A single step in a template migration."""

    step_number: int
    description: str
    action_type: str  # "modify", "add", "remove", "rename"
    target: str  # What to modify (variable, content, file, etc.)
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    required: bool = True
    validation: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "step_number": self.step_number,
            "description": self.description,
            "action_type": self.action_type,
            "target": self.target,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "required": self.required,
            "validation": self.validation,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MigrationStep:
        """Create from dictionary."""
        return cls(
            step_number=data["step_number"],
            description=data["description"],
            action_type=data["action_type"],
            target=data["target"],
            old_value=data.get("old_value"),
            new_value=data.get("new_value"),
            required=data.get("required", True),
            validation=data.get("validation"),
        )


@dataclass
class TemplateMigration:
    """Migration instructions for updating a template."""

    from_version: VersionInfo
    to_version: VersionInfo
    migration_steps: List[MigrationStep]
    breaking_changes: List[str] = field(default_factory=list)
    deprecations: List[str] = field(default_factory=list)
    new_features: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "from_version": str(self.from_version),
            "to_version": str(self.to_version),
            "migration_steps": [step.to_dict() for step in self.migration_steps],
            "breaking_changes": self.breaking_changes,
            "deprecations": self.deprecations,
            "new_features": self.new_features,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TemplateMigration:
        """Create from dictionary."""
        return cls(
            from_version=VersionInfo.parse(data["from_version"]),
            to_version=VersionInfo.parse(data["to_version"]),
            migration_steps=[
                MigrationStep.from_dict(step) for step in data["migration_steps"]
            ],
            breaking_changes=data.get("breaking_changes", []),
            deprecations=data.get("deprecations", []),
            new_features=data.get("new_features", []),
        )


class TemplateVersionManager:
    """Manages template versions, updates, and migrations."""

    def __init__(self, template_manager: TemplateManager, workspace_dir: Path):
        """Initialize version manager."""
        self.template_manager = template_manager
        self.workspace_dir = Path(workspace_dir)
        self.versions_dir = self.workspace_dir / "versions"
        self.migrations_dir = self.workspace_dir / "migrations"

        # Create directories
        self.versions_dir.mkdir(parents=True, exist_ok=True)
        self.migrations_dir.mkdir(parents=True, exist_ok=True)

    def get_template_version(self, template_id: str) -> Optional[VersionInfo]:
        """Get the current version of a template."""
        template = self.template_manager.get_template(template_id)
        if not template:
            return None

        try:
            return VersionInfo.parse(template.version)
        except ValidationError:
            return None

    def check_for_updates(
        self,
        template_id: Optional[str] = None,
        registry_name: Optional[str] = None,
    ) -> List[TemplateUpdate]:
        """Check for available template updates."""
        updates = []

        # Get templates to check
        if template_id:
            template = self.template_manager.get_template(template_id)
            templates_to_check = [template] if template else []
        else:
            templates_to_check = self.template_manager.list_templates()

        # Check each template for updates
        for template in templates_to_check:
            try:
                current_version = VersionInfo.parse(template.version)
                available_updates = self._find_available_updates(
                    template.name, current_version, registry_name
                )
                updates.extend(available_updates)
            except ValidationError:
                # Skip templates with invalid versions
                continue

        return updates

    def _find_available_updates(
        self,
        template_name: str,
        current_version: VersionInfo,
        registry_name: Optional[str] = None,
    ) -> List[TemplateUpdate]:
        """Find available updates for a specific template."""
        # TODO: This would integrate with the template registry system
        # to check for newer versions in configured registries

        # For now, return empty list - this would be implemented
        # when the registry system is fully integrated
        return []

    def create_template_version(
        self,
        template: Template,
        change_type: VersionChangeType,
        changelog: str,
        breaking_changes: Optional[List[str]] = None,
        deprecations: Optional[List[str]] = None,
        new_features: Optional[List[str]] = None,
    ) -> Template:
        """Create a new version of a template."""
        current_version = VersionInfo.parse(template.version)
        new_version = current_version.bump(change_type)

        # Create new template with updated version
        new_template = Template(
            id=template.id,
            name=template.name,
            friendly_name=template.friendly_name,
            description=template.description,
            template_type=template.template_type,
            version=str(new_version),
            author=template.author,
            created=template.created,
            updated=datetime.now(UTC),
            tags=template.tags,
            variables=template.variables,
            extends=template.extends,
            content=template.content,
            files=template.files,
            metadata={
                **template.metadata,
                "version_history": template.metadata.get("version_history", [])
                + [
                    {
                        "version": str(current_version),
                        "date": template.updated.isoformat(),
                        "changelog": changelog,
                        "change_type": change_type.value,
                    }
                ],
            },
        )

        # Save version history
        self._save_version_history(template.name, new_version, changelog, change_type)

        # Create migration if needed
        if change_type == VersionChangeType.MAJOR and breaking_changes:
            self._create_migration(
                template.name,
                current_version,
                new_version,
                breaking_changes,
                deprecations or [],
                new_features or [],
            )

        return new_template

    def _save_version_history(
        self,
        template_name: str,
        version: VersionInfo,
        changelog: str,
        change_type: VersionChangeType,
    ) -> None:
        """Save version history to disk."""
        history_file = self.versions_dir / f"{template_name}-history.yaml"

        history_data: Dict[str, Any] = {"versions": []}
        if history_file.exists():
            with open(history_file, "r", encoding="utf-8") as f:
                history_data = yaml.safe_load(f) or {"versions": []}

        # Add new version entry
        version_entry = {
            "version": str(version),
            "date": datetime.now(UTC).isoformat(),
            "changelog": changelog,
            "change_type": change_type.value,
        }

        history_data["versions"].append(version_entry)
        history_data["versions"].sort(
            key=lambda v: VersionInfo.parse(v["version"]), reverse=True
        )

        # Save updated history
        with open(history_file, "w", encoding="utf-8") as f:
            yaml.dump(history_data, f, default_flow_style=False, sort_keys=False)

    def _create_migration(
        self,
        template_name: str,
        from_version: VersionInfo,
        to_version: VersionInfo,
        breaking_changes: List[str],
        deprecations: List[str],
        new_features: List[str],
    ) -> None:
        """Create a migration file for major version changes."""
        migration = TemplateMigration(
            from_version=from_version,
            to_version=to_version,
            migration_steps=[],  # Would be populated based on actual changes
            breaking_changes=breaking_changes,
            deprecations=deprecations,
            new_features=new_features,
        )

        migration_file = (
            self.migrations_dir / f"{template_name}-{from_version}-to-{to_version}.yaml"
        )

        with open(migration_file, "w", encoding="utf-8") as f:
            yaml.dump(migration.to_dict(), f, default_flow_style=False, sort_keys=False)

    def get_migration_path(
        self,
        template_name: str,
        from_version: VersionInfo,
        to_version: VersionInfo,
    ) -> List[TemplateMigration]:
        """Get the migration path between two versions."""
        migrations = []

        # Find all migration files for this template
        migration_files = list(self.migrations_dir.glob(f"{template_name}-*.yaml"))

        # Load and sort migrations
        available_migrations = []
        for migration_file in migration_files:
            try:
                with open(migration_file, "r", encoding="utf-8") as f:
                    migration_data = yaml.safe_load(f)
                    migration = TemplateMigration.from_dict(migration_data)
                    available_migrations.append(migration)
            except Exception:  # nosec B112
                # Skip invalid migration files during discovery (expected behavior)
                continue

        # Find path from from_version to to_version
        current_version = from_version
        while current_version < to_version:
            # Find next migration step
            next_migration: Optional[TemplateMigration] = None
            for migration in available_migrations:
                if (
                    migration.from_version == current_version
                    and migration.to_version <= to_version
                ):
                    if next_migration is None:
                        next_migration = migration
                    elif migration.to_version > next_migration.to_version:
                        next_migration = migration

            if next_migration is None:
                break  # No migration path found

            migrations.append(next_migration)
            current_version = next_migration.to_version

        return migrations

    def apply_migration(
        self,
        template: Template,
        migration: TemplateMigration,
    ) -> Template:
        """Apply a migration to a template."""
        # This would implement the actual migration logic
        # For now, just return the template unchanged
        # In a full implementation, this would:
        # 1. Apply each migration step
        # 2. Validate the result
        # 3. Update the template version

        updated_template = Template(
            id=template.id,
            name=template.name,
            friendly_name=template.friendly_name,
            description=template.description,
            template_type=template.template_type,
            version=str(migration.to_version),
            author=template.author,
            created=template.created,
            updated=datetime.now(UTC),
            tags=template.tags,
            variables=template.variables,
            extends=template.extends,
            content=template.content,
            files=template.files,
            metadata={
                **template.metadata,
                "migrated_from": str(migration.from_version),
                "migration_date": datetime.now(UTC).isoformat(),
            },
        )

        return updated_template

    def get_version_history(self, template_name: str) -> List[Dict[str, Any]]:
        """Get version history for a template."""
        history_file = self.versions_dir / f"{template_name}-history.yaml"

        if not history_file.exists():
            return []

        try:
            with open(history_file, "r", encoding="utf-8") as f:
                history_data = yaml.safe_load(f) or {"versions": []}
                versions = history_data.get("versions", [])
                # Ensure we return the correct type
                if isinstance(versions, list):
                    return versions
                else:
                    return []
        except Exception:
            return []

    def validate_version_constraints(
        self,
        template_name: str,
        version_constraint: str,
    ) -> bool:
        """Validate if a template version satisfies a constraint."""
        # Parse constraint (e.g., ">=1.0.0", "~1.2.0", "^2.0.0")
        # This is a simplified implementation

        template = self.template_manager.get_template_by_name(template_name)
        if not template:
            return False

        try:
            current_version = VersionInfo.parse(template.version)

            # Simple constraint parsing
            if version_constraint.startswith(">="):
                min_version = VersionInfo.parse(version_constraint[2:])
                return current_version >= min_version
            elif version_constraint.startswith("^"):
                base_version = VersionInfo.parse(version_constraint[1:])
                return (
                    current_version.major == base_version.major
                    and current_version >= base_version
                )
            elif version_constraint.startswith("~"):
                base_version = VersionInfo.parse(version_constraint[1:])
                return (
                    current_version.major == base_version.major
                    and current_version.minor == base_version.minor
                    and current_version >= base_version
                )
            else:
                # Exact version match
                required_version = VersionInfo.parse(version_constraint)
                return current_version == required_version

        except ValidationError:
            return False

    def cleanup_old_versions(
        self,
        template_name: str,
        keep_versions: int = 5,
    ) -> int:
        """Clean up old version history entries."""
        history_file = self.versions_dir / f"{template_name}-history.yaml"

        if not history_file.exists():
            return 0

        try:
            with open(history_file, "r", encoding="utf-8") as f:
                history_data = yaml.safe_load(f) or {"versions": []}

            versions = history_data.get("versions", [])
            if len(versions) <= keep_versions:
                return 0

            # Keep only the most recent versions
            versions.sort(key=lambda v: VersionInfo.parse(v["version"]), reverse=True)
            removed_count = len(versions) - keep_versions
            history_data["versions"] = versions[:keep_versions]

            # Save updated history
            with open(history_file, "w", encoding="utf-8") as f:
                yaml.dump(history_data, f, default_flow_style=False, sort_keys=False)

            return removed_count

        except Exception:
            return 0

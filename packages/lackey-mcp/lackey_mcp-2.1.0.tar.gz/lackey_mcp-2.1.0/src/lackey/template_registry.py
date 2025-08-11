"""Template registry and sharing system.

This module provides functionality for sharing, discovering, and distributing
templates across different Lackey installations.
"""

from __future__ import annotations

import hashlib
import json
import os
import tarfile
import tempfile
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from lackey.validation import ValidationError

from .path_security import validate_path
from .template_validation import TemplateValidator, ValidationSeverity
from .templates import Template, TemplateManager, TemplateType


class RegistryType(Enum):
    """Template registry type enumeration."""

    LOCAL = "local"
    REMOTE = "remote"
    GIT = "git"
    HTTP = "http"


@dataclass
class TemplatePackage:
    """Represents a packaged template for distribution."""

    template: Template
    checksum: str
    package_size: int
    created: datetime = field(default_factory=lambda: datetime.now(UTC))
    dependencies: List[str] = field(default_factory=list)
    compatibility: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "template": self.template.to_dict(),
            "checksum": self.checksum,
            "package_size": self.package_size,
            "created": self.created.isoformat(),
            "dependencies": self.dependencies,
            "compatibility": self.compatibility,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TemplatePackage:
        """Create from dictionary."""
        return cls(
            template=Template.from_dict(data["template"]),
            checksum=data["checksum"],
            package_size=data["package_size"],
            created=datetime.fromisoformat(data["created"]),
            dependencies=data.get("dependencies", []),
            compatibility=data.get("compatibility", {}),
        )


@dataclass
class TemplateRegistry:
    """Template registry configuration."""

    name: str
    registry_type: RegistryType
    url: Optional[str] = None
    path: Optional[Path] = None
    enabled: bool = True
    priority: int = 100
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "registry_type": self.registry_type.value,
            "url": self.url,
            "path": str(self.path) if self.path else None,
            "enabled": self.enabled,
            "priority": self.priority,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TemplateRegistry:
        """Create from dictionary."""
        return cls(
            name=data["name"],
            registry_type=RegistryType(data["registry_type"]),
            url=data.get("url"),
            path=Path(data["path"]) if data.get("path") else None,
            enabled=data.get("enabled", True),
            priority=data.get("priority", 100),
            metadata=data.get("metadata", {}),
        )


class TemplateDistributor:
    """Manages template packaging, sharing, and distribution."""

    def __init__(self, workspace_dir: Path):
        """Initialize template distributor."""
        self.workspace_dir = Path(workspace_dir)
        self.packages_dir = self.workspace_dir / "packages"
        self.registries_dir = self.workspace_dir / "registries"
        self.cache_dir = self.workspace_dir / "cache"

        # Create directories
        self.packages_dir.mkdir(parents=True, exist_ok=True)
        self.registries_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.registries: Dict[str, TemplateRegistry] = {}
        self._load_registries()

    def _load_registries(self) -> None:
        """Load registry configurations."""
        registry_file = self.registries_dir / "registries.yaml"
        if registry_file.exists():
            try:
                with open(registry_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                    for registry_data in data.get("registries", []):
                        registry = TemplateRegistry.from_dict(registry_data)
                        self.registries[registry.name] = registry
            except Exception as e:
                print(f"Warning: Failed to load registries: {e}")

        # Add default local registry if none exist
        if not self.registries:
            self.add_registry(
                name="local",
                registry_type=RegistryType.LOCAL,
                path=self.packages_dir,
            )

    def _save_registries(self) -> None:
        """Save registry configurations."""
        registry_file = self.registries_dir / "registries.yaml"
        data = {
            "registries": [registry.to_dict() for registry in self.registries.values()]
        }
        with open(registry_file, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def add_registry(
        self,
        name: str,
        registry_type: RegistryType,
        url: Optional[str] = None,
        path: Optional[Path] = None,
        enabled: bool = True,
        priority: int = 100,
    ) -> TemplateRegistry:
        """Add a new template registry."""
        if name in self.registries:
            raise ValidationError(f"Registry '{name}' already exists")

        registry = TemplateRegistry(
            name=name,
            registry_type=registry_type,
            url=url,
            path=path,
            enabled=enabled,
            priority=priority,
        )

        self.registries[name] = registry
        self._save_registries()
        return registry

    def remove_registry(self, name: str) -> bool:
        """Remove a template registry."""
        if name not in self.registries:
            return False

        del self.registries[name]
        self._save_registries()
        return True

    def package_template(
        self,
        template: Template,
        output_path: Optional[Path] = None,
        include_dependencies: bool = True,
    ) -> TemplatePackage:
        """Package a template for distribution."""
        # Validate template first
        validator = TemplateValidator()
        issues = validator.validate_template(template)

        # Check for critical issues
        critical_issues = [
            i for i in issues if i.severity == ValidationSeverity.CRITICAL
        ]
        if critical_issues:
            raise ValidationError(
                f"Cannot package template with critical issues: {critical_issues}"
            )

        # Create package directory
        if output_path is None:
            output_path = (
                self.packages_dir / f"{template.name}-{template.version}.tar.gz"
            )

        # Create temporary directory for packaging
        with tempfile.TemporaryDirectory() as temp_dir:
            package_dir = Path(temp_dir) / template.name
            package_dir.mkdir(parents=True)

            # Write template file
            template_file = package_dir / "template.yaml"
            with open(template_file, "w", encoding="utf-8") as f:
                yaml.dump(
                    template.to_dict(), f, default_flow_style=False, sort_keys=False
                )

            # Write template files
            if template.files:
                files_dir = package_dir / "files"
                files_dir.mkdir()
                for filename, content in template.files.items():
                    file_path = os.path.join(files_dir, filename)
                    validate_path(file_path, [str(files_dir)])
                    file_path_obj = Path(file_path)
                    file_path_obj.parent.mkdir(parents=True, exist_ok=True)
                    with open(file_path_obj, "w", encoding="utf-8") as f:
                        f.write(content)

            # Create package metadata
            metadata = {
                "name": template.name,
                "version": template.version,
                "template_type": template.template_type.value,
                "created": datetime.now(UTC).isoformat(),
                "lackey_version": "1.0.0",  # TODO: Get from version module
            }

            metadata_file = package_dir / "package.json"
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)

            # Create tarball
            with tarfile.open(output_path, "w:gz") as tar:
                tar.add(package_dir, arcname=template.name)

            # Calculate checksum
            checksum = self._calculate_checksum(output_path)
            package_size = output_path.stat().st_size

            return TemplatePackage(
                template=template,
                checksum=checksum,
                package_size=package_size,
            )

    def install_template_package(
        self,
        package_path: Path,
        template_manager: TemplateManager,
        verify_checksum: bool = True,
    ) -> Template:
        """Install a template package."""
        if not package_path.exists():
            raise ValidationError(f"Package file not found: {package_path}")

        # Extract package to temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            extract_dir = Path(temp_dir)

            with tarfile.open(package_path, "r:gz") as tar:
                # Security check: ensure all paths are safe
                safe_members = []
                for member in tar.getmembers():
                    if member.name.startswith("/") or ".." in member.name:
                        raise ValidationError(f"Unsafe path in package: {member.name}")
                    safe_members.append(member)

                # Path validation performed above - safe_members validated
                tar.extractall(extract_dir, members=safe_members)  # nosec B202

            # Find template directory (should be the only directory)
            template_dirs = [d for d in extract_dir.iterdir() if d.is_dir()]
            if len(template_dirs) != 1:
                raise ValidationError("Invalid package structure")

            template_dir = template_dirs[0]

            # Load template
            template_file = template_dir / "template.yaml"
            if not template_file.exists():
                raise ValidationError("Template file not found in package")

            with open(template_file, "r", encoding="utf-8") as f:
                template_data = yaml.safe_load(f)

            template = Template.from_dict(template_data)

            # Validate template
            validator = TemplateValidator()
            issues = validator.validate_template(template)

            critical_issues = [
                i for i in issues if i.severity == ValidationSeverity.CRITICAL
            ]
            if critical_issues:
                raise ValidationError(
                    f"Cannot install template with critical issues: {critical_issues}"
                )

            # Load template files if they exist
            files_dir = template_dir / "files"
            if files_dir.exists():
                for file_path in files_dir.rglob("*"):
                    if file_path.is_file():
                        relative_path = file_path.relative_to(files_dir)
                        with open(file_path, "r", encoding="utf-8") as f:
                            template.files[str(relative_path)] = f.read()

            # Install template using template manager
            installed_template = template_manager.create_template(
                name=template.name,
                friendly_name=template.friendly_name,
                description=template.description,
                template_type=template.template_type,
                version=template.version,
                author=template.author,
                tags=template.tags,
                variables=template.variables,
                extends=template.extends,
                content=template.content,
                files=template.files,
                metadata=template.metadata,
            )

            return installed_template

    def search_templates(
        self,
        query: Optional[str] = None,
        template_type: Optional[TemplateType] = None,
        tags: Optional[List[str]] = None,
        registry_name: Optional[str] = None,
    ) -> List[TemplatePackage]:
        """Search for templates across registries."""
        results = []

        # Determine which registries to search
        registries_to_search = []
        if registry_name:
            if registry_name in self.registries:
                registries_to_search = [self.registries[registry_name]]
        else:
            registries_to_search = [r for r in self.registries.values() if r.enabled]

        # Sort by priority
        registries_to_search.sort(key=lambda r: r.priority)

        # Search each registry
        for registry in registries_to_search:
            try:
                registry_results = self._search_registry(
                    registry, query, template_type, tags
                )
                results.extend(registry_results)
            except Exception as e:
                print(f"Warning: Failed to search registry '{registry.name}': {e}")

        return results

    def _search_registry(
        self,
        registry: TemplateRegistry,
        query: Optional[str] = None,
        template_type: Optional[TemplateType] = None,
        tags: Optional[List[str]] = None,
    ) -> List[TemplatePackage]:
        """Search a specific registry for templates."""
        if registry.registry_type == RegistryType.LOCAL:
            return self._search_local_registry(registry, query, template_type, tags)
        else:
            # TODO: Implement remote registry search
            return []

    def _search_local_registry(
        self,
        registry: TemplateRegistry,
        query: Optional[str] = None,
        template_type: Optional[TemplateType] = None,
        tags: Optional[List[str]] = None,
    ) -> List[TemplatePackage]:
        """Search local registry for templates."""
        results: List[TemplatePackage] = []

        if not registry.path or not registry.path.exists():
            return results

        # Find all package files
        for package_file in registry.path.glob("*.tar.gz"):
            try:
                # Extract and examine package
                with tempfile.TemporaryDirectory() as temp_dir:
                    extract_dir = Path(temp_dir)

                    with tarfile.open(package_file, "r:gz") as tar:
                        # Security check: ensure all paths are safe
                        safe_members = []
                        for member in tar.getmembers():
                            if member.name.startswith("/") or ".." in member.name:
                                continue  # Skip unsafe paths
                            safe_members.append(member)
                        # Path validation performed above - safe_members validated
                        tar.extractall(extract_dir, members=safe_members)  # nosec B202

                    # Find template directory
                    template_dirs = [d for d in extract_dir.iterdir() if d.is_dir()]
                    if len(template_dirs) != 1:
                        continue

                    template_dir = template_dirs[0]
                    template_file = template_dir / "template.yaml"

                    if not template_file.exists():
                        continue

                    # Load template
                    with open(template_file, "r", encoding="utf-8") as f:
                        template_data = yaml.safe_load(f)

                    template = Template.from_dict(template_data)

                    # Apply filters
                    if (
                        query
                        and query.lower() not in template.friendly_name.lower()
                        and query.lower() not in template.description.lower()
                    ):
                        continue

                    if template_type and template.template_type != template_type:
                        continue

                    if tags and not any(tag in template.tags for tag in tags):
                        continue

                    # Create package info
                    checksum = self._calculate_checksum(package_file)
                    package_size = package_file.stat().st_size

                    package = TemplatePackage(
                        template=template,
                        checksum=checksum,
                        package_size=package_size,
                    )

                    results.append(package)

            except Exception as e:
                print(f"Warning: Failed to examine package {package_file}: {e}")

        return results

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def list_registries(self) -> List[TemplateRegistry]:
        """List all configured registries."""
        return list(self.registries.values())

    def get_registry(self, name: str) -> Optional[TemplateRegistry]:
        """Get a registry by name."""
        return self.registries.get(name)

    def enable_registry(self, name: str) -> bool:
        """Enable a registry."""
        if name not in self.registries:
            return False

        self.registries[name].enabled = True
        self._save_registries()
        return True

    def disable_registry(self, name: str) -> bool:
        """Disable a registry."""
        if name not in self.registries:
            return False

        self.registries[name].enabled = False
        self._save_registries()
        return True

    def update_registry_priority(self, name: str, priority: int) -> bool:
        """Update registry priority."""
        if name not in self.registries:
            return False

        self.registries[name].priority = priority
        self._save_registries()
        return True

    def publish_template(
        self,
        template: Template,
        registry_name: str,
        force: bool = False,
    ) -> bool:
        """Publish a template to a registry."""
        registry = self.registries.get(registry_name)
        if not registry:
            raise ValidationError(f"Registry '{registry_name}' not found")

        if not registry.enabled:
            raise ValidationError(f"Registry '{registry_name}' is disabled")

        # Package the template
        package = self.package_template(template)

        # Publish based on registry type
        if registry.registry_type == RegistryType.LOCAL:
            return self._publish_to_local_registry(package, registry, force)
        elif registry.registry_type == RegistryType.GIT:
            return self._publish_to_git_registry(package, registry, force)
        elif registry.registry_type == RegistryType.HTTP:
            return self._publish_to_http_registry(package, registry, force)
        else:
            raise ValidationError(
                f"Publishing to {registry.registry_type} not implemented"
            )

    def _publish_to_local_registry(
        self,
        package: TemplatePackage,
        registry: TemplateRegistry,
        force: bool = False,
    ) -> bool:
        """Publish template to local registry."""
        if not registry.path:
            raise ValidationError("Local registry must have a path")

        registry.path.mkdir(parents=True, exist_ok=True)

        # Check if template already exists
        package_filename = f"{package.template.name}-{package.template.version}.tar.gz"
        package_path = registry.path / package_filename

        if package_path.exists() and not force:
            raise ValidationError(
                f"Template {package.template.name} v{package.template.version} "
                f"already exists in registry. Use force=True to overwrite."
            )

        # Create the package file
        temp_package = self.package_template(
            package.template,
            output_path=package_path,
        )

        # Create registry index if it doesn't exist
        index_file = registry.path / "index.yaml"
        index_data: Dict[str, Any] = {"templates": []}

        if index_file.exists():
            with open(index_file, "r", encoding="utf-8") as f:
                index_data = yaml.safe_load(f) or {"templates": []}

        # Update index
        template_entry = {
            "name": package.template.name,
            "version": package.template.version,
            "friendly_name": package.template.friendly_name,
            "description": package.template.description,
            "template_type": package.template.template_type.value,
            "tags": package.template.tags,
            "author": package.template.author,
            "created": package.template.created.isoformat(),
            "updated": package.template.updated.isoformat(),
            "package_file": package_filename,
            "checksum": temp_package.checksum,
            "package_size": temp_package.package_size,
        }

        # Remove existing entry if updating
        index_data["templates"] = [
            t
            for t in index_data["templates"]
            if not (
                t["name"] == package.template.name
                and t["version"] == package.template.version
            )
        ]

        index_data["templates"].append(template_entry)
        index_data["templates"].sort(key=lambda t: (t["name"], t["version"]))

        # Save updated index
        with open(index_file, "w", encoding="utf-8") as f:
            yaml.dump(index_data, f, default_flow_style=False, sort_keys=False)

        return True

    def _publish_to_git_registry(
        self,
        package: TemplatePackage,
        registry: TemplateRegistry,
        force: bool = False,
    ) -> bool:
        """Publish template to Git registry."""
        # TODO: Implement Git registry publishing
        # This would involve:
        # 1. Clone the repository
        # 2. Add the template package
        # 3. Update the index
        # 4. Commit and push changes
        raise NotImplementedError("Git registry publishing not yet implemented")

    def _publish_to_http_registry(
        self,
        package: TemplatePackage,
        registry: TemplateRegistry,
        force: bool = False,
    ) -> bool:
        """Publish template to HTTP registry."""
        # TODO: Implement HTTP registry publishing
        # This would involve:
        # 1. Upload package file via HTTP API
        # 2. Update registry index
        # 3. Handle authentication if required
        raise NotImplementedError("HTTP registry publishing not yet implemented")

    def download_template(
        self,
        template_name: str,
        version: Optional[str] = None,
        registry_name: Optional[str] = None,
    ) -> Optional[TemplatePackage]:
        """Download a template package from registries."""
        # Search for the template
        search_results = self.search_templates(
            query=template_name,
            registry_name=registry_name,
        )

        # Filter by exact name match
        matching_templates = [
            pkg for pkg in search_results if pkg.template.name == template_name
        ]

        if not matching_templates:
            return None

        # Filter by version if specified
        if version:
            matching_templates = [
                pkg for pkg in matching_templates if pkg.template.version == version
            ]

        if not matching_templates:
            return None

        # Return the first match (highest priority registry)
        return matching_templates[0]

    def get_template_info(
        self,
        template_name: str,
        version: Optional[str] = None,
        registry_name: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Get detailed information about a template."""
        package = self.download_template(template_name, version, registry_name)
        if not package:
            return None

        return {
            "template": package.template.to_dict(),
            "package_info": {
                "checksum": package.checksum,
                "size": package.package_size,
                "created": package.created.isoformat(),
                "dependencies": package.dependencies,
                "compatibility": package.compatibility,
            },
        }

    def list_available_templates(
        self,
        registry_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List all available templates across registries."""
        templates = []

        registries_to_check = []
        if registry_name:
            if registry_name in self.registries:
                registries_to_check = [self.registries[registry_name]]
        else:
            registries_to_check = [r for r in self.registries.values() if r.enabled]

        for registry in registries_to_check:
            try:
                if registry.registry_type == RegistryType.LOCAL:
                    registry_templates = self._list_local_registry_templates(registry)
                    for template_info in registry_templates:
                        template_info["registry"] = registry.name
                        templates.append(template_info)
            except Exception as e:
                print(
                    (
                        f"Warning: Failed to list templates from registry "
                        f"'{registry.name}': {e}"
                    )
                )

        return templates

    def _list_local_registry_templates(
        self,
        registry: TemplateRegistry,
    ) -> List[Dict[str, Any]]:
        """List templates in a local registry."""
        if not registry.path or not registry.path.exists():
            return []

        index_file = registry.path / "index.yaml"
        if not index_file.exists():
            return []

        try:
            with open(index_file, "r", encoding="utf-8") as f:
                index_data = yaml.safe_load(f) or {}
                templates = index_data.get("templates", [])
                # Ensure we return the correct type
                if isinstance(templates, list):
                    return templates
                else:
                    return []
        except Exception:
            return []

    def cleanup_cache(self, max_age_days: int = 30) -> int:
        """Clean up old cached template packages."""
        if not self.cache_dir.exists():
            return 0

        cutoff_time = datetime.now(UTC).timestamp() - (max_age_days * 24 * 60 * 60)
        cleaned_count = 0

        for cache_file in self.cache_dir.glob("*.tar.gz"):
            try:
                if cache_file.stat().st_mtime < cutoff_time:
                    cache_file.unlink()
                    cleaned_count += 1
            except Exception as e:
                print(f"Warning: Failed to clean cache file {cache_file}: {e}")

        return cleaned_count

    def validate_registry_health(self, registry_name: str) -> Dict[str, Any]:
        """Validate the health and accessibility of a registry."""
        registry = self.registries.get(registry_name)
        if not registry:
            return {
                "healthy": False,
                "error": f"Registry '{registry_name}' not found",
            }

        health_info = {
            "name": registry.name,
            "type": registry.registry_type.value,
            "enabled": registry.enabled,
            "healthy": False,
            "template_count": 0,
            "last_checked": datetime.now(UTC).isoformat(),
        }

        try:
            if registry.registry_type == RegistryType.LOCAL:
                if registry.path and registry.path.exists():
                    templates = self._list_local_registry_templates(registry)
                    health_info["template_count"] = len(templates)
                    health_info["healthy"] = True
                else:
                    health_info["error"] = "Registry path does not exist"
            else:
                health_info["error"] = (
                    f"Health check for {registry.registry_type} not implemented"
                )

        except Exception as e:
            health_info["error"] = str(e)

        return health_info


def create_builtin_templates(template_manager: TemplateManager) -> None:
    """Create built-in templates if they don't exist."""
    builtin_templates_dir = Path(__file__).parent / "builtin_templates"

    if not builtin_templates_dir.exists():
        return

    for template_file in builtin_templates_dir.glob("*.yaml"):
        try:
            with open(template_file, "r", encoding="utf-8") as f:
                template_data = yaml.safe_load(f)

            template = Template.from_dict(template_data)

            # Check if template already exists
            existing = template_manager.get_template_by_name(template.name)
            if existing:
                continue  # Skip if already exists

            # Create the template
            template_manager.create_template(
                name=template.name,
                friendly_name=template.friendly_name,
                description=template.description,
                template_type=template.template_type,
                version=template.version,
                author=template.author,
                tags=template.tags,
                variables=template.variables,
                extends=template.extends,
                content=template.content,
                files=template.files,
                metadata=template.metadata,
            )

        except Exception as e:
            print(f"Warning: Failed to load built-in template {template_file}: {e}")

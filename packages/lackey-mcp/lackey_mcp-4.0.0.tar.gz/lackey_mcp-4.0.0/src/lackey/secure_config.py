"""Secure configuration management for Lackey.

This module provides secure configuration handling with encryption,
validation, and secure storage of sensitive configuration data.
"""

import json
import os
import time
from base64 import b64decode, b64encode
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

from cryptography.fernet import Fernet

from lackey.security import SecurityError, SecurityEvent, get_security_manager


@dataclass
class ConfigSchema:
    """Configuration schema definition for validation."""

    field_name: str
    field_type: type
    required: bool = False
    default_value: Any = None
    sensitive: bool = False  # Whether to encrypt this field
    validation_pattern: Optional[str] = None
    allowed_values: Optional[Set[Any]] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    description: str = ""


class SecureConfigManager:
    """Secure configuration manager with encryption and validation."""

    def __init__(self, config_dir: str = ".lackey/config"):
        """Initialize secure configuration manager."""
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.security_manager = get_security_manager()
        self._encryption_key: Optional[bytes] = None
        self._config_cache: Dict[str, Dict[str, Any]] = {}

        # Configuration schemas
        self.schemas: Dict[str, List[ConfigSchema]] = {}

        # Initialize default schemas
        self._setup_default_schemas()

        # Load master key or create new one
        self._initialize_encryption()

    def _setup_default_schemas(self) -> None:
        """Set up default configuration schemas."""
        # Security configuration schema
        security_schema = [
            ConfigSchema(
                "max_requests_per_minute",
                int,
                True,
                60,
                False,
                None,
                None,
                1,
                10000,
                "Maximum requests per minute",
            ),
            ConfigSchema(
                "max_file_size_mb",
                float,
                True,
                10.0,
                False,
                None,
                None,
                0.1,
                1000.0,
                "Maximum file size in MB",
            ),
            ConfigSchema(
                "session_timeout_minutes",
                int,
                True,
                60,
                False,
                None,
                None,
                1,
                1440,
                "Session timeout in minutes",
            ),
            ConfigSchema(
                "password_min_length",
                int,
                True,
                8,
                False,
                None,
                None,
                4,
                128,
                "Minimum password length",
            ),
            ConfigSchema(
                "encryption_key",
                str,
                False,
                None,
                True,
                None,
                None,
                None,
                None,
                "Encryption key for sensitive data",
            ),
            ConfigSchema(
                "jwt_secret",
                str,
                False,
                None,
                True,
                None,
                None,
                None,
                None,
                "JWT signing secret",
            ),
            ConfigSchema(
                "api_key_prefix",
                str,
                True,
                "lk_",
                False,
                None,
                None,
                None,
                None,
                "API key prefix",
            ),
        ]
        self.schemas["security"] = security_schema

        # Database configuration schema
        database_schema = [
            ConfigSchema(
                "host",
                str,
                True,
                "localhost",
                False,
                None,
                None,
                None,
                None,
                "Database host",
            ),
            ConfigSchema(
                "port", int, True, 5432, False, None, None, 1, 65535, "Database port"
            ),
            ConfigSchema(
                "database",
                str,
                True,
                "lackey",
                False,
                None,
                None,
                None,
                None,
                "Database name",
            ),
            ConfigSchema(
                "username",
                str,
                True,
                None,
                False,
                None,
                None,
                None,
                None,
                "Database username",
            ),
            ConfigSchema(
                "password",
                str,
                True,
                None,
                True,
                None,
                None,
                None,
                None,
                "Database password",
            ),
            ConfigSchema(
                "ssl_mode",
                str,
                True,
                "prefer",
                False,
                None,
                {"disable", "allow", "prefer", "require"},
                None,
                None,
                "SSL mode",
            ),
            ConfigSchema(
                "connection_timeout",
                int,
                True,
                30,
                False,
                None,
                None,
                1,
                300,
                "Connection timeout in seconds",
            ),
        ]
        self.schemas["database"] = database_schema

        # Logging configuration schema
        logging_schema = [
            ConfigSchema(
                "level",
                str,
                True,
                "INFO",
                False,
                None,
                {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"},
                None,
                None,
                "Log level",
            ),
            ConfigSchema(
                "file_path",
                str,
                False,
                None,
                False,
                None,
                None,
                None,
                None,
                "Log file path",
            ),
            ConfigSchema(
                "max_file_size_mb",
                float,
                True,
                10.0,
                False,
                None,
                None,
                0.1,
                1000.0,
                "Maximum log file size",
            ),
            ConfigSchema(
                "backup_count",
                int,
                True,
                5,
                False,
                None,
                None,
                1,
                100,
                "Number of backup log files",
            ),
            ConfigSchema(
                "format",
                str,
                True,
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                False,
                None,
                None,
                None,
                None,
                "Log format",
            ),
        ]
        self.schemas["logging"] = logging_schema

        # MCP server configuration schema
        mcp_schema = [
            ConfigSchema(
                "host",
                str,
                True,
                "localhost",
                False,
                None,
                None,
                None,
                None,
                "MCP server host",
            ),
            ConfigSchema(
                "port", int, True, 8000, False, None, None, 1, 65535, "MCP server port"
            ),
            ConfigSchema(
                "max_connections",
                int,
                True,
                100,
                False,
                None,
                None,
                1,
                10000,
                "Maximum concurrent connections",
            ),
            ConfigSchema(
                "request_timeout",
                int,
                True,
                30,
                False,
                None,
                None,
                1,
                300,
                "Request timeout in seconds",
            ),
            ConfigSchema(
                "enable_cors",
                bool,
                True,
                False,
                False,
                None,
                None,
                None,
                None,
                "Enable CORS",
            ),
            ConfigSchema(
                "cors_origins",
                list,
                False,
                [],
                False,
                None,
                None,
                None,
                None,
                "Allowed CORS origins",
            ),
        ]
        self.schemas["mcp"] = mcp_schema

    def _initialize_encryption(self) -> None:
        """Initialize encryption key for sensitive configuration data."""
        key_file = self.config_dir / ".encryption_key"

        if key_file.exists():
            # Load existing key
            try:
                with open(key_file, "rb") as f:
                    self._encryption_key = f.read()

                # Validate key
                Fernet(self._encryption_key)  # This will raise an exception if invalid

            except Exception as e:
                self.security_manager.log_security_event(
                    SecurityEvent(
                        event_type="config_encryption_key_invalid",
                        severity="high",
                        message=f"Invalid encryption key found: {str(e)}",
                        metadata={"key_file": str(key_file)},
                    )
                )
                # Generate new key
                self._generate_new_encryption_key()
        else:
            # Generate new key
            self._generate_new_encryption_key()

    def _generate_new_encryption_key(self) -> None:
        """Generate a new encryption key."""
        self._encryption_key = Fernet.generate_key()

        key_file = self.config_dir / ".encryption_key"

        # Write key with restricted permissions
        with open(key_file, "wb") as f:
            if self._encryption_key is not None:
                f.write(self._encryption_key)

        # Set restrictive permissions (owner read/write only)
        os.chmod(key_file, 0o600)

        self.security_manager.log_security_event(
            SecurityEvent(
                event_type="config_encryption_key_generated",
                severity="medium",
                message="New encryption key generated for configuration",
                metadata={"key_file": str(key_file)},
            )
        )

    def _encrypt_value(self, value: str) -> str:
        """Encrypt a sensitive configuration value."""
        if not self._encryption_key:
            # Return base64 encoded value if encryption key not available
            return b64encode(value.encode("utf-8")).decode("utf-8")

        fernet = Fernet(self._encryption_key)
        encrypted_bytes = fernet.encrypt(value.encode("utf-8"))
        return b64encode(encrypted_bytes).decode("utf-8")

    def _decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a sensitive configuration value."""
        if not self._encryption_key:
            # Try base64 decode if encryption key not available
            try:
                return b64decode(encrypted_value.encode("utf-8")).decode("utf-8")
            except Exception as e:
                raise SecurityError(f"Failed to decode configuration value: {str(e)}")

        try:
            fernet = Fernet(self._encryption_key)
            encrypted_bytes = b64decode(encrypted_value.encode("utf-8"))
            decrypted_bytes: bytes = fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode("utf-8")
        except Exception as e:
            raise SecurityError(f"Failed to decrypt configuration value: {str(e)}")

    def validate_config(
        self, config_name: str, config_data: Dict[str, Any]
    ) -> List[str]:
        """Validate configuration data against schema."""
        if config_name not in self.schemas:
            return [f"Unknown configuration schema: {config_name}"]

        schema = self.schemas[config_name]
        errors = []

        # Check required fields
        for field_schema in schema:
            field_name = field_schema.field_name

            if field_schema.required and field_name not in config_data:
                if field_schema.default_value is not None:
                    config_data[field_name] = field_schema.default_value
                else:
                    errors.append(f"Required field missing: {field_name}")
                    continue

            if field_name not in config_data:
                continue

            value = config_data[field_name]

            # Type validation
            if not isinstance(value, field_schema.field_type):
                try:
                    # Try to convert
                    if field_schema.field_type == int:
                        config_data[field_name] = int(value)
                    elif field_schema.field_type == float:
                        config_data[field_name] = float(value)
                    elif field_schema.field_type == bool:
                        config_data[field_name] = bool(value)
                    elif field_schema.field_type == str:
                        config_data[field_name] = str(value)
                    elif field_schema.field_type == list:
                        if not isinstance(value, list):
                            errors.append(f"Field {field_name} must be a list")
                            continue
                except (ValueError, TypeError):
                    errors.append(
                        f"Field {field_name} must be of type "
                        f"{field_schema.field_type.__name__}"
                    )
                    continue

            value = config_data[field_name]  # Get potentially converted value

            # Range validation
            if field_schema.min_value is not None and isinstance(value, (int, float)):
                if value < field_schema.min_value:
                    errors.append(
                        f"Field {field_name} must be >= {field_schema.min_value}"
                    )

            if field_schema.max_value is not None and isinstance(value, (int, float)):
                if value > field_schema.max_value:
                    errors.append(
                        f"Field {field_name} must be <= {field_schema.max_value}"
                    )

            # Allowed values validation
            if field_schema.allowed_values and value not in field_schema.allowed_values:
                errors.append(
                    f"Field {field_name} must be one of: "
                    f"{', '.join(map(str, field_schema.allowed_values))}"
                )

            # Pattern validation (for strings)
            if field_schema.validation_pattern and isinstance(value, str):
                import re

                if not re.match(field_schema.validation_pattern, value):
                    errors.append(f"Field {field_name} does not match required pattern")

        return errors

    def save_config(self, config_name: str, config_data: Dict[str, Any]) -> None:
        """Save configuration with validation and encryption."""
        # Validate configuration
        errors = self.validate_config(config_name, config_data.copy())
        if errors:
            raise SecurityError(f"Configuration validation failed: {'; '.join(errors)}")

        # Get schema for encryption info
        schema = self.schemas.get(config_name, [])
        sensitive_fields = {s.field_name for s in schema if s.sensitive}

        # Prepare data for storage
        storage_data = {}
        for key, value in config_data.items():
            if key in sensitive_fields:
                # Encrypt sensitive values
                storage_data[key] = {
                    "encrypted": True,
                    "value": self._encrypt_value(str(value)),
                }
            else:
                storage_data[key] = {"encrypted": False, "value": value}

        # Add metadata
        storage_data["_metadata"] = {
            "schema_name": config_name,
            "created_at": time.time(),
            "version": "1.0",
        }

        # Save to file
        config_file = self.config_dir / f"{config_name}.json"

        try:
            with open(config_file, "w") as f:
                json.dump(storage_data, f, indent=2)

            # Set restrictive permissions
            os.chmod(config_file, 0o600)

            # Update cache
            self._config_cache[config_name] = config_data.copy()

            self.security_manager.log_security_event(
                SecurityEvent(
                    event_type="config_saved",
                    severity="low",
                    message=f"Configuration saved: {config_name}",
                    metadata={
                        "config_name": config_name,
                        "file_path": str(config_file),
                        "sensitive_fields_count": len(sensitive_fields),
                    },
                )
            )

        except Exception as e:
            raise SecurityError(f"Failed to save configuration: {str(e)}")

    def load_config(self, config_name: str) -> Dict[str, Any]:
        """Load configuration with decryption."""
        # Check cache first
        if config_name in self._config_cache:
            return self._config_cache[config_name].copy()

        config_file = self.config_dir / f"{config_name}.json"

        if not config_file.exists():
            # Return default configuration if schema exists
            if config_name in self.schemas:
                default_config = {}
                for field_schema in self.schemas[config_name]:
                    if field_schema.default_value is not None:
                        default_config[field_schema.field_name] = (
                            field_schema.default_value
                        )
                return default_config
            else:
                raise SecurityError(f"Configuration file not found: {config_name}")

        try:
            with open(config_file, "r") as f:
                storage_data = json.load(f)

            # Extract actual configuration data
            config_data = {}
            for key, value_info in storage_data.items():
                if key.startswith("_"):  # Skip metadata
                    continue

                if isinstance(value_info, dict) and "encrypted" in value_info:
                    if value_info["encrypted"]:
                        # Decrypt sensitive value
                        config_data[key] = self._decrypt_value(value_info["value"])
                    else:
                        config_data[key] = value_info["value"]
                else:
                    # Legacy format or direct value
                    config_data[key] = value_info

            # Validate loaded configuration
            errors = self.validate_config(config_name, config_data.copy())
            if errors:
                self.security_manager.log_security_event(
                    SecurityEvent(
                        event_type="config_validation_failed",
                        severity="medium",
                        message=(
                            f"Loaded configuration failed validation: " f"{config_name}"
                        ),
                        metadata={"config_name": config_name, "errors": errors},
                    )
                )
                # Continue with invalid config but log the issue

            # Cache the configuration
            self._config_cache[config_name] = config_data.copy()

            return config_data

        except Exception as e:
            raise SecurityError(f"Failed to load configuration: {str(e)}")

    def get_config_value(
        self, config_name: str, field_name: str, default: Any = None
    ) -> Any:
        """Get a specific configuration value."""
        try:
            config = self.load_config(config_name)
            return config.get(field_name, default)
        except SecurityError:
            return default

    def set_config_value(self, config_name: str, field_name: str, value: Any) -> None:
        """Set a specific configuration value."""
        try:
            config = self.load_config(config_name)
        except SecurityError:
            config = {}

        config[field_name] = value
        self.save_config(config_name, config)

    def delete_config(self, config_name: str) -> None:
        """Delete a configuration file."""
        config_file = self.config_dir / f"{config_name}.json"

        if config_file.exists():
            config_file.unlink()

            # Remove from cache
            if config_name in self._config_cache:
                del self._config_cache[config_name]

            self.security_manager.log_security_event(
                SecurityEvent(
                    event_type="config_deleted",
                    severity="medium",
                    message=f"Configuration deleted: {config_name}",
                    metadata={"config_name": config_name},
                )
            )

    def list_configs(self) -> List[str]:
        """List available configuration files."""
        config_files = []
        for file_path in self.config_dir.glob("*.json"):
            if not file_path.name.startswith("."):
                config_files.append(file_path.stem)
        return sorted(config_files)

    def export_config(
        self, config_name: str, include_sensitive: bool = False
    ) -> Dict[str, Any]:
        """Export configuration (optionally excluding sensitive data)."""
        config = self.load_config(config_name)

        if not include_sensitive:
            # Remove sensitive fields
            schema = self.schemas.get(config_name, [])
            sensitive_fields = {s.field_name for s in schema if s.sensitive}

            filtered_config = {}
            for key, value in config.items():
                if key not in sensitive_fields:
                    filtered_config[key] = value
                else:
                    filtered_config[key] = "***REDACTED***"

            return filtered_config

        return config

    def backup_configs(self, backup_dir: Optional[str] = None) -> str:
        """Create a backup of all configuration files."""
        if backup_dir is None:
            backup_dir_path = self.config_dir / "backups"
        else:
            backup_dir_path = Path(backup_dir)

        backup_dir_path.mkdir(parents=True, exist_ok=True)

        timestamp = int(time.time())
        backup_file = backup_dir_path / f"config_backup_{timestamp}.tar.gz"

        # Create tar.gz backup
        import tarfile

        with tarfile.open(backup_file, "w:gz") as tar:
            for config_file in self.config_dir.glob("*.json"):
                if not config_file.name.startswith("."):
                    tar.add(config_file, arcname=config_file.name)

        self.security_manager.log_security_event(
            SecurityEvent(
                event_type="config_backup_created",
                severity="low",
                message="Configuration backup created",
                metadata={
                    "backup_file": str(backup_file),
                    "config_count": len(list(self.config_dir.glob("*.json"))),
                },
            )
        )

        return str(backup_file)

    def get_schema_info(self, config_name: str) -> Dict[str, Any]:
        """Get schema information for a configuration."""
        if config_name not in self.schemas:
            return {}

        schema_info: Dict[str, Any] = {
            "fields": [],
            "required_fields": [],
            "sensitive_fields": [],
        }

        for field_schema in self.schemas[config_name]:
            field_info = {
                "name": field_schema.field_name,
                "type": field_schema.field_type.__name__,
                "required": field_schema.required,
                "sensitive": field_schema.sensitive,
                "description": field_schema.description,
                "default_value": field_schema.default_value,
            }

            if field_schema.allowed_values:
                field_info["allowed_values"] = list(field_schema.allowed_values)

            if field_schema.min_value is not None:
                field_info["min_value"] = field_schema.min_value

            if field_schema.max_value is not None:
                field_info["max_value"] = field_schema.max_value

            schema_info["fields"].append(field_info)

            if field_schema.required:
                schema_info["required_fields"].append(field_schema.field_name)

            if field_schema.sensitive:
                schema_info["sensitive_fields"].append(field_schema.field_name)

        return schema_info


# Global configuration manager
_config_manager: Optional[SecureConfigManager] = None


def get_config_manager(config_dir: Optional[str] = None) -> SecureConfigManager:
    """Return or create global configuration manager."""
    global _config_manager
    if _config_manager is None or config_dir:
        _config_manager = SecureConfigManager(config_dir or ".lackey/config")
    return _config_manager


def get_config(config_name: str, field_name: str, default: Any = None) -> Any:
    """Return a configuration value."""
    manager = get_config_manager()
    return manager.get_config_value(config_name, field_name, default)


def set_config(config_name: str, field_name: str, value: Any) -> None:
    """Set a configuration value."""
    manager = get_config_manager()
    manager.set_config_value(config_name, field_name, value)

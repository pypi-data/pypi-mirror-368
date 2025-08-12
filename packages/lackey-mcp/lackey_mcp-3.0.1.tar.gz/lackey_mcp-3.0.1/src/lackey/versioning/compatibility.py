"""API compatibility checking for Lackey."""

from typing import List, Optional

from lackey import API_COMPATIBILITY_MATRIX, __version__


def get_supported_api_versions(package_version: Optional[str] = None) -> List[str]:
    """Get list of API versions supported by a package version.

    Args:
        package_version: Package version to check. If None, uses current version.

    Returns:
        List of supported API versions in semantic versioning format.
    """
    if package_version is None:
        package_version = __version__

    return list(API_COMPATIBILITY_MATRIX.get(package_version, []))


def check_api_compatibility(
    client_api_version: str, server_package_version: Optional[str] = None
) -> bool:
    """Check if a client API version is compatible with server package version.

    Args:
        client_api_version: API version the client expects (e.g., "1.0.0")
        server_package_version: Server package version. If None, uses current version.

    Returns:
        True if compatible, False otherwise.
    """
    if server_package_version is None:
        server_package_version = __version__

    supported_versions = get_supported_api_versions(server_package_version)
    return client_api_version in supported_versions


def get_compatibility_info(package_version: Optional[str] = None) -> dict:
    """Get detailed compatibility information for a package version.

    Args:
        package_version: Package version to check. If None, uses current version.

    Returns:
        Dictionary with compatibility information.
    """
    if package_version is None:
        package_version = __version__

    supported_apis = get_supported_api_versions(package_version)

    return {
        "package_version": package_version,
        "supported_api_versions": supported_apis,
        "backward_compatible": len(supported_apis) > 1,
        "latest_api_version": max(supported_apis) if supported_apis else None,
    }


def validate_version_compatibility(
    required_api_version: str, available_package_version: Optional[str] = None
) -> dict:
    """Validate version compatibility and provide detailed feedback.

    Args:
        required_api_version: API version required by client
        available_package_version: Available package version. If None, uses current.

    Returns:
        Dictionary with validation results and recommendations.
    """
    if available_package_version is None:
        available_package_version = __version__

    is_compatible = check_api_compatibility(
        required_api_version, available_package_version
    )
    supported_versions = get_supported_api_versions(available_package_version)

    result = {
        "compatible": is_compatible,
        "required_api_version": required_api_version,
        "available_package_version": available_package_version,
        "supported_api_versions": supported_versions,
    }

    if not is_compatible:
        if supported_versions:
            latest_supported = max(supported_versions)
            if required_api_version < latest_supported:
                result["recommendation"] = (
                    f"Client API version {required_api_version} is outdated. "
                    f"Consider upgrading to {latest_supported}."
                )
            else:
                result["recommendation"] = (
                    f"Client requires API version {required_api_version}, "
                    f"but server only supports {supported_versions}. "
                    f"Server upgrade needed."
                )
        else:
            result["recommendation"] = (
                f"No API version information available for package version "
                f"{available_package_version}."
            )
    else:
        result["recommendation"] = "Versions are compatible."

    return result

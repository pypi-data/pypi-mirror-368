"""Authentication and authorization framework for Lackey.

This module provides comprehensive authentication and authorization capabilities
including user management, role-based access control, session management,
and API key authentication.
"""

import hashlib
import secrets
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from lackey.security import SecurityError, SecurityEvent, get_security_manager


class AuthMethod(Enum):
    """Authentication method types."""

    PASSWORD = "password"  # nosec B105
    API_KEY = "api_key"
    TOKEN = "token"  # nosec B105
    CERTIFICATE = "certificate"


class Role(Enum):
    """User role definitions."""

    ADMIN = "admin"
    MANAGER = "manager"
    DEVELOPER = "developer"
    VIEWER = "viewer"
    GUEST = "guest"


class Permission(Enum):
    """Permission types for authorization."""

    # Project permissions
    PROJECT_CREATE = "project:create"
    PROJECT_READ = "project:read"
    PROJECT_UPDATE = "project:update"
    PROJECT_DELETE = "project:delete"
    PROJECT_ARCHIVE = "project:archive"

    # Task permissions
    TASK_CREATE = "task:create"
    TASK_READ = "task:read"
    TASK_UPDATE = "task:update"
    TASK_DELETE = "task:delete"
    TASK_ASSIGN = "task:assign"
    TASK_COMPLETE = "task:complete"

    # Note permissions
    NOTE_CREATE = "note:create"
    NOTE_READ = "note:read"
    NOTE_UPDATE = "note:update"
    NOTE_DELETE = "note:delete"

    # System permissions
    SYSTEM_ADMIN = "system:admin"
    SYSTEM_CONFIG = "system:config"
    SYSTEM_LOGS = "system:logs"
    SYSTEM_USERS = "system:users"

    # Bulk operations
    BULK_OPERATIONS = "bulk:operations"

    # Advanced features
    DEPENDENCIES_MANAGE = "dependencies:manage"
    WORKFLOW_MANAGE = "workflow:manage"


@dataclass
class User:
    """User account information."""

    id: str
    username: str
    email: str
    password_hash: str
    salt: str
    role: Role
    permissions: Set[Permission] = field(default_factory=set)

    # Account status
    is_active: bool = True
    is_verified: bool = False
    is_locked: bool = False

    # Timestamps
    created_at: float = field(default_factory=time.time)
    last_login: Optional[float] = None
    last_activity: Optional[float] = None
    password_changed_at: float = field(default_factory=time.time)

    # Security settings
    failed_login_attempts: int = 0
    lockout_until: Optional[float] = None
    require_password_change: bool = False

    # API keys
    api_keys: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary (excluding sensitive data)."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role.value,
            "permissions": [p.value for p in self.permissions],
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "is_locked": self.is_locked,
            "created_at": self.created_at,
            "last_login": self.last_login,
            "last_activity": self.last_activity,
            "api_key_count": len(self.api_keys),
            "metadata": self.metadata,
        }


@dataclass
class Session:
    """User session information."""

    id: str
    user_id: str
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    expires_at: float = field(default_factory=lambda: time.time() + 3600)  # 1 hour

    # Session metadata
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    auth_method: AuthMethod = AuthMethod.PASSWORD

    # Security flags
    is_valid: bool = True
    is_elevated: bool = False  # For sensitive operations

    def is_expired(self) -> bool:
        """Check if session is expired."""
        return time.time() > self.expires_at

    def refresh(self, extend_minutes: int = 60) -> None:
        """Refresh session expiration."""
        self.last_activity = time.time()
        self.expires_at = time.time() + (extend_minutes * 60)


@dataclass
class ApiKey:
    """API key for programmatic access."""

    id: str
    user_id: str
    name: str
    key_hash: str
    permissions: Set[Permission] = field(default_factory=set)

    # Status
    is_active: bool = True

    # Timestamps
    created_at: float = field(default_factory=time.time)
    last_used: Optional[float] = None
    expires_at: Optional[float] = None

    # Usage tracking
    usage_count: int = 0
    rate_limit_override: Optional[int] = None

    # Restrictions
    allowed_ips: Set[str] = field(default_factory=set)
    allowed_endpoints: Set[str] = field(default_factory=set)

    def is_expired(self) -> bool:
        """Check if API key is expired."""
        return self.expires_at is not None and time.time() > self.expires_at

    def is_ip_allowed(self, ip_address: str) -> bool:
        """Check if IP address is allowed for this API key."""
        return not self.allowed_ips or ip_address in self.allowed_ips

    def is_endpoint_allowed(self, endpoint: str) -> bool:
        """Check if endpoint is allowed for this API key."""
        return not self.allowed_endpoints or endpoint in self.allowed_endpoints


class AuthenticationManager:
    """Manages user authentication and session handling."""

    def __init__(self) -> None:
        """Initialize authentication manager."""
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Session] = {}
        self.api_keys: Dict[str, ApiKey] = {}
        self.security_manager = get_security_manager()

        # Configuration
        self.session_timeout_minutes = 60
        self.max_failed_attempts = 5
        self.lockout_duration_minutes = 30
        self.password_min_length = 8
        self.require_password_complexity = True

        # Initialize default roles and permissions
        self._setup_role_permissions()

    def _setup_role_permissions(self) -> None:
        """Set up default role permissions."""
        self.role_permissions = {
            Role.ADMIN: {
                Permission.PROJECT_CREATE,
                Permission.PROJECT_READ,
                Permission.PROJECT_UPDATE,
                Permission.PROJECT_DELETE,
                Permission.PROJECT_ARCHIVE,
                Permission.TASK_CREATE,
                Permission.TASK_READ,
                Permission.TASK_UPDATE,
                Permission.TASK_DELETE,
                Permission.TASK_ASSIGN,
                Permission.TASK_COMPLETE,
                Permission.NOTE_CREATE,
                Permission.NOTE_READ,
                Permission.NOTE_UPDATE,
                Permission.NOTE_DELETE,
                Permission.SYSTEM_ADMIN,
                Permission.SYSTEM_CONFIG,
                Permission.SYSTEM_LOGS,
                Permission.SYSTEM_USERS,
                Permission.BULK_OPERATIONS,
                Permission.DEPENDENCIES_MANAGE,
                Permission.WORKFLOW_MANAGE,
            },
            Role.MANAGER: {
                Permission.PROJECT_CREATE,
                Permission.PROJECT_READ,
                Permission.PROJECT_UPDATE,
                Permission.PROJECT_ARCHIVE,
                Permission.TASK_CREATE,
                Permission.TASK_READ,
                Permission.TASK_UPDATE,
                Permission.TASK_ASSIGN,
                Permission.TASK_COMPLETE,
                Permission.NOTE_CREATE,
                Permission.NOTE_READ,
                Permission.NOTE_UPDATE,
                Permission.BULK_OPERATIONS,
                Permission.DEPENDENCIES_MANAGE,
                Permission.WORKFLOW_MANAGE,
            },
            Role.DEVELOPER: {
                Permission.PROJECT_READ,
                Permission.TASK_CREATE,
                Permission.TASK_READ,
                Permission.TASK_UPDATE,
                Permission.TASK_COMPLETE,
                Permission.NOTE_CREATE,
                Permission.NOTE_READ,
                Permission.NOTE_UPDATE,
                Permission.DEPENDENCIES_MANAGE,
            },
            Role.VIEWER: {
                Permission.PROJECT_READ,
                Permission.TASK_READ,
                Permission.NOTE_READ,
            },
            Role.GUEST: {Permission.PROJECT_READ, Permission.TASK_READ},
        }

    def create_user(
        self, username: str, email: str, password: str, role: Role = Role.DEVELOPER
    ) -> User:
        """Create a new user account."""
        # Validate input
        if not username or len(username) < 3:
            raise SecurityError("Username must be at least 3 characters long")

        if not email or "@" not in email:
            raise SecurityError("Valid email address required")

        if not self._validate_password(password):
            raise SecurityError("Password does not meet complexity requirements")

        # Check for existing user
        for user in self.users.values():
            if user.username == username:
                raise SecurityError("Username already exists")
            if user.email == email:
                raise SecurityError("Email already registered")

        # Create user
        user_id = secrets.token_urlsafe(16)
        password_hash, salt = self.security_manager.hash_password(password)

        user = User(
            id=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            salt=salt,
            role=role,
            permissions=self.role_permissions.get(role, set()).copy(),
        )

        self.users[user_id] = user

        # Log user creation
        self.security_manager.log_security_event(
            SecurityEvent(
                event_type="user_created",
                severity="low",
                message=f"User account created: {username}",
                metadata={
                    "user_id": user_id,
                    "username": username,
                    "role": role.value,
                },
            )
        )

        return user

    def authenticate_user(
        self, username: str, password: str, ip_address: Optional[str] = None
    ) -> Optional[User]:
        """Authenticate user with username and password."""
        # Find user
        user = None
        for u in self.users.values():
            if u.username == username:
                user = u
                break

        if not user:
            self._log_failed_login(username, "User not found", ip_address)
            return None

        # Check if account is locked
        if user.is_locked or (user.lockout_until and time.time() < user.lockout_until):
            self._log_failed_login(username, "Account locked", ip_address)
            return None

        # Check if account is active
        if not user.is_active:
            self._log_failed_login(username, "Account inactive", ip_address)
            return None

        # Verify password
        if not self.security_manager.verify_password(
            password, user.password_hash, user.salt
        ):
            user.failed_login_attempts += 1

            # Lock account if too many failed attempts
            if user.failed_login_attempts >= self.max_failed_attempts:
                user.is_locked = True
                user.lockout_until = time.time() + (self.lockout_duration_minutes * 60)

                self.security_manager.log_security_event(
                    SecurityEvent(
                        event_type="account_locked",
                        severity="high",
                        message=f"Account locked due to failed login attempts: "
                        f"{username}",
                        metadata={
                            "user_id": user.id,
                            "username": username,
                            "failed_attempts": user.failed_login_attempts,
                            "ip_address": ip_address,
                        },
                    )
                )

            self._log_failed_login(username, "Invalid password", ip_address)
            return None

        # Successful authentication
        user.failed_login_attempts = 0
        user.last_login = time.time()
        user.last_activity = time.time()

        self.security_manager.log_security_event(
            SecurityEvent(
                event_type="user_authenticated",
                severity="low",
                message=f"User successfully authenticated: {username}",
                metadata={
                    "user_id": user.id,
                    "username": username,
                    "ip_address": ip_address,
                },
            )
        )

        return user

    def create_session(
        self,
        user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Session:
        """Create a new user session."""
        session_id = secrets.token_urlsafe(32)

        session = Session(
            id=session_id,
            user_id=user.id,
            expires_at=time.time() + (self.session_timeout_minutes * 60),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self.sessions[session_id] = session

        # Clean up expired sessions
        self._cleanup_expired_sessions()

        return session

    def validate_session(self, session_id: str) -> Optional[User]:
        """Validate session and return associated user."""
        session = self.sessions.get(session_id)

        if not session or not session.is_valid or session.is_expired():
            if session:
                del self.sessions[session_id]
            return None

        # Get user
        user = self.users.get(session.user_id)
        if not user or not user.is_active:
            del self.sessions[session_id]
            return None

        # Refresh session
        session.refresh()
        user.last_activity = time.time()

        return user

    def create_api_key(
        self,
        user: User,
        name: str,
        permissions: Optional[Set[Permission]] = None,
        expires_days: Optional[int] = None,
    ) -> Tuple[str, ApiKey]:
        """Create a new API key for user."""
        # Generate API key
        api_key_value = f"lk_{secrets.token_urlsafe(32)}"
        api_key_hash = hashlib.sha256(api_key_value.encode()).hexdigest()

        # Set permissions (default to user's permissions)
        if permissions is None:
            permissions = user.permissions.copy()
        else:
            # Ensure user has the permissions they're granting
            if not permissions.issubset(user.permissions):
                raise SecurityError("Cannot grant permissions user doesn't have")

        # Set expiration
        expires_at = None
        if expires_days:
            expires_at = time.time() + (expires_days * 24 * 3600)

        api_key = ApiKey(
            id=secrets.token_urlsafe(16),
            user_id=user.id,
            name=name,
            key_hash=api_key_hash,
            permissions=permissions,
            expires_at=expires_at,
        )

        self.api_keys[api_key.id] = api_key
        user.api_keys[api_key.id] = {
            "name": name,
            "created_at": api_key.created_at,
            "last_used": api_key.last_used,
        }

        self.security_manager.log_security_event(
            SecurityEvent(
                event_type="api_key_created",
                severity="medium",
                message=f"API key created for user: {user.username}",
                metadata={
                    "user_id": user.id,
                    "api_key_id": api_key.id,
                    "api_key_name": name,
                    "permissions_count": len(permissions),
                },
            )
        )

        return api_key_value, api_key

    def authenticate_api_key(
        self,
        api_key_value: str,
        endpoint: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> Optional[Tuple[User, ApiKey]]:
        """Authenticate using API key."""
        if not api_key_value.startswith("lk_"):
            return None

        api_key_hash = hashlib.sha256(api_key_value.encode()).hexdigest()

        # Find API key
        api_key = None
        for key in self.api_keys.values():
            if key.key_hash == api_key_hash:
                api_key = key
                break

        if not api_key:
            self.security_manager.log_security_event(
                SecurityEvent(
                    event_type="api_key_authentication_failed",
                    severity="medium",
                    message="Invalid API key used",
                    metadata={"endpoint": endpoint, "ip_address": ip_address},
                )
            )
            return None

        # Check if API key is active and not expired
        if not api_key.is_active or api_key.is_expired():
            return None

        # Check IP restrictions
        if ip_address and not api_key.is_ip_allowed(ip_address):
            self.security_manager.log_security_event(
                SecurityEvent(
                    event_type="api_key_ip_violation",
                    severity="high",
                    message=f"API key used from unauthorized IP: {ip_address}",
                    metadata={
                        "api_key_id": api_key.id,
                        "ip_address": ip_address,
                        "allowed_ips": list(api_key.allowed_ips),
                    },
                )
            )
            return None

        # Check endpoint restrictions
        if endpoint and not api_key.is_endpoint_allowed(endpoint):
            return None

        # Get user
        user = self.users.get(api_key.user_id)
        if not user or not user.is_active:
            return None

        # Update usage
        api_key.last_used = time.time()
        api_key.usage_count += 1
        user.last_activity = time.time()

        return user, api_key

    def _validate_password(self, password: str) -> bool:
        """Validate password complexity."""
        if len(password) < self.password_min_length:
            return False

        if not self.require_password_complexity:
            return True

        # Check complexity requirements
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

        return has_upper and has_lower and has_digit and has_special

    def _log_failed_login(
        self, username: str, reason: str, ip_address: Optional[str]
    ) -> None:
        """Log failed login attempt."""
        self.security_manager.log_security_event(
            SecurityEvent(
                event_type="login_failed",
                severity="medium",
                message=f"Failed login attempt: {reason}",
                metadata={
                    "username": username,
                    "reason": reason,
                    "ip_address": ip_address,
                },
            )
        )

    def _cleanup_expired_sessions(self) -> None:
        """Clean up expired sessions."""
        expired_sessions = [
            session_id
            for session_id, session in self.sessions.items()
            if session.is_expired()
        ]

        for session_id in expired_sessions:
            del self.sessions[session_id]


class AuthorizationManager:
    """Manages user authorization and permissions."""

    def __init__(self, auth_manager: AuthenticationManager):
        """Initialize authorization manager."""
        self.auth_manager = auth_manager
        self.security_manager = get_security_manager()

    def check_permission(
        self, user: User, permission: Permission, resource_id: Optional[str] = None
    ) -> bool:
        """Check if user has specific permission."""
        # Check if user is active
        if not user.is_active:
            return False

        # Admin users have all permissions
        if user.role == Role.ADMIN:
            return True

        # Check user's permissions
        has_permission = permission in user.permissions

        # Log authorization check
        self.security_manager.log_security_event(
            SecurityEvent(
                event_type="authorization_check",
                severity="low",
                message=f"Permission check: {permission.value}",
                metadata={
                    "user_id": user.id,
                    "username": user.username,
                    "permission": permission.value,
                    "granted": has_permission,
                    "resource_id": resource_id,
                },
            )
        )

        return has_permission

    def require_permission(
        self, user: User, permission: Permission, resource_id: Optional[str] = None
    ) -> None:
        """Require user to have specific permission (raises exception if not)."""
        if not self.check_permission(user, permission, resource_id):
            self.security_manager.log_security_event(
                SecurityEvent(
                    event_type="authorization_denied",
                    severity="medium",
                    message="Access denied: insufficient permissions",
                    metadata={
                        "user_id": user.id,
                        "username": user.username,
                        "required_permission": permission.value,
                        "resource_id": resource_id,
                    },
                )
            )

            raise SecurityError(
                f"Access denied: {permission.value} permission required"
            )

    def check_multiple_permissions(
        self, user: User, permissions: List[Permission], require_all: bool = True
    ) -> bool:
        """Check multiple permissions (AND or OR logic)."""
        if require_all:
            return all(self.check_permission(user, perm) for perm in permissions)
        else:
            return any(self.check_permission(user, perm) for perm in permissions)


# Global instances
_auth_manager: Optional[AuthenticationManager] = None
_authz_manager: Optional[AuthorizationManager] = None


def get_auth_manager() -> AuthenticationManager:
    """Get or create global authentication manager."""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthenticationManager()
    return _auth_manager


def get_authz_manager() -> AuthorizationManager:
    """Get or create global authorization manager."""
    global _authz_manager
    if _authz_manager is None:
        _authz_manager = AuthorizationManager(get_auth_manager())
    return _authz_manager


def require_auth(permission: Optional[Permission] = None) -> Callable:
    """Require authentication and optional permission."""

    def decorator(func: Callable) -> Callable:
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Extract authentication info from kwargs or context
            # This would need to be adapted based on how MCP passes auth info
            auth_token = kwargs.get("auth_token") or kwargs.get("session_id")
            api_key = kwargs.get("api_key")

            auth_manager = get_auth_manager()
            authz_manager = get_authz_manager()

            user = None

            # Try API key authentication first
            if api_key:
                result = auth_manager.authenticate_api_key(api_key, func.__name__)
                if result:
                    user, _ = result

            # Try session authentication
            elif auth_token:
                user = auth_manager.validate_session(auth_token)

            if not user:
                raise SecurityError("Authentication required")

            # Check permission if specified
            if permission:
                authz_manager.require_permission(user, permission)

            # Add user to kwargs for the function
            kwargs["current_user"] = user

            return await func(*args, **kwargs)

        return wrapper

    return decorator

"""Advanced rate limiting system for Lackey MCP server endpoints.

This module provides sophisticated rate limiting with multiple algorithms,
adaptive limits, and comprehensive monitoring capabilities.
"""

import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Optional, Set, Tuple

from lackey.security import SecurityError, SecurityEvent, get_security_manager


class RateLimitAlgorithm(Enum):
    """Rate limiting algorithm types."""

    TOKEN_BUCKET = "token_bucket"  # nosec B105
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    ADAPTIVE = "adaptive"


class RateLimitScope(Enum):
    """Rate limit scope definitions."""

    GLOBAL = "global"
    PER_IP = "per_ip"
    PER_USER = "per_user"
    PER_ENDPOINT = "per_endpoint"
    PER_IP_ENDPOINT = "per_ip_endpoint"


@dataclass
class RateLimitRule:
    """Rate limiting rule configuration."""

    # Basic configuration
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000

    # Burst configuration
    burst_size: int = 10
    burst_window_seconds: int = 60

    # Algorithm and scope
    algorithm: RateLimitAlgorithm = RateLimitAlgorithm.SLIDING_WINDOW
    scope: RateLimitScope = RateLimitScope.PER_IP

    # Adaptive settings
    adaptive_increase_factor: float = 1.1
    adaptive_decrease_factor: float = 0.9
    adaptive_min_limit: int = 10
    adaptive_max_limit: int = 1000

    # Penalty settings
    violation_penalty_minutes: int = 15
    max_violations_before_ban: int = 5
    ban_duration_hours: int = 24

    # Whitelist/blacklist
    whitelisted_ips: Set[str] = field(default_factory=set)
    blacklisted_ips: Set[str] = field(default_factory=set)

    # Description
    description: str = ""


@dataclass
class RateLimitState:
    """Current state for rate limiting."""

    # Request tracking
    request_timestamps: deque = field(default_factory=deque)
    token_bucket_tokens: float = 0.0
    token_bucket_last_refill: float = 0.0

    # Violation tracking
    violation_count: int = 0
    last_violation_time: float = 0.0
    penalty_end_time: float = 0.0
    ban_end_time: float = 0.0

    # Adaptive limits
    current_limit: Optional[int] = None
    success_streak: int = 0
    failure_streak: int = 0

    # Statistics
    total_requests: int = 0
    total_violations: int = 0
    last_request_time: float = 0.0


class RateLimiter:
    """Advanced rate limiter with multiple algorithms and adaptive behavior."""

    def __init__(self, rule: RateLimitRule):
        """Initialize rate limiter with rule configuration."""
        self.rule = rule
        self.states: Dict[str, RateLimitState] = defaultdict(RateLimitState)
        self.security_manager = get_security_manager()

        # Initialize adaptive limits
        for state in self.states.values():
            if state.current_limit is None:
                state.current_limit = rule.requests_per_minute

    def check_rate_limit(
        self, identifier: str, endpoint: str = ""
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check if request is within rate limits.

        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        current_time = time.time()

        # Create composite key based on scope
        key = self._create_rate_limit_key(identifier, endpoint)
        state = self.states[key]

        # Check blacklist
        if identifier in self.rule.blacklisted_ips:
            return False, self._create_rate_limit_info(state, "blacklisted")

        # Check whitelist
        if identifier in self.rule.whitelisted_ips:
            return True, self._create_rate_limit_info(state, "whitelisted")

        # Check if currently banned
        if current_time < state.ban_end_time:
            return False, self._create_rate_limit_info(state, "banned")

        # Check if in penalty period
        if current_time < state.penalty_end_time:
            return False, self._create_rate_limit_info(state, "penalty")

        # Apply rate limiting algorithm
        is_allowed = self._apply_rate_limit_algorithm(state, current_time)

        # Update statistics
        state.total_requests += 1
        state.last_request_time = current_time

        if is_allowed:
            state.success_streak += 1
            state.failure_streak = 0

            # Adaptive increase if enabled
            if self.rule.algorithm == RateLimitAlgorithm.ADAPTIVE:
                self._adapt_limit_increase(state)
        else:
            state.failure_streak += 1
            state.success_streak = 0
            state.total_violations += 1

            # Handle violation
            self._handle_rate_limit_violation(state, current_time, identifier, endpoint)

            # Adaptive decrease if enabled
            if self.rule.algorithm == RateLimitAlgorithm.ADAPTIVE:
                self._adapt_limit_decrease(state)

        return is_allowed, self._create_rate_limit_info(state, "checked")

    def _create_rate_limit_key(self, identifier: str, endpoint: str) -> str:
        """Create rate limit key based on scope."""
        if self.rule.scope == RateLimitScope.GLOBAL:
            return "global"
        elif self.rule.scope == RateLimitScope.PER_IP:
            return f"ip:{identifier}"
        elif self.rule.scope == RateLimitScope.PER_USER:
            return f"user:{identifier}"
        elif self.rule.scope == RateLimitScope.PER_ENDPOINT:
            return f"endpoint:{endpoint}"
        elif self.rule.scope == RateLimitScope.PER_IP_ENDPOINT:
            return f"ip_endpoint:{identifier}:{endpoint}"

    def _apply_rate_limit_algorithm(
        self, state: RateLimitState, current_time: float
    ) -> bool:
        """Apply the configured rate limiting algorithm."""
        if self.rule.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
            return self._token_bucket_check(state, current_time)
        elif self.rule.algorithm == RateLimitAlgorithm.SLIDING_WINDOW:
            return self._sliding_window_check(state, current_time)
        elif self.rule.algorithm == RateLimitAlgorithm.FIXED_WINDOW:
            return self._fixed_window_check(state, current_time)
        elif self.rule.algorithm == RateLimitAlgorithm.ADAPTIVE:
            return self._adaptive_check(state, current_time)

    def _token_bucket_check(self, state: RateLimitState, current_time: float) -> bool:
        """Token bucket rate limiting algorithm."""
        # Initialize bucket if needed
        if state.token_bucket_last_refill == 0:
            state.token_bucket_tokens = self.rule.burst_size
            state.token_bucket_last_refill = current_time

        # Calculate tokens to add
        time_passed = current_time - state.token_bucket_last_refill
        tokens_to_add = time_passed * (self.rule.requests_per_minute / 60.0)

        # Refill bucket
        state.token_bucket_tokens = min(
            self.rule.burst_size, state.token_bucket_tokens + tokens_to_add
        )
        state.token_bucket_last_refill = current_time

        # Check if token available
        if state.token_bucket_tokens >= 1.0:
            state.token_bucket_tokens -= 1.0
            return True

        return False

    def _sliding_window_check(self, state: RateLimitState, current_time: float) -> bool:
        """Sliding window rate limiting algorithm."""
        # Clean old timestamps
        window_start = current_time - 60  # 1 minute window
        while state.request_timestamps and state.request_timestamps[0] < window_start:
            state.request_timestamps.popleft()

        # Check current limit
        current_limit = state.current_limit or self.rule.requests_per_minute

        if len(state.request_timestamps) < current_limit:
            state.request_timestamps.append(current_time)
            return True

        return False

    def _fixed_window_check(self, state: RateLimitState, current_time: float) -> bool:
        """Check fixed window rate limiting algorithm."""
        # Calculate current window
        window_start = int(current_time / 60) * 60  # 1-minute windows

        # Clean timestamps from previous windows
        state.request_timestamps = deque(
            [ts for ts in state.request_timestamps if ts >= window_start]
        )

        # Check limit
        current_limit = state.current_limit or self.rule.requests_per_minute

        if len(state.request_timestamps) < current_limit:
            state.request_timestamps.append(current_time)
            return True

        return False

    def _adaptive_check(self, state: RateLimitState, current_time: float) -> bool:
        """Adaptive rate limiting algorithm."""
        # Use sliding window as base algorithm
        return self._sliding_window_check(state, current_time)

    def _adapt_limit_increase(self, state: RateLimitState) -> None:
        """Increase rate limit adaptively."""
        if state.success_streak >= 10:  # Increase after 10 successful requests
            if state.current_limit is None:
                state.current_limit = self.rule.requests_per_minute

            new_limit = int(state.current_limit * self.rule.adaptive_increase_factor)
            state.current_limit = min(new_limit, self.rule.adaptive_max_limit)
            state.success_streak = 0  # Reset streak

    def _adapt_limit_decrease(self, state: RateLimitState) -> None:
        """Decrease rate limit adaptively."""
        if state.failure_streak >= 3:  # Decrease after 3 failures
            if state.current_limit is None:
                state.current_limit = self.rule.requests_per_minute

            new_limit = int(state.current_limit * self.rule.adaptive_decrease_factor)
            state.current_limit = max(new_limit, self.rule.adaptive_min_limit)
            state.failure_streak = 0  # Reset streak

    def _handle_rate_limit_violation(
        self, state: RateLimitState, current_time: float, identifier: str, endpoint: str
    ) -> None:
        """Handle rate limit violation with penalties."""
        state.violation_count += 1
        state.last_violation_time = current_time

        # Apply penalty
        state.penalty_end_time = current_time + (
            self.rule.violation_penalty_minutes * 60
        )

        # Check for ban
        if state.violation_count >= self.rule.max_violations_before_ban:
            state.ban_end_time = current_time + (self.rule.ban_duration_hours * 3600)

            # Log ban event
            self.security_manager.log_security_event(
                SecurityEvent(
                    event_type="rate_limit_ban_applied",
                    severity="high",
                    message=f"Rate limit ban applied to {identifier}",
                    metadata={
                        "identifier": identifier,
                        "endpoint": endpoint,
                        "violation_count": state.violation_count,
                        "ban_duration_hours": self.rule.ban_duration_hours,
                    },
                )
            )
        else:
            # Log violation
            self.security_manager.log_security_event(
                SecurityEvent(
                    event_type="rate_limit_violation",
                    severity="medium",
                    message=f"Rate limit violation for {identifier}",
                    metadata={
                        "identifier": identifier,
                        "endpoint": endpoint,
                        "violation_count": state.violation_count,
                        "penalty_minutes": self.rule.violation_penalty_minutes,
                    },
                )
            )

    def _create_rate_limit_info(
        self, state: RateLimitState, status: str
    ) -> Dict[str, Any]:
        """Create rate limit information dictionary."""
        current_time = time.time()
        current_limit = state.current_limit or self.rule.requests_per_minute

        # Calculate remaining requests
        window_start = current_time - 60
        recent_requests = sum(
            1 for ts in state.request_timestamps if ts >= window_start
        )
        remaining_requests = max(0, current_limit - recent_requests)

        # Calculate reset time
        if state.request_timestamps:
            oldest_in_window = min(
                ts for ts in state.request_timestamps if ts >= window_start
            )
            reset_time = oldest_in_window + 60
        else:
            reset_time = current_time + 60

        return {
            "status": status,
            "limit": current_limit,
            "remaining": remaining_requests,
            "reset_time": reset_time,
            "retry_after": max(0, state.penalty_end_time - current_time),
            "total_requests": state.total_requests,
            "total_violations": state.total_violations,
            "violation_count": state.violation_count,
            "is_banned": current_time < state.ban_end_time,
            "ban_end_time": (
                state.ban_end_time if state.ban_end_time > current_time else None
            ),
            "algorithm": self.rule.algorithm.value,
            "scope": self.rule.scope.value,
        }

    def reset_state(self, identifier: str, endpoint: str = "") -> None:
        """Reset rate limit state for identifier."""
        key = self._create_rate_limit_key(identifier, endpoint)
        if key in self.states:
            del self.states[key]

    def get_statistics(self) -> Dict[str, Any]:
        """Get rate limiter statistics."""
        current_time = time.time()

        total_identifiers = len(self.states)
        total_requests = sum(state.total_requests for state in self.states.values())
        total_violations = sum(state.total_violations for state in self.states.values())

        active_bans = sum(
            1 for state in self.states.values() if current_time < state.ban_end_time
        )

        active_penalties = sum(
            1 for state in self.states.values() if current_time < state.penalty_end_time
        )

        return {
            "total_identifiers": total_identifiers,
            "total_requests": total_requests,
            "total_violations": total_violations,
            "active_bans": active_bans,
            "active_penalties": active_penalties,
            "violation_rate": (
                (total_violations / total_requests * 100) if total_requests > 0 else 0
            ),
            "rule_description": self.rule.description,
            "algorithm": self.rule.algorithm.value,
            "scope": self.rule.scope.value,
        }


class RateLimitManager:
    """Manager for multiple rate limiters with different rules."""

    def __init__(self) -> None:
        """Initialize rate limit manager."""
        self.limiters: Dict[str, RateLimiter] = {}
        self.endpoint_rules: Dict[str, str] = {}  # endpoint -> rule_name mapping
        self.security_manager = get_security_manager()

        # Set up default rules
        self._setup_default_rules()

    def _setup_default_rules(self) -> None:
        """Set up default rate limiting rules."""
        # Default rule for most endpoints
        default_rule = RateLimitRule(
            requests_per_minute=60,
            requests_per_hour=1000,
            burst_size=10,
            algorithm=RateLimitAlgorithm.SLIDING_WINDOW,
            scope=RateLimitScope.PER_IP,
            description="Default rate limit for standard operations",
        )
        self.add_rule("default", default_rule)

        # Strict rule for sensitive operations
        strict_rule = RateLimitRule(
            requests_per_minute=10,
            requests_per_hour=100,
            burst_size=3,
            violation_penalty_minutes=30,
            max_violations_before_ban=3,
            algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
            scope=RateLimitScope.PER_IP,
            description="Strict rate limit for sensitive operations",
        )
        self.add_rule("strict", strict_rule)

        # Lenient rule for read-only operations
        lenient_rule = RateLimitRule(
            requests_per_minute=120,
            requests_per_hour=2000,
            burst_size=20,
            violation_penalty_minutes=5,
            algorithm=RateLimitAlgorithm.SLIDING_WINDOW,
            scope=RateLimitScope.PER_IP,
            description="Lenient rate limit for read-only operations",
        )
        self.add_rule("lenient", lenient_rule)

        # Adaptive rule for dynamic adjustment
        adaptive_rule = RateLimitRule(
            requests_per_minute=60,
            requests_per_hour=1000,
            burst_size=10,
            algorithm=RateLimitAlgorithm.ADAPTIVE,
            scope=RateLimitScope.PER_IP_ENDPOINT,
            adaptive_min_limit=10,
            adaptive_max_limit=200,
            description="Adaptive rate limit that adjusts based on behavior",
        )
        self.add_rule("adaptive", adaptive_rule)

    def add_rule(self, name: str, rule: RateLimitRule) -> None:
        """Add a rate limiting rule."""
        self.limiters[name] = RateLimiter(rule)

        self.security_manager.log_security_event(
            SecurityEvent(
                event_type="rate_limit_rule_added",
                severity="low",
                message=f"Rate limit rule added: {name}",
                metadata={
                    "rule_name": name,
                    "requests_per_minute": rule.requests_per_minute,
                    "algorithm": rule.algorithm.value,
                    "scope": rule.scope.value,
                },
            )
        )

    def assign_rule_to_endpoint(self, endpoint: str, rule_name: str) -> None:
        """Assign a rate limiting rule to an endpoint."""
        if rule_name not in self.limiters:
            raise ValueError(f"Rate limit rule '{rule_name}' not found")

        self.endpoint_rules[endpoint] = rule_name

    def check_rate_limit(
        self, identifier: str, endpoint: str = "", rule_name: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check rate limit for identifier and endpoint."""
        # Determine which rule to use
        if rule_name:
            limiter_name = rule_name
        elif endpoint in self.endpoint_rules:
            limiter_name = self.endpoint_rules[endpoint]
        else:
            limiter_name = "default"

        if limiter_name not in self.limiters:
            limiter_name = "default"

        limiter = self.limiters[limiter_name]
        return limiter.check_rate_limit(identifier, endpoint)

    def get_all_statistics(self) -> Dict[str, Any]:
        """Get statistics for all rate limiters."""
        stats = {}
        for name, limiter in self.limiters.items():
            stats[name] = limiter.get_statistics()

        return {
            "limiters": stats,
            "endpoint_assignments": self.endpoint_rules.copy(),
            "total_limiters": len(self.limiters),
        }

    def reset_all_states(self) -> None:
        """Reset all rate limit states."""
        for limiter in self.limiters.values():
            limiter.states.clear()

        self.security_manager.log_security_event(
            SecurityEvent(
                event_type="rate_limit_states_reset",
                severity="medium",
                message="All rate limit states have been reset",
                metadata={"limiter_count": len(self.limiters)},
            )
        )


# Global rate limit manager
_rate_limit_manager: Optional[RateLimitManager] = None


def get_rate_limit_manager() -> RateLimitManager:
    """Get or create global rate limit manager."""
    global _rate_limit_manager
    if _rate_limit_manager is None:
        _rate_limit_manager = RateLimitManager()
    return _rate_limit_manager


def rate_limit(
    rule_name: str = "default", identifier_key: str = "client_id"
) -> Callable:
    """Add rate limiting to MCP endpoints."""

    def decorator(func: Callable) -> Callable:
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            manager = get_rate_limit_manager()

            # Extract identifier (could be IP, user ID, etc.)
            identifier = kwargs.get(identifier_key, "unknown")
            endpoint = func.__name__

            # Check rate limit
            is_allowed, rate_info = manager.check_rate_limit(
                identifier, endpoint, rule_name
            )

            if not is_allowed:
                error_msg = f"Rate limit exceeded. Status: {rate_info['status']}"
                if rate_info.get("retry_after", 0) > 0:
                    error_msg += f" Retry after {rate_info['retry_after']:.0f} seconds."

                raise SecurityError(error_msg)

            # Add rate limit info to response metadata if possible
            try:
                result = await func(*args, **kwargs)
                # Could add rate limit headers here if the MCP protocol supports it
                return result
            except Exception as e:
                # Log the error but don't modify rate limiting behavior
                raise e

        return wrapper

    return decorator

import inspect
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, List, Optional, Tuple  # , Dict, Union, Iterable

from fastapi import FastAPI  # , Depends, Header, HTTPException
from fastapi.routing import APIRoute
from fastapi.security import (
    APIKeyHeader,
    APIKeyQuery,
    HTTPAuthorizationCredentials,  # noqa: F401
    HTTPBasic,
    HTTPBearer,
)


class AuthType(Enum):
    """Supported authentication types"""

    NONE = "none"
    API_KEY_HEADER = "api_key_header"
    API_KEY_QUERY = "api_key_query"
    HTTP_BEARER = "http_bearer"
    HTTP_BASIC = "http_basic"
    CUSTOM_HEADER = "custom_header"


@dataclass
class AuthConfig:
    """Configuration for detected authentication"""

    auth_type: AuthType
    parameter_name: str
    security_scheme: Optional[Any] = None
    dependency_function: Optional[Callable] = None
    header_name: Optional[str] = None


@dataclass
class RouteAuthConfig:
    """Configuration for all authentication dependencies on a route"""

    auth_dependencies: List[AuthConfig]
    has_auth: bool = False

    def __post_init__(self):
        self.has_auth = len(self.auth_dependencies) > 0

    def get_primary_auth(self) -> Optional[AuthConfig]:
        """Get the primary (first) authentication dependency"""
        return self.auth_dependencies[0] if self.auth_dependencies else None

    def get_auth_by_type(self, auth_type: AuthType) -> List[AuthConfig]:
        """Get all auth dependencies of a specific type"""
        return [auth for auth in self.auth_dependencies if auth.auth_type == auth_type]


class AuthenticationDetector:
    """Detects authentication patterns in FastAPI applications"""

    def __init__(self, app: FastAPI):
        self.app = app
        self.detected_auth: Optional[AuthConfig] = None

        # run detect authentication for self.detected_auth
        self.detect_authentication()

    def detect_authentication(self) -> AuthConfig:
        """
        Determine the most common auth pattern across the app's routes.
        Falls back to NONE if nothing is detected.
        """
        if self.detected_auth:
            return self.detected_auth

        # Ignore obviously public/system routes
        PUBLIC = {"/docs", "/redoc", "/openapi.json"}

        counts: Counter[Tuple[AuthType, str]] = Counter()
        # Keep one real example per pattern so we can return a full AuthConfig later
        example_by_pattern: dict[Tuple[AuthType, str], AuthConfig] = {}

        for route in self.app.routes:
            if not isinstance(route, APIRoute):
                continue
            if route.path in PUBLIC:
                continue

            rac = self._analyze_route_auth(route)
            if not rac:
                continue

            # Avoid double-counting the same pattern multiple times on the *same* route
            seen_on_this_route: set[Tuple[AuthType, str]] = set()

            for cfg in rac.auth_dependencies:
                # Build a stable pattern key. Prefer explicit header name if present.
                name = cfg.header_name or cfg.parameter_name or ""
                key = (cfg.auth_type, name)

                if key in seen_on_this_route:
                    continue
                seen_on_this_route.add(key)

                counts[key] += 1
                # keep first example so we can return a representative AuthConfig
                example_by_pattern.setdefault(key, cfg)

        if counts:
            # Pick the true mode (highest count). Tie-breaker: a simple strength order.
            strength = {
                AuthType.HTTP_BEARER: 4,
                AuthType.API_KEY_HEADER: 3,
                AuthType.API_KEY_QUERY: 2,
                AuthType.HTTP_BASIC: 1,
                AuthType.CUSTOM_HEADER: 0,
                AuthType.NONE: -1,
            }

            # Most common with deterministic tie-breaks
            winners = counts.most_common()  # list of ((auth_type, name), count)
            top_count = winners[0][1]
            candidates = [(k, c) for k, c in winners if c == top_count]

            # Prefer stronger scheme on ties; then lexical by name for stability
            candidates.sort(key=lambda item: (-strength[item[0][0]], item[0][1]))
            best_key, _ = candidates[0]

            self.detected_auth = example_by_pattern[best_key]
        else:
            self.detected_auth = AuthConfig(AuthType.NONE, "")

        return self.detected_auth

    def _analyze_route_auth(self, route: APIRoute) -> Optional[RouteAuthConfig]:
        """Analyze a single route to detect all its authentication methods"""
        all_auth_configs: List[AuthConfig] = []

        # Route-level dependencies
        if getattr(route, "dependencies", None):
            for dep in route.dependencies:
                for cfg in self._analyze_dependency(dep.dependency):
                    all_auth_configs.append(cfg)

        # Endpoint function dependencies (Dependant graph)
        if getattr(route, "dependant", None) and route.dependant.dependencies:
            for depend in route.dependant.dependencies:
                for cfg in self._analyze_dependency(depend.call):
                    all_auth_configs.append(cfg)

        # Function signature Depends(...) params
        if route.endpoint:
            sig = inspect.signature(route.endpoint)
            for _, param in sig.parameters.items():
                default = getattr(param, "default", inspect._empty)
                if hasattr(default, "dependency"):
                    for cfg in self._analyze_dependency(default.dependency):
                        all_auth_configs.append(cfg)

        # De-duplicate by (function, type, header_name, parameter_name)
        unique_auth_configs: List[AuthConfig] = []
        seen: set[Tuple[Callable, AuthType, Optional[str], str]] = set()
        for cfg in all_auth_configs:
            key = (
                cfg.dependency_function,
                cfg.auth_type,
                cfg.header_name,
                cfg.parameter_name,
            )
            if key not in seen:
                seen.add(key)
                unique_auth_configs.append(cfg)

        return (
            RouteAuthConfig(auth_dependencies=unique_auth_configs)
            if unique_auth_configs
            else None
        )

    def _analyze_dependency(self, dependency_func: Callable) -> List[AuthConfig]:
        """Analyze a dependency function to determine ALL auth types it declares"""
        results: List[AuthConfig] = []

        if not callable(dependency_func):
            return results

        try:
            sig = inspect.signature(dependency_func)
            for param_name, param in sig.parameters.items():
                # skip *args/**kwargs
                if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                    continue

                param_annotation = (
                    str(param.annotation) if param.annotation != param.empty else ""
                )
                param_default = param.default if param.default != param.empty else None

                # Extract the actual dependency from Depends wrapper (if any)
                actual_dependency = getattr(param_default, "dependency", param_default)

                # HTTP Bearer via HTTPAuthorizationCredentials + HTTPBearer()
                if "HTTPAuthorizationCredentials" in param_annotation and isinstance(
                    actual_dependency, HTTPBearer
                ):
                    results.append(
                        AuthConfig(
                            auth_type=AuthType.HTTP_BEARER,
                            parameter_name=param_name,
                            security_scheme=actual_dependency,
                            dependency_function=dependency_func,
                        )
                    )
                    # no return; continue to find more auth params

                # API Key (Header)
                if isinstance(actual_dependency, APIKeyHeader):
                    results.append(
                        AuthConfig(
                            auth_type=AuthType.API_KEY_HEADER,
                            parameter_name=param_name,
                            security_scheme=actual_dependency,
                            header_name=actual_dependency.model.name,
                            dependency_function=dependency_func,
                        )
                    )

                # API Key (Query)
                if isinstance(actual_dependency, APIKeyQuery):
                    results.append(
                        AuthConfig(
                            auth_type=AuthType.API_KEY_QUERY,
                            parameter_name=param_name,
                            security_scheme=actual_dependency,
                            dependency_function=dependency_func,
                        )
                    )

                # HTTP Basic
                if isinstance(actual_dependency, HTTPBasic):
                    results.append(
                        AuthConfig(
                            auth_type=AuthType.HTTP_BASIC,
                            parameter_name=param_name,
                            security_scheme=actual_dependency,
                            dependency_function=dependency_func,
                        )
                    )

                # Direct Header(...) param (fastapi.params.Param)
                # Header(...) returns Param with .alias/.field_info
                if (
                    param_default is not None
                    and param_default.__class__.__name__ == "Header"
                ):
                    header_name = self._extract_header_name_from_header_param(
                        param_default, param_name
                    )
                    results.append(
                        AuthConfig(
                            auth_type=AuthType.CUSTOM_HEADER,
                            parameter_name=param_name,
                            header_name=header_name,
                            dependency_function=dependency_func,
                        )
                    )

                # Depends(Header(...)) pattern
                if hasattr(param_default, "dependency"):
                    dep_str = str(param_default.dependency)
                    if "Header" in dep_str:
                        header_name = self._extract_header_name_from_depends(
                            param_default
                        )
                        if header_name:
                            results.append(
                                AuthConfig(
                                    auth_type=AuthType.CUSTOM_HEADER,
                                    parameter_name=param_name,
                                    header_name=header_name,
                                    dependency_function=dependency_func,
                                )
                            )

                # Fallback: something that stringifies with "Header"
                if param_default and "Header" in str(param_default):
                    header_name = self._extract_header_name(param_default)
                    if header_name:
                        results.append(
                            AuthConfig(
                                auth_type=AuthType.CUSTOM_HEADER,
                                parameter_name=param_name,
                                header_name=header_name,
                                dependency_function=dependency_func,
                            )
                        )

        except Exception as e:
            print(f"Error analyzing dependency {dependency_func}: {e}")

        return results

    def _extract_header_name_from_header_param(
        self, header_param, param_name: str
    ) -> str:
        """Extract header name from fastapi.params.Header object"""
        try:
            # Check for alias (custom header name)
            if hasattr(header_param, "alias") and header_param.alias:
                return header_param.alias

            # Check for other header name attributes
            if hasattr(header_param, "name") and header_param.name:
                return header_param.name

            # Fallback: convert parameter name to header format
            # Convert snake_case to kebab-case and capitalize
            header_name = param_name.replace("_", "-")
            if not header_name.startswith(("x-", "X-")):
                # Convert to proper header case (e.g., "api_key" -> "Api-Key")
                header_name = "-".join(
                    word.capitalize() for word in header_name.split("-")
                )

            return header_name

        except Exception as e:
            print(f"Error extracting header name: {e}")
            # Ultimate fallback
            return param_name.replace("_", "-").title()

    def _extract_header_name_from_depends(self, depends_obj) -> Optional[str]:
        """Extract header name from Depends(Header()) object"""
        try:
            if hasattr(depends_obj, "dependency"):
                header_func = depends_obj.dependency
                # If it's a Header function, inspect its call signature
                if callable(header_func):
                    # Try to get the alias from Header() call
                    if hasattr(header_func, "alias") and header_func.alias:
                        return header_func.alias
                    # Could inspect the Header() constructor args here if needed
        except Exception:
            pass
        return None

    def _extract_header_name(self, header_default) -> Optional[str]:
        """Extract header name from Header() dependency"""
        try:
            if hasattr(header_default, "alias") and header_default.alias:
                return header_default.alias
            # Could add more logic here to extract header name
        except:  # noqa: E722
            pass
        return None

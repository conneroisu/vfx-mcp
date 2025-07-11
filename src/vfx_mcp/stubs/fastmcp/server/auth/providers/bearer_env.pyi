"""
This type stub file was generated by pyright.
"""

from types import EllipsisType
from pydantic_settings import BaseSettings
from fastmcp.server.auth.providers.bearer import BearerAuthProvider

class EnvBearerAuthProviderSettings(BaseSettings):
    """Settings for the BearerAuthProvider."""
    model_config = ...
    public_key: str | None = ...
    jwks_uri: str | None = ...
    issuer: str | None = ...
    audience: str | None = ...
    required_scopes: list[str] | None = ...


class EnvBearerAuthProvider(BearerAuthProvider):
    """
    A BearerAuthProvider that loads settings from environment variables. Any
    providing setting will always take precedence over the environment
    variables.
    """
    def __init__(self, public_key: str | None | EllipsisType = ..., jwks_uri: str | None | EllipsisType = ..., issuer: str | None | EllipsisType = ..., audience: str | None | EllipsisType = ..., required_scopes: list[str] | None | EllipsisType = ...) -> None:
        """
        Initialize the provider.

        Args:
            public_key: RSA public key in PEM format (for static key)
            jwks_uri: URI to fetch keys from (for key rotation)
            issuer: Expected issuer claim (optional)
            audience: Expected audience claim (optional)
            required_scopes: List of required scopes for access (optional)
        """
        ...
    



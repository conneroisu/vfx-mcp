"""
This type stub file was generated by pyright.
"""

from mcp.server.auth.provider import AccessToken, AuthorizationCode, OAuthAuthorizationServerProvider, RefreshToken
from mcp.server.auth.settings import ClientRegistrationOptions, RevocationOptions
from pydantic import AnyHttpUrl

class OAuthProvider(OAuthAuthorizationServerProvider[AuthorizationCode, RefreshToken, AccessToken]):
    def __init__(self, issuer_url: AnyHttpUrl | str, service_documentation_url: AnyHttpUrl | str | None = ..., client_registration_options: ClientRegistrationOptions | None = ..., revocation_options: RevocationOptions | None = ..., required_scopes: list[str] | None = ...) -> None:
        """
        Initialize the OAuth provider.

        Args:
            issuer_url: The URL of the OAuth issuer.
            service_documentation_url: The URL of the service documentation.
            client_registration_options: The client registration options.
            revocation_options: The revocation options.
            required_scopes: Scopes that are required for all requests.
        """
        ...
    



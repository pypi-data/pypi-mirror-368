from _typeshed import Incomplete
from bosa_core import ConfigService as ConfigService
from bosa_core.authentication.client.service import ClientAwareService as ClientAwareService
from bosa_core.authentication.plugin.service import ThirdPartyIntegrationService as ThirdPartyIntegrationService
from bosa_core.authentication.token.service.verify_token_service import VerifyTokenService as VerifyTokenService
from bosa_server_plugins.auth.scheme import AuthenticationScheme as AuthenticationScheme
from bosa_server_plugins.cache import CacheService as CacheService
from bosa_server_plugins.common.exception import IntegrationDoesNotExistException as IntegrationDoesNotExistException, IntegrationExistsException as IntegrationExistsException
from bosa_server_plugins.common.helper.integration import IntegrationHelper as IntegrationHelper
from bosa_server_plugins.common.plugin import ThirdPartyIntegrationPlugin as ThirdPartyIntegrationPlugin
from bosa_server_plugins.google.router import GoogleApiRoutes as GoogleApiRoutes
from bosa_server_plugins.handler import ExposedDefaultHeaders as ExposedDefaultHeaders, Router as Router
from typing import Any

TOKEN_NOT_FOUND_MESSAGE: str

class GoogleApiPlugin(ThirdPartyIntegrationPlugin):
    """Google API Plugin."""
    CACHE_STATE_PREFIX: str
    BEARER_TOKEN_PREFIX: str
    STATE_TTL: Incomplete
    name: str
    version: str
    description: str
    scope: Incomplete
    client_config: dict[str, Any]
    config: ConfigService
    cache: CacheService
    router: Router
    client_aware_service: ClientAwareService
    verify_token_service: VerifyTokenService
    third_party_integration_service: ThirdPartyIntegrationService
    auth_scheme: AuthenticationScheme
    def __init__(self) -> None:
        """Initializes the plugin."""
    def initialize_authorization(self, callback_url: str, headers: ExposedDefaultHeaders):
        """Initializes the plugin authorization.

        Args:
            callback_url: The callback URL.
            headers: The headers.

        Returns:
            The authorization URL.
        """
    def initialize_custom_configuration(self, configuration: dict[str, Any], headers: ExposedDefaultHeaders):
        """Initializes the plugin with custom configuration.

        Args:
            configuration: The custom configuration dictionary.
            headers: The headers.

        Returns:
            The configuration result URL or status.
        """
    def success_authorize_callback(self, **kwargs):
        """Callback for successful authorization.

        Args:
            **kwargs: The keyword arguments.
        """
    def remove_integration(self, user_identifier: str, headers: ExposedDefaultHeaders):
        """Removes the integration.

        Args:
            user_identifier: The user identifier to remove.
            headers: The headers.
        """
    def select_integration(self, user_identifier: str, headers: ExposedDefaultHeaders):
        """Selects the integration.

        Args:
            user_identifier: The user identifier to select.
            headers: The headers.
        """
    def user_has_integration(self, headers: ExposedDefaultHeaders):
        """Checks if the current active user has integration with Github.

        Args:
            headers (ExposedDefaultHeaders): The headers to use.

        Returns:
            bool: True if the user has integration with Github, False otherwise.
        """
    def get_integration(self, user_identifier: str, headers: ExposedDefaultHeaders):
        """Get the integration.

        Args:
            user_identifier: The user identifier.
            headers: The headers.
        """
    def with_authentication_scheme(self, scheme: AuthenticationScheme):
        """Sets the authentication scheme for the plugin.

        Args:
            scheme (AuthenticationScheme): The authentication scheme to use.
        """
    def create_flow(self, redirect_uri: str):
        """Create OAuth 2.0 flow object.

        Args:
            redirect_uri (str): redirect uri
        """

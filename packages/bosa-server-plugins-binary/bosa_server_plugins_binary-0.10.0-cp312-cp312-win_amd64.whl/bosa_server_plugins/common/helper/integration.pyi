from _typeshed import Incomplete
from bosa_core.authentication.client.service import ClientAwareService as ClientAwareService
from bosa_core.authentication.plugin.service import ThirdPartyIntegrationService as ThirdPartyIntegrationService
from bosa_core.authentication.token.service import VerifyTokenService as VerifyTokenService

class IntegrationHelper:
    """Helper class for integration operations."""
    third_party_integration_service: Incomplete
    token_service: Incomplete
    client_aware_service: Incomplete
    def __init__(self, third_party_integration_service: ThirdPartyIntegrationService, token_service: VerifyTokenService, client_aware_service: ClientAwareService) -> None:
        """Initialize the integration helper with required services.

        Args:
            third_party_integration_service: Service for third-party integration operations
            token_service: Service for token verification
            client_aware_service: Service for client-aware operations
        """
    def get_integration_by_name(self, user_identifier: str, token: str, api_key: str, connector_name: str):
        """Get integration by name for a specific connector.

        Args:
            user_identifier: The user identifier to get integration for
            token: The bearer token (without 'Bearer ' prefix)
            api_key: The API key for client authentication
            connector_name: The name of the connector (e.g., 'github', 'google')

        Returns:
            The integration object if found

        Raises:
            NotFoundException: If integration is not found
        """

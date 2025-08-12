from _typeshed import Incomplete
from bosa_core.authentication.client.service.client_aware_service import ClientAwareService as ClientAwareService
from bosa_core.authentication.config import AuthenticationDbSettings as AuthenticationDbSettings
from bosa_core.authentication.token.repository.base_repository import BaseRepository as BaseRepository
from bosa_core.exception import InvalidClientException as InvalidClientException

class RevokeTokenService:
    """Revoke Token Service."""
    token_repository: Incomplete
    client_aware_service: Incomplete
    def __init__(self, token_repository: BaseRepository, client_aware_service: ClientAwareService) -> None:
        """Initialize the service.

        Args:
            token_repository (BaseRepository): The token repository
            client_aware_service (ClientAwareService): The client aware service
        """
    def revoke_token(self, api_key: str, access_token: str) -> bool:
        """Revoke a token.

        Args:
            api_key: The API key for client authentication
            access_token: The JWT access token to revoke

        Returns:
            bool: True if token was found and revoked, False otherwise

        Raises:
            InvalidClientException: If client is not found or token is invalid
        """

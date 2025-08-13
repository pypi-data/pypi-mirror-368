from _typeshed import Incomplete
from bosa_core.authentication.client.helper.helper import ClientHelper as ClientHelper
from bosa_core.authentication.client.repository.base_repository import BaseRepository as BaseRepository
from bosa_core.authentication.client.repository.models import ClientModel as ClientModel
from bosa_core.authentication.client.service.verify_client_service import VerifyClientService as VerifyClientService
from bosa_core.exception import InvalidClientException as InvalidClientException
from uuid import UUID

class ClientAwareService:
    """Services marked by this abstract class are client-aware.

    These services will have access to the client information via the api_key or client_id method.
    """
    client_repository: Incomplete
    verify_client_service: Incomplete
    client_helper: Incomplete
    def __init__(self, client_repository: BaseRepository) -> None:
        """Initialize the service.

        Args:
            client_repository (BaseRepository): The client repository
        """
    def get_client_by_api_key(self, api_key: str) -> ClientModel:
        """Get client by API key.

        Args:
            api_key (str): The API key for client authentication

        Returns:
            ClientModel: The client

        Raises:
            InvalidClientException: If the client is not found
        """
    def get_client_id_by_api_key(self, api_key: str) -> UUID:
        """Get client ID by API key.

        Args:
            api_key (str): The API key for client authentication

        Returns:
            UUID: The client ID

        Raises:
            InvalidClientException: If the client is not found
        """
    def get_client_by_id(self, client_id: UUID) -> ClientModel:
        """Get a client by their unique ID.

        Args:
            client_id: The UUID of the client to retrieve

        Returns:
            The ClientModel instance if found

        Raises:
            InvalidClientException: If no client with the given ID exists
        """

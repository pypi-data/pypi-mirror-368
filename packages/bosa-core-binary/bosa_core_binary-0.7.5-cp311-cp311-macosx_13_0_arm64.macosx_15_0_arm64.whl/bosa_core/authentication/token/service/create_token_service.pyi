from _typeshed import Incomplete
from bosa_core.authentication.config import AuthenticationDbSettings as AuthenticationDbSettings
from bosa_core.authentication.token.repository.base_repository import BaseRepository as BaseRepository
from bosa_core.authentication.token.repository.models import Token as Token, TokenComplete as TokenComplete
from bosa_core.authentication.user.repository.models import User as User

class CreateTokenService:
    """Create Token Service."""
    token_repository: Incomplete
    def __init__(self, token_repository: BaseRepository) -> None:
        """Initialize the service.

        Args:
            token_repository (BaseRepository): The token repository
        """
    def create_token(self, user: User) -> TokenComplete:
        """Create token.

        Args:
            user: The user

        Returns:
            TokenComplete: The token complete
        """

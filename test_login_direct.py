import sys
sys.path.insert(0, 'C:/dev/astrojoy-platform/backend')

from src.application.dtos.auth_dtos import LoginDTO
from src.application.use_cases.auth import LoginUseCase
from src.adapters.repositories.sqlalchemy import SQLAlchemyUserRepository
from src.application.services.password_service import PasswordService
from src.application.services.token_service import TokenService

# Get a database session
from src.infrastructure.database.connection import get_db_context

with get_db_context() as db:
    # Manually create dependencies
    user_repo = SQLAlchemyUserRepository(db)
    password_service = PasswordService()
    token_service = TokenService()

    # Create use case
    use_case = LoginUseCase(user_repo, password_service, token_service)

    # Try to login
    try:
        credentials = LoginDTO(email="consultant@astrojoy.com", password="Consultant123!")
        tokens, user = use_case.execute(credentials)
        print(f"SUCCESS! Access token: {tokens.access_token[:20]}...")
        print(f"User: {user.email} ({user.role})")
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

import uuid

from fastapi import Depends
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import AuthenticationBackend, CookieTransport, JWTStrategy
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.config import settings
from app.core.logger import get_logger
from app.models.user import User

logger = get_logger("app.core.security")

async def get_user_db(session: AsyncSession = Depends(get_db)):
    yield SQLAlchemyUserDatabase(session, User)

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]): 
    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY

    async def on_after_register(self, user: User, request=None) -> None: 
        logger.info("User registered: %s", user.id)

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

cookie_transport = CookieTransport(
    cookie_name=settings.COOKIE_NAME,
    cookie_max_age=settings.ACCESS_TOKEN_LIFETIME_SECONDS, 
    cookier_secure=settings.COOKIE_SECURE, 
    cookie_httponly=True, 
    cookie_samesite="lax", 
)

def get_jwt_strategy() -> JWTStrategy: 
    return JWTStrategy(
        secret=settings.SECRET_KEY, 
        lifetime_seconds=settings.ACCESS_TOKEN_LIFETIME_SECONDS, 
    )

auth_backend = AuthenticationBackend(
    name="jwt", 
    transport=cookie_transport, 
    get_strategy=get_jwt_strategy, 
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

# The dependency routers use to require an authenticated, active user. 
current_active_user = fastapi_users.current_user(active=True)
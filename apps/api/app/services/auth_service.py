from sqlalchemy.orm import Session
from apps.api.app.core.config import settings
from apps.api.app.core.errors import AuthenticationError, ConflictError, NotFoundError
from apps.api.app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from apps.api.app.models.entities import User
from apps.api.app.repositories.audit_repository import AuditRepository
from apps.api.app.repositories.user_repository import UserRepository
from apps.api.app.schemas.auth import (
    AuthResponse,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.audit_repo = AuditRepository(db)

    def register(self, payload: UserRegisterRequest, ip_address: str = "127.0.0.1") -> AuthResponse:
        existing = self.user_repo.get_by_email(payload.email)
        if existing:
            raise ConflictError("An account with this email address already exists")

        user = User(
            email=payload.email.lower().strip(),
            hashed_password=get_password_hash(payload.password),
            full_name=payload.full_name.strip(),
            is_active=True,
            is_platform_admin=False,
        )
        created_user = self.user_repo.create(user)

        # Audit log registration
        self.audit_repo.log(
            action="USER_REGISTERED",
            resource_type="USER",
            user_id=created_user.id,
            resource_id=created_user.id,
            ip_address=ip_address,
        )

        token = create_access_token(subject=created_user.id)
        return AuthResponse(
            user=UserResponse.model_validate(created_user),
            token=TokenResponse(
                access_token=token,
                expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            ),
        )

    def login(self, payload: UserLoginRequest, ip_address: str = "127.0.0.1") -> AuthResponse:
        user = self.user_repo.get_by_email(payload.email)
        if not user or not verify_password(payload.password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")

        if not user.is_active:
            raise AuthenticationError("Account is currently disabled")

        # Audit log login
        self.audit_repo.log(
            action="USER_LOGIN",
            resource_type="USER",
            user_id=user.id,
            resource_id=user.id,
            ip_address=ip_address,
        )

        token = create_access_token(subject=user.id)
        return AuthResponse(
            user=UserResponse.model_validate(user),
            token=TokenResponse(
                access_token=token,
                expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            ),
        )

    def get_user_by_id(self, user_id: str) -> UserResponse:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return UserResponse.model_validate(user)


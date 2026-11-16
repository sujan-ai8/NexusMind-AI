import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Force testing configuration
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["ENVIRONMENT"] = "testing"
os.environ["SECRET_KEY"] = "test-secret-key-for-nexusmind-phase1-testing-32chars"

from apps.api.app.core.security import get_password_hash
from apps.api.app.db.base import Base
from apps.api.app.db.session import get_db
from apps.api.app.main import app
from apps.api.app.models.entities import User, Workspace, WorkspaceMember, WorkspaceSettings
from apps.api.app.models.enums import RoleEnum

# Test in-memory database engine
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session) -> User:
    user = User(
        email="test_user@nexusmind.ai",
        hashed_password=get_password_hash("Password123!"),
        full_name="Test Engineer",
        is_active=True,
        is_platform_admin=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin_user(db_session) -> User:
    admin = User(
        email="platform_admin@nexusmind.ai",
        hashed_password=get_password_hash("AdminPass123!"),
        full_name="Platform Admin",
        is_active=True,
        is_platform_admin=True,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def test_workspace(db_session, test_user) -> Workspace:
    ws = Workspace(
        name="Test Analytics Workspace",
        slug="test-analytics-ws",
        description="Workspace for test suite",
        type="ENTERPRISE",
        cloud_provider="AWS",
        owner_id=test_user.id,
    )
    db_session.add(ws)
    db_session.flush()

    member = WorkspaceMember(
        workspace_id=ws.id,
        user_id=test_user.id,
        role=RoleEnum.WORKSPACE_ADMIN.value,
    )
    db_session.add(member)

    settings = WorkspaceSettings(
        workspace_id=ws.id,
        telemetry_enabled=True,
        aws_region="us-east-1",
    )
    db_session.add(settings)

    db_session.commit()
    db_session.refresh(ws)
    return ws


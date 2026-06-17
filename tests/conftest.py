import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.database import Base, get_db
from src.keycloak_auth import get_current_user

# Setup the in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def setup_database():
    # Create the database tables once for the test session
    Base.metadata.create_all(bind=engine)
    yield
    # Drop the database tables after the test session
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(setup_database):
    """
    Creates a fresh database session for a test.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    """
    Returns a TestClient with overridden dependencies for db and auth.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_current_user():
        return {
            "sub": "test-admin-uuid",
            "email": "admin@test.com",
            "preferred_username": "admin-test",
            "realm_roles": ["admin", "advogado"]
        }

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()

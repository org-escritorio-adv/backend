import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from src.main import app
from src.database import Base, get_db
from src.keycloak_auth import get_current_user

# Setup PostgreSQL test database
DB_NAME = "org-escritorio-adv-test"
DB_USER = "org-escritorio-adv"
DB_PASSWORD = "org-escritorio-adv"
DB_HOST = "postgres"

def _ensure_test_db():
    try:
        conn = psycopg2.connect(dbname='postgres', user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}'")
        if not cursor.fetchone():
            cursor.execute(f'CREATE DATABASE "{DB_NAME}"')
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Warning: could not create test DB: {e}")

_ensure_test_db()

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
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

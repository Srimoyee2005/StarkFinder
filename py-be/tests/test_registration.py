"""Integration tests for the user registration endpoint."""

import os
import tempfile
from typing import Generator

import pytest
from app.api.routes import app
from app.models.base import Base
from app.models.user import User
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


@pytest.fixture(scope="session")
def test_db_url() -> str:
    """Create a temporary SQLite database for testing."""
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_db.close()

    db_url = f"sqlite:///{temp_db.name}"

    yield db_url

    try:
        os.unlink(temp_db.name)
    except OSError:
        pass


@pytest.fixture(scope="session")
def test_engine(test_db_url: str):
    """Create a test database engine."""
    engine = create_engine(test_db_url, connect_args={"check_same_thread": False})

    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Clean up
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def test_session(test_engine) -> Generator[Session, None, None]:
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client(test_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with a test database session."""

    def override_get_db():
        try:
            yield test_session
        finally:
            pass

    app.dependency_overrides[app.dependency_overrides.get] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Clean up dependency overrides
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
    }


class TestUserRegistration:
    """Test cases for the /reg endpoint."""

    def test_valid_registration_request(self, client, sample_user_data):
        """Test that valid registration requests succeed."""
        response = client.post("/reg", json=sample_user_data)

        assert response.status_code == 201
        assert response.json()["username"] == sample_user_data["username"]
        assert response.json()["email"] == sample_user_data["email"]
        assert "id" in response.json()
        assert "password" not in response.json()  # Password should not be returned

    def test_invalid_request_missing_fields(self, client):
        """Test that requests with missing fields are rejected."""
        # Missing username
        response = client.post(
            "/reg", json={"email": "test@example.com", "password": "testpass123"}
        )
        assert response.status_code == 422

        # Missing email
        response = client.post(
            "/reg", json={"username": "testuser", "password": "testpass123"}
        )
        assert response.status_code == 422

        # Missing password
        response = client.post(
            "/reg", json={"username": "testuser", "email": "test@example.com"}
        )
        assert response.status_code == 422

    def test_invalid_email_format(self, client):
        """Test that invalid email formats are rejected."""
        invalid_emails = [
            "invalid-email",
            "test@",
            "@example.com",
            "test.example.com",
            "test@.com",
            "",
        ]

        for email in invalid_emails:
            response = client.post(
                "/reg",
                json={
                    "username": "testuser",
                    "email": email,
                    "password": "testpass123",
                },
            )
            assert response.status_code == 422

    def test_invalid_username_length(self, client):
        """Test that usernames that are too short are rejected."""
        response = client.post(
            "/reg",
            json={
                "username": "ab",  # Less than 3 characters
                "email": "test@example.com",
                "password": "testpass123",
            },
        )
        assert response.status_code == 422

    def test_invalid_password_length(self, client):
        """Test that passwords that are too short are rejected."""
        response = client.post(
            "/reg",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "12345",  # Less than 6 characters
            },
        )
        assert response.status_code == 422

    def test_duplicate_username_registration(self, client, sample_user_data):
        """Test that duplicate usernames are rejected."""
        # First registration should succeed
        response = client.post("/reg", json=sample_user_data)
        assert response.status_code == 201

        # Second registration with same username should fail
        duplicate_data = sample_user_data.copy()
        duplicate_data["email"] = "different@example.com"
        response = client.post("/reg", json=duplicate_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_duplicate_email_registration(self, client, sample_user_data):
        """Test that duplicate emails are rejected."""
        # First registration should succeed
        response = client.post("/reg", json=sample_user_data)
        assert response.status_code == 201

        # Second registration with same email should fail
        duplicate_data = sample_user_data.copy()
        duplicate_data["username"] = "differentuser"
        response = client.post("/reg", json=duplicate_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_db_persistence_after_successful_registration(
        self, client, sample_user_data, test_session: Session
    ):
        """Test that successful registrations are persisted to the database."""
        response = client.post("/reg", json=sample_user_data)
        assert response.status_code == 201

        # Verify the user exists in the database
        user = (
            test_session.query(User)
            .filter(User.username == sample_user_data["username"])
            .first()
        )
        assert user is not None
        assert user.email == sample_user_data["email"]
        assert (
            user.password == sample_user_data["password"]
        )  # In real app, this would be hashed

    def test_multiple_valid_registrations(self, client):
        """Test that multiple different users can register successfully."""
        users = [
            {"username": "user1", "email": "user1@example.com", "password": "pass123"},
            {"username": "user2", "email": "user2@example.com", "password": "pass456"},
            {"username": "user3", "email": "user3@example.com", "password": "pass789"},
        ]

        for user_data in users:
            response = client.post("/reg", json=user_data)
            assert response.status_code == 201
            assert response.json()["username"] == user_data["username"]
            assert response.json()["email"] == user_data["email"]

    def test_edge_case_empty_strings(self, client):
        """Test edge cases with empty strings."""
        # Empty username (will fail length validation)
        response = client.post(
            "/reg",
            json={
                "username": "",
                "email": "test@example.com",
                "password": "testpass123",
            },
        )
        assert response.status_code == 422

        # Empty password (will fail length validation)
        response = client.post(
            "/reg",
            json={"username": "testuser", "email": "test@example.com", "password": ""},
        )
        assert response.status_code == 422

    def test_special_characters_in_username(self, client):
        """Test that usernames with special characters are handled properly."""
        special_usernames = ["user_name", "user-name", "user123", "user_name_123"]

        for username in special_usernames:
            response = client.post(
                "/reg",
                json={
                    "username": username,
                    "email": f"{username}@example.com",
                    "password": "testpass123",
                },
            )
            assert response.status_code == 201
            assert response.json()["username"] == username

"""Integration tests for the user registration endpoint."""

import os
import tempfile
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.routes import app
from app.models.base import Base
from app.models.user import User


@pytest.fixture(scope="session")
def test_db_url() -> str:
    """Create a temporary SQLite database for testing."""
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_db.close()
    
    db_url = f"sqlite:///{temp_db.name}"
    
    yield db_url
    
    try:
        os.unlink(temp_db.name)
    except OSError:
        pass


@pytest.fixture(scope="session")
def test_engine(test_db_url: str):
    """Create a test database engine."""
    engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Clean up
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def test_session(test_engine) -> Generator[Session, None, None]:
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client(test_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with a test database session."""
    def override_get_db():
        try:
            yield test_session
        finally:
            pass
    
    app.dependency_overrides[app.dependency_overrides.get] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up dependency overrides
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }


class TestUserRegistration:
    """Test cases for the /reg endpoint."""

    def test_valid_registration_request(self, client, sample_user_data):
        """Test that valid registration requests succeed."""
        response = client.post("/reg", json=sample_user_data)
        
        assert response.status_code == 201
        assert response.json()["username"] == sample_user_data["username"]
        assert response.json()["email"] == sample_user_data["email"]
        assert "id" in response.json()
        assert "password" not in response.json()  # Password should not be returned

    def test_invalid_request_missing_fields(self, client):
        """Test that requests with missing fields are rejected."""
        # Missing username
        response = client.post("/reg", json={
            "email": "test@example.com",
            "password": "testpass123"
        })
        assert response.status_code == 422
        
        # Missing email
        response = client.post("/reg", json={
            "username": "testuser",
            "password": "testpass123"
        })
        assert response.status_code == 422
        
        # Missing password
        response = client.post("/reg", json={
            "username": "testuser",
            "email": "test@example.com"
        })
        assert response.status_code == 422

    def test_invalid_email_format(self, client):
        """Test that invalid email formats are rejected."""
        invalid_emails = [
            "invalid-email",
            "test@",
            "@example.com",
            "test.example.com",
            "test@.com",
            ""
        ]
        
        for email in invalid_emails:
            response = client.post("/reg", json={
                "username": "testuser",
                "email": email,
                "password": "testpass123"
            })
            assert response.status_code == 422

    def test_invalid_username_length(self, client):
        """Test that usernames that are too short are rejected."""
        response = client.post("/reg", json={
            "username": "ab",  # Less than 3 characters
            "email": "test@example.com",
            "password": "testpass123"
        })
        assert response.status_code == 422

    def test_invalid_password_length(self, client):
        """Test that passwords that are too short are rejected."""
        response = client.post("/reg", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "12345"  # Less than 6 characters
        })
        assert response.status_code == 422

    def test_duplicate_username_registration(self, client, sample_user_data):
        """Test that duplicate usernames are rejected."""
        # First registration should succeed
        response = client.post("/reg", json=sample_user_data)
        assert response.status_code == 201
        
        # Second registration with same username should fail
        duplicate_data = sample_user_data.copy()
        duplicate_data["email"] = "different@example.com"
        response = client.post("/reg", json=duplicate_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_duplicate_email_registration(self, client, sample_user_data):
        """Test that duplicate emails are rejected."""
        # First registration should succeed
        response = client.post("/reg", json=sample_user_data)
        assert response.status_code == 201
        
        # Second registration with same email should fail
        duplicate_data = sample_user_data.copy()
        duplicate_data["username"] = "differentuser"
        response = client.post("/reg", json=duplicate_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_db_persistence_after_successful_registration(self, client, sample_user_data, test_session: Session):
        """Test that successful registrations are persisted to the database."""
        response = client.post("/reg", json=sample_user_data)
        assert response.status_code == 201
        
        # Verify the user exists in the database
        user = test_session.query(User).filter(User.username == sample_user_data["username"]).first()
        assert user is not None
        assert user.email == sample_user_data["email"]
        assert user.password == sample_user_data["password"]  # In real app, this would be hashed

    def test_multiple_valid_registrations(self, client):
        """Test that multiple different users can register successfully."""
        users = [
            {"username": "user1", "email": "user1@example.com", "password": "pass123"},
            {"username": "user2", "email": "user2@example.com", "password": "pass456"},
            {"username": "user3", "email": "user3@example.com", "password": "pass789"}
        ]
        
        for user_data in users:
            response = client.post("/reg", json=user_data)
            assert response.status_code == 201
            assert response.json()["username"] == user_data["username"]
            assert response.json()["email"] == user_data["email"]

    def test_edge_case_empty_strings(self, client):
        """Test edge cases with empty strings."""
        # Empty username (will fail length validation)
        response = client.post("/reg", json={
            "username": "",
            "email": "test@example.com",
            "password": "testpass123"
        })
        assert response.status_code == 422
        
        # Empty password (will fail length validation)
        response = client.post("/reg", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": ""
        })
        assert response.status_code == 422

    def test_special_characters_in_username(self, client):
        """Test that usernames with special characters are handled properly."""
        special_usernames = [
            "user_name",
            "user-name",
            "user123",
            "user_name_123"
        ]
        
        for username in special_usernames:
            response = client.post("/reg", json={
                "username": username,
                "email": f"{username}@example.com",
                "password": "testpass123"
            })
            assert response.status_code == 201
            assert response.json()["username"] == username

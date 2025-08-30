import pytest
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

# -----------------------
# Define User Model
# -----------------------
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)


# -----------------------
# Database Fixtures
# -----------------------
@pytest.fixture(scope="session")
def engine():
    """
    Create an in-memory test database (use PostgreSQL test DB in production).
    """
    engine = create_engine(
        "sqlite:///:memory:", echo=False
    )  # for real PostgreSQL, replace URL
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_session(engine):
    """
    Creates a new database session for each test.
    Rolls back any changes after the test finishes.
    """
    connection = engine.connect()
    transaction = connection.begin()

    Session = scoped_session(sessionmaker(bind=connection))
    session = Session()

    yield session  # this is where the test runs

    session.close()
    transaction.rollback()
    connection.close()


# -----------------------
# CRUD Tests
# -----------------------


def test_create_user(db_session):
    """Test Create operation"""
    user = User(name="Alice", email="alice@example.com")
    db_session.add(user)
    db_session.commit()

    saved_user = db_session.query(User).filter_by(email="alice@example.com").first()
    assert saved_user is not None
    assert saved_user.name == "Alice"
    assert saved_user.email == "alice@example.com"


def test_read_user(db_session):
    """Test Read operation"""
    user = User(name="Bob", email="bob@example.com")
    db_session.add(user)
    db_session.commit()

    fetched_user = db_session.query(User).filter_by(email="bob@example.com").first()
    assert fetched_user is not None
    assert fetched_user.name == "Bob"
    assert fetched_user.email == "bob@example.com"


def test_update_user(db_session):
    """Test Update operation"""
    user = User(name="Charlie", email="charlie@example.com")
    db_session.add(user)
    db_session.commit()

    user_to_update = (
        db_session.query(User).filter_by(email="charlie@example.com").first()
    )
    user_to_update.name = "Charlie Updated"
    db_session.commit()

    updated_user = db_session.query(User).filter_by(email="charlie@example.com").first()
    assert updated_user.name == "Charlie Updated"


def test_delete_user(db_session):
    """Test Delete operation"""
    user = User(name="Dave", email="dave@example.com")
    db_session.add(user)
    db_session.commit()

    user_to_delete = db_session.query(User).filter_by(email="dave@example.com").first()
    db_session.delete(user_to_delete)
    db_session.commit()

    deleted_user = db_session.query(User).filter_by(email="dave@example.com").first()
    assert deleted_user is None

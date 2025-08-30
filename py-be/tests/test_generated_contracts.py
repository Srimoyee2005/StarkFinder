from app.models.generated_contract import GeneratedContract


def create_user(
    client, username: str = "testuser", email: str = "test@example.com"
) -> int:
    """Helper to create a user and return the user_id."""
    res = client.post(
        "/reg",
        json={"username": username, "email": email, "password": "password"},
    )
    assert res.status_code == 201
    return res.json()["id"]


def create_generated_contract(client, user_id: int, name: str = "Test Contract") -> int:
    """Helper to create a generated contract and return the contract_id."""
    payload = {
        "user_id": user_id,
        "contract_type": "generic",
        "contract_name": name,
        "description": "A test contract",
    }
    res = client.post("/generate", json=payload)
    assert res.status_code == 201
    return res.json()["id"]


def test_get_generated_contracts_for_user(db_session, client):
    """Test that a user can fetch their generated contracts."""
    user_id = create_user(client, username="user1", email="user1@test.com")
    create_generated_contract(client, user_id, name="Contract 1")
    create_generated_contract(client, user_id, name="Contract 2")

    # Create another user and contract to ensure we only get the first user's contracts
    user2_id = create_user(client, username="user2", email="user2@test.com")
    create_generated_contract(client, user2_id, name="Contract 3")

    res = client.get(
        f"/generated_contracts?user_id={user_id}",
        headers={"X-Token": "fake-super-secret-token"},
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2
    assert {c["contract_name"] for c in data} == {"Contract 1", "Contract 2"}


def test_get_generated_contracts_no_contracts(db_session, client):
    """Test that a user with no contracts gets an empty list."""
    user_id = create_user(client, username="user3", email="user3@test.com")

    res = client.get(
        f"/generated_contracts?user_id={user_id}",
        headers={"X-Token": "fake-super-secret-token"},
    )
    assert res.status_code == 200
    assert res.json() == []


def test_get_all_generated_contracts(db_session, client):
    """Test that the endpoint returns all contracts when no user_id is provided."""
    # Clear existing contracts to ensure a clean slate
    db_session.query(GeneratedContract).delete()
    db_session.commit()

    user1_id = create_user(client, username="user4", email="user4@test.com")
    create_generated_contract(client, user1_id, name="Contract 4")

    user2_id = create_user(client, username="user5", email="user5@test.com")
    create_generated_contract(client, user2_id, name="Contract 5")

    res = client.get(
        "/generated_contracts", headers={"X-Token": "fake-super-secret-token"}
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 2  # Can be more if other tests ran
    contract_names = {c["contract_name"] for c in data}
    assert "Contract 4" in contract_names
    assert "Contract 5" in contract_names


def test_get_generated_contracts_pagination(db_session, client):
    """Test pagination of generated contracts."""
    db_session.query(GeneratedContract).delete()
    db_session.commit()

    user_id = create_user(client, username="user6", email="user6@test.com")
    for i in range(5):
        create_generated_contract(client, user_id, name=f"Paginated Contract {i}")

    # Get first page (2 items)
    res = client.get(
        f"/generated_contracts?user_id={user_id}&skip=0&limit=2",
        headers={"X-Token": "fake-super-secret-token"},
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2
    assert data[0]["contract_name"] == "Paginated Contract 0"
    assert data[1]["contract_name"] == "Paginated Contract 1"

    # Get second page (2 items)
    res = client.get(
        f"/generated_contracts?user_id={user_id}&skip=2&limit=2",
        headers={"X-Token": "fake-super-secret-token"},
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2
    assert data[0]["contract_name"] == "Paginated Contract 2"
    assert data[1]["contract_name"] == "Paginated Contract 3"

    # Get last page (1 item)
    res = client.get(
        f"/generated_contracts?user_id={user_id}&skip=4&limit=2",
        headers={"X-Token": "fake-super-secret-token"},
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["contract_name"] == "Paginated Contract 4"


def test_get_generated_contracts_unauthorized(client):
    """Test that accessing /generated_contracts without a token returns 401 Unauthorized."""
    res = client.get("/generated_contracts")
    assert res.status_code == 401
    assert res.json() == {"detail": "Unauthorized"}

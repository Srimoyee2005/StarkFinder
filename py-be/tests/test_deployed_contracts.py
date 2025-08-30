"""Tests for the GET /deployed_contracts endpoint."""

from datetime import datetime, timedelta

from app.api import routes
from app.models.deployed_contract import DeployedContract
from fastapi.testclient import TestClient

client = TestClient(routes.app)


def seed_contracts(db):
    """Insert sample deployed contracts into the database."""
    db.query(DeployedContract).delete()
    now = datetime.utcnow()
    contracts = [
        DeployedContract(
            contract_name="A",
            contract_address="0x1",
            contract_metadata={"v": 1},
            deployed_at=now - timedelta(days=1),
        ),
        DeployedContract(
            contract_name="B",
            contract_address="0x2",
            deployed_at=now,
        ),
        DeployedContract(
            contract_name="C",
            contract_address="0x3",
            deployed_at=now - timedelta(days=2),
        ),
    ]
    db.add_all(contracts)
    db.commit()
    return contracts


def test_list_deployed_contracts_default_order(db_session):
    seed_contracts(db_session)
    res = client.get("/deployed_contracts")
    assert res.status_code == 200
    data = res.json()
    assert [c["contract_name"] for c in data] == ["B", "A", "C"]


def test_list_deployed_contracts_filter_and_sort(db_session):
    seed_contracts(db_session)
    res = client.get(
        "/deployed_contracts",
        params={"name": "A", "sort_by": "contract_name", "order": "asc"},
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["contract_name"] == "A"

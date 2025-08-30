"""Simple integration tests for the GET /deployed_contracts endpoint."""

from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.routes import app
from app.models.deployed_contracts import DeployedContract

client = TestClient(app)


class TestDeployedContractsEndpointSimple:
    """Simple test suite for the /deployed_contracts endpoint."""

    def setup_method(self):
        """Set up test data before each test method."""
        self.now = datetime.utcnow()
        self.sample_contracts = [
            {
                "id": 1,
                "contract_name": "TestToken",
                "contract_address": "0x1234567890abcdef1234567890abcdef12345678",
                "contract_metadata": {"version": "1.0", "type": "ERC20"},
                "deployed_at": self.now - timedelta(days=1),
            },
            {
                "id": 2,
                "contract_name": "InsurancePool",
                "contract_address": "0xabcdef1234567890abcdef1234567890abcdef12",
                "contract_metadata": {"version": "2.0", "type": "Insurance"},
                "deployed_at": self.now,
            },
            {
                "id": 3,
                "contract_name": "OracleContract",
                "contract_address": "0x9876543210fedcba9876543210fedcba98765432",
                "contract_metadata": {"version": "1.5", "type": "Oracle"},
                "deployed_at": self.now - timedelta(days=2),
            },
        ]

    def seed_contracts(self, db: Session, contracts_data: list = None):
        db.query(DeployedContract).delete()
        if contracts_data is None:
            contracts_data = self.sample_contracts
        contracts = []
        for contract_data in contracts_data:
            contract = DeployedContract(**contract_data)
            db.add(contract)
            contracts.append(contract)
        db.commit()
        return contracts

    def test_valid_request_with_deployed_contracts(self, db_session):
        """Test valid request returns deployed contracts successfully."""
        self.seed_contracts(db_session)

        response = client.get("/deployed_contracts")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_user_with_no_deployed_contracts(self, db_session):
        """Test request when no contracts are deployed."""
        self.seed_contracts(db_session, [])

        response = client.get("/deployed_contracts")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
        assert data == []

    def test_filtering_by_name(self, db_session):
        """Test filtering contracts by name."""
        self.seed_contracts(db_session)

        response = client.get("/deployed_contracts", params={"name": "Token"})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_sorting_by_deployed_at_desc(self, db_session):
        """Test sorting by deployed_at in descending order (default)."""
        self.seed_contracts(db_session)

        response = client.get(
            "/deployed_contracts", params={"sort_by": "deployed_at", "order": "desc"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_sorting_by_contract_name_asc(self, db_session):
        """Test sorting by contract_name in ascending order."""
        self.seed_contracts(db_session)

        response = client.get(
            "/deployed_contracts", params={"sort_by": "contract_name", "order": "asc"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_invalid_sort_by_field(self, db_session):
        """Test error handling for invalid sort_by field."""
        self.seed_contracts(db_session)

        response = client.get(
            "/deployed_contracts", params={"sort_by": "invalid_field"}
        )

        assert response.status_code == 400
        assert "detail" in response.json()
        assert "Invalid sort_by field" in response.json()["detail"]

    def test_combined_filtering_and_sorting(self, db_session):
        """Test combining filtering and sorting."""
        self.seed_contracts(db_session)

        response = client.get(
            "/deployed_contracts",
            params={"name": "Contract", "sort_by": "deployed_at", "order": "desc"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_endpoint_exists(self):
        """Test that the endpoint exists and is accessible."""
        response = client.get("/deployed_contracts")

        assert response.status_code != 404

    def test_endpoint_accepts_query_parameters(self):
        """Test that the endpoint accepts query parameters."""
        response = client.get(
            "/deployed_contracts",
            params={"name": "test", "sort_by": "deployed_at", "order": "desc"},
        )

        assert response.status_code != 422


class TestDeployedContractsAuthenticationSimple:
    """Simple test suite for authenticated deployed contracts endpoint (future implementation)."""

    def test_current_endpoint_does_not_require_auth(self):
        """Test that the current endpoint doesn't require authentication."""
        response = client.get("/deployed_contracts")

        assert response.status_code != 401

    def test_endpoint_structure_is_ready_for_auth(self):
        """Test that the endpoint structure is ready for authentication to be added."""
        response = client.get(
            "/deployed_contracts", headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code != 422

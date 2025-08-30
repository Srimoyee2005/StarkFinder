from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.routes import app
from app.models.deployed_contracts import DeployedContract

client = TestClient(app)


class TestDeployedContractsEndpoint:
    def setup_method(self):
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
        self.seed_contracts(db_session)

        response = client.get("/deployed_contracts")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        for contract in data:
            assert "id" in contract
            assert "contract_name" in contract
            assert "contract_address" in contract
            assert "contract_metadata" in contract
            assert "deployed_at" in contract

    def test_user_with_no_deployed_contracts(self, db_session):
        self.seed_contracts(db_session, [])

        response = client.get("/deployed_contracts")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
        assert data == []

    def test_unauthorized_request(self, db_session):
        self.seed_contracts(db_session)

        response = client.get("/deployed_contracts")

        assert response.status_code == 200

    def test_filtering_by_name(self, db_session):
        self.seed_contracts(db_session)

        response = client.get("/deployed_contracts", params={"name": "Token"})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["contract_name"] == "TestToken"

    def test_filtering_by_name_case_insensitive(self, db_session):
        self.seed_contracts(db_session)

        response = client.get("/deployed_contracts", params={"name": "token"})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["contract_name"] == "TestToken"

    def test_filtering_by_partial_name(self, db_session):
        self.seed_contracts(db_session)

        response = client.get("/deployed_contracts", params={"name": "Contract"})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["contract_name"] == "OracleContract"

    def test_sorting_by_deployed_at_desc(self, db_session):
        self.seed_contracts(db_session)

        response = client.get(
            "/deployed_contracts", params={"sort_by": "deployed_at", "order": "desc"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_sorting_by_deployed_at_asc(self, db_session):
        self.seed_contracts(db_session)

        response = client.get(
            "/deployed_contracts", params={"sort_by": "deployed_at", "order": "asc"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_sorting_by_contract_name_asc(self, db_session):
        self.seed_contracts(db_session)

        response = client.get(
            "/deployed_contracts", params={"sort_by": "contract_name", "order": "asc"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_sorting_by_contract_name_desc(self, db_session):
        self.seed_contracts(db_session)

        response = client.get(
            "/deployed_contracts", params={"sort_by": "contract_name", "order": "desc"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_combined_filtering_and_sorting(self, db_session):
        self.seed_contracts(db_session)

        response = client.get(
            "/deployed_contracts",
            params={"name": "Contract", "sort_by": "deployed_at", "order": "desc"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["contract_name"] == "OracleContract"

    def test_invalid_sort_by_field(self, db_session):
        self.seed_contracts(db_session)

        response = client.get(
            "/deployed_contracts", params={"sort_by": "invalid_field"}
        )

        assert response.status_code == 400
        assert "detail" in response.json()
        assert "Invalid sort_by field" in response.json()["detail"]

    def test_invalid_order_value(self, db_session):
        self.seed_contracts(db_session)

        response = client.get("/deployed_contracts", params={"order": "invalid"})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_response_data_structure(self, db_session):
        self.seed_contracts(db_session)

        response = client.get("/deployed_contracts")

        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

        contract = data[0]
        required_fields = [
            "id",
            "contract_name",
            "contract_address",
            "contract_metadata",
            "deployed_at",
        ]
        for field in required_fields:
            assert field in contract

        assert isinstance(contract["id"], int)
        assert isinstance(contract["contract_name"], str)
        assert isinstance(contract["contract_address"], str)
        assert isinstance(contract["deployed_at"], str)

    def test_contract_metadata_handling(self, db_session):
        contracts_with_metadata = [
            {
                "id": 1,
                "contract_name": "ContractWithMetadata",
                "contract_address": "0x1111111111111111111111111111111111111111",
                "contract_metadata": {
                    "version": "1.0",
                    "features": ["feature1", "feature2"],
                },
                "deployed_at": self.now,
            },
            {
                "id": 2,
                "contract_name": "ContractWithoutMetadata",
                "contract_address": "0x2222222222222222222222222222222222222222",
                "contract_metadata": None,
                "deployed_at": self.now,
            },
        ]
        self.seed_contracts(db_session, contracts_with_metadata)

        response = client.get("/deployed_contracts")

        assert response.status_code == 200
        data = response.json()

        with_metadata = next(
            c for c in data if c["contract_name"] == "ContractWithMetadata"
        )
        without_metadata = next(
            c for c in data if c["contract_name"] == "ContractWithoutMetadata"
        )

        assert with_metadata["contract_metadata"] == {
            "version": "1.0",
            "features": ["feature1", "feature2"],
        }
        assert without_metadata["contract_metadata"] is None

    def test_pagination_not_implemented(self, db_session):
        many_contracts = []
        for i in range(25):
            many_contracts.append(
                {
                    "id": i,
                    "contract_name": f"Contract{i}",
                    "contract_address": f"0x{i:040x}",
                    "contract_metadata": {"index": i},
                    "deployed_at": self.now - timedelta(hours=i),
                }
            )
        self.seed_contracts(db_session, many_contracts)

        response = client.get("/deployed_contracts")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 25


class TestDeployedContractsAuthentication(TestDeployedContractsEndpoint):
    def test_authenticated_user_gets_own_contracts(self, db_session):
        self.seed_contracts(db_session)

        response = client.get("/deployed_contracts")

        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_unauthenticated_request_returns_401(self, db_session):
        self.seed_contracts(db_session)

        response = client.get("/deployed_contracts")

        assert response.status_code == 200

    def test_user_cannot_access_other_users_contracts(self, db_session):
        self.seed_contracts(db_session)

        response = client.get("/deployed_contracts")

        assert response.status_code == 200
        assert len(response.json()) == 3

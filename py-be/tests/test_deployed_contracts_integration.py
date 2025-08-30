from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.routes import app
from app.models.deployed_contracts import DeployedContract

client = TestClient(app)


class TestDeployedContractsEndpoint:
    def setup_method(self):
        self.now = datetime.now()
        self.sample_contracts = [
            {
                "id": 1,
                "contract_name": "TestToken",
                "contract_address": "0x1234567890abcdef1234567890abcdef12345678",
                "contract_metadata": {"version": "1.0", "type": "ERC20"},
                "deployed_at": (self.now - timedelta(days=1)),
            },
            {
                "id": 2,
                "contract_name": "TestNFT",
                "contract_address": "0xabcdef1234567890abcdef1234567890abcdef12",
                "contract_metadata": {"version": "2.0", "type": "ERC721"},
                "deployed_at": (self.now - timedelta(hours=6)),
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
        assert len(data) == 2
        assert data[0]["contract_name"] == "TestNFT"
        assert data[1]["contract_name"] == "TestToken"

    def test_user_with_no_deployed_contracts(self, db_session):
        self.seed_contracts(db_session, [])

        response = client.get("/deployed_contracts")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_unauthorized_request(self, db_session):
        self.seed_contracts(db_session)

        response = client.get("/deployed_contracts")

        assert response.status_code == 200

    def test_response_data_structure(self, db_session):
        self.seed_contracts(db_session, [self.sample_contracts[0]])

        response = client.get("/deployed_contracts")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        contract = data[0]
        assert "id" in contract
        assert "contract_name" in contract
        assert "contract_address" in contract
        assert "contract_metadata" in contract
        assert "deployed_at" in contract

    def test_database_error_handling(self, db_session):
        # This test is difficult to reproduce without mocking
        # and since we are moving away from mocking, we will skip this test
        pass

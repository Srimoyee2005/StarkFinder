"""Model for storing deployed contract metadata."""

from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Integer, String

from .base import Base


class DeployedContract(Base):
    """SQLAlchemy model for a deployed contract."""

    __tablename__ = "deployed_contracts"

    id = Column(Integer, primary_key=True, index=True)
    contract_name = Column(String, nullable=False)
    contract_address = Column(String, unique=True, nullable=False, index=True)
    contract_metadata = Column("metadata", JSON, nullable=True)
    deployed_at = Column(DateTime, default=datetime.utcnow)

from sqlalchemy import Column, Text, String, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from ..base import Base
from .enums import StateCodeEnum

class StatePincodeMap(Base):
    __tablename__ = "state_pincode_map"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pincode = Column(Text, unique=True, nullable=False)
    city = Column(Text, nullable=False)
    state_code = Column(SQLEnum(StateCodeEnum, name="state_code_enum"), nullable=False)
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.connection import Base


class ExecutionEvent(Base):
    __tablename__ = "execution_events"

    id = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    execution_id = Column(
        Integer,
        ForeignKey(
            "executions.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    event_order = Column(
        Integer,
        nullable=False
    )

    state_name = Column(
        String(150),
        nullable=True,
        index=True
    )

    state_type = Column(
        String(50),
        nullable=True
    )

    status = Column(
        String(30),
        nullable=False,
        index=True
    )

    input = Column(
        JSONB,
        nullable=True
    )

    output = Column(
        JSONB,
        nullable=True
    )

    error = Column(
        Text,
        nullable=True
    )

    cause = Column(
        Text,
        nullable=True
    )

    retry_attempt = Column(
        Integer,
        nullable=False,
        default=0
    )

    started_at = Column(
        DateTime,
        nullable=True
    )

    finished_at = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    execution = relationship(
        "Execution",
        back_populates="events"
    )

    __table_args__ = (
        UniqueConstraint(
            "execution_id",
            "event_order",
            name="uq_execution_event_order"
        ),
    )
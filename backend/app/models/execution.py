from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Execution(Base):
    __tablename__ = "executions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    workflow_id = Column(
        Integer,
        ForeignKey(
            "workflows.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    status = Column(
        String(30),
        nullable=False,
        default="PENDING",
        index=True
    )

    input = Column(
        JSONB,
        nullable=False,
        default=dict
    )

    output = Column(
        JSONB,
        nullable=True
    )

    error = Column(
        Text,
        nullable=True
    )

    current_state = Column(
        String(150),
        nullable=True
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

    workflow = relationship(
        "Workflow",
        back_populates="executions"
    )

    events = relationship(
        "ExecutionEvent",
        back_populates="execution",
        cascade="all, delete-orphan",
        order_by="ExecutionEvent.event_order"
    )
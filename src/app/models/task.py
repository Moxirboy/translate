from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db.database import Base
from datetime import UTC, datetime
import uuid as uuid_pkg

class Tasks(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid_pkg.UUID] = mapped_column(
        primary_key=True,
        unique=True,
    )
    job_id: Mapped[str | None] = mapped_column(String, default=None)
    user_id: Mapped[uuid_pkg.UUID] = mapped_column(
        UUID(as_uuid=True),
        default_factory=uuid_pkg.uuid4
    )
    master_lang: Mapped[str | None] = mapped_column(String, default=None)
    slave_lang: Mapped[str | None] = mapped_column(String, default=None)
    name: Mapped[str | None] = mapped_column(String, default=None)
    status: Mapped[str | None] = mapped_column(String, default=None)
    requested_path: Mapped[str | None] = mapped_column(String, default=None)
    processed_path: Mapped[str | None] = mapped_column(String, default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default_factory=lambda: datetime.now(UTC),
        nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None
    )

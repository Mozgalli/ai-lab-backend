from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import UUIDMixin, TimestampMixin

class Dataset(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "datasets"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    kind: Mapped[str] = mapped_column(String(50), nullable=False, default="tabular")  # tabular/text/image/audio
    description: Mapped[str | None] = mapped_column(Text)

    # file storage path (local volume now; later S3/minio)
    uri: Mapped[str] = mapped_column(String(500), nullable=False)

    # for tabular supervised learning
    target_col: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # free-form json (as text) for dataset-specific metadata (encoding, delimiter, etc.)
    meta_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    project = relationship("Project", lazy="joined")

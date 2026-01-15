import enum
from sqlalchemy import String, Text, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import UUIDMixin, TimestampMixin

class AIBranch(str, enum.Enum):
    ML = "ML"
    DL = "DL"
    NLP = "NLP"
    LLM = "LLM"
    CV = "CV"
    SPEECH = "SPEECH"
    ROBOTICS = "ROBOTICS"
    EXPERT = "EXPERT"
    EVO = "EVO"
    ETHICS = "ETHICS"

class Project(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "projects"
    __table_args__ = (UniqueConstraint("slug", name="uq_projects_slug"),)

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), nullable=False)
    branch: Mapped[AIBranch] = mapped_column(Enum(AIBranch), nullable=False, default=AIBranch.ML)
    description: Mapped[str | None] = mapped_column(Text)

    experiments: Mapped[list["Experiment"]] = relationship(back_populates="project", cascade="all, delete-orphan")

class Experiment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "experiments"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    note: Mapped[str | None] = mapped_column(Text)

    project: Mapped[Project] = relationship(back_populates="experiments")
    runs: Mapped[list["Run"]] = relationship(back_populates="experiment", cascade="all, delete-orphan")

class RunStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"

class Run(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "runs"

    experiment_id: Mapped[str] = mapped_column(ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False)

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[RunStatus] = mapped_column(Enum(RunStatus), nullable=False, default=RunStatus.QUEUED)

    # JSON as text for simplicity; you can upgrade to JSONB later
    params_json: Mapped[str | None] = mapped_column(Text)
    metrics_json: Mapped[str | None] = mapped_column(Text)
    error: Mapped[str | None] = mapped_column(Text)

    experiment: Mapped[Experiment] = relationship(back_populates="runs")

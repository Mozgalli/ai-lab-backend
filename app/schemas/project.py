from pydantic import BaseModel, Field
from app.schemas.common import UUIDOut
from app.models.project import AIBranch, RunStatus
import uuid
from datetime import datetime

class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    slug: str = Field(min_length=2, max_length=200)
    branch: AIBranch = AIBranch.ML
    description: str | None = None

class ProjectOut(UUIDOut):
    name: str
    slug: str
    branch: AIBranch
    description: str | None = None

class ExperimentCreate(BaseModel):
    project_id: uuid.UUID
    name: str
    note: str | None = None

class ExperimentOut(UUIDOut):
    project_id: uuid.UUID
    name: str
    note: str | None = None

class RunCreate(BaseModel):
    experiment_id: uuid.UUID
    name: str
    params_json: str | None = None

class RunOut(UUIDOut):
    experiment_id: uuid.UUID
    name: str
    status: RunStatus
    params_json: str | None = None
    metrics_json: str | None = None
    error: str | None = None

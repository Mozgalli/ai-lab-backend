from pydantic import BaseModel, Field
from app.schemas.common import UUIDOut
import uuid

class DatasetCreate(BaseModel):
    project_id: uuid.UUID
    name: str = Field(min_length=2, max_length=200)
    kind: str = Field(default="tabular")
    description: str | None = None
    uri: str = Field(min_length=1, max_length=500)
    target_col: str | None = None
    meta_json: str | None = None

class DatasetOut(UUIDOut):
    project_id: uuid.UUID
    name: str
    kind: str
    description: str | None = None
    uri: str
    target_col: str | None = None
    meta_json: str | None = None

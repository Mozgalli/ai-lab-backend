from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime

class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class UUIDOut(ORMBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

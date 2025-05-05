from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class BaseModel(BaseModel):
    id: Optional[str] = Field(None, description="Unique identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Config:
        from_attributes = True 
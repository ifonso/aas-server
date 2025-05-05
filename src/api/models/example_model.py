from pydantic import Field
from .base_model import BaseModel

class ExampleModel(BaseModel):
    name: str = Field(..., description="Name of the example")
    description: str = Field(..., description="Description of the example")
    is_active: bool = Field(default=True, description="Whether the example is active") 
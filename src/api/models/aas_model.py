from typing import List, Optional
from pydantic import Field
from .base_model import BaseModel


class AASModel(BaseModel):
    id: str = Field(..., description="ID of the Asset Administration Shell")
    id_short: str = Field(..., description="Short ID of the Asset Administration Shell")
    name: str = Field(..., description="Name of the Asset Administration Shell")
    submodels: List[Submodel] = Field(default_factory=list, description="List of submodels in this AAS")

    def get_mqtt_topic(self, submodel_id_short: str, property_name: str) -> str:
        """Generate MQTT topic in the format: aas_id_short/submodel_id_short/property_name"""
        return f"{self.id_short}/{submodel_id_short}/{property_name}"
    
    
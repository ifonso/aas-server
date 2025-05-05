from typing import List, Optional, Dict, Any
from ..models.aas_model import AASModel, Submodel, VariableProperty
from ..repositories.aas_repository import AASRepository
from ..repositories.mongodb_repository import MongoDBRepository
from .mqtt_service import MQTTService

class AASService:
    def __init__(
        self, 
        aas_repository: AASRepository, 
        mongodb_repository: MongoDBRepository,
        mqtt_service: MQTTService
    ):
        self.aas_repository = aas_repository
        self.mongodb_repository = mongodb_repository
        self.mqtt_service = mqtt_service

    async def create(self, item: AASModel) -> AASModel:
        # Generate MQTT topics for all variable properties
        for submodel in item.submodels:
            for prop in submodel.variable_properties:
                prop.mqtt_topic = item.get_mqtt_topic(submodel.id_short, prop.name)
        
        # Create AAS in repository
        created_aas = await self.aas_repository.create(item)
        
        # Subscribe to MQTT topics for this AAS
        await self.mqtt_service.subscribe_to_aas(created_aas.id, created_aas.id_short)
        
        return created_aas

    async def get(self, id: str) -> Optional[AASModel]:
        aas = await self.aas_repository.get(id)
        if not aas:
            return None

        # Get latest values for all variable properties
        for submodel in aas.submodels:
            for prop in submodel.variable_properties:
                latest_value = await self.mongodb_repository.get_latest_value(
                    aas.id,
                    submodel.id,
                    prop.name
                )
                if latest_value:
                    prop.current_value = str(latest_value["value"])

        return aas

    async def get_all(self) -> List[AASModel]:
        aas_list = await self.aas_repository.get_all()
        
        # Get latest values for all variable properties in all AAS
        for aas in aas_list:
            for submodel in aas.submodels:
                for prop in submodel.variable_properties:
                    latest_value = await self.mongodb_repository.get_latest_value(
                        aas.id,
                        submodel.id,
                        prop.name
                    )
                    if latest_value:
                        prop.current_value = str(latest_value["value"])

        return aas_list

    async def update(self, id: str, item: AASModel) -> Optional[AASModel]:
        # Generate MQTT topics for all variable properties
        for submodel in item.submodels:
            for prop in submodel.variable_properties:
                prop.mqtt_topic = item.get_mqtt_topic(submodel.id_short, prop.name)
        
        # Update AAS in repository
        updated_aas = await self.aas_repository.update(id, item)
        if updated_aas:
            # Resubscribe to MQTT topics for this AAS
            await self.mqtt_service.unsubscribe_from_aas(updated_aas.id_short)
            await self.mqtt_service.subscribe_to_aas(updated_aas.id, updated_aas.id_short)
        
        return updated_aas

    async def delete(self, id: str) -> bool:
        # Get AAS before deleting to get its id_short
        aas = await self.aas_repository.get(id)
        if aas:
            # Unsubscribe from MQTT topics
            await self.mqtt_service.unsubscribe_from_aas(aas.id_short)
        
        return await self.aas_repository.delete(id)

    async def get_submodel_from_aas(self, aas_id: str, id_short: str) -> Optional[Submodel]:
        """
        Get a specific submodel from an AAS using either its id or id_short
        """
        aas = await self.get(aas_id)
        if not aas:
            return None

        # Try to find submodel by id or id_short
        for submodel in aas.submodels:
            if submodel.id == id_short or submodel.id_short == id_short:
                # Get latest values for all variable properties
                for prop in submodel.variable_properties:
                    latest_value = await self.mongodb_repository.get_latest_value(
                        aas.id,
                        submodel.id,
                        prop.name
                    )
                    if latest_value:
                        prop.current_value = str(latest_value["value"])
                return submodel
        return None

    async def update_property_value(
        self, 
        aas_id: str, 
        submodel_id: str, 
        property_name: str, 
        value: Any
    ) -> None:
        """Update a property value and store it in MongoDB"""
        await self.mongodb_repository.store_property_value(
            aas_id,
            submodel_id,
            property_name,
            value
        ) 
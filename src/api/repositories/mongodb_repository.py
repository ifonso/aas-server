from typing import Optional, Any, Dict
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

class MongoDBRepository:
    def __init__(self, connection_string: str, database_name: str = "aas_core"):
        self.client = AsyncIOMotorClient(connection_string)
        self.db = self.client[database_name]
        self.collection = self.db["property_values"]

    async def store_property_value(
        self,
        aas_id: str,
        submodel_id: str,
        property_name: str,
        value: Any
    ) -> None:
        """Store a property value with timestamp"""
        document = {
            "aas_id": aas_id,
            "submodel_id": submodel_id,
            "property_name": property_name,
            "value": value,
            "timestamp": datetime.utcnow()
        }
        await self.collection.insert_one(document)

    async def get_latest_value(
        self,
        aas_id: str,
        submodel_id: str,
        property_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get the latest value for a property"""
        cursor = self.collection.find(
            {
                "aas_id": aas_id,
                "submodel_id": submodel_id,
                "property_name": property_name
            }
        ).sort("timestamp", -1).limit(1)
        
        document = await cursor.to_list(length=1)
        return document[0] if document else None

    async def get_value_history(
        self,
        aas_id: str,
        submodel_id: str,
        property_name: str,
        limit: int = 100
    ) -> list:
        """Get the history of values for a property"""
        cursor = self.collection.find(
            {
                "aas_id": aas_id,
                "submodel_id": submodel_id,
                "property_name": property_name
            }
        ).sort("timestamp", -1).limit(limit)
        
        return await cursor.to_list(length=limit)

    async def close(self):
        """Close the MongoDB connection"""
        self.client.close() 
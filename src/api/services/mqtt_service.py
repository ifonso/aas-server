import asyncio
from typing import Dict, Any, Optional
import aiomqtt
from ..repositories.mongodb_repository import MongoDBRepository

class MQTTService:
    def __init__(self, mongodb_repository: MongoDBRepository, broker: str = "localhost", port: int = 1883):
        self.mongodb_repository = mongodb_repository
        self.broker = broker
        self.port = port
        self.client: Optional[aiomqtt.Client] = None
        self.subscribed_topics: Dict[str, asyncio.Task] = {}

    async def connect(self):
        """Connect to MQTT broker"""
        self.client = aiomqtt.Client(hostname=self.broker, port=self.port)
        await self.client.connect()

    async def subscribe_to_aas(self, aas_id: str, aas_id_short: str):
        """Subscribe to all topics for a specific AAS"""
        if not self.client:
            await self.connect()

        # Subscribe to all topics for this AAS
        topic = f"{aas_id_short}/#"
        await self.client.subscribe(topic)
        
        # Start listening for messages
        task = asyncio.create_task(self._listen_for_messages(aas_id, topic))
        self.subscribed_topics[topic] = task

    async def _listen_for_messages(self, aas_id: str, topic: str):
        """Listen for messages on a topic and store them in MongoDB"""
        try:
            async for message in self.client.messages:
                if message.topic.matches(topic):
                    # Parse topic to get submodel and property information
                    # Topic format: aas_id_short/submodel_id_short/property_name
                    parts = message.topic.value.split('/')
                    if len(parts) == 3:
                        _, submodel_id_short, property_name = parts
                        
                        # Store the value in MongoDB
                        await self.mongodb_repository.store_property_value(
                            aas_id=aas_id,
                            submodel_id=submodel_id_short,
                            property_name=property_name,
                            value=message.payload.decode()
                        )
        except Exception as e:
            print(f"Error in MQTT listener for topic {topic}: {e}")
            # Reconnect and resubscribe
            await self.connect()
            await self.client.subscribe(topic)

    async def unsubscribe_from_aas(self, aas_id_short: str):
        """Unsubscribe from all topics for a specific AAS"""
        topic = f"{aas_id_short}/#"
        if topic in self.subscribed_topics:
            task = self.subscribed_topics.pop(topic)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            await self.client.unsubscribe(topic)

    async def close(self):
        """Close MQTT connection"""
        if self.client:
            await self.client.disconnect() 
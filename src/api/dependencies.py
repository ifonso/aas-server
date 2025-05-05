from fastapi import Depends
from .repositories.aas_repository import AASRepository
from .repositories.mongodb_repository import MongoDBRepository
from .services.aas_service import AASService
from .services.mqtt_service import MQTTService
import os

# MongoDB connection string from environment variable
MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017")

# MQTT configuration from environment variables
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

async def get_mongodb_repository():
    repository = MongoDBRepository(MONGODB_CONNECTION_STRING)
    try:
        yield repository
    finally:
        await repository.close()

async def get_mqtt_service(mongodb_repository: MongoDBRepository = Depends(get_mongodb_repository)):
    service = MQTTService(mongodb_repository, MQTT_BROKER, MQTT_PORT)
    try:
        yield service
    finally:
        await service.close()

async def get_aas_repository():
    repository = AASRepository()
    try:
        yield repository
    finally:
        await repository.close()

async def get_aas_service(
    aas_repository: AASRepository = Depends(get_aas_repository),
    mongodb_repository: MongoDBRepository = Depends(get_mongodb_repository),
    mqtt_service: MQTTService = Depends(get_mqtt_service)
):
    return AASService(aas_repository, mongodb_repository, mqtt_service) 
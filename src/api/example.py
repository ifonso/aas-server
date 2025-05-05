from fastapi import FastAPI
from .models.example_model import ExampleModel
from .repositories.base_repository import BaseRepository
from .services.base_service import BaseService
from .controllers.base_controller import BaseController

def setup_example_routes(app: FastAPI):
    # Create repository
    repository = BaseRepository[ExampleModel]()
    
    # Create service
    service = BaseService[ExampleModel](repository)
    
    # Create controller
    controller = BaseController[ExampleModel](service, "/examples")
    
    # Include router
    app.include_router(controller.router) 
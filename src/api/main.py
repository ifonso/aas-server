from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .repositories.aas_repository import AASRepository
from .services.aas_service import AASService
from .controllers.aas_controller import AASController

app = FastAPI(
    title="AAS Core API",
    description="Asset Administration Shell Core API",
    version="1.0.0"
)

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to AAS Core API"}

# Inicializa repositories
aas_repository = AASRepository()

# Inicializa services
aas_service = AASService(aas_repository)

# Inicializa controllers
aas_controller = AASController(aas_service)

# Setup das rotas
aas_controller.setup_routes()

# Incluir rotas
app.include_router(aas_controller.router) 
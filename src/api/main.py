from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .example import setup_example_routes

app = FastAPI(
    title="AAS Core API",
    description="Asset Administration Shell Core API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to AAS Core API"}

# Setup example routes
setup_example_routes(app) 
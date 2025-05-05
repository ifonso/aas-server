from typing import List, Optional, Any
from fastapi import APIRouter, HTTPException, Depends
from ..models.aas_model import AASModel, SubmodelInfo, Submodel
from ..services.aas_service import AASService
from ..dependencies import get_aas_service

class AASController:
    def __init__(self, service: AASService):
        self.service = service
        self.router = APIRouter(prefix="/aas", tags=["AAS"])

    def setup_routes(self):
        @self.router.post("/", response_model=AASModel)
        async def create_aas(item: AASModel, service: AASService = Depends(get_aas_service)):
            return await service.create(item)

        @self.router.get("/{id}", response_model=AASModel)
        async def get_aas(id: str, service: AASService = Depends(get_aas_service)):
            item = await service.get(id)
            if not item:
                raise HTTPException(status_code=404, detail="AAS not found")
            return item

        @self.router.get("/", response_model=List[AASModel])
        async def get_all_aas(service: AASService = Depends(get_aas_service)):
            return await service.get_all()

        @self.router.put("/{id}", response_model=AASModel)
        async def update_aas(id: str, item: AASModel, service: AASService = Depends(get_aas_service)):
            updated_item = await service.update(id, item)
            if not updated_item:
                raise HTTPException(status_code=404, detail="AAS not found")
            return updated_item

        @self.router.delete("/{id}")
        async def delete(id: str):
            if not await self.service.delete(id):
                raise HTTPException(status_code=404, detail="AAS not found")
            return {"message": "AAS deleted successfully"}

        @self.router.get("/{aas_id}/submodels/{submodel_id}", response_model=Submodel)
        async def get_submodel(
            aas_id: str,
            submodel_id: str,
            service: AASService = Depends(get_aas_service)
        ):
            submodel = await service.get_submodel_from_aas(aas_id, submodel_id)
            if not submodel:
                raise HTTPException(status_code=404, detail="Submodel not found")
            return submodel

        @self.router.post("/{aas_id}/submodels/{submodel_id}/properties/{property_name}/value")
        async def update_property_value(
            aas_id: str,
            submodel_id: str,
            property_name: str,
            value: Any,
            service: AASService = Depends(get_aas_service)
        ):
            """Update a property value and store it in MongoDB"""
            await service.update_property_value(aas_id, submodel_id, property_name, value)
            return {"status": "success", "message": "Property value updated"} 
from typing import Generic, TypeVar, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.base_service import BaseService

T = TypeVar('T', bound=BaseModel)

class BaseController(Generic[T]):
    def __init__(self, service: BaseService[T], prefix: str):
        self.service = service
        self.router = APIRouter(prefix=prefix, tags=[prefix])
        self._setup_routes()

    def _setup_routes(self):
        @self.router.post("/", response_model=T)
        async def create(item: T):
            return await self.service.create(item)

        @self.router.get("/{id}", response_model=T)
        async def get(id: str):
            item = await self.service.get(id)
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")
            return item

        @self.router.get("/", response_model=List[T])
        async def get_all():
            return await self.service.get_all()

        @self.router.put("/{id}", response_model=T)
        async def update(id: str, item: T):
            updated_item = await self.service.update(id, item)
            if not updated_item:
                raise HTTPException(status_code=404, detail="Item not found")
            return updated_item

        @self.router.delete("/{id}")
        async def delete(id: str):
            if not await self.service.delete(id):
                raise HTTPException(status_code=404, detail="Item not found")
            return {"message": "Item deleted successfully"} 
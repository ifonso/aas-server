from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel
from ..repositories.base_repository import BaseRepository

T = TypeVar('T', bound=BaseModel)

class BaseService(Generic[T]):
    def __init__(self, repository: BaseRepository[T]):
        self.repository = repository

    async def create(self, item: T) -> T:
        return await self.repository.create(item)

    async def get(self, id: str) -> Optional[T]:
        return await self.repository.get(id)

    async def get_all(self) -> List[T]:
        return await self.repository.get_all()

    async def update(self, id: str, item: T) -> Optional[T]:
        return await self.repository.update(id, item)

    async def delete(self, id: str) -> bool:
        return await self.repository.delete(id) 
from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class BaseRepository(Generic[T]):
    def __init__(self):
        self.items: List[T] = []

    async def create(self, item: T) -> T:
        self.items.append(item)
        return item

    async def get(self, id: str) -> Optional[T]:
        return next((item for item in self.items if item.id == id), None)

    async def get_all(self) -> List[T]:
        return self.items

    async def update(self, id: str, item: T) -> Optional[T]:
        for i, existing_item in enumerate(self.items):
            if existing_item.id == id:
                self.items[i] = item
                return item
        return None

    async def delete(self, id: str) -> bool:
        for i, item in enumerate(self.items):
            if item.id == id:
                self.items.pop(i)
                return True
        return False 
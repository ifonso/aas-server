from typing import List, Optional
from ..models.aas_model import AASModel

class AASRepository:
    def __init__(self):
        self.items: List[AASModel] = []

    async def create(self, item: AASModel) -> AASModel:
        self.items.append(item)
        return item

    async def get(self, id: str) -> Optional[AASModel]:
        return next((item for item in self.items if item.id == id), None)

    async def get_all(self) -> List[AASModel]:
        return self.items

    async def update(self, id: str, item: AASModel) -> Optional[AASModel]:
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
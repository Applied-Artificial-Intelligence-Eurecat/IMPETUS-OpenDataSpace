from pydantic import BaseModel
from typing import Optional, List
from schemas.datacatalog import (TypeCatalog)

class Subscription(BaseModel):
    subscription_name: str
    callback_url: str
    owners: Optional[List[str]]
    tags: Optional[List[str]]

class EntitySubscription(Subscription):
    catalog_id: Optional[str]
    entities: Optional[List[str]]

class DataCatalogSubscription(Subscription):
    types: Optional[List[TypeCatalog]]
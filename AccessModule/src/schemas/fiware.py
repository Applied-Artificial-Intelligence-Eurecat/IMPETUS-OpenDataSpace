from pydantic import BaseModel
from typing import Optional, Any, Dict, List
from datetime import datetime
import utils
import config

from schemas.datacatalog import DataCatalogCreate
from schemas.enums import TypeCatalog

class FiwareProperty(BaseModel):
    property_key: str
    property_value: Any
    property_type: str = "Property"
    observed_at: Optional[datetime] = None

    def to_fiware(self) -> Dict[str, Any]:
        try:
            if self.property_type == "Property":
                fiware_dict = utils.get_property(self.property_value)
            elif self.property_type == "Relationship":
                fiware_dict = utils.get_relationship(self.property_value)
            else:
                fiware_dict = utils.get_property(self.property_value)

            if self.observed_at:
                fiware_dict["observedAt"] = self.observed_at

            return fiware_dict
        except Exception as e:
            raise ValueError(f"Error converting to Fiware format: {str(e)}")


class FiwareEntity(BaseModel):
    id: str
    type: str
    tags: Optional[List[str]]
    entity_values: List[FiwareProperty]

    def to_fiware(self) -> Dict[str, Any]:
        try:
            fiware_dict: Dict[str, Any] = {}
            fiware_dict["@context"] = config.FIWARE_CONTEXT
            fiware_dict["id"] = self.id
            fiware_dict["tags"] = utils.get_property(self.tags)
            fiware_dict["type"] = self.type
            fiware_dict["data_catalog"] = utils.get_relationship(utils.get_full_catalog_id(self.type))

            for value in self.entity_values:
                fiware_dict[value.property_key] = value.to_fiware()

            return fiware_dict
        except Exception as e:
            raise ValueError(f"Error converting FiwareEntity to Fiware format: {str(e)}")


class OrionSubscription(BaseModel):
    description: str
    entities_type: list[str]
    watched_attribute: list[str]
    subscription_endpoint: str

class OrionSubscriptionCreate(OrionSubscription):
    id: str

    def subscription_to_fiware(self) -> dict:
        fiware_obj = {}
        fiware_obj["@context"] = config.FIWARE_CONTEXT
        fiware_obj["id"] = self.id
        fiware_obj["type"] = "Subscription"
        fiware_obj["entities"] = [ {"type": type_id} for type_id in self.entities_type]
        fiware_obj["watchedAttributes"] = self.watched_attribute
        fiware_obj["notification"] = {"endpoint": {"uri": self.subscription_endpoint, "accept": "application/ld+json"}}
        return fiware_obj
    

def empty_datacatalog() -> DataCatalogCreate:
    return DataCatalogCreate(
        **{    
            "name": "" ,
            "description": "" ,
            "is_public": False ,
            "type": TypeCatalog.GENERIC,
            "tags": [],
            "extra_relationships":[],
            "catalog_context": [] ,
            "entities_context": []
        }
    )
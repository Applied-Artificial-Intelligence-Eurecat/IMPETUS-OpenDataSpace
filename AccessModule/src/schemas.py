from pydantic import BaseModel, ConfigDict
from typing import Optional
from enum import Enum
from datetime import datetime
from typing import Any
import utils
import config
class OutputFormat(str, Enum):
    CSV = "CSV"
    JSON = "JSON"

class TypeCatalog(str, Enum):
    TIMESERIES = "TIMESERIES"
    FILE = "FILE"
    TABLE = "TABLE"
    GENERIC = "GENERIC"

class TypeAttribute(str, Enum):
    STRING = "STRING"
    INTEGER = "INTEGER"
    DOUBLE = "DOUBLE"
    COORDINATE = "COORDINATE"
    TIMESTAMP = "TIMESTAMP"
    OBJECT = "OBJECT"

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str
    disabled: Optional[bool]  = None

class UserInDB(User):
    hashed_password: str

class Context(BaseModel):
    context_key: str
    context_description: str

class ContextDefinition(Context):
    context_type: TypeAttribute

class ContextValue(Context):
    context_relation: Optional[str] = None
    context_value: Any = None

class GeneralEntityRequest(BaseModel):
    datacatalog_id: str 
    id: str
    model_config = ConfigDict(extra='allow')


class TimeSeriesEntry(BaseModel):
    id: str
    timestamp: int
    model_config = ConfigDict(extra='allow')

class TimeSeriesRequest(BaseModel):
    datacatalog_id: str 
    values: list[TimeSeriesEntry] 

class Subscription(BaseModel):
    subscription_name: str
    catalog_id: str
#    entities: list[str]
    callback_url: str

class TimeFilter(BaseModel):
    start_date: int
    end_date: str

class ContextParamenter(BaseModel):
    context_key: str
    context_value: str

class CatalogRequest(BaseModel):
    catalog_id: list[str]
    catalog_owner: list[str]
    tags: list[str]
    context: list[ContextParamenter]

class QueryRequest(BaseModel):
    catalog_id: str
    entities: list[str]
    fields: list[str]
    time_filter: Optional[TimeFilter] = None
    output: OutputFormat = OutputFormat.CSV

class FiwareProperty(BaseModel):
    property_key: str
    property_value: Any
    property_type: str = "Property"
    observed_at: Optional[datetime] = None

    def to_fiware(self) -> dict:
        fiware_dict = utils.get_property(self.property_value) if self.property_type == "Property" else utils.get_relationship(self.property_value) if self.property_type == "Relationship" else utils.get_property(self.property_value)
        if self.observed_at:
            fiware_dict["observedAt"] = self.observed_at
        return fiware_dict
class FiwareEntity(BaseModel):
    id: str
    type: str
    entity_values: list[FiwareProperty] 
    def to_fiware(self) -> dict:
        fiware_dict = {}
        fiware_dict["@context"] = config.FIWARE_CONTEXT
        fiware_dict["id"] = self.id
        fiware_dict["type"] = self.type
        fiware_dict["data_catalog"] = utils.get_relationship(utils.get_full_catalog_id(self.type))

        for value in self.entity_values:
            fiware_dict[value.property_key] = value.to_fiware()
        return fiware_dict
class DataCatalogBase(BaseModel):
    name: str 
    description: str 
    is_public: bool 
    type: TypeCatalog
    tags: list[str] 
    catalog_context: list[ContextValue] 
    entities_context: list[ContextDefinition]
    
class DataCatalogCreate(DataCatalogBase):
    id: str = ""
    owner: str = ""
    def from_fiware(self, fiware_body: dict):
        self.id = utils.get_id_from_fiware_id(fiware_body["id"])
        self.name = fiware_body["name"]["value"]
        self.description = fiware_body["description"]["value"]
        self.type = fiware_body["catalog_type"]["value"]
        self.is_public = fiware_body["public"]["value"]
        self.owner = utils.get_owner_from_fiware_id(fiware_body["owner"]["object"])
        self.catalog_context = [
                ContextValue(context_key=context, 
                    context_description=fiware_body["catalog_context"]["value"][context]["description"], 
                    context_value=fiware_body["catalog_context"]["value"][context]["value"]
                ) for context in fiware_body["catalog_context"]["value"] 
            ]
        self.entities_context = [
                ContextDefinition(context_key=context, 
                    context_description=fiware_body["entities_structure"]["value"][context]["description"], 
                    context_type=fiware_body["entities_structure"]["value"][context]["type"]
                ) for context in fiware_body["entities_structure"]["value"] 
            ]
        extra_relations = {key: value for key, value in fiware_body.items() if key not in {"id","name","description",
                                                                                           "catalog_type", "public", "owner",
                                                                                           "catalog_context", "entities_structure"}}
        for element in extra_relations:
            if type(extra_relations[element]) == dict and "type" in extra_relations[element] and  extra_relations[element]["type"] == "Relationship" and "value" in  extra_relations[element]:
                catalog_id, element_id = utils.get_entity_and_catalog_from_fiware_id(extra_relations[element]["value"])
                self.catalog_context.append(ContextValue(context_key=element, 
                    context_description= "", 
                    context_value= element_id,
                    context_relation = catalog_id
                ))
    def get_catalog_type_id(self) -> str:
        return self.id[len(config.ORION_ENTITY_PREFIX) + 1:]
        
    def datacatalog_to_fiawre(self) -> dict:
        fiware_obj = {}
        fiware_obj["@context"] = config.FIWARE_CONTEXT
        fiware_obj["id"] = utils.get_full_catalog_id(catalog_id=self.id)
        fiware_obj["type"] = config.CATALOG_ENTITY
        fiware_obj["owner"] = utils.get_relationship(utils.get_full_user_id(self.owner))
        fiware_obj["public"] = utils.get_property(self.is_public)
        fiware_obj["catalog_type"] = utils.get_property(self.type)
        fiware_obj["name"] = utils.get_property(self.name)
        fiware_obj["description"] = utils.get_property(self.description)
        fiware_obj["entities_structure"] = utils.get_property({entitie.context_key: {"type": entitie.context_type, "description": entitie.context_description } for entitie in self.entities_context})
        normal_context : list[ContextValue]= []
        for catalog_context in self.catalog_context:
            if catalog_context.context_relation is None:
                normal_context.append(catalog_context)
            else:
                fiware_obj[catalog_context.context_key] = utils.get_relationship(utils.get_entity_id(catalog_id=catalog_context.context_relation, entity_id= catalog_context.context_value))

        fiware_obj["catalog_context"] = utils.get_property({context.context_key: {"value": context.context_value, "description": context.context_description} for context in normal_context})
        
        return fiware_obj
    
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
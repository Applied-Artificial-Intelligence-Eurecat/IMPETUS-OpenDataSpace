from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from schemas.enums import (TypeCatalog, TypeAttribute)
import utils
import config

class Context(BaseModel):
    context_key: str
    context_description: str

class ContextDefinition(Context):
    context_type: TypeAttribute


class ContextValue(Context):
    context_relation: Optional[str] = None
    context_value: Optional[Any] = None

class ContextParameter(BaseModel):
    context_key: str
    context_value: str

## 
class CatalogFilter(BaseModel):
    name: str
    id: str
    owner: str
    type: TypeCatalog
    tags: List[str]
    def get_q_filter(self) -> str:
        conditions = []

        # Añadir condiciones para los atributos no nulos
        if self.name:
            conditions.append(f"name~={self.name}")
        if self.id:
            conditions.append(f"id~={self.id}")
        if self.owner:
            conditions.append(f"owner~={self.owner}")
        if self.type:
            conditions.append(f"catalog_type~={self.type}")
        if self.tags and len(self.tags) > 0:
            tag_conditions = "|".join([f"tag~={tag}" for tag in self.tags])
            conditions.append(f"({tag_conditions})")

        query = f"({')&('.join(conditions)})" if conditions else ""
        return query

class CatalogQueryRequest(BaseModel):
    limit: int
    page: int
    filter: CatalogFilter
    def get_q_filter(self) -> str:
        return self.filter.get_q_filter()

class CatalogRequest(BaseModel):
    catalog_id: List[str]
    catalog_owner: List[str]
    tags: List[str]
    context: List[ContextParameter]


class DataCatalogBase(BaseModel):
    name: str
    description: str
    is_public: bool
    type: TypeCatalog
    tags: List[str]
    catalog_context: List[ContextValue]
    entities_context: List[ContextDefinition]


class DataCatalogCreate(DataCatalogBase):
    id: str = ""
    owner: str = ""

    @staticmethod
    def empty_datacatalog() -> 'DataCatalogCreate':
        return DataCatalogCreate(
            **{
                "name": "",
                "description": "",
                "is_public": False,
                "type": TypeCatalog.GENERIC,
                "tags": [],
                "extra_relationships": [],
                "catalog_context": [],
                "entities_context": []
            }
        )

    @staticmethod
    def from_fiware(fiware_body: Dict[str, Any]) -> 'DataCatalogCreate':
        try:
            # Initialize the catalog with required fields populated
            catalog = DataCatalogCreate(
                id=utils.get_id_from_fiware_id(fiware_body["id"]),
                name=fiware_body["name"]["value"],
                tags=[] if "tags" not in fiware_body else fiware_body["tags"]["value"],
                description=fiware_body["description"]["value"],
                type=fiware_body["catalog_type"]["value"],
                is_public=fiware_body["public"]["value"],
                owner=utils.get_owner_from_fiware_id(fiware_body["owner"]["object"]),
                catalog_context=[
                    ContextValue(
                        context_key=context,
                        context_description=fiware_body["catalog_context"]["value"][context]["description"],
                        context_value=fiware_body["catalog_context"]["value"][context]["value"]
                    ) for context in fiware_body["catalog_context"]["value"]
                ],
                entities_context=[
                    ContextDefinition(
                        context_key=context,
                        context_description=fiware_body["entities_structure"]["value"][context]["description"],
                        context_type=fiware_body["entities_structure"]["value"][context]["type"]
                    ) for context in fiware_body["entities_structure"]["value"]
                ]
            )

            # Handle any additional relationships
            # TODO: Check issue - could not be reassembling?
            extra_relations = {
                key: value for key, value in fiware_body.items()
                if key not in {
                    "id", "name", "description", "catalog_type", "public", "owner",
                    "catalog_context", "entities_structure"
                }
            }

            for element in extra_relations:
                if isinstance(extra_relations[element], dict) and "type" in extra_relations[element] and \
                        extra_relations[element]["type"] == "Relationship" and "value" in extra_relations[element]:
                    catalog_id, element_id = utils.get_entity_and_catalog_from_fiware_id(
                        extra_relations[element]["value"])
                    catalog.catalog_context.append(ContextValue(
                        context_key=element,
                        context_description="",
                        context_value=element_id,
                        context_relation=catalog_id
                    ))

            return catalog
        except Exception as e:
            raise ValueError(f"Error creating DataCatalogCreate from Fiware data: {str(e)}")

    def get_catalog_type_id(self) -> str:
        return self.id[len(config.ORION_ENTITY_PREFIX) + 1:]

    def datacatalog_to_fiware(self) -> Dict[str, Any]:
        try:
            fiware_obj: Dict[str, Any] = {}
            fiware_obj["@context"] = config.FIWARE_CONTEXT
            fiware_obj["id"] = utils.get_full_catalog_id(catalog_id=self.id)
            fiware_obj["type"] = config.CATALOG_ENTITY
            fiware_obj["owner"] = utils.get_relationship(utils.get_full_user_id(self.owner))
            fiware_obj["public"] = utils.get_property(self.is_public)
            fiware_obj["catalog_type"] = utils.get_property(self.type)
            fiware_obj["tags"] = utils.get_property(self.tags)
            fiware_obj["name"] = utils.get_property(self.name)
            fiware_obj["description"] = utils.get_property(self.description)
            fiware_obj["entities_structure"] = utils.get_property(
                {entitie.context_key: {"type": entitie.context_type, "description": entitie.context_description}
                 for entitie in self.entities_context}
            )
            normal_context: List[ContextValue] = []
            for catalog_context in self.catalog_context:
                if catalog_context.context_relation is None:
                    normal_context.append(catalog_context)
                else:
                    fiware_obj[catalog_context.context_key] = utils.get_relationship(
                        utils.get_entity_id(catalog_id=catalog_context.context_relation,
                                            entity_id=catalog_context.context_value)
                    )

            fiware_obj["catalog_context"] = utils.get_property(
                {context.context_key: {"value": context.context_value, "description": context.context_description}
                 for context in normal_context}
            )

            return fiware_obj
        except Exception as e:
            raise ValueError(f"Error converting DataCatalogCreate to Fiware format: {str(e)}")


class CatalogQueryResponse(BaseModel):
    size: int
    entries: List[DataCatalogCreate]
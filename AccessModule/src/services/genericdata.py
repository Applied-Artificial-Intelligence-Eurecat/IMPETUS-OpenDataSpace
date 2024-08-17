from schemas import (TypeCatalog, GeneralEntityRequest, 
                     FiwareEntity, FiwareProperty, QueryRequest, 
                     DataCatalogCreate, OutputFormat)
from repository.fiware import send_entity, get_entity, query_entity
import utils 
import services.datacatalog as services
import exceptions
import csv

def insert_data(entry: GeneralEntityRequest, user: str) -> bool:
    data_catalog = services.get_catalog(entry.datacatalog_id)
    if not data_catalog: raise exceptions.DataCatalogNotFound()
    if data_catalog.owner != user and not data_catalog.is_public:
        raise exceptions.ODSPermissionException()
    if data_catalog.type  != TypeCatalog.GENERIC:
        raise exceptions.ODSException()
    entity = FiwareEntity(id = utils.get_entity_id(entry.datacatalog_id, user, entry.id), type=entry.datacatalog_id, entity_values= [])
    for entry_attribute in data_catalog.entities_context:
        if entry_attribute.context_key not in entry.model_dump_json():
            raise exceptions.ODSException()
        entity.entity_values.append(FiwareProperty(
            property_key= entry_attribute.context_key,
            property_value= getattr(entry, entry_attribute.context_key)
        ))
    response = send_entity([entity.to_fiware()])
    if not response: raise exceptions.ODSException()
    return entity.id

def get_data(datacatalog: DataCatalogCreate, query: QueryRequest):
    response = query_entity(type_id=query.catalog_id, entity_patterns=query.entities, attributes=query.fields)
    return response.json() if response else None
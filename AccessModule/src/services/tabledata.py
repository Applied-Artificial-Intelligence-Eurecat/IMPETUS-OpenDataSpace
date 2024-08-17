from schemas import (TypeCatalog, GeneralEntityRequest, 
                     FiwareEntity, FiwareProperty, QueryRequest, 
                     DataCatalogCreate, OutputFormat)
from repository.fiware import send_entity, get_entity, query_entity
import utils 
import services.datacatalog as services
import exceptions
from csv import DictReader
 
def insert_data(entrydata: DictReader, catalog_id: str, entity, user: str) -> bool:
    data_catalog = services.get_catalog(catalog_id)
    if not data_catalog: raise exceptions.DataCatalogNotFound()
    if data_catalog.owner != user and not data_catalog.is_public:
        raise exceptions.ODSPermissionException()
    if data_catalog.type  != TypeCatalog.TABLE:
        raise exceptions.ODSException()
    entity = FiwareEntity(id = utils.get_entity_id(catalog_id, user, entity), type=catalog_id, entity_values= [])
    data = {}
    for entry_attribute in data_catalog.entities_context:
        data[entry_attribute.context_key] = []

    for row in entrydata:
        for entry_attribute in data_catalog.entities_context:
            data[entry_attribute.context_key].append(row[entry_attribute.context_key])
    for entry_attribute in data_catalog.entities_context:
        entity.entity_values.append(FiwareProperty(
            property_key = entry_attribute.context_key,
            property_value = data[entry_attribute.context_key]
        ))
    response = send_entity([entity.to_fiware()])
    if not response: raise exceptions.ODSException()
    return True
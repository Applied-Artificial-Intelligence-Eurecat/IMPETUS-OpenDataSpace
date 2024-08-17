from schemas import TypeCatalog, TimeSeriesEntry, FiwareEntity, FiwareProperty, DataCatalogCreate, QueryRequest
from repository.fiware import send_entity
import utils 
import json
from datetime import datetime
import services.datacatalog as services
import exceptions

def insert_data(catalog_name: str, entry: TimeSeriesEntry, user: str) -> bool:
    data_catalog = services.get_catalog(catalog_name)
    if not data_catalog: raise exceptions.DataCatalogNotFound()
    if data_catalog.owner != user and not data_catalog.is_public:
        raise exceptions.ODSPermissionException()
    if data_catalog.type  != TypeCatalog.TIMESERIES:
        raise exceptions.ODSException()
    entity = FiwareEntity(id = utils.get_entity_id(catalog_name, user, entry.id), type=catalog_name, entity_values= [])
    for entry_attribute in data_catalog.entities_context:
        if entry_attribute.context_key not in entry.model_dump_json():
            raise exceptions.ODSException()
        entity.entity_values.append(FiwareProperty(
            property_key= entry_attribute.context_key,
            property_value= getattr(entry, entry_attribute.context_key),
            observed_at= datetime.fromtimestamp(entry.timestamp)
        ))
    response = send_entity([json.loads(json.dumps(entity.to_fiware(), default=lambda o: o.isoformat() if isinstance(o, datetime) else None))])
    if not response: raise exceptions.ODSException()
    return entity.id

def get_data(datacatalog: DataCatalogCreate, query: QueryRequest):
    pass
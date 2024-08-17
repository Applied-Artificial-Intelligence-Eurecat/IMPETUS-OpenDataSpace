from schemas import DataCatalogCreate, DataCatalogBase, TypeCatalog, OrionSubscriptionCreate, empty_datacatalog
from utils import get_full_catalog_id, get_full_subscription_id, get_internal_catalog_id, get_full_user_id
from exceptions import DataCatalogExists, DataCatalogNotFound, DataCatalogUpdateError, FiwareException, ODSPermissionException, ODSException
import config
import repository.fiware as fiware_repository
def get_catalog(catalog_id: str) -> DataCatalogCreate:
    catalog_json = fiware_repository.get_datacatalog(get_full_catalog_id(catalog_id))
    if catalog_json:
        datacatalog = empty_datacatalog()
        datacatalog.from_fiware(catalog_json.json())
        return datacatalog
    raise DataCatalogNotFound(config.C404_DATACATALOG_NOT_FOUND.format(catalog_id))
def get_catalogs(user: str = None, request = None):
    if not user and not request:
        query_response = fiware_repository.get_entity(config.CATALOG_ENTITY, method= None)
    else:
        query_response = fiware_repository.get_entity(config.CATALOG_ENTITY, method= None)
    if query_response:
        return query_response.json()
def _check_catalog_exists(id: str) -> bool:
    return True if fiware_repository.get_datacatalog(catalog_id=get_full_catalog_id(catalog_id=id)) else False

def create_catalog(datacatalog: DataCatalogBase, username: str) -> DataCatalogCreate:
    catalog_id = get_internal_catalog_id(datacatalog.name, username)
    if _check_catalog_exists(catalog_id): raise DataCatalogExists(config.C400_DATACATALOG_ALREADY_EXISTS.format(catalog_id))
    catalog: DataCatalogCreate = DataCatalogCreate(**datacatalog.model_dump(), id=catalog_id, owner=username)
    result = fiware_repository.send_entity([catalog.datacatalog_to_fiawre()])
    if not result.ok or "errors" in result.json():
        raise FiwareException()
    if datacatalog.type == TypeCatalog.TIMESERIES:
        subscription = OrionSubscriptionCreate(
            description=config.INTERNAL_QL_SUBSCRIPTION_DESC, 
            entities_type= [catalog_id],
            watched_attribute= [attribute.context_key for attribute in catalog.entities_context],
            subscription_endpoint=config.QL_NOTIFY, 
            id=get_full_subscription_id(catalog.get_catalog_type_id(), config.QL_NAME))
        fiware_repository.subscribe(subscription.subscription_to_fiware())
    return catalog if result else None
def update_catalog(catalog_id: str, datacatalog: DataCatalogBase, current_user: str) -> DataCatalogCreate:
    current_datacatalog = get_catalog(catalog_id)
    if not current_datacatalog: raise DataCatalogNotFound(config.C404_DATACATALOG_NOT_FOUND.format(catalog_id))
    if current_datacatalog.owner != current_user: raise ODSPermissionException(config.C401_DATACATALOG_OWNER_ERROR)
    if current_datacatalog.type != datacatalog.type: raise DataCatalogUpdateError(config.C400_DATACATALOG_TYPE_CHANGED.format(current_datacatalog.type, datacatalog.type))
    catalog: DataCatalogCreate = DataCatalogCreate(**datacatalog.model_dump(), id=current_datacatalog.id, owner=current_datacatalog.owner)
    result = fiware_repository.send_entity([catalog.datacatalog_to_fiawre()])
    print(result)
    if not result: raise ODSException()
    return catalog 

def delete_catalog(catalog_id: str, current_user: str) -> bool :
    current_datacatalog = get_catalog(catalog_id)
    if not current_datacatalog: raise DataCatalogNotFound(config.C404_DATACATALOG_NOT_FOUND.format(catalog_id))
    if current_datacatalog.owner != current_user: raise ODSPermissionException(config.C401_DATACATALOG_OWNER_ERROR)

    result = fiware_repository.delete(get_full_catalog_id(catalog_id))
    if not result.ok: raise ODSException()
    return True
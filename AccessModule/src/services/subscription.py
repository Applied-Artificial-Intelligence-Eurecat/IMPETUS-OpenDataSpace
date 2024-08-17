from schemas import  Subscription, OrionSubscriptionCreate
from utils import get_full_user_subscription_id
import config
import repository.fiware as fiware_repository
import services.datacatalog as services

def create_subscription(subscription: Subscription, user: str) -> OrionSubscriptionCreate:
    data_catalog = services.get_catalog(subscription.catalog_id)
    
    orion_subscription = OrionSubscriptionCreate(
        description=config.INTERNAL_QL_SUBSCRIPTION_DESC, 
        entities_type= [subscription.catalog_id],
        watched_attribute= [attribute.context_key for attribute in data_catalog.entities_context],
        subscription_endpoint=subscription.callback_url, 
        id=get_full_user_subscription_id(data_catalog.get_catalog_type_id(), user, subscription.subscription_name))
    fiware_repository.subscribe(orion_subscription.subscription_to_fiware())
    return orion_subscription
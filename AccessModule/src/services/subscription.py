"""
subscription.py

This module provides a service to create subscriptions to a Fiware-based data catalog.
It involves retrieving the catalog information, constructing an Orion subscription,
and sending it to the Fiware repository.
"""

from schemas import EntitySubscription, OrionSubscriptionCreate, DataCatalogSubscription
from utils import get_full_user_subscription_id
import config
import repository.fiware as fiware_repository
import services.datacatalog as services
import exceptions

def create_entity_subscription(subscription: EntitySubscription, user: str) -> OrionSubscriptionCreate:
    """
    Create a subscription to a Fiware data catalog for a specific user.

    Args:
        subscription (Subscription): The subscription details provided by the user.
        user (str): The user who is creating the subscription.

    Returns:
        OrionSubscriptionCreate: The created subscription object.

    Raises:
        exceptions.DataCatalogNotFound: If the specified data catalog does not exist.
        exceptions.ODSException: For any other errors related to the operation.
    """
    try:
        data_catalog = services.get_catalog(subscription.catalog_id)
        if not data_catalog:
            raise exceptions.DataCatalogNotFound(f"Data catalog {subscription.catalog_id} not found.")
        print(data_catalog)
        print(data_catalog.entities_context)
        orion_subscription = OrionSubscriptionCreate(
            description=config.INTERNAL_QL_SUBSCRIPTION_DESC,
            entities_type=[subscription.catalog_id],
            watched_attributes=[attribute.context_key for attribute in data_catalog.entities_context],
            subscription_endpoint=subscription.callback_url,
            id=get_full_user_subscription_id(data_catalog.get_catalog_type_id(), user, subscription.subscription_name)
        )
        response = fiware_repository.subscribe(orion_subscription.subscription_to_fiware())
        if not response.ok:
            raise exceptions.ODSException("Failed to create subscription in Fiware.")

        return orion_subscription
    except Exception as e:
        raise exceptions.ODSException(f"Error creating subscription: {str(e)}")



def create_datacatalog_subscription(subscription: DataCatalogSubscription, user: str) -> OrionSubscriptionCreate:
    """
    Create a subscription to a Fiware data catalog for a specific user.

    Args:
        subscription (Subscription): The subscription details provided by the user.
        user (str): The user who is creating the subscription.

    Returns:
        OrionSubscriptionCreate: The created subscription object.

    Raises:
        exceptions.DataCatalogNotFound: If the specified data catalog does not exist.
        exceptions.ODSException: For any other errors related to the operation.
    """
    # try:
    orion_subscription = OrionSubscriptionCreate(
        description=config.INTERNAL_QL_SUBSCRIPTION_DESC,
        entities_type=[config.CATALOG_ENTITY],
        watched_attributes=["name"],
        subscription_endpoint=subscription.callback_url,
        id=get_full_user_subscription_id(config.SUBSCRIPTION_ENTITY, user, subscription.subscription_name)
    )
    response = fiware_repository.subscribe(orion_subscription.subscription_to_fiware())
    if not response.ok:
        raise exceptions.ODSException("Failed to create subscription in Fiware.")

    return orion_subscription

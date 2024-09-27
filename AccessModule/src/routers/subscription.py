"""
Subscription API Endpoints

This module defines the FastAPI routes for managing subscriptions in the system. It includes
an endpoint for creating a new subscription, ensuring that the user is authenticated before performing the operation.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated, Union
from sqlalchemy.orm import Session

import config
from services.auth import get_current_active_user
import services.subscription as service_subscription
from exceptions import ODSPermissionException, ODSException, DataCatalogUpdateError, DataCatalogNotFound
from schemas import User, Subscription, DataCatalogSubscription, EntitySubscription

# APIRouter object to define all routes for subscription management
subscription_router = APIRouter()

@subscription_router.post("/", summary="Create a new subscription", tags=["Subscription"])
async def create_subscription(
    subscription: Union[EntitySubscription, DataCatalogSubscription],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Create a new subscription in the system.

    Args:
        form_data (Subscription): The subscription data to be created.
        current_user (User): The user making the subscription request (injected by FastAPI dependency).

    Returns:
        dict: A dictionary representing the newly created subscription.

    Raises:
        HTTPException: If there is an ODS-related exception, an appropriate HTTP error is raised.
    """
    # try:
        # Call the service layer to create the subscription
    if isinstance(subscription, EntitySubscription):
        subscription = service_subscription.create_entity_subscription(subscription, current_user.username)
    elif isinstance(subscription, DataCatalogSubscription):
        subscription = service_subscription.create_datacatalog_subscription(subscription, current_user.username)
    
    return subscription
    # except ODSException as ex:
    #     print(ex)
    #     # Raise an HTTP error if there is an exception in the subscription creation process
    #     raise HTTPException(status_code=400, detail=ex.args)

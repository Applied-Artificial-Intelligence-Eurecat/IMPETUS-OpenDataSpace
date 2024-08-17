from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, Form
from typing import Annotated
from sqlalchemy.orm import Session

import config
from repository.database import get_db
from services.auth import get_current_active_user
import services.subscription as service_subscription
from exceptions import ODSPermissionException, ODSException, DataCatalogUpdateError, DataCatalogNotFound
from schemas import User, Subscription

subscription_router = APIRouter()

@subscription_router.post("/")
async def create_subscription(
    form_data: Subscription,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    subscription = service_subscription.create_subscription(form_data, current_user.username)
    return subscription
from fastapi import APIRouter, Depends, HTTPException, Response
from typing import Annotated
from sqlalchemy.orm import Session

import config
from repository.database import get_db
from services.auth import get_current_active_user
import services.datacatalog as service
from exceptions import ODSPermissionException, ODSException, DataCatalogUpdateError, DataCatalogNotFound
from schemas import User, DataCatalogBase, DataCatalogCreate
from typing import Optional

datacatalog_router = APIRouter()

@datacatalog_router.get("/")
async def list_user_catalog(
    # current_user: Optional[User] = Depends(get_current_active_user),
):
    try:
        return service.get_catalogs(None)
    except ODSPermissionException as ex:
        raise HTTPException(status_code=403, detail=ex.args)
    except DataCatalogNotFound as ex:
        raise HTTPException(status_code=404, detail=ex.args)
    

@datacatalog_router.post("/", response_model=DataCatalogCreate)
async def register_datacatalog(
    form_data: DataCatalogBase,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    try:
        response = service.create_catalog(form_data, current_user.username)
        return response
    except ODSException as ex:
        raise HTTPException(status_code=400, detail=ex.args)

@datacatalog_router.get("/{catalog_id}", response_model=DataCatalogCreate)
async def get_datacatalog(
    catalog_id: str,
):
    try:
        return service.get_catalog(catalog_id)
    except ODSException as ex:
        raise HTTPException(status_code=404, detail=ex.args)

@datacatalog_router.put("/{catalog_id}", response_model=DataCatalogCreate)
async def upload_datacatalog(
    catalog_id: str,
    form_data: DataCatalogBase,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    try:
        return service.update_catalog(catalog_id, form_data, current_user.username)
    except ODSPermissionException as ex:
        raise HTTPException(status_code=403, detail=ex.args)
    except DataCatalogNotFound as ex:
        raise HTTPException(status_code=404, detail=ex.args)
    except DataCatalogUpdateError as ex:
        raise HTTPException(status_code=400, detail=ex.args)


@datacatalog_router.delete("/{catalog_id}")
async def delete_datacatalog(
    catalog_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    try:
        result = service.delete_catalog(catalog_id, current_user.username)
        if result:
            return Response(status_code=200)
    except ODSPermissionException as ex:
        raise HTTPException(status_code=403, detail=ex.args)
    except DataCatalogNotFound as ex:
        raise HTTPException(status_code=404, detail=ex.args)
    
@datacatalog_router.post("/page")
async def page_catalog(
    query: dict,
    current_user: Optional[User] = Depends(get_current_active_user),
):
    try:
        return service.get_catalogs(current_user)
    except ODSPermissionException as ex:
        raise HTTPException(status_code=403, detail=ex.args)
    except DataCatalogNotFound as ex:
        raise HTTPException(status_code=404, detail=ex.args)


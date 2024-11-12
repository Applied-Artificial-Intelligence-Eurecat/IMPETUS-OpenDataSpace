"""
Data Catalog API Endpoints

This module defines the FastAPI routes for managing Data Catalogs. It provides 
endpoints for creating, retrieving, updating, and deleting data catalogs, as well 
as a paginated catalog retrieval endpoint. Each operation is secured by user 
authentication, and access to specific operations may be restricted based on 
the user's permissions.
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from typing import Annotated, Optional

import config
from services.auth import get_current_active_user
import services.datacatalog as service
from exceptions import (
    ODSPermissionException, 
    ODSException, 
    DataCatalogUpdateError, 
    DataCatalogNotFound
)
from schemas import User, DataCatalogBase, DataCatalogCreate, CatalogQueryRequest, CatalogQueryResponse

# APIRouter object to define all routes for Data Catalogs
datacatalog_router = APIRouter()

@datacatalog_router.post("/", response_model=DataCatalogCreate, tags=["Data Catalog"])
async def register_datacatalog(
    form_data: DataCatalogBase,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Register a new Data Catalog.

    Args:
        form_data (DataCatalogBase): The data catalog information.
        current_user (User): The currently authenticated user (injected by FastAPI dependency).

    Returns:
        DataCatalogCreate: The created Data Catalog object.

    Raises:
        HTTPException: If there is an ODS-related exception, a 400 error is raised.
    """
    try:
        response = service.create_catalog(form_data, current_user.username)
        return response
    except ODSException as ex:
        raise HTTPException(status_code=400, detail=ex.args)


@datacatalog_router.get("/{catalog_id}", response_model=DataCatalogCreate, tags=["Data Catalog"])
async def get_datacatalog(catalog_id: str):
    """
    Retrieve a Data Catalog by its ID.

    Args:
        catalog_id (str): The unique identifier for the catalog.

    Returns:
        DataCatalogCreate: The data catalog object if found.

    Raises:
        HTTPException: If the catalog is not found, a 404 error is raised.
    """
    try:
        return service.get_catalog(catalog_id)
    except ODSException as ex:
        raise HTTPException(status_code=404, detail=ex.args)


@datacatalog_router.put("/{catalog_id}", response_model=DataCatalogCreate, tags=["Data Catalog"])
async def upload_datacatalog(
    catalog_id: str,
    form_data: DataCatalogBase,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Update an existing Data Catalog by its ID.

    Args:
        catalog_id (str): The unique identifier for the catalog.
        form_data (DataCatalogBase): The updated data catalog information.
        current_user (User): The currently authenticated user (injected by FastAPI dependency).

    Returns:
        DataCatalogCreate: The updated data catalog object.

    Raises:
        HTTPException: 
            - 403 if the user does not have permission to update the catalog.
            - 404 if the catalog is not found.
            - 400 if there is an error updating the catalog.
    """
    try:
        return service.update_catalog(catalog_id, form_data, current_user.username)
    except ODSPermissionException as ex:
        raise HTTPException(status_code=403, detail=ex.args)
    except DataCatalogNotFound as ex:
        raise HTTPException(status_code=404, detail=ex.args)
    except DataCatalogUpdateError as ex:
        raise HTTPException(status_code=400, detail=ex.args)


@datacatalog_router.delete("/{catalog_id}", tags=["Data Catalog"])
async def delete_datacatalog(
    catalog_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Delete a Data Catalog by its ID.

    Args:
        catalog_id (str): The unique identifier for the catalog.
        current_user (User): The currently authenticated user (injected by FastAPI dependency).

    Returns:
        Response: A 200 HTTP response if successful, otherwise raises an exception.

    Raises:
        HTTPException: 
            - 403 if the user does not have permission to delete the catalog.
            - 404 if the catalog is not found.
    """
    try:
        result = service.delete_catalog(catalog_id, current_user.username)
        if result:
            return Response(status_code=200)
    except ODSPermissionException as ex:
        raise HTTPException(status_code=403, detail=ex.args)
    except DataCatalogNotFound as ex:
        raise HTTPException(status_code=404, detail=ex.args)


@datacatalog_router.post("/page", tags=["Data Catalog"])
async def page_catalog(query: CatalogQueryRequest) -> CatalogQueryResponse:
    """
    Retrieve multiple Data Catalogs using a query. Pagination is supported.

    Args:
        query (dict): The filter criteria for retrieving the catalogs.

    Returns:
        List[DataCatalogCreate]: A list of matching data catalogs.

    Raises:
        HTTPException: 
            - 403 if the user does not have permission to access the catalogs.
            - 404 if no catalogs are found.
    """
    try:
        catalogs = service.get_catalogs(query)
        return CatalogQueryResponse(size=len(catalogs), entries=catalogs)
    except ODSPermissionException as ex:
        raise HTTPException(status_code=403, detail=ex.args)
    except DataCatalogNotFound as ex:
        raise HTTPException(status_code=404, detail=ex.args)

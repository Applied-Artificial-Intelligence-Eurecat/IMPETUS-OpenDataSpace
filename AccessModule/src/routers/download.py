"""
File Download API Endpoints

This module defines the FastAPI routes for downloading files from the data catalog. 
It includes endpoints for fetching specific files using the catalog name, file owner, 
and entity ID.
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import FileResponse
from typing import Annotated
import os

from utils import json_to_csv, table_to_csv
import config
from services.auth import get_current_active_user
import services.files as service_file
from exceptions import (
    ODSPermissionException, 
    ODSException, 
    DataCatalogUpdateError, 
    DataCatalogNotFound
)
from schemas import User, QueryRequest, TypeCatalog, OutputFormat

# APIRouter object to define all routes for file download
download_router = APIRouter()

@download_router.get("/{datacatalog_name}/{file_owner}/{entity_id}", tags=["File Download"])
async def fetch_data(
    datacatalog_name: str,
    file_owner: str,
    entity_id: str,
):
    """
    Fetch a file from the data catalog.

    Args:
        datacatalog_name (str): The name of the data catalog.
        file_owner (str): The owner of the file.
        entity_id (str): The unique identifier for the entity.

    Returns:
        FileResponse: The requested file if found.

    Raises:
        HTTPException: 
            - 404 if the file is not found.
    """
    # Get the file path and filename using the service layer
    file_path, filename = service_file.get_file_path(datacatalog_name, file_owner, entity_id)

    # Debugging output
    print(file_path)

    # Check if file exists, if not, return 404 error
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=config.F404_FILE_NOT_FOUND)

    # Return the file as a response
    return FileResponse(file_path, filename=filename)

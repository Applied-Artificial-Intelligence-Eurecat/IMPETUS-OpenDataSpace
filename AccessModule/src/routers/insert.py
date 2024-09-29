"""
Insert Data API Endpoints

This module defines the FastAPI routes for uploading different types of data, including 
time series data, generic entity data, table data from CSV files, and regular files with metadata.
Each endpoint allows authenticated users to insert data into a specified data catalog.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, Form, Response
from typing import Annotated, List
import codecs
import json
import csv

from services.auth import get_current_active_user
import services.timeseries as service_timeseries
import services.tabledata as service_tables
import services.genericdata as service_genericdata
import services.files as service_files
from exceptions import ODSPermissionException, ODSException, DataCatalogUpdateError, DataCatalogNotFound
from schemas import User, TimeSeriesRequest, GeneralEntityRequest

# APIRouter object to define all routes for data insertion
inserdata_router = APIRouter()

@inserdata_router.post("/timeseries", summary="Upload time series data", tags=["Insert Data"])
async def upload_timeseries_data(
    form_data: TimeSeriesRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Upload time series data to the specified data catalog.

    Args:
        form_data (TimeSeriesRequest): The time series data to be uploaded.
        current_user (User): The user making the upload request (injected by FastAPI dependency).

    Returns:
        dict: A JSON object indicating the number of successful and failed insertions.
    """
    inserted = 0
    error = 0
    for data in form_data.values:
        try:
            service_timeseries.insert_data(form_data.datacatalog_id, data, current_user.username)
            inserted += 1
        except ODSException as ex:
            error += 1
    return {"success": inserted, "errors": error}


@inserdata_router.post("/generic", summary="Upload generic entity data", tags=["Insert Data"])
async def upload_general_data(
    form_data: GeneralEntityRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Upload general entity data to the specified data catalog.

    Args:
        form_data (GeneralEntityRequest): The general entity data to be uploaded.
        current_user (User): The user making the upload request (injected by FastAPI dependency).

    Returns:
        dict: A JSON object indicating success or failure.

    Raises:
        HTTPException: If there is an error during the data insertion, a 400 error is raised.
    """
    try:
        print(form_data)
        service_genericdata.insert_data(form_data, current_user.username)
    except ODSException as ex:
        raise HTTPException(status_code=400, detail=ex.args)
    return {"success": True}


@inserdata_router.post("/table", summary="Upload table data from CSV", tags=["Insert Data"])
async def upload_table_data(
    file: UploadFile,
    datacatalog: Annotated[str, Form()],
    entity: Annotated[str, Form()],
    tags: Annotated[List[str], Form()],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Upload table data from a CSV file to the specified data catalog.

    Args:
        file (UploadFile): The CSV file containing table data.
        datacatalog (str): The ID of the data catalog to upload the data to.
        entity (str): The entity associated with the data.
        current_user (User): The user making the upload request (injected by FastAPI dependency).

    Returns:
        dict: A JSON object indicating success or failure.

    Raises:
        HTTPException: If there is an error during the data insertion, a 400 error is raised.
    """
    try:
        csvReader = csv.DictReader(codecs.iterdecode(file.file, 'utf-8'))
        service_tables.insert_data(csvReader, datacatalog, entity, current_user.username)
    except ODSException as ex:
        raise HTTPException(status_code=400, detail=ex.args)
    return {"success": True}


@inserdata_router.post("/file", summary="Upload a file with metadata", tags=["Insert Data"])
async def upload_file(
    file: UploadFile,
    datacatalog: Annotated[str, Form()],
    entity: Annotated[str, Form()],
    metadata: Annotated[str, Form()],
    tags: Annotated[List[str], Form()],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Upload a file with associated metadata to the specified data catalog.

    Args:
        file (UploadFile): The file to be uploaded.
        datacatalog (str): The ID of the data catalog.
        entity (str): The entity associated with the file.
        metadata (str): Metadata in JSON format associated with the file.
        current_user (User): The user making the upload request (injected by FastAPI dependency).

    Returns:
        dict: A JSON object indicating success or failure.

    Raises:
        HTTPException: If there is an error during the data insertion, a 400 error is raised.
    """
    try:
        metadata_json = json.loads(metadata)
        service_files.insert_data(file.file, file.filename, datacatalog, entity, metadata_json, current_user.username)
    except ODSException as ex:
        raise HTTPException(status_code=400, detail=ex.args)
    return {"success": True}

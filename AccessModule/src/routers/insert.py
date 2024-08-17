from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, Form
from typing import Annotated
from sqlalchemy.orm import Session
import codecs
import json
import csv
from repository.database import get_db
from services.auth import get_current_active_user
import services.timeseries as service_timeseries
import services.tabledata as service_tables
import services.genericdata as service_genericdata
import services.files as service_files
from exceptions import ODSPermissionException, ODSException, DataCatalogUpdateError, DataCatalogNotFound
from schemas import User, TimeSeriesRequest, GeneralEntityRequest
    
inserdata_router = APIRouter()

@inserdata_router.post("/timeseries")
async def upload_timeseries_data(
    form_data: TimeSeriesRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    inserted = 0
    error = 0
    for data in form_data.values:
        try:
            service_timeseries.insert_data(form_data.datacatalog_id, data, current_user.username)
            inserted += 1
        except ODSException as ex:
            error += 1
    return {"success": inserted, "errors": error}

@inserdata_router.post("/generic")
async def upload_general_data(
    form_data: GeneralEntityRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    try:
        service_genericdata.insert_data(form_data, current_user.username)
    except ODSException as ex:
        raise HTTPException(status_code=400, detail=ex.args)
    return {"success": True}

@inserdata_router.post("/table")
async def upload_table_data(
    file: UploadFile,
    datacatalog: Annotated[str, Form()],
    entity: Annotated[str, Form()],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    try:
        csvReader = csv.DictReader(codecs.iterdecode(file.file, 'utf-8'))
        service_tables.insert_data(csvReader, datacatalog, entity, current_user.username)
    except ODSException as ex:
        raise HTTPException(status_code=400, detail=ex.args)
    return {"success": True}

@inserdata_router.post("/file")
async def upload_file(
    file: UploadFile,
    datacatalog: Annotated[str, Form()],
    entity: Annotated[str, Form()],
    metadata: Annotated[str, Form()],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    try:
        metadata_json = json.loads(metadata)
        service_files.insert_data(file.file, file.filename, datacatalog, entity, metadata_json, current_user.username)
    except ODSException as ex:
        raise HTTPException(status_code=400, detail=ex.args)
    return {"success": True}
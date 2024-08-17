from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import FileResponse

from typing import Annotated
from utils import json_to_csv, table_to_csv
import config
import os
from repository.database import get_db
from services.auth import get_current_active_user
import services.files as service_file
from exceptions import ODSPermissionException, ODSException, DataCatalogUpdateError, DataCatalogNotFound
from schemas import User, QueryRequest, TypeCatalog, OutputFormat

download_router = APIRouter()

@download_router.get("/{datacatalog_name}/{file_owner}/{entity_id}")
async def fetch_data(
    datacatalog_name: str,
    file_owner: str,
    entity_id: str,
):
    file_path, filename = service_file.get_file_path(datacatalog_name, file_owner, entity_id)
    print(file_path)
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=config.F404_FILE_NOT_FOUND)
    else:
        return FileResponse(file_path, filename=filename)




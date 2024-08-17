from fastapi import APIRouter, Depends, HTTPException, Response
from typing import Annotated
from utils import json_to_csv, table_to_csv

from repository.database import get_db
from services.auth import get_current_active_user
import services.timeseries as service_timeseries
import services.datacatalog as service_datacatlog
import services.genericdata as service_genericdata
from exceptions import ODSPermissionException, ODSException, DataCatalogUpdateError, DataCatalogNotFound
from schemas import User, QueryRequest, TypeCatalog, OutputFormat, DataCatalogCreate

query_router = APIRouter()

@query_router.post("/")
async def fetch_data(
    form_data: QueryRequest,
):
    data = {}
    try:
        datacatalog: DataCatalogCreate = service_datacatlog.get_catalog(form_data.catalog_id)
        if datacatalog.type in [TypeCatalog.GENERIC, TypeCatalog.TABLE, TypeCatalog.FILE]:
            data = service_genericdata.get_data(datacatalog, form_data)
        elif datacatalog.type in [TypeCatalog.TIMESERIES]:
            data = service_timeseries.get_data(datacatalog, form_data)
    except DataCatalogNotFound as ex:
        raise HTTPException(status_code=400, detail= ex.args)

    
    if data and form_data.output == OutputFormat.CSV:
        if datacatalog.type in [TypeCatalog.GENERIC, TypeCatalog.FILE]:
            content = json_to_csv(data)
        elif datacatalog.type in [TypeCatalog.TABLE, TypeCatalog.TIMESERIES]:
            content = table_to_csv(data)
        return Response(content, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=data.csv"})
    return data




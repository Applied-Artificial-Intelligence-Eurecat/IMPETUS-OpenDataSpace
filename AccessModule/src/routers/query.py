"""
Query Data API Endpoints

This module defines the FastAPI route for querying data from various data catalogs. It supports
multiple types of catalogs (Generic, Table, File, and Time Series) and returns data in JSON or CSV format
based on the request.
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from typing import Annotated

from utils import json_to_csv, table_to_csv
from services.auth import get_current_active_user
import services.timeseries as service_timeseries
import services.datacatalog as service_datacatalog
import services.genericdata as service_genericdata
from exceptions import ODSPermissionException, ODSException, DataCatalogUpdateError, DataCatalogNotFound
from schemas import User, QueryRequest, TypeCatalog, OutputFormat, DataCatalogCreate

# APIRouter object to define all routes for data querying
query_router = APIRouter()

@query_router.post("/", summary="Fetch data from catalog", tags=["Query Data"])
async def fetch_data(
    form_data: QueryRequest,
):
    """
    Query data from the specified catalog based on the provided query request.

    Args:
        form_data (QueryRequest): The form data containing catalog ID, entities, fields, and output format.

    Returns:
        dict or Response: 
            - JSON object with queried data if requested in JSON format.
            - CSV file if requested in CSV format.
    
    Raises:
        HTTPException: 
            - 400 if the catalog is not found.
    """
    data = {}

    try:
        # Get the catalog based on the provided catalog ID
        datacatalog: DataCatalogCreate = service_datacatalog.get_catalog(form_data.catalog_id)
        if not datacatalog:
            raise HTTPException(status_code=404, detail="Data catalog not found")
        # Handle data fetching based on the type of catalog
        if datacatalog.type in [TypeCatalog.GENERIC, TypeCatalog.TABLE, TypeCatalog.FILE]:
            data = service_genericdata.get_data(form_data, datacatalog)
        elif datacatalog.type == TypeCatalog.TIMESERIES:
            data = service_timeseries.get_data(form_data)
    except DataCatalogNotFound as ex:
        # Raise HTTP 400 error if the catalog is not found
        raise HTTPException(status_code=400, detail=ex.args)
    except ODSException as ex:
        raise HTTPException(status_code=400, detail=ex.args)

    # Handle the output format, converting data to CSV if requested
    if data and form_data.output == OutputFormat.CSV:
        if datacatalog.type in [TypeCatalog.GENERIC, TypeCatalog.FILE]:
            content = json_to_csv(data)
        elif datacatalog.type in [TypeCatalog.TABLE, TypeCatalog.TIMESERIES]:
            content = table_to_csv(data)
        return Response(content, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=data.csv"})

    # Return the data in JSON format by default
    return data

"""
timeseries_data_service.py

This module provides functionality to insert time series data into a Fiware data catalog.
It includes validation for user permissions, catalog type verification, and proper structuring
of the data in accordance with Fiware's expectations.

Dependencies:
- Fiware repository: For sending data.
- Utils: For utility functions, such as generating entity IDs.
- Services: For interacting with data catalogs.
- Exceptions: For custom errors related to data catalogs.
"""

from schemas import TypeCatalog, TimeSeriesEntry, FiwareEntity, FiwareProperty, DataCatalogCreate, QueryRequest
from repository.fiware import send_entity
import utils
import json
from datetime import datetime
from typing import Optional
import services.datacatalog as services
import exceptions


def insert_data(catalog_name: str, entry: TimeSeriesEntry, user: str) -> Optional[str]:
    """
    Inserts a time series entry into a Fiware catalog.

    Args:
        catalog_name (str): The name of the catalog to insert data into.
        entry (TimeSeriesEntry): The data entry to be inserted.
        user (str): The username of the user performing the operation.

    Returns:
        Optional[str]: The entity ID of the inserted data if successful, None otherwise.

    Raises:
        exceptions.DataCatalogNotFound: If the catalog does not exist.
        exceptions.ODSPermissionException: If the user lacks permission to modify the catalog.
        exceptions.ODSException: If the catalog type is incompatible or other errors occur.
    """
    # Fetch the data catalog
    data_catalog = services.get_catalog(catalog_name)
    
    if not data_catalog:
        raise exceptions.DataCatalogNotFound(f"Catalog '{catalog_name}' not found.")
    
    # Check permissions
    if data_catalog.owner != user and not data_catalog.is_public:
        raise exceptions.ODSPermissionException(f"User '{user}' does not have permission to modify this catalog.")
    
    # Ensure the catalog is of the correct type (timeseries)
    if data_catalog.type != TypeCatalog.TIMESERIES:
        raise exceptions.ODSException(f"Catalog type '{data_catalog.type}' is not compatible with time series data insertion.")
    
    # Create the Fiware entity for this timeseries data
    entity = FiwareEntity(
        id=utils.get_entity_id(catalog_name, user, entry.id), 
        type=catalog_name,
        tags=[],
        entity_values=[]
    )
    
    # Populate the entity with values from the entry
    entry_json = entry.model_dump_json()
    for entry_attribute in data_catalog.entities_context:
        context_key = entry_attribute.context_key
        if context_key not in entry_json:
            raise exceptions.ODSException(f"Missing attribute '{context_key}' in time series entry.")
        
        entity.entity_values.append(FiwareProperty(
            property_key=context_key,
            property_value=getattr(entry, context_key),
            observed_at=datetime.fromtimestamp(entry.timestamp)
        ))
    
    # Convert entity to JSON and handle datetime serialization
    entity_payload = json.loads(json.dumps(
        entity.to_fiware(), 
        default=lambda o: o.isoformat() if isinstance(o, datetime) else None
    ))
    
    # Send the entity to Fiware
    response = send_entity([entity_payload])
    
    if not response or not response.ok:
        raise exceptions.ODSException(f"Failed to insert data into catalog '{catalog_name}'.")
    
    return entity.id


def get_data(query: QueryRequest):
    """
    Placeholder function for retrieving data from the catalog.

    Args:
        query (QueryRequest): The query parameters for retrieving data.

    Returns:
        None: Function is not implemented yet.
    """
    raise NotImplementedError()

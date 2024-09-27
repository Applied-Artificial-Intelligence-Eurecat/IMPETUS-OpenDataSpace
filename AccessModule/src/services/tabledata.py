"""
tabledata.py

This module provides a function to insert data into a Fiware data catalog. The function processes a CSV 
file using a `DictReader`, validates user permissions, and formats the data to Fiware's required structure 
before sending it for storage.

Dependencies:
- Fiware repository: To send and query data.
- Utils: For utility functions such as generating entity IDs.
- Services: For interacting with the data catalog.
- Exceptions: For handling custom errors such as permission or catalog-related issues.
"""

from schemas import (TypeCatalog, GeneralEntityRequest, 
                     FiwareEntity, FiwareProperty, QueryRequest, 
                     DataCatalogCreate, OutputFormat)
from repository.fiware import send_entity, get_entity, query_entity
import utils 
import services.datacatalog as services
import exceptions
from csv import DictReader
from typing import Dict

def insert_data(entrydata: DictReader, catalog_id: str, entity: str, user: str) -> bool:
    """
    Inserts data from a CSV file into a specified data catalog in Fiware.

    Args:
        entrydata (DictReader): The data to insert, typically parsed from a CSV file.
        catalog_id (str): The ID of the catalog where the data will be inserted.
        entity (str): The name or ID of the entity in Fiware.
        user (str): The username of the person attempting to insert data.

    Returns:
        bool: True if the data was inserted successfully, False otherwise.

    Raises:
        exceptions.DataCatalogNotFound: If the catalog does not exist.
        exceptions.ODSPermissionException: If the user does not have permission to modify the catalog.
        exceptions.ODSException: If the catalog type is not compatible, or other errors occur during insertion.
    """
    # Fetch the data catalog
    data_catalog = services.get_catalog(catalog_id)
    
    if not data_catalog:
        raise exceptions.DataCatalogNotFound(f"Catalog with ID {catalog_id} not found.")
    
    # Check for permissions
    if data_catalog.owner != user and not data_catalog.is_public:
        raise exceptions.ODSPermissionException(f"User '{user}' does not have permission to modify the catalog.")
    
    # Validate the catalog type
    if data_catalog.type != TypeCatalog.TABLE:
        raise exceptions.ODSException(f"Catalog type '{data_catalog.type}' is not compatible with data insertion.")
    
    # Create a new Fiware entity
    entity = FiwareEntity(
        id=utils.get_entity_id(catalog_id, user, entity), 
        type=catalog_id, 
        entity_values=[]
    )
    
    # Prepare the data storage structure
    data: Dict[str, list] = {entry_attribute.context_key: [] for entry_attribute in data_catalog.entities_context}
    
    # Read data from the entrydata (CSV rows)
    for row in entrydata:
        for entry_attribute in data_catalog.entities_context:
            context_key = entry_attribute.context_key
            if context_key in row:
                data[context_key].append(row[context_key])
            else:
                raise exceptions.ODSException(f"Missing attribute '{context_key}' in CSV data.")
    
    # Populate the entity with the data collected
    for entry_attribute in data_catalog.entities_context:
        entity.entity_values.append(FiwareProperty(
            property_key=entry_attribute.context_key,
            property_value=data[entry_attribute.context_key]
        ))
    
    # Send the entity to Fiware
    response = send_entity([entity.to_fiware()])
    
    if not response or not response.ok:
        raise exceptions.ODSException("Failed to insert data into Fiware.")
    
    return True

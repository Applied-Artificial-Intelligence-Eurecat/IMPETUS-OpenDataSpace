"""
Author: [Your Name]
Date: [Today's Date]

Summary:
This module provides services for inserting data into a Fiware-based data catalog and 
retrieving data based on queries. It includes functions to validate user permissions, 
ensure the data catalog type is appropriate, and interact with the Fiware repository.
"""

from typing import Optional, Any, Dict
from schemas import (TypeCatalog, GeneralEntityRequest, 
                     FiwareEntity, FiwareProperty, QueryRequest, 
                     DataCatalogCreate, OutputFormat)
from repository.fiware import send_entity, query_entity, get_entity, get_datacatalog
import utils 
import services.datacatalog as services
import exceptions

def insert_data(entry: GeneralEntityRequest, user: str) -> str:
    """
    Insert data into a Fiware entity within a specified data catalog.

    Args:
        entry (GeneralEntityRequest): The general entity request containing the data to be inserted.
        user (str): The user who owns the data catalog.

    Returns:
        str: The ID of the created or updated entity.

    Raises:
        exceptions.DataCatalogNotFound: If the specified data catalog does not exist.
        exceptions.ODSPermissionException: If the user does not have permission to access the catalog.
        exceptions.ODSException: For any other errors related to the operation.
    """
    try:
        data_catalog = services.get_catalog(entry.datacatalog_id)
        if not data_catalog:
            raise exceptions.DataCatalogNotFound(f"Data catalog {entry.datacatalog_id} not found.")
        if data_catalog.owner != user and not data_catalog.is_public:
            raise exceptions.ODSPermissionException(f"User {user} does not have permission to access this catalog.")
        if data_catalog.type != TypeCatalog.GENERIC:
            raise exceptions.ODSException(f"Data catalog type is not 'GENERIC'. Found {data_catalog.type}.")

        entity = FiwareEntity(
            id=utils.get_entity_id(entry.datacatalog_id, user, entry.id),
            type=entry.datacatalog_id,
            tags=entry.tags,
            entity_values=[]
        )

        for entry_attribute in data_catalog.entities_context:
            if entry_attribute.context_key not in entry.model_dump_json():
                raise exceptions.ODSException(f"Missing attribute {entry_attribute.context_key} in entry data.")
            entity.entity_values.append(FiwareProperty(
                property_key=entry_attribute.context_key,
                property_value=getattr(entry, entry_attribute.context_key)
            ))

        response = send_entity([entity.to_fiware()])
        if not response.ok:
            raise exceptions.ODSException("Failed to send entity to Fiware.")

        return entity.id
    except Exception as e:
        raise exceptions.ODSException(f"Error inserting data: {str(e)}")

def get_data(query: QueryRequest, datacatalog: DataCatalogCreate) -> Optional[Dict[str, Any]]:
    """
    Retrieve data from a Fiware entity based on a query request.

    Args:
        query (QueryRequest): The query request specifying the catalog ID, entities, and fields to retrieve.

    Returns:
        Optional[Dict[str, Any]]: The retrieved data in JSON format, or None if the query fails.
    """
    try:
        response = get_entity(type_id=query.catalog_id, entities=query.entities, fields=query.fields)
        response = response.json() if response else None
        if response:
            for entity in response:
                entity["id"] = utils.get_id_from_fiware_id(entity["id"])
                if query.include_context:
                    for property in datacatalog.catalog_context:
                        entity[property.context_key] = property.context_value
                entity["data_catalog"] = entity["type"]
                entity.pop("type")

        return response if response else None
    except Exception as e:
        raise exceptions.ODSException(f"Error retrieving data: {str(e)}")

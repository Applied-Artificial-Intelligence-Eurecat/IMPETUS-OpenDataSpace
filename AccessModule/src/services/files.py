"""
files.py

This module provides services for handling file insertion and retrieval related to a Fiware-based 
data catalog. It includes functions for inserting data from a file into a Fiware entity and 
retrieving file paths for stored entities.
"""

from typing import BinaryIO, Tuple
from schemas import (TypeCatalog, GeneralEntityRequest, 
                     FiwareEntity, FiwareProperty, QueryRequest, 
                     DataCatalogCreate, OutputFormat)
from repository.fiware import send_entity, get_entity, get_specific_entity
import utils 
import config
import os
import services.datacatalog as services
import exceptions
import shutil

def insert_data(file: BinaryIO, filename: str, datacatalog_name: str, entity_name: str, metadata: dict, user: str) -> str:
    """
    Insert data from a file into a Fiware entity within a specified data catalog.

    Args:
        file (BinaryIO): The file object to be inserted.
        filename (str): The original name of the file.
        datacatalog_name (str): The name of the data catalog.
        entity_name (str): The name of the entity to be created/updated.
        metadata (dict): Metadata associated with the entity.
        user (str): The user who owns the data catalog.

    Returns:
        str: The ID of the created or updated entity.

    Raises:
        exceptions.DataCatalogNotFound: If the specified data catalog does not exist.
        exceptions.ODSPermissionException: If the user does not have permission to access the catalog.
        exceptions.ODSException: For any other errors related to the operation.
    """
    try:
        data_catalog = services.get_catalog(datacatalog_name)
        print(metadata)
        if not data_catalog:
            raise exceptions.DataCatalogNotFound()
        if data_catalog.owner != user and not data_catalog.is_public:
            raise exceptions.ODSPermissionException()
        if data_catalog.type != TypeCatalog.FILE:
            raise exceptions.ODSException("Data catalog type is not 'FILE'.")

        entity = FiwareEntity(
            id=utils.get_entity_id(datacatalog_name, user, entity_name),
            type=datacatalog_name,
            entity_values=[]
        )

        for entry_attribute in data_catalog.entities_context:
            if entry_attribute.context_key not in metadata:
                raise exceptions.ODSException(f"Metadata key {entry_attribute.context_key} missing.")
            entity.entity_values.append(FiwareProperty(
                property_key=entry_attribute.context_key,
                property_value=metadata[entry_attribute.context_key]
            ))

        # Save the file to the specified location and add the path to the entity data
        file_path = config.FIWARE_FILE_FORMAT.format(config.FIWARE_FILE_PATH, datacatalog_name, user)
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        with open(os.path.join(file_path, entity_name), 'wb+') as buffer:
            shutil.copyfileobj(file, buffer)

        entity.entity_values.append(FiwareProperty(
            property_key=config.FIWARE_FILE_PROPERTY,
            property_value=config.FIWARE_FILE_URL_FORMAT.format(config.HOSTMANE, datacatalog_name, user, entity_name)
        ))
        entity.entity_values.append(FiwareProperty(
            property_key=config.FIWARE_FILENAME_PROPERTY,
            property_value=filename
        ))

        response = send_entity([entity.to_fiware()])
        if not response.ok:
            raise exceptions.ODSException("Failed to send entity to Fiware.")

        return entity.id
    except Exception as e:
        raise exceptions.ODSException(f"Error inserting data: {str(e)}")

def get_file_path(datacatalog: str, owner: str, entity: str) -> Tuple[str, str]:
    """
    Retrieve the file path and original filename for a specified entity.

    Args:
        datacatalog (str): The name of the data catalog.
        owner (str): The owner of the data catalog.
        entity (str): The name of the entity.

    Returns:
        Tuple[str, str]: A tuple containing the file path and the original filename.

    Raises:
        exceptions.ODSException: If the file path cannot be retrieved.
    """
    try:
        response = get_specific_entity(utils.get_entity_id(datacatalog, owner, entity))
        if response:
            file_path = config.FIWARE_FILE_FORMAT.format(config.FIWARE_FILE_PATH, datacatalog, owner) + entity
            return file_path, response.json()[config.FIWARE_FILENAME_PROPERTY]["value"]
        else:
            raise exceptions.ODSException("Entity not found in Fiware.")
    except Exception as e:
        raise exceptions.ODSException(f"Error retrieving file path: {str(e)}")

from schemas import (TypeCatalog, GeneralEntityRequest, 
                     FiwareEntity, FiwareProperty, QueryRequest, 
                     DataCatalogCreate, OutputFormat)
from typing import BinaryIO
from repository.fiware import send_entity, get_entity, get_specific_entity
import utils 
import config
import os
import services.datacatalog as services
import exceptions
import csv
import shutil

def insert_data(file: BinaryIO, filename: str, datacatalog_name: str, entity_name: str, metadata: dict, user: str) -> bool:
    data_catalog = services.get_catalog(datacatalog_name)
    print(metadata)
    if not data_catalog: raise exceptions.DataCatalogNotFound()
    if data_catalog.owner != user and not data_catalog.is_public:
        raise exceptions.ODSPermissionException()
    if data_catalog.type  != TypeCatalog.FILE:
        raise exceptions.ODSException()
    entity = FiwareEntity(id = utils.get_entity_id(datacatalog_name, user, entity_name), type=datacatalog_name, entity_values= [])
    for entry_attribute in data_catalog.entities_context:
        if entry_attribute.context_key not in metadata:
            raise exceptions.ODSException()
        entity.entity_values.append(FiwareProperty(
            property_key= entry_attribute.context_key,
            property_value= metadata[entry_attribute.context_key]
        ))
    # Falta aqui guardar el ficher en el coso de ficheros + añadir el path a los datos de la entity
    file_path = config.FIWARE_FILE_FORMAT.format(config.FIWARE_FILE_PATH, datacatalog_name, user)
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    with open(file_path + entity_name, 'wb+') as buffer:
        shutil.copyfileobj(file, buffer)
    entity.entity_values.append(FiwareProperty(
        property_key= config.FIWARE_FILE_PROPERTY,
        property_value= config.FIWARE_FILE_URL_FORMAT.format(config.HOSTMANE, datacatalog_name, user, entity_name)
    ))
    entity.entity_values.append(FiwareProperty(
        property_key= config.FIWARE_FILENAME_PROPERTY,
        property_value= filename
    ))
    response = send_entity([entity.to_fiware()])
    if not response: raise exceptions.ODSException()
    return entity.id

def get_file_path(datacatalog: str, owner:str, entity: str) -> str:
    response = get_specific_entity(utils.get_entity_id(datacatalog, owner, entity))
    if response:
        file_path = config.FIWARE_FILE_FORMAT.format(config.FIWARE_FILE_PATH, datacatalog, owner) + entity

        return file_path, response.json()[config.FIWARE_FILENAME_PROPERTY]["value"]
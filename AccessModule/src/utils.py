import config
import re
import io
import csv
def get_property(value: object) -> dict:
    return {"type": "Property", "value": value}

def get_relationship(relation_id: str) -> dict:
    return {"type": "Relationship", "object": relation_id}

def get_internal_catalog_id(catalog_name: str, catalog_owner: str) -> str:
    return "{}:{}".format(catalog_owner, catalog_name)

def get_internal_entity_id(full_entity_id: str):
    patron = r':([^:]+:[^:]+)$'
    id_splited = re.search(patron, full_entity_id)
    return id_splited.group(1) if id_splited else None
def get_user_from_fiware_id(full_id:str):
    keywords =  full_id.split(":")
    return keywords[-1]
def get_id_from_fiware_id(full_id:str):
    keywords =  full_id.split(":")
    return ':'.join(keywords[-2:])
def get_owner_from_fiware_id(full_id:str):
    keywords =  full_id.split(":")
    return keywords[-1]
def get_entity_and_catalog_from_fiware_id(full_id:str):
    keywords =  full_id.split(":")
    return ':'.join(keywords[-4:-2]), ':'.join(keywords[-2:])

def get_full_user_id(user: str = None) -> str:
    return "{}:{}:{}".format(config.ORION_ENTITY_PREFIX, config.USER_ENTITY, user)


def get_full_catalog_id(catalog_id: str = None, catalog_name: str = None, catalog_owner: str = None) -> str:
    if catalog_owner and catalog_name:
        return "{}:{}:{}:{}".format(config.ORION_ENTITY_PREFIX, config.CATALOG_ENTITY, catalog_owner, catalog_name)
    elif catalog_id:
        return "{}:{}:{}".format(config.ORION_ENTITY_PREFIX, config.CATALOG_ENTITY, catalog_id)

def get_entity_id(catalog_id: str, data_owner: str = None, entity_id: str = None) -> str:
    if data_owner and entity_id:
        return "{}:{}:{}:{}".format(config.ORION_ENTITY_PREFIX, catalog_id, data_owner, entity_id)
    elif entity_id and not data_owner:
        return "{}:{}:{}".format(config.ORION_ENTITY_PREFIX, catalog_id, entity_id)

def get_full_user_id(user: str) -> str:
    return "{}:{}:{}".format(config.ORION_ENTITY_PREFIX, config.USER_ENTITY, user)

def get_full_subscription_id(catalog: str, service: str) -> str:
    return "{}:{}:{}:{}".format(config.ORION_ENTITY_PREFIX, config.SUBSCRIPTION_ENTITY,catalog, service)

def get_full_user_subscription_id(catalog: str, username:str, service: str) -> str:
    return "{}:{}:{}:{}:{}".format(config.ORION_ENTITY_PREFIX, config.SUBSCRIPTION_ENTITY,username, catalog, service)


def get_full_user_id(user: str) -> str:
    return "{}:{}:{}".format(config.ORION_ENTITY_PREFIX, config.USER_ENTITY, user)


def json_to_csv(data: dict):
    headers = []
    values = []
    for entry in data:
        for key in entry:
            headers.append(key)
    for entry in data:
        values.append((entry[key]["value"]
                            if type(entry[key])==dict else entry[key]
                        for key in headers))
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(values)
    content = output.getvalue()
    output.close()
    return content

def table_to_csv(data: dict):
    headers = []
    values = []
    array_fields = []
    for entry in data:
        for key in entry:
            if type(data[0][key]) == dict and type(data[0][key]["value"]) == list:
                array_fields.append(key)
            headers.append(key)

    
    for entry in data:
        total_rows = len(entry[array_fields[0]]["value"])
        for index in range(0, total_rows):
            values.append((entry[key]["value"]
                                if type(entry[key])==dict and type(entry[key]["value"])!=list 
                                else entry[key]["value"][index] if type(entry[key])==dict and type(entry[key]["value"])==list
                                else entry[key]
                            for key in headers))
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        writer.writerows(values)
        content = output.getvalue()
        output.close()
        return content
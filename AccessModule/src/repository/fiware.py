import requests

import config
from schemas import DataCatalogCreate

def get_datacatalog(catalog_id: str) -> requests.Response:
    url = config.ORION_URL + config.ORION_PATH_GET_ENTITY.format(catalog_id)
    headers = {"Link": f'<{config.FIWARE_CONTEXT}>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'}
    response = requests.get(url, headers=headers)
    return None if not response.ok else response

def send_entity(entity_json: list[dict]) -> requests.Response:
    print(entity_json)
    url = config.ORION_URL + config.ORION_PATH_UPLOAD_ENTITY
    headers = {"Content-Type": "application/ld+json"}
    response = requests.post(url, json=entity_json, headers=headers)
    return None if not response.ok else response

def subscribe(catalog_id: dict) -> requests.Response:
    url = config.ORION_URL + config.ORION_PATH_SUBSCRIBE
    headers = {"Content-Type": "application/ld+json"}
    response = requests.post(url=url, json=catalog_id, headers=headers)
    return None if not response.ok else response

def delete(entity_id: str) -> requests.Response:
    url = config.ORION_URL + config.ORION_PATH_DELETE.format(entity_id)
    response = requests.delete(url=url)
    return None if not response.ok else response

def get_specific_entity(entity_full_id: str):
    url = config.ORION_URL + config.ORION_PATH_GET_ENTITY.format(entity_full_id)
    headers = {"Link": f'<{config.FIWARE_CONTEXT}>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'}
    response = requests.get(url, headers=headers)
    return None if not response.ok else response

def get_entity_full(type_id: str, method: str = "keyValues", fields: list[str] = ['*'], query: str = None):
    url = config.ORION_URL + config.ORION_PATH_GET
    headers = {"Link": f'<{config.FIWARE_CONTEXT}>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'}

    params = []
    params.append(("type", type_id))
    if method:
        params.append(("options", method))
    if fields and len(fields) > 0 and "*" not in fields:
        params.append(("attrs", ','.join(fields)))
    if query:
        params.append(("q", query))
    print(params)
    response = requests.get(url=url, params=params, headers=headers)
    return None if not response.ok else response

def get_entity(type_id: str, method: str = "keyValues", entities: list[str] = None, fields: list[str] = ['*'], filters: dict = {}):
    get_entity_full(type_id, method, fields, "|".join([f"name~={entitie}" for entitie in entities]) if entities and len(entities)>0 else None)

def query_entity(type_id: str, entity_patterns:list[str], attributes: list[str] = None):
    url = config.ORION_URL + config.ORION_PATH_QUERY
    headers = {"Link": f'<{config.FIWARE_CONTEXT}>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'}
    body = {
       
    }
    if entity_patterns and len(entity_patterns) > 0:
        body["entities"] = [
            {
                "idPattern": entity_pattern,
                "type": type_id
            }
        for entity_pattern in entity_patterns]
    else:
        body["entities"] = [
            {
                "idPattern": ".*",
                "type": type_id
            }
        ]
    if attributes and len(attributes) > 0:
        body["attrs"] = attributes 
    print(body)
    response = requests.post(url=url, json=body, headers=headers)
    return None if not response.ok else response

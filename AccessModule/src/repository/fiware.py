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

def get_entity(type_id: str, method: str = "keyValues", entities: list[str] = None, fields: list[str] = ['*'], filters: dict = {}):
    url = config.ORION_URL + config.ORION_PATH_GET

    params = []
    params.append(("type", type_id))
    if method:
        params.append(("options", method))
    if fields and len(fields) > 0 and "*" not in fields:
        params.append(("attrs", ','.join(fields)))
    if entities:
        params.append(("q", "name~=[" + ']|['.join(entities) + ']'))
    # for filter in filters:
    #     params.app
    response = requests.get(url=url, params=params)
    return None if not response.ok else response

def query_entity(type_id: str, entity_patterns:list[str], attributes: list[str] = None):
    url = config.ORION_URL + config.ORION_PATH_QUERY
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
    response = requests.post(url=url, json=body)
    return None if not response.ok else response

import os
FIWARE_CONTEXT = os.getenv("ORION_CONTEXT") 
ORION_URL = os.getenv("ORION_URL") 
# ORION_URL = "http://localhost:1026"
ORION_PATH_UPLOAD_ENTITY = "/ngsi-ld/v1/entityOperations/upsert"
ORION_PATH_SUBSCRIBE = "/ngsi-ld/v1/subscriptions"
ORION_PATH_DELETE = "/v1/contextEntities/{}"
ORION_PATH_GET = "/ngsi-ld/v1/entities"
ORION_PATH_GET_ENTITY = "/ngsi-ld/v1/entities/{}"
ORION_PATH_QUERY = "/v2/op/query"

ORION_ENTITY_PREFIX = "urn:ngsi-ld"
QL_NOTIFY = os.getenv("QUANTUMLEAD_NOTIFY")
QL_NAME = "quantumlead"

CATALOG_ENTITY = "datacatalog"
USER_ENTITY = "users"
SUBSCRIPTION_ENTITY = "subscription"

# FIWARE_FILE_PATH = "/Users/paula.gallucci/EURECAT-Proyectos/Impetus-OpenDataSpace/AccessModule/files"
FIWARE_FILE_PATH = os.getenv("FIWARE_FILES_PATH")
FIWARE_FILE_URL_FORMAT = "{}/download/{}/{}/{}"
FIWARE_FILE_FORMAT = "{}/{}/{}/"
FIWARE_FILE_PROPERTY ="file_url"
FIWARE_FILENAME_PROPERTY ="filename"
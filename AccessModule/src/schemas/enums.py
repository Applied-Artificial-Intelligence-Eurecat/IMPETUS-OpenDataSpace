
from enum import Enum

class OutputFormat(str, Enum):
    CSV = "CSV"
    JSON = "JSON"


class TypeCatalog(str, Enum):
    TIMESERIES = "TIMESERIES"
    FILE = "FILE"
    TABLE = "TABLE"
    GENERIC = "GENERIC"
    EXTERNAL = "EXTERNAL"


class TypeAttribute(str, Enum):
    STRING = "STRING"
    INTEGER = "INTEGER"
    DOUBLE = "DOUBLE"
    COORDINATE = "COORDINATE"
    TIMESTAMP = "TIMESTAMP"
    OBJECT = "OBJECT"

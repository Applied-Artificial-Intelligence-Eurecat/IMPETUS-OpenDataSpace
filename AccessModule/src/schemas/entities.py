from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from schemas.enums import OutputFormat

class GeneralEntityRequest(BaseModel):
    datacatalog_id: str
    id: str
    tags: Optional[List[str]]
    model_config: ConfigDict = ConfigDict(extra='allow')


class TimeSeriesEntry(BaseModel):
    id: str
    timestamp: int
    tags: Optional[List[str]]
    model_config: ConfigDict = ConfigDict(extra='allow')


class TimeSeriesRequest(BaseModel):
    datacatalog_id: str
    values: List[TimeSeriesEntry]

class TimeFilter(BaseModel):
    start_date: int
    end_date: str

class QueryRequest(BaseModel):
    catalog_id: str
    entities: List[str]
    fields: List[str]
    time_filter: Optional[TimeFilter] = None
    output: OutputFormat = OutputFormat.CSV

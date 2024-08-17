# Open Data Space v2
This module provides a logic layer for the `orion-ld` Context Broker and other fiware compatible software.

It offers the capability of storing generic documents and files organized by Data Catalogs, and provides a simplified API layer to easily upload and download the data without specifying the full `NGSI-LD` properties in each request.

## Usage
- [OpenAPI Documentation](docs/openapi.json)
### Create a DataCatalog
Before being able to upload actual data, it is mandatory to define a DataCatalog.

The DataCatalog will define the data structure, context structure, and can provide a generic context for all data related to this DataCatalog.

To efficiently store different kinds of data, there are different types of DataCatalogs available.

| **Type of Data** 	| **Usage**                                                                                                                                                                       	|
|------------------	|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	|
| TABLE            	| Used to store a table with records originally stored as a CSV file.                                                                                                             	|
| TIMESERIES       	| Instead of recording a value for an entity only, a TimeSeries DataCatalog will store the full history of data. A specific timestamp can be specified to upload historical data. 	|
| FILE             	| Entities from a File DataCatalog will be associated with any file type.                                                                                                         	|
| GENERIC          	| Any other data that can be represented as a JSON object can be related to an entity from a generic DataCatalog.                                                                 	|

The DataCatalog can be created into the Platform through the Open Data Space API.

 **POST** /DataCatalog
>```json
> {
>  "name": "string",
>  "description": "string",
>  "is_public": true,
>  "type": "TIMESERIES",
>  "tags": [
>    "string"
>  ],
>  "extra_relationships": [
>    {
>      "context_key": "string",
>      "context_description": "string",
>      "relation_entity": "string",
>      "relation_type": "string"
>    }
>  ],
>  "catalog_context": [
>    {
>      "context_key": "string",
>      "context_description": "string",
>      "context_value": "string"
>    }
>  ],
>  "entities_context": [
>    {
>      "context_key": "string",
>      "context_description": "string",
>      "context_type": "STRING"
>    }
>  ]
>}
>```
> **Name**\
> Name given to identify the DataCatalog. Must be unique for the user that is creating the DataCatalog
>
> **Description**\
> Text to give some additional informations to the users. 
>
> **Is Public**\
> True for allow any user insert their own data related to this DataCatalog. 
>
> **Type**\
> The DataCatalog type (Generic, Table, File or Timeseries)
>
> **Tags**\
> Custom tags to easily filter the available datacatalogs
>
> **Extra Relationships**\
> Relations to other platform entities and datacatalogs to provide additional context to the DataCatalog
>
> **Catalog Context**\
> DataCatalog specific context. It will provide filtrable properties to the datacatalog and a static key-value for all the entities related to this DataCatalog
>
> **Entities Context**\
> It defines the entities context structure. Each upload entity related to this DataCatalog must provide a value for each field defined here.
> 

### Upload Data
As soon as the DataCatalog has been created, you can upload registres of Data to the platform through the specific endpoints.

> **FILES** `insert/file`
```
entity:         entityId
datacatalog:    catalogId
metadata:       {entity context JSON}
file:           file.ext
```
> **TABLE**  `insert/table`
```
entity:         entityId
datacatalog:    catalogId
file:           table.csv
```


> **TIMESERIES** `insert/timeseries`
```json
{
  "datacatalog_id": "catalogId",
  "values": [
    {
      "id": "entityId",
      "timestamp": 329123921,
      "contextProp1": "exampleValue",
      ...
    }
  ]
}
```

> **GENERIC** `insert/generic`
```json
{
  "datacatalog_id": "catalogId",
  "id": "entityId",
  "contextProp1": "exampleValue",
  ...
}
```

You can find more information about the available endpoints and calls in the Swagger documentation.

### Retrieve Data
The available data can be retrieved through the `/query` endpoint.

It requires specifying a DataCatalog entity to perform the query, and additional filter queries are available.

**POST `/query`**
> ```json
> {
>  "catalog_id": "string",
>  "entities": [
>    "string"
>  ],
>  "fields": [
>    "string"
>  ],
>  "time_filter": {
>    "start_date": 0,
>    "end_date": 0
>  },
>  "output": "CSV"
> }
>```
>**Catalog ID**\
> The DataCatalog ID, in the format {catalog_owner}:{catalog_name}.
>
>**Entities**\
> List of entities from the DataCatalog to fetch. An empty list will retrieve all available entities. It is possible to specify a Regex pattern.
>
>**Fields**\
> List of fields from the entity to fetch. An empty list will retrieve all available fields.
>
>**Time Filter**\
> Optional for Time Series data. The start and end parameters must be specified in Epoch milliseconds.
>
> **Output**\
> Specifies the data format. You can choose between `JSON` and `CSV`.


The list of available DataCatalogs can be retrieved through a `POST` call to `/datacatalog/page`.

**POST `/datacatalog/page`**

> ```json
> {
>  "id_pattern": "string",
>  "owner": "string",
>  "tags": [
>    "string"
>  ],
>  "types": [
>    "string"
>  ],
>  "size": 10,
>  "page": 1
> }
>```
>**ID Pattern**\
>The DataCatalog ID. It is possible to specify a Regex expression (like `.*` to retrieve any).
>
>**Owner**\
> Specify the DataCatalog owner. An empty string will indicate any owner. This parameter will be ignored if an ID Pattern is specified.
>
>**Tags**\
> List of tags from the DataCatalog to filter. Tag entries can be defined as regex expressions.
>
>**Types**\
> DataCatalog types to fetch.
>
> **Size**\
> Maximum number of DataCatalog entries to retrieve in the query.
>
> **Page**\
> Page number of the request.

## Development
### Requirements
**Minimum Requirements**
- Docker
- Python 3.12

**Recommended Requirements**
- PGAdmin (or another relational database management tool)
- MongoCompass
- Visual Studio Code

### Installation
It is recommended to use _Python virtual environments_ to avoid compatibility issues with libraries from other projects.


You can create one with:
```
python3 -m venv AccessModule/env
```
and activate it with:

- Linux:
```
source AccessModule/env/bin/activate
```
- Windows:
```
./AccessModule/env/Scripts/activate.sh
```

You need to install the Python dependencies. You can use the `requirements.txt` file:
```
python3 -m pip install -r AccessModule/requirements.txt
```

### Execution
All resources beyond the API are orchestrated via Docker Compose to facilitate the deployment and development of Open Data Space tools.

For this, Docker must be running, and you can deploy it using the command:
```
docker compose up -f docker-compose.dev.yaml
```
For Mac M1/M2 or other devices using ARM architectures, you should deploy using the `docker-compose.dev.mac.yaml` file:


```
docker compose up -f docker-compose.dev.mac.yaml
```

To run the API in development, it is recommended to use the following command via Uvicorn:
```
cd AccessModule/src
uvicorn main:app --reload
```


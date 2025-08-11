# Usage

## Local Installation

For local development, the package can be installed locally in editable mode:

```bash
pip install -e .
```

This will also install the required dependencies, taken from the setup.py, install_requires section (which will also be installed if this package is later installed via pip).
If you want to just test the dependencies, you can install them using the requirements.txt file:

```bash
pip install -r requirements.txt
```

The requirements.txt and setup.py files should be kept in sync, so that the package can be installed in the same way in the production environment. Unfortunatelly, the setup.py file does not support the use of the requirements.txt file, so the dependencies have to be listed in both files.

## Connect

Interactive with client id from your OAuth 2 provider:

```python
from seven2one import TechStack
client = TechStack(host, client_id)
```

In unattended scripts via service account:

```python
from seven2one import TechStack
client = TechStack(host, client_id, service_account_name='my-serviceuser', service_account_secret='some token')
```

## Logging

By default the Python lib writes logs to console and to the server the user connects to.

Configure log levels and server endpoint by environment variables if needed:

| Variable       | Description | Default |
| -------------- | ----------- | ------- |
|LOGLEVEL        | Set the log level for console output | 'INFO' |
|LOGLEVEL_SERVER | Set the log level for logs sent to the server (Loki). Log levels are 'ERROR', 'WARNING', 'INFO' and 'DEBUG'. | 'ERROR' |
|LOG_TO_SERVER   | Disable logging to Loki server | 'TRUE' |
|LOG_SERVER      | Overwrite the log server endpoint if e.g. running inside the same cluster | 'https://{host}/logging/loki/api/v1/push' |

## Basic read operations

```python
client.inventories()
client.items('appartments', references=True)
client.inventoryProperties('appartments')
client.propertyList('appartments', references=True, dataTypes=True)
```

## Write operations

### Create inventory

```python
properties = [
   {
        'dataType': 'DATE_TIME_OFFSET',
        'name': 'fieldDATETIMEOFFSET',
        'nullable': True
    },
    {
        'dataType': 'BOOLEAN',
        'name': 'fieldBOOLEAN',
        'nullable': True
    }
]

client.createInventory('testInventory', properties)
```

### Add (basic) items

```python
items =  [
        {
        "fieldSTRING": "bla",
        "fieldDECIMAL": 0,
        "fieldLONG": 0,
        "fieldINT": 0,
        "fieldBOOLEAN": True,
        "fieldDATETIME":  "2021-09-14T00:00:00.000Z",
        "fieldDATETIMEOFFSET": "2021-09-14T00:00:00.000Z"
    }
]

addBasicItems('testInventory', items)

```

## Advanced

To change one or more used service endpoints (e.g. for tests against custom deployments) you can overwrite them by environment variables. You have to provide complete URL's.

| Environment variable | Description | Example |
| -------------------- | --|--|
| IDENDITYPROVIDER_URL     | Identity provider base url | `https://authentik.mytechstack` |
| DYNAMIC_OBJECTS_ENDPOINT | DynO graphQL endpoint | `https://run.integrationtest.s2o.dev/itest-375545a3-dynamic-objects/graphql/` |
| AUTOMATION_ENDPOINT      | Automation service graphQL endpoint |  |
| SCHEDULE_ENDPOINT        | Schedule service graphQL endpoint | |
| PROGRAMMING_ENDPOINT     | Programming service graphQL endpoint | |
| TIMESERIES_ENDPOINT      | TimeSeries gateway graphQL endpoint | |
| LOGGING_ENDPOINT         | Logging reverse proxy endpoint | `http://mytechstack:8123/loki/api/v1/push` |
| AUTHORIZATION_ENDPOINT   | Authorization service graphQL endpoint | |

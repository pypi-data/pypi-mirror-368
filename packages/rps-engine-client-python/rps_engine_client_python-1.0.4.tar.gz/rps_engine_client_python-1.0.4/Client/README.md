#  Quick Start Guide `rps-engine-client-python`

This guide explains how to install and use the `rps-engine-client-python` library from PyPI to interact with the REGDATA's RPS Engine API.

---

## Install the Library

Install the latest version from PyPI using pip:

```bash
pip install rps-engine-client-python
```

---

## Configure Your Environment

The library requires configuration for authentication and engine connection. You can provide this information via a `settings.json` file or `.env` file.

### 1. Location of the configuration file

The default location of the configuration file is the root project folder. If a dedicated folder or location is necessary, it could be applied by setting the environment variable `RPS_CLIENT_CONFIG_DIR`.
- Set configuration file location: 
 ```powershell
$env:RPS_CLIENT_CONFIG_DIR = "path/to/config_folder"
```
- Remove file location:
 ```powershell
Remove-Item Env:RPS_CLIENT_CONFIG_DIR
```

### 2.  Choosing source to load Rights Contexts and Processing Contexts

Choose by setting the `context_source` parameter when creating the `engine` instance: 

1. To load from JSON files (the default behavior, `external_source_files` must be included in the configuration file) = `ContextSource.JSON`.
2. From the configuration settings (inside `.env` or `settings.json`) = `ContextSource.SETTINGS`.

Example:

```python
engine = EngineFactory.get_engine(context_source=ContextSource.JSON)
```

### 3. Create the configuration file

#### Option A - Create a `settings.json` file

```json
{
  "rps": {
    "engineHostName": "https://your-rps-engine-url",
    "identityServiceHostName": "https://your-identity-url",
    "clientId": "YOUR_CLIENT_ID",
    "clientSecret": "YOUR_CLIENT_SECRET",
    "timeout": 30
  },
  // Specify either the "external_source_files" section or the "rights_contexts" & "processing_contexts", according to the contexts source
  "external_source_files": {
    "rightsContextsFilePath": "path/to/rights_contexts.json",
    "processingContextsFilePath": "path/to/processing_contexts.json"
  },
  "rights_contexts": {
    "Admin": {
      "evidences": [
        { "name": "Role", "value": "Admin" }
      ]
    }
  },
  "processing_contexts": {
    "Protect": {
      "evidences": [
        { "name": "Action", "value": "Protect" }
      ]
    },
    "Deprotect": {
      "evidences": [
        { "name": "Action", "value": "Deprotect" }
      ]
    }
  }
}
```

- Replace the URLs, `clientId`, and `clientSecret` with your actual values which are relevant to the Configuration in RPS CoreAdmin platform.
- If you want to load rights and processing contexts from JSON files, provide the correct file paths in `external_source_files`.

#### Option B - Using .Env file with Environment Variables

```bash
rps__engineHostName="https://your-rps-engine-url"
rps__identityServiceHostName="https://your-identity-url"
rps__clientId="YOUR_CLIENT_ID"
rps__clientSecret="YOUR_CLIENT_SECRET"
rps__timeout=30

// One of the followings:
external_source_files__rightsContextsFilePath=path/to/rights_contexts.json
external_source_files__processingContextsFilePath=path/to/processing_contexts.json

// OR
rights_contexts__Admin__evidences__0__name="Role"
rights_contexts__Admin__evidences__0__value="Admin"

processing_contexts__Protect__evidences__0__name=Action
processing_contexts__Protect__evidences__0__value=Protect
processing_contexts__Deprotect__evidences__0__name=Action
processing_contexts__Deprotect__evidences__0__value=Deprotect
```
---

## Create a Python Script

Write a python script that uses the library.

Below is a minimal example which uses the [`EngineFactory`](Client/engine/engine_factory.py) class for the engine connection, getting the contexts from a JSON file.


```python
from Client.engine.engine_factory import EngineFactory
from Client.context_source import ContextSource
from Client.instance.rps_instance import RPSInstance
from Client.engine_context.processing_context import ProcessingContext
from Client.engine_context.rights_context import RightsContext
from Client.evidence import Evidence
from Client.value.rps_value import RPSValue

engine = EngineFactory.get_engine(context_source=ContextSource.JSON)

# Example usage
admin_rights_context = RightsContext(evidences=[Evidence(name='Role', value='Admin')])
protect_processing_context = ProcessingContext(evidences=[Evidence(name='Action', value='Protect')])

raw_first_name = RPSValue(instance=RPSInstance(className='User', propertyName='Name'), originalValue='Jonny')

request_context = engine.create_context().with_request(
    rps_values=[raw_first_name],
    rights_context=admin_rights_context,
    processing_context=protect_processing_context
)

request_context.transform_async()

print(f'Original: {raw_first_name.original}, Transformed: {raw_first_name.transformed}')
```


- See the [examples folder](https://github.com/your-org/rps-engine-client-python/tree/main/Client/Client/examples) in the source repository for more advanced usage patterns.

---

## Run Your Script


```bash
python your_script.py
```

---
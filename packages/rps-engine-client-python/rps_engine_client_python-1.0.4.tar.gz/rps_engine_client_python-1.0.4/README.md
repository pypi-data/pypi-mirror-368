# Introduction 
This project is a Python Client library for integrating with RPS Engine API for the sake of performing transformation to your data.

# Getting Started
**Pre requisites**
- Python version : >=3.10,<=3.11.9
- Install poetry for dependency management : https://python-poetry.org/docs/#installing-with-pipx
- **Enabled configuration** in RPS Core Admin website, filled with Transformation sequences, instances, rights and processing contexts.

*Disclaimer : This project was only tested with python 3.11*

## Starting the Application
The project uses poetry for dependency management and a pyproject.toml

To get started with poetry and you have pipx installed run
```bash
pipx install poetry 
```

Install the project dependencies (under the folder which contains the pyproject.toml)

```bash
poetry install
```

## Configuring the environment

The RPS Platform client supports flexible configuration through both `.env` file,  a `settings.json` file and environment variables. You can choose the method that best fits your deployment and development workflow.

The precedence order for loading configuration is : env -> settings.json 

### a. Location of the configuration file

The default location of the configuration file is the root project folder. If a dedicated folder or location is necessary, it could be applied by setting the environment variable `RPS_CLIENT_CONFIG_DIR`.
- Set configuration file location: 
 ```powershell
$env:RPS_CLIENT_CONFIG_DIR = "path/to/config_folder"
```
- Remove file location:
 ```powershell
Remove-Item Env:RPS_CLIENT_CONFIG_DIR
```

### b.  Choosing source to load Rights Contexts and Processing Contexts

Choose by setting the `context_source` parameter when creating the `engine` instance: 

1. To load from JSON files (the default behavior, `external_source_files` must be included in the configuration file) = `ContextSource.JSON`.
2. From the configuration settings (inside `.env` or `settings.json`) = `ContextSource.SETTINGS`.

Example:

```python
engine = EngineFactory.get_engine(context_source=ContextSource.JSON)
```


#### Option A - Create a `settings.json` file

Must be a valid JSON syntax for more complex or nested configuration. Using double quotes for all keys and string values, and proper nesting for objects and arrays. This is the recommended approach for most use cases.

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
Use standard key-value pairs, one per line, with no quotes or commas, (e.g., KEY=value) for environment-based configuration (with __ as a nesting separator for env variables)

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

## Examples of usage

The examples folder contains several ready-to-run scripts that demonstrate different usage scenarios of the RPS Engine client. Each example is designed to help you understand how to configure, invoke, and extend the client for your own use cases. Below is a brief explanation of each example:

- [`SimpleUsageExample`](Client/Client/examples/simple_usage_example.py)
Demonstrates the most basic workflow: manually creating rights and processing contexts, constructing RPSValue objects, and performing protection and deprotection operations. This is a good starting point for understanding the core API and data flow.

- [`ContextsProvidedByResolverExample`](Client/Client/examples/contexts_provided_by_resolver_example.py)
shows how to use context names instead of full context objects. The example leverages the context resolver to fetch rights and processing contexts by name, simplifying the request construction process.

- [`UsageWithDependenciesExample`](Client/Client/examples/usage_with_dependencies_example.py)
Illustrates how to handle RPSValue objects that have dependencies (such as minimum or maximum values). This is useful for scenarios where the transformation logic depends on related data fields.

- [`UsageWithRelatedObjectExample`](Client/Client/examples/usage_with_related_object_example.py)
Demonstrates how to load data from an external JSON file, convert it into RPSValue objects, and perform protection operations. This example is ideal for batch processing or integrating with external data sources.

**Each example is self-contained and can be run directly.** Review and adapt these scripts to accelerate your own integration with the RPS Platform.

```powershell
poetry run python client/examples/usage_with_related_object_example.py
```
---


# Contribute
To add libraries update the **dependencies** section in the ``pyproject.toml`` 

It is mandatory to use version pins for the dependency to ensure reproducible builds 
```toml
dependencies = [
    "pydantic (>=2.10.6,<3.0.0)",
    "pydantic-settings (>=2.8.1,<3.0.0)",
    "dotenv (>=0.9.9,<0.10.0)" ,
    "python-dotenv==1.0.0",
    "certifi==2023.7.22",
    "<INSERT YOUR DEPENDENCY>"
]
```

To install the dependencies update the peotry.lock with poetry
```
poetry lock
```

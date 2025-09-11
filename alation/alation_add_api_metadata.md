# Alation: Register Metadata using API

## What is Alation

When your datasets, reports, and other assets are spread across environments (AWS, Azure, GitHub, Power Bi etc), it can take days to hunt down the right information (to find out where is what data). Metadata management is the cornerstone of modern data strategy. Like a skilled librarian, it ensures the right data is cataloged, easy to locate, properly maintained, and aligned with organizational needs. One of the Metadata management solutions is Alation.

[Short explanation 1](https://youtu.be/G3OT-GNxK0w?feature=shared)
[Short explanation 2](https://youtu.be/sEgPNk-vSyc?feature=shared)

## Connectors

Alation provides connectors for over 120 sources.
[all connectors](https://www.alation.com/product/connectors/all-connectors/)

Alation can extract most of the metadata automatically but not all.
Let's take the example of Denodo & Alation case. Alation has a connector for Denodo.
[Denode connector](https://www.alation.com/docs/en/latest/OpenConnectorFramework/DataSourceConnectors/Denodo/DenodoOCFConnectorOverview.html)
[Connection explanation by Denodo](https://community.denodo.com/kb/en/view/document/How%20to%20integrate%20Alation%20with%20Denodo)

Supported Authentications methods:

- Authentication with username and password
- SSL Authentication

Alation automatically extracts following metadata :

- List of schemas
- List of tables
- List of views
- List of columns
- popularity of the data
- Primary key information for extracted tables
- Retrieval of data samples from extracted table
- Retrieval of data samples from extracted columns

But, connector cannot extract:

- Column comments
- Column data types
- Source comments

To compliment the metadata extracted by the connector (to add the metadata that Alation does not automatically extract), API can/should be used.

## Create Custom Fields

Before explaining how to use API to add metadata fields to the data sources, I need to explain custom fields.

On the Alation UI, the data sources such as tables, schemas etc. are presented with the metadata fields like `title` and `description`. Often times default metadata fields such as `title`, `description` etc. is enough, but if you need to add new, custom fields, [it is possible](https://www.alation.com/docs/en/latest/steward/TemplatesAndCustomFields/index.html).

Alation has [built-in fields](https://www.alation.com/docs/en/latest/steward/TemplatesAndCustomFields/AboutTemplatesAndFields.html) such as `title` and `description`. In addition tot hat, Alation also allows creation of the custom fields. Custom fields are reusable objects.
Custom fields are attached to object templates. A (object) template specifies how metadata is presented for a type of object (table, schema, column etc).
Each object type has its own template.

Almost all the objects of the same type share a common template, in other words, a template applies to all the objects of the same type. For example, all the schemas use the same schema template.

To add a custom field (to a schema).

1. You must have the Catalog Admin or Server Admin role to customize the Alation catalog.
1. [Create a custom field](https://www.alation.com/docs/en/latest/steward/TemplatesAndCustomFields/ManageCustomFields.html?version=neo)
1. [Edit the (schema) template](https://www.alation.com/docs/en/latest/steward/TemplatesAndCustomFields/ManageTemplates.html#edit-a-template) by adding the newly created custom field.

![graph](https://imgur.com/pLOVpGL.png)
_(it is AI generated image, there are some inaccuracies in the text)_

Note: Alation assigns an ID to every custom field. The title of the custom field might be "Data Sensitivity" and its field_id 1002.

## APIs

### Upload Logical Metadata (ULM) API

This api is deprecated. DO NOT USE IT. (Alation doesn’t recommend using the ULM API.)
[Upload Logical Metadata (ULM) API](https://developer.alation.com/dev/reference/upload-logical-metadata)
[Upload Logical Metadata (ULM) API Deprecation](https://docs.alation.com/en/latest/releases/releasenotes/ReleaseNotes20243.html#upload-logical-metadata-ulm-api-deprecation)

### Relational Integration API

To update titles, descriptions and custom fields, use [Relational Integration APIs](https://developer.alation.com/dev/reference/relational-integration-api-v2-overview).

Permissions needed: Data Source Viewer or Data Source Admin

API Payload limitation per api call:

|Object Type| Max Objects in POST Payload|
|----|----|
|Schema | 1,000|
|Table | 1,000|
|Column | 10,000|

[Update schema example](https://developer.alation.com/dev/reference/patchschemas)

```python
import requests

url = "https://alation_domain/integration/v2/schema/"

payload = [
    {
        "key": "95.employees", # schema name is employees
        "title": "Schema for employees data.",
        "description": "Stores all the tables related to employees from marketing department.",
        "db_comment": "This schema is part of company database storing important PII data.",
        "custom_fields": [
             {
            "field_id": 101,
            "value": "Finance Team"       // Business Owner custom field
            "op": "replace"
            },
            {
            "field_id": 102,
            "value": "Highly Confidential" // Data Sensitivity custom field
            "op": "replace"
            }
        ]
    }
]
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "TOKEN": "my_secret_token"
}

response = requests.patch(url, json=payload, headers=headers)

print(response.text)
```

|Term|Explanation|
|---|---|
|key|Name of a schema/table etc|
|title|title of a schema/table (It exits only in Alation’s catalog, not in the database.)|
|db_comment|Comments on the schema from the data source.|
|op|Operation need to perform for custom field. It can be `add`, `remove` or `replace`. `add` and `remove` operation are only apllicable for MULTI_PICKER and OBJECT_SET. `replace` is applicable for all custom fields. |

`custom_fields` should be array of objects.
Alation assigns an ID to every custom field. The title of the custom field might be "Data Sensitivity" and its field_id 1002.
But, Relational Integration API does NOT allow creation of new custom fields. It can also update them.

> These custom fields first should be associated with the schema otype template. You can create and add a new custom field to the schema otype template from Customize Catalog option in the UI.

### Custom Field Value API

[Custom Field Values Async API](https://developer.alation.com/dev/reference/putcustomfieldvaluesasync) can be used to update custom fields.

Note: The Custom Field Value APIs will not allow you to update titles and descriptions on schemas, tables, and columns. Use Relational Integration API instead.

Limit: Maximum of 10,000 objects per request.

```python
import requests

url = "https://alation_domain/integration/v2/custom_field_value/async/"

payload = [
    {
        "field_id": 10006, # custom field id
        "oid": 5,  # id of the object this custom field belongs to
        "otype": "table", # the type of the object this field belongs to
        "ts_updated": "2025-09-10T07:07:33.884Z",
        "value": "my custom field value"
    },
    {
        "field_id": 10007,
        "oid": "7", # id of the object this custom field belongs to
        "otype": "attribute", # the type of the object this field belongs to
        "ts_updated": "2025-09-10T07:07:33.884Z",
        "value": ["high, medium, low"]
    }
]
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "TOKEN": "my_secret_token"
}

response = requests.put(url, json=payload, headers=headers)

print(response.text)
```

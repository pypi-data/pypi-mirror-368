# Quipubase Client

Interactive API Docs

- [Quipubase Client](#quipubase-client)
- [Quipubase](#quipubase)
- [Quipubase Python Client](#quipubase-python-client)
	- [Introduction](#introduction)
	- [Installation](#installation)
	- [Getting Started](#getting-started)
	- [Collections](#collections)
	- [Objects (Pub/Sub)](#objects-pubsub)
	- [Vectors](#vectors)
	- [Live Query](#live-query)
	- [Blobs (File Storage)](#blobs-file-storage)

# Quipubase

![Quipubase Logo](logo.png)

# Quipubase Python Client

API Docs

[Quipubase API Docs](https://quipubase.oscarbahamonde.com/docs)

## Introduction

Welcome to the interactive documentation for the official asynchronous Python client for the Quipubase API. This guide provides everything you need to get started and effectively use the library's features.

This client is built on top of \`httpx\` and \`pydantic\`, and extends the \`openai\` Python client, providing a familiar interface for interacting with all Quipubase resources. You can navigate through the different API resources using the sidebar to explore their functionalities and see practical code examples.

## Installation

To get started, install the library from PyPI using pip. It's recommended to do this within a virtual environment.

```bash
pip install quipubase
```

## Getting Started

First, initialize the `Quipubase` client with your API key and the base URL of the service. The following example demonstrates how to set up the client and make a simple request to verify your connection.

```python
import asyncio
from quipubase import Quipubase

# It's recommended to load the API key from environment variables
# from os import getenv
# api_key = getenv("QUIPUBASE_API_KEY", "YOUR_API_KEY")

client = Quipubase(
    base_url="https://quipubase.oscarbahamonde.com/v1",
    api_key="YOUR_API_KEY"
)

async def main():
    # Your asynchronous code will go here
    # Example: list all collections
    try:
        collections = await client.collections.list()
        print("Successfully connected to Quipubase!")
        print(collections)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
```

## Collections

Collections define the schema for your data objects. You can use the `collections` resource to create, list, retrieve, and delete collections. A collection's schema, defined using JSON Schema, ensures data integrity for all objects stored within it.

```python
async def manage_collections():
    # Create a new collection with a JSON schema
    schema = {
        "type": "object",
        "properties": {
            "user_id": {"type": "string"},
            "post_content": {"type": "string"},
            "timestamp": {"type": "string", "format": "date-time"}
        },
        "required": ["user_id", "post_content"]
    }
    
    new_collection = await client.collections.create(json_schema=schema)
    print("--- Created Collection ---")
    print(new_collection)
    
    collection_id = new_collection.id

    # List all collections
    all_collections = await client.collections.list()
    print("\\n--- All Collections ---")
    print(all_collections)

    # Delete the collection
    delete_response = await client.collections.delete(collection_id=collection_id)
    print("\\n--- Deleted Collection ---")
    print(delete_response)

# To run: asyncio.run(manage_collections())
```

## Objects (Pub/Sub)

Objects are individual records within a collection. The `objects` resource provides real-time, bidirectional communication using a publish/subscribe model. You can publish events (like create, update, delete) to a collection and subscribe to receive real-time updates from other clients.

```python
async def manage_objects(collection_id: str):
    # 1. Publish a 'create' event with new data
    print("--- Publishing Message ---")
    pub_response = await client.objects.pub(
        collection_id=collection_id,
        event="create",
        data={"user_id": "user-123", "post_content": "Hello from Python!"}
    )
    print(pub_response)

    # 2. Subscribe to events from the collection
    print("\\n--- Subscribing to Events (waiting for 1 message) ---")
    async for event in client.objects.sub(collection_id=collection_id):
        print("Received event:")
        print(event)
        # Add logic to break the loop as needed
        break

# You need a valid collection_id to run this example
# To run: asyncio.run(manage_objects("your_collection_id"))
```

## Vectors

The `vector` resource allows you to perform powerful vector search operations. You can upsert text data, which Quipubase will automatically convert into vector embeddings using the specified model. You can then query the store to find semantically similar content, which is ideal for search, recommendations, and RAG applications.

```python
async def manage_vectors():
    NAMESPACE = "my-document-store"

    # 1. Upsert text into a namespace
    print("--- Upserting Vectors ---")
    upsert_response = await client.vector.upsert(
        namespace=NAMESPACE,
        input=["The sun is the center of our solar system.", "A banana is a yellow fruit."],
        model="gemini-embedding-001"
    )
    print(upsert_response)

    # 2. Query for similar text
    print("\\n--- Querying Vectors ---")
    query_response = await client.vector.query(
        namespace=NAMESPACE,
        input="What is a banana?",
        top_k=1,
        model="gemini-embedding-001"
    )
    print(query_response)

# To run: asyncio.run(manage_vectors())
```

## Live Query

The `query` resource lets you create, manage, and query live datasets from various data sources like files, MongoDB, or PostgreSQL. This allows you to run SQL-like queries against data sources that don't natively support them, all through a unified API.

Conceptual Example

The following code is a conceptual example. The service must have network access to the URI provided for it to work.

```python
async def manage_live_query():
    # 1. Create a dataset from a source
    print("--- Creating Live Query Dataset ---")
    try:
        create_response = await client.query.create(
            engine="file",
            uri="public_data.csv", # A URI accessible by the Quipubase service
            query="SELECT * FROM root",
            key="my-csv-dataset"
        )
        print(create_response)

        # 2. Retrieve data by querying the live dataset
        print("\\n--- Retrieving from Live Query Dataset ---")
        retrieve_response = await client.query.retrieve(
            key="my-csv-dataset",
            query="SELECT * FROM `root` WHERE category = 'A' LIMIT 5"
        )
        print(retrieve_response)
    except Exception as e:
        print(f"Could not run live query example: {e}")
        print("This is expected if the remote URI is not configured.")

# To run: asyncio.run(manage_live_query())
```

## Blobs (File Storage)

The `blobs` resource provides a simple and effective interface for file storage. You can upload, retrieve, and manage files and binary data ("blobs") in designated buckets, making it easy to handle assets for your application.

```python
async def manage_blobs():
    BUCKET = "my-general-bucket"
    FILE_PATH = "my-test-file.txt"

    # 1. Create a file to upload
    with open(FILE_PATH, "w") as f:
        f.write("This is a test file for Quipubase blob storage.")
    
    # 2. Upload the file
    print("--- Uploading File ---")
    with open(FILE_PATH, "rb") as f:
        upload_response = await client.blobs.create(
            path=f"uploads/{FILE_PATH}",
            file=f,
            bucket=BUCKET
        )
    print(upload_response)

    # 3. Retrieve the file's metadata
    print("\\n--- Retrieving File ---")
    retrieve_response = await client.blobs.retrieve(
        path=f"uploads/{FILE_PATH}", bucket=BUCKET
    )
    print(retrieve_response)

    # 4. Delete the file
    print("\\n--- Deleting File ---")
    delete_response = await client.blobs.delete(
        path=f"uploads/{FILE_PATH}", bucket=BUCKET
    )
    print(delete_response)

# To run: asyncio.run(manage_blobs())
```
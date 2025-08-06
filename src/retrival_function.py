import os
import json
from azure.cosmos import CosmosClient, exceptions
from azure.storage.blob import BlobServiceClient
import logging

COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")
COSMOS_DATABASE = os.getenv("COSMOS_DATABASE")
COSMOS_CONTAINER = os.getenv("COSMOS_CONTAINER")

BLOB_CONNECTION_STRING = os.getenv("BLOB_CONNECTION_STRING")
BLOB_CONTAINER = os.getenv("BLOB_CONTAINER", "billing-archives")

cosmos_client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
database = cosmos_client.get_database_client(COSMOS_DATABASE)
container = database.get_container_client(COSMOS_CONTAINER)

blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
blob_container_client = blob_service_client.get_container_client(BLOB_CONTAINER)

def estimate_blob_path_from_record_id(record_id):
    # Assuming the record_id starts with YYYYMMDD- , e.g., "20240515-abc123"
    try:
        date_str = record_id.split('-')[0]  # "20240515"
        year = date_str[:4]
        month = date_str[4:6]
        # Constructing blob path according to the saving info
        blob_path = f"archive/{year}/{month}/{record_id}.json"
        return blob_path
    except Exception as e:
        raise ValueError(f"Invalid record_id format: {record_id}") from e


def main(req):
    try:
        record_id = req.params.get('id')
        if not record_id:
            return {"status": 400, "body": "Missing 'id' parameter"}

        # Trying to get the data from Cosmos DB first
        try:
            response = container.read_item(item=record_id, partition_key=record_id)
            return {"status": 200, "body": response}
        except exceptions.CosmosResourceNotFoundError:
            pass  # If data Not found in Cosmos DB, falling back to blob storage

        # Fetching data from blob storage
        blob_path = estimate_blob_path_from_record_id(record_id)

        blob_client = blob_container_client.get_blob_client(blob_path)
        blob_data = blob_client.download_blob().readall()
        record = json.loads(blob_data)

        return {"status": 200, "body": record}

    except Exception as e:
        logging.error(f"Error retrieving record {record_id}: {e}")
        return {"status": 500, "body": f"Error: {str(e)}"}

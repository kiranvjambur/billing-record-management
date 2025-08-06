import os
import json
from datetime import datetime, timedelta
from azure.cosmos import CosmosClient, exceptions
from azure.storage.blob import BlobServiceClient
import logging

# Initializing DB clients with environment variables
COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")
COSMOS_DATABASE = os.getenv("COSMOS_DATABASE")
COSMOS_CONTAINER = os.getenv("COSMOS_CONTAINER")

BLOB_CONNECTION_STRING = os.getenv("BLOB_CONNECTION_STRING")
BLOB_CONTAINER = os.getenv("BLOB_CONTAINER", "billing-archives")

# Setting up DB clients
cosmos_client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
database = cosmos_client.get_database_client(COSMOS_DATABASE)
container = database.get_container_client(COSMOS_CONTAINER)

blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
blob_container_client = blob_service_client.get_container_client(BLOB_CONTAINER)

def main(mytimer):
    logging.info('Starting archival process...')
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=90)  # For 3 months old
        cutoff_iso = cutoff_date.isoformat()

        # Querying old records in the DB
        query = "SELECT * FROM c WHERE c.createdDate < @cutoffDate"
        parameters = [{"name": "@cutoffDate", "value": cutoff_iso}]
        items = list(container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))

        logging.info(f"Found {len(items)} items to archive")

        for item in items:
            created_date_str = item.get("createdDate")
            created_date = datetime.fromisoformat(created_date_str)
            year = created_date.year
            month = created_date.month

            blob_path = f"archive/{year}/{month}/{item['id']}.json"
            blob_data = json.dumps(item)

            # Upload data older than 3 months to blob
            blob_client = blob_container_client.get_blob_client(blob_path)
            blob_client.upload_blob(blob_data, overwrite=True)

            # Delete from Cosmos DB only after successful upload
            container.delete_item(item, partition_key=item["partitionKey"])  # Adjust the partition key as per schema as It wasn't specified in the assignment

            logging.info(f"Archived and deleted record ID: {item['id']}")

        logging.info('Archival process completed successfully.')

    except Exception as e:
        logging.error(f"Error in archival process: {e}")
        raise

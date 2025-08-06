# Azure Cost Optimization Challenge: Billing Records Tiered Storage Solution

## Overview

This project implements a tiered storage solution to reduce Azure Cosmos DB costs by archiving billing records older than 3 months to lower-cost Azure Blob Storage tiers. It provides a seamless access layer so users can query data transparently without API changes.

## Features

- Automatic archival of older billing records to Azure Blob Storage (Cool/Archive).
- Unified access layer fetching from Cosmos DB or Blob.
- Zero downtime migration and no data loss.
- Azure Functions implementation for serverless execution.
- Infrastructure deployment using Bicep.
- Monitoring and lifecycle management recommendations.

## Repository Structure

- `/src/` – Source code for Azure Functions (`archive_function.py`, `retrival_function.py`)
- `/infrastructure/` – Bicep template for Azure resources
- `/docs/` – Architecture and detailed documentation
- `.gitignore` – Git ignore settings

## Getting Started

1. **Deploy Infrastructure:** Use the Bicep template to create resources.
2. **Configure Environment:** Set environment variables for connection strings and keys.
3. **Deploy Functions:** Deploy the archival and access layer Azure Functions.
4. **Schedule Archival:** Configure Timer Trigger to run archival regularly.
5. **Use Access Layer:** Point your API calls to the access function endpoint.

## Dependencies

- Python 3.8+
- `azure-cosmos` package
- `azure-storage-blob` package

## Common edge cases and how to handle them:

- Record missing everywhere: Return “not found” to the user and log it for checking.
- Corrupted archived data: Catch errors when reading, log details, and notify the team to fix or restore backups.
- Archival function fails: Use retries, only delete data after confirming archive success, and make the process safe to rerun without problems.
- Duplicate or bad keys: Ensure IDs are unique and handle errors gracefully if conflicts arise.
- Partial migration: Save to archive first, confirm it’s safe, then delete from main database to avoid data loss.
- Sudden demand for old data: Monitor access. If old records get frequent requests, consider moving them to faster storage temporarily.
- Can’t figure out archive path: Keep a simple lookup table linking record IDs to archive locations.
- Storage limits hit: Watch storage usage and set alerts to expand capacity before problems happen.
- Data format changes: Version your stored data and convert old formats on access if needed.
- Permission issues: Use managed identities, keep keys safe, and monitor permission errors closely.



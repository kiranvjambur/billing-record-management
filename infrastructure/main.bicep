// Location for all resources
param location string = resourceGroup().location

// Name for Cosmos DB account
param cosmosAccountName string

// Name for Cosmos DB database
param cosmosDatabaseName string

// Name for Cosmos DB container
param cosmosContainerName string

// Name for Storage Account
param storageAccountName string

// Storage container name for blobs (default: 'billing-archives')
param blobContainerName string = 'billing-archives'

// Cosmos DB Account resource definition
resource cosmosAccount 'Microsoft.DocumentDB/databaseAccounts@2021-04-15' = {
  name: cosmosAccountName
  location: location
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    locations: [
      {
        locationName: location
      }
    ]
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
    enableFreeTier: true
  }
}

// Cosmos DB SQL Database resource
resource cosmosDatabase 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2021-04-15' = {
  name: '${cosmosAccountName}/${cosmosDatabaseName}'
  properties: {
    resource: {
      id: cosmosDatabaseName
    }
  }
  dependsOn: [
    cosmosAccount
  ]
}

// Cosmos DB Container resource definition with partition key
resource cosmosContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2021-04-15' = {
  name: '${cosmosAccountName}/${cosmosDatabaseName}/${cosmosContainerName}'
  properties: {
    resource: {
      id: cosmosContainerName
      partitionKey: {
        paths: ['/partitionKey']
        kind: 'Hash'
      }
    }
  }
  dependsOn: [
    cosmosDatabase
  ]
}

// Storage Account resource with Cool tier and LRS redundancy
resource storageAccount 'Microsoft.Storage/storageAccounts@2021-09-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Cool'  // Set default access tier to Cool for cost-saving
    minimumTlsVersion: 'TLS1_2'
  }
}

// Blob container for storing archived billing records
resource storageContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2021-09-01' = {
  name: '${storageAccountName}/default/${blobContainerName}'
  properties: {
    publicAccess: 'None' // Restrict public access for security
  }
  dependsOn: [
    storageAccount
  ]
}

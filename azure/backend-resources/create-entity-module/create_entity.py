from azure.data.tables import TableServiceClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ResourceNotFoundError
import os
# from dotenv import load_dotenv

# load_dotenv()

required_vars = ['COSMOS_DB_ACCOUNT_NAME', 'COSMOS_DB_TABLE_NAME', 
                 'COSMOS_DB_PARTITION_KEY', 'COSMOS_DB_ROW_KEY']
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

account_name = os.getenv('COSMOS_DB_ACCOUNT_NAME')
table_name = os.getenv('COSMOS_DB_TABLE_NAME')
partition_key = os.getenv('COSMOS_DB_PARTITION_KEY')
row_key = os.getenv('COSMOS_DB_ROW_KEY')

credential = DefaultAzureCredential()
table_service_client = TableServiceClient(
    endpoint=f"https://{account_name}.table.cosmos.azure.com:443/",
    credential=credential
)
table_client = table_service_client.get_table_client(table_name)

entity = {
    'PartitionKey': partition_key,
    'RowKey': row_key,
    'visitor_counter': 0,
}

try:
    table_client.get_entity(partition_key, row_key)
    print("Entity already exists; no action taken")
except ResourceNotFoundError:
    table_client.create_entity(entity)
    print("Entity created successfully")

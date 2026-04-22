import azure.functions as func
import logging
import os
import json
from azure.data.tables import TableServiceClient, UpdateMode
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ResourceNotFoundError

account_name = os.environ['COSMOS_DB_ACCOUNT_NAME']
table_name = os.environ['COSMOS_DB_TABLE_NAME']
partition_key = os.environ['COSMOS_DB_PARTITION_KEY']
row_key = os.environ['COSMOS_DB_ROW_KEY']

credential = DefaultAzureCredential()
account_url = f"https://{account_name}.table.cosmos.azure.com:443"
table_service = TableServiceClient(endpoint=account_url, credential=credential)
table_client = table_service.get_table_client(table_name=table_name)

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="visitor_counter")
def visitor_counter(req: func.HttpRequest) -> func.HttpResponse:
    """
    This function is triggered by an HTTP request every time someone visits the cloud resume app.
    The current "visitor_counter" value is retrieved from the "counter" table in the "cosmos-crc-prod" database and updated by one. 
    Finally, the updated value is returned to the cloud resume app for display.

    Parameters:
    req (func.HttpRequest): The HTTP request object.

    Returns:
    func.HttpResponse: The HTTP response object containing the updated visitor counter value or an error message.
    """
    logging.info('Python HTTP trigger function processed a request.')

    try:
        counter_entity = table_client.get_entity(partition_key=partition_key, row_key=row_key)
        current_value = counter_entity['visitor_counter']
    except ResourceNotFoundError:
        logging.error("Counter entity not found")
        return func.HttpResponse(
            json.dumps({"error": "Counter not found"}),
            status_code=404,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error retrieving counter: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Error retrieving counter: Check the database!"}),
            status_code=511,
            mimetype="application/json"
        )

    updated_value = current_value + 1
    counter_entity['visitor_counter'] = updated_value

    try:
        table_client.update_entity(mode=UpdateMode.REPLACE, entity=counter_entity)
    except Exception as e:
        logging.error(f"Error updating counter: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to update counter"}),
            status_code=500,
            mimetype="application/json"
        )
    return func.HttpResponse(
        json.dumps({"visitor_counter": updated_value}),
        status_code=200,
        mimetype="application/json"
    )
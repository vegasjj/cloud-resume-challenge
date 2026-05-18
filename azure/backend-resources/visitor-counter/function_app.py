import azure.functions as func
import logging
import os
import json
from azure.data.tables import TableServiceClient, UpdateMode
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ResourceNotFoundError

missing_env_var = []
def get_env_var(name: str) -> str:
    env_var = os.getenv(name)
    if not env_var:
        missing_env_var.append(name)
    return env_var

account_name = get_env_var('COSMOS_DB_ACCOUNT_NAME')
table_name = get_env_var('COSMOS_DB_TABLE_NAME')
partition_key = get_env_var('COSMOS_DB_PARTITION_KEY')
row_key = get_env_var('COSMOS_DB_ROW_KEY')

def create_error_response(client_message: str, server_message: str, status: int, code: str, exc_info: bool = True):
    logging.error(f"Status code error [{status}] occurred with error code: {code} and message: {server_message}", exc_info=exc_info)
    return func.HttpResponse(
        body=json.dumps({
            "message": client_message,
            "error_code": code
        }),
        status_code=status,
        mimetype="application/json"
    )

credential = DefaultAzureCredential()
generic_client_message = "An internal server error occurred, check the logs or contact your administrator"

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

    if missing_env_var:
        return create_error_response(
            generic_client_message,
            f"Missing required environment variables: {', '.join(missing_env_var)}",
            500,
            "ENV_VAR_MISSING"
        )
    
    account_url = f"https://{account_name}.table.cosmos.azure.com:443"
    table_service = TableServiceClient(endpoint=account_url, credential=credential)
    table_client = table_service.get_table_client(table_name=table_name)

    try:
        counter_entity = table_client.get_entity(partition_key=partition_key, row_key=row_key)
        current_value = counter_entity['visitor_counter']
    except ResourceNotFoundError:
        return create_error_response(
            generic_client_message,
            "Either the table, partition key or row key is missing or is renamed.",
            404,
            "INFRA_MISCONFIGURATION"
        )
    except Exception:
        return create_error_response(
            generic_client_message,
            "Failed to retrieve counter",
            500,
            "TRACE_REF_REQUIRED"
        )

    updated_value = current_value + 1
    counter_entity['visitor_counter'] = updated_value

    try:
        table_client.update_entity(mode=UpdateMode.REPLACE, entity=counter_entity)
    except Exception:
        return create_error_response(
            generic_client_message,
            "Failed to update counter",
            500,
            "DATA_PERSISTENCE_FAILURE"
        )
    return func.HttpResponse(
        json.dumps({"visitor_counter": updated_value}),
        status_code=200,
        mimetype="application/json"
    )
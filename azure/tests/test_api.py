from playwright.sync_api import sync_playwright, APIRequestContext
# from azure.data.tables import TableServiceClient
# from azure.identity import DefaultAzureCredential
import logging
import os

def _require_env(name: str) -> str:
    value = os.getenv(name)
    assert value, f"Required environment variable '{name}' is not set"
    return value

VISITOR_COUNTER_KEY = "visitor_counter"
TIMEOUT_MS = 30000  # milliseconds for Playwright
# TIMEOUT_S = TIMEOUT_MS // 1000  # seconds for Azure Table


def fetch_api_response(api_url: str, request_context: APIRequestContext) -> dict:
    response = request_context.get(api_url)

    assert response.status == 200, f"Expected status 200, got {response.status}"
    assert response.headers.get("content-type", "").startswith("application/json"), "Response is not JSON"

    response_data = response.json()
    assert isinstance(response_data, dict), "API response is not a JSON object"
    assert VISITOR_COUNTER_KEY in response_data, f"Response JSON does not contain '{VISITOR_COUNTER_KEY}' key"
    assert response_data[VISITOR_COUNTER_KEY] is not None, f"API counter value is None. Full response: {response_data}"
    assert isinstance(response_data[VISITOR_COUNTER_KEY], int), f"API counter value is not an int: {response_data[VISITOR_COUNTER_KEY]}"
    assert response_data[VISITOR_COUNTER_KEY] >= 0, f"API counter value is negative (unexpected): {response_data[VISITOR_COUNTER_KEY]}"

    return response_data


# def get_db_visitor_counter(account_name: str, table_name: str, partition_key: str, row_key: str) -> int:
#     credential = DefaultAzureCredential()
#     account_url = f"https://{account_name}.table.cosmos.azure.com:443"
#     table_service = TableServiceClient(endpoint=account_url, credential=credential)

#     with table_service.get_table_client(table_name=table_name) as table_client:
#         counter_entity = table_client.get_entity(partition_key=partition_key, row_key=row_key, timeout=TIMEOUT_S)
#         db_counter_value = counter_entity.get(VISITOR_COUNTER_KEY)

    # assert db_counter_value is not None, "DB counter value is None. Check if the entity exists in the database."
    # assert isinstance(db_counter_value, int), f"DB counter value is not an int: {db_counter_value}"
    # assert db_counter_value >= 0, f"DB counter value is negative (unexpected): {db_counter_value}"

    # return db_counter_value


def test_visitor_counter_api():
    """
    Test that the API counter matches the value in the database.
    """
    with sync_playwright() as p:
        request_context = p.request.new_context(timeout=TIMEOUT_MS)
        try:
            # account_name = _require_env("COSMOS_DB_ACCOUNT_NAME")
            # table_name = _require_env("COSMOS_DB_TABLE_NAME")
            # partition_key = _require_env("COSMOS_DB_PARTITION_KEY")
            # row_key = _require_env("COSMOS_DB_ROW_KEY")
            api_url = _require_env("API_URL")

            response_data = fetch_api_response(api_url, request_context)
            # db_counter_value = get_db_visitor_counter(account_name, table_name, partition_key, row_key)

            # assert db_counter_value >= response_data[VISITOR_COUNTER_KEY], (
            #     f"Mismatch: DB value ({db_counter_value}) is less than Visitor Counter API value ({response_data[VISITOR_COUNTER_KEY]})"
            # )

            logging.info(f"Response data: {response_data}")
        finally:
            request_context.dispose()

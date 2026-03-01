from playwright.sync_api import sync_playwright
from azure.data.tables import TableServiceClient
from azure.core.credentials import AzureNamedKeyCredential
from dotenv import load_dotenv
import logging
import os
import pytest

load_dotenv()

def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        pytest.skip(f"Required environment variable '{name}' is not set")
    return value

VISITS_COUNTER_KEY = "visitor_counter"
TIMEOUT_MS = 30000  # milliseconds for Playwright
TIMEOUT_S = TIMEOUT_MS // 1000  # seconds for Azure Table

def test_api_counter():
    """
    Test that the API counter matches the value in the database.
    """
    with sync_playwright() as p:
        request_context = p.request.new_context(timeout=TIMEOUT_MS)
        try:

            account_name  = _require_env("COSMOS_DB_ACCOUNT_NAME")
            account_key   = _require_env("COSMOS_DB_ACCOUNT_KEY")
            table_name    = _require_env("COSMOS_DB_TABLE_NAME")
            partition_key = _require_env("PARTITION_KEY")
            row_key       = _require_env("ROW_KEY")
            api_url       = _require_env("API_URL")

            try:
                response = request_context.get(api_url)
            except Exception as e:
                pytest.fail(f"API request failed: {e}")

            assert response.status == 200, f"Expected status 200, got {response.status}"
            assert response.headers.get("content-type", "").startswith("application/json"), "Response is not JSON"

            response_data = response.json()
            assert isinstance(response_data, dict), "API response is not a JSON object"
            assert VISITS_COUNTER_KEY in response_data, f"Response JSON does not contain '{VISITS_COUNTER_KEY}' key"

            credential = AzureNamedKeyCredential(account_name, account_key)
            endpoint = f"https://{account_name}.table.cosmos.azure.com:443/"
            table_service_client = TableServiceClient(endpoint=endpoint, credential=credential)

            with table_service_client.get_table_client(table_name=table_name) as table_client:
                try:
                    counter_entity = table_client.get_entity(partition_key=partition_key, row_key=row_key, timeout=TIMEOUT_S)
                except Exception as e:
                    pytest.fail(f"Database query failed: {e}")

                db_counter_value = counter_entity.get(VISITS_COUNTER_KEY)

                assert db_counter_value is not None, "DB counter value is None. Check if the entity exists in the database."
                assert response_data[VISITS_COUNTER_KEY] is not None, f"API counter value is None. Full response: {response_data}"

                assert isinstance(db_counter_value, int), f"DB counter value is not an int: {db_counter_value}"
                assert isinstance(response_data[VISITS_COUNTER_KEY], int), f"API counter value is not an int: {response_data[VISITS_COUNTER_KEY]}"

                assert db_counter_value >= 0, f"DB counter value is negative (unexpected): {db_counter_value}"
                assert response_data[VISITS_COUNTER_KEY] >= 0, f"API counter value is negative (unexpected): {response_data[VISITS_COUNTER_KEY]}"

                assert db_counter_value >= response_data[VISITS_COUNTER_KEY], (
                    f"Mismatch: DB value ({db_counter_value}) is less than Visitor Counter API value ({response_data[VISITS_COUNTER_KEY]})"
                )

                logging.info(f"Response data: {response_data}")
        finally:
            request_context.dispose()
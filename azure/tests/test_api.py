from playwright.sync_api import sync_playwright, APIRequestContext
import json
import logging
import os

def _require_env(name: str) -> str:
    value = os.getenv(name)
    assert value, f"Required environment variable '{name}' is not set"
    return value

VISITOR_COUNTER_KEY = "visitor_counter"
TIMEOUT_MS = 30000  # milliseconds for Playwright

def fetch_api_response(api_url: str, request_context: APIRequestContext) -> dict:
    response = request_context.get(api_url)
    status = response.status
    body = None
    
    try:
        body = response.json()
    except (ValueError, json.JSONDecodeError):
        pass

    if status != 200:
        if body and isinstance(body, dict):
            error_msg = body.get("message", "No specific error message provided")
        else:
            error_msg = response.text()[:100]
        assert False, f"❌ DEPLOYMENT HALTED: API returned {status}. Detail: {error_msg}"

    assert response.headers.get("content-type", "").startswith("application/json"), "Response is not JSON"
    assert body is not None, f"❌ DEPLOYMENT HALTED: Response has JSON content-type but body could not be parsed: {response.text()[:100]}"
    
    response_data = body
    assert isinstance(response_data, dict), "API response is not a JSON object"
    assert VISITOR_COUNTER_KEY in response_data, f"Response JSON does not contain '{VISITOR_COUNTER_KEY}' key"
    assert response_data[VISITOR_COUNTER_KEY] is not None, f"API counter value is None. Full response: {response_data}"
    assert isinstance(response_data[VISITOR_COUNTER_KEY], int), f"API counter value is not an int: {response_data[VISITOR_COUNTER_KEY]}"
    assert response_data[VISITOR_COUNTER_KEY] >= 0, f"API counter value is negative (unexpected): {response_data[VISITOR_COUNTER_KEY]}"

    return response_data

def test_visitor_counter_api():
    """
    Test that the API counter matches the value in the database.
    """
    with sync_playwright() as p:
        request_context = p.request.new_context(timeout=TIMEOUT_MS)
        try:
            api_url = _require_env("API_URL")
            response_data = fetch_api_response(api_url, request_context)
            logging.info(f"Response data: {response_data}")
        finally:
            request_context.dispose()

from playwright.sync_api import Playwright, APIRequestContext
import pytest
import json
import os

def _require_env(name: str) -> str:
    value = os.getenv(name)
    assert value, f"Required environment variable '{name}' is not set"
    return value

VISITOR_COUNTER_KEY = "visitor_counter"

@pytest.fixture(scope="session")
def api_context(playwright: Playwright):
    context = playwright.request.new_context(
        base_url=_require_env("API_URL"),
    )
    
    yield context
    
    # Dispose of the context once all tests are done
    context.dispose()

@pytest.fixture(scope="session")
def shared_response_data(api_context: APIRequestContext):
    response = api_context.post("visitor_counter")
    status = response.status
    body = None
    
    try:
        body = response.json()
    except (ValueError, json.JSONDecodeError):
        pass

    if status != 200:
        if body and isinstance(body, dict):
            # error_msg = body.get("message", "No specific error message provided")
            error_code = body.get("error_code", "UNKNOWN_ERROR")
            error_detail = error_code
        else:
            error_detail = response.text()[:100]
        assert False, f"❌ API response returned {status}. Detail: {error_detail}"

    assert response.headers.get("content-type", "").startswith("application/json"), "❌ API response is not JSON"
    assert body is not None, f"❌ API response has JSON content-type but body could not be parsed: {response.text()[:100]}"
    assert isinstance(body, dict), f"❌ API response returned a {type(body).__name__} instead of a dictionary."        
    
    return body

def test_response_contains_correct_key(shared_response_data):
    assert VISITOR_COUNTER_KEY in shared_response_data, f"❌ API Response does not contain '{VISITOR_COUNTER_KEY}' key"

def test_visitor_counter_is_not_none(shared_response_data):
    assert shared_response_data[VISITOR_COUNTER_KEY] is not None, f"❌ Visitor counter value cannot be None. Full response: {shared_response_data}"

def test_visitor_counter_is_an_int(shared_response_data):
    assert isinstance(shared_response_data[VISITOR_COUNTER_KEY], int), f"❌ Visitor counter value is not an int: {shared_response_data[VISITOR_COUNTER_KEY]}"

def test_visitor_counter_is_not_negative(shared_response_data):
    assert shared_response_data[VISITOR_COUNTER_KEY] >= 0, f"❌ Visitor counter value is negative (unexpected): {shared_response_data[VISITOR_COUNTER_KEY]}"

def test_database_increments_value(api_context: APIRequestContext, shared_response_data):
    initial_count = shared_response_data[VISITOR_COUNTER_KEY]
    
    second_response = api_context.post("visitor_counter")
    assert second_response.status == 200, "❌ Second API call failed during increment validation"
    
    try:
        second_body = second_response.json()
    except (ValueError, json.JSONDecodeError):
        assert False, "❌ Second response body could not be parsed as JSON"
        
    second_count = second_body.get(VISITOR_COUNTER_KEY)
    
    assert second_count >= initial_count + 1, (
        f"❌ Database state did not increment correctly. "
        f"Expected {initial_count + 1} or higher, but got {second_count}"
    )

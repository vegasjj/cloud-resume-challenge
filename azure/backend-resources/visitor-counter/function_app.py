import azure.functions as func
import logging
import os
import json
from azure.data.tables import TableServiceClient, UpdateMode
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.core.exceptions import ResourceNotFoundError
from openai import AzureOpenAI
from functools import lru_cache

missing_env_var = []
missing_openai_env_var = []

def get_env_var(name: str) -> str:
    env_var = os.getenv(name)
    if not env_var:
        if name.startswith("AZURE_OPENAI"):
            missing_openai_env_var.append(name)
        else:
            missing_env_var.append(name)
    return env_var

account_name = get_env_var('COSMOS_DB_ACCOUNT_NAME')
table_name = get_env_var('COSMOS_DB_TABLE_NAME')
partition_key = get_env_var('COSMOS_DB_PARTITION_KEY')
row_key = get_env_var('COSMOS_DB_ROW_KEY')

openai_endpoint = get_env_var('AZURE_OPENAI_ENDPOINT')
openai_deployment = get_env_var('AZURE_OPENAI_DEPLOYMENT')

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


# --- Resume Summarizer Function ---
SYSTEM_PROMPT = """You are a professional resume reviewer. Given a resume text, produce a concise 
summary (3-5 sentences) highlighting the candidate's key qualifications, most relevant experience, 
and core technical skills. Be objective, professional, and focus on what makes this candidate stand out."""

MAX_RESUME_LENGTH = 10000

token_provider = get_bearer_token_provider(
    credential,
    "https://cognitiveservices.azure.com/.default"
)

@lru_cache(maxsize=1)
def get_openai_client() -> AzureOpenAI:
    return AzureOpenAI(
        azure_endpoint=openai_endpoint,
        azure_ad_token_provider=token_provider,
        api_version="2025-04-01-preview"
    )

@app.route(route="summarize", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def resume_summarizer(req: func.HttpRequest) -> func.HttpResponse:
    """
    Accepts resume text via POST and returns an AI-generated summary
    using Azure OpenAI GPT-4.1 Nano via system-assigned managed identity.
    Uses the Responses API for streamlined model interaction.
    
    Parameters:
    req (func.HttpRequest): The HTTP request with JSON body { "resume_text": "..." }
    
    Returns:
    func.HttpResponse: JSON response { "summary": "..." } or error details.
    """
    logging.info('Resume summarizer function processed a request.')

    if missing_openai_env_var:
        return create_error_response(
            generic_client_message,
            f"Missing required environment variables: {', '.join(missing_openai_env_var)}",
            500,
            "ENV_VAR_MISSING"
        )

    try:
        req_body = req.get_json()
    except ValueError:
        return create_error_response(
            "Resume summarization request was malformed, please try again or contact support.",
            "Invalid JSON in request body",
            400,
            "INVALID_REQUEST_BODY"
        )

    if not isinstance(req_body, dict):
        return create_error_response(
            "Resume summarization request was malformed, please try again or contact support.",
            "Root JSON is not an object",
            400,
            "INVALID_REQUEST_BODY"
        )

    raw_resume_text = req_body.get('resume_text')

    if not isinstance(raw_resume_text, str):
        return create_error_response(
            "Resume summarization request must contain a valid string of characters.",
            "Invalid resume_text type",
            400,
            "INVALID_RESUME_TEXT"
        )

    resume_text = raw_resume_text.strip()
    if not resume_text:
        return create_error_response(
            "Resume summarization request cannot be empty.",
            "Empty resume_text field",
            400,
            "EMPTY_RESUME_TEXT"
        )

    if len(resume_text) > MAX_RESUME_LENGTH:
        return create_error_response(
            f"Resume summarization request must be {MAX_RESUME_LENGTH} characters or fewer.",
            f"Resume summarization request length {len(resume_text)} exceeds limit {MAX_RESUME_LENGTH}",
            400,
            "RESUME_TEXT_TOO_LONG"
        )

    try:
        client = get_openai_client()
        response = client.responses.create(
            model=openai_deployment,
            instructions=SYSTEM_PROMPT,
            input=resume_text,
            max_output_tokens=500,
            temperature=0.3
        )

    except Exception:
        return create_error_response(
            generic_client_message,
            "Failed to generate summary from Azure OpenAI",
            500,
            "OPENAI_API_FAILURE"
        )

    if response.status != "completed":
        reason = getattr(response.incomplete_details, "reason", "unknown")
        return create_error_response(
            "Failed to generate a complete summary. Please try again.",
            f"Model response status '{response.status}' (reason: {reason})",
            502,
            "OPENAI_INCOMPLETE_RESPONSE"
        )

    return func.HttpResponse(
        json.dumps({"summary": response.output_text}),
        status_code=200,
        mimetype="application/json"
    )

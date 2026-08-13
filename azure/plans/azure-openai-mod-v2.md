## Resume Generative AI Summarization
This plan adds a new feature to the Cloud Resume Challenge frontend: a form that accepts a text-based resume and generates a summary using generative AI. It implements a new Azure OpenAI resource connected via a private endpoint, and processes the AI generation within the existing `func-crc-prod-001` Azure Function using system-assigned managed identity.

## User Review Required
> [!CAUTION]
> **Virtual Network Addition**: In order to place the Azure OpenAI model behind a Private Endpoint, a Virtual Network (VNet) must be introduced into the Terraform state. This involves creating a VNet, two subnets (one for the Private Endpoint, one for Function App VNet Integration), and linking them. This will add new architectural components to your environment. Please confirm this infrastructure expansion is acceptable.
> 
> **Pricing Tier Changes**: VNet integration for Azure Functions requires a supported tier. Flex Consumption supports it, but we should verify region availability for OpenAI in the same region.

## Open Questions
> [!IMPORTANT]
> 1. Should the Virtual Network use a specific address space (e.g., `10.0.0.0/16`)?
> 2. What region should the Azure OpenAI resource be deployed in? (It defaults to the resource group's location, `eastus`, but OpenAI availability varies by region. `eastus` usually has `gpt-4o-mini`).
> 3. Does the frontend need any specific styling (CSS) changes for the new form, or should it inherit the existing styles?

## Proposed Changes

### Frontend
Updates to the `index.html` file to add the resume input form and the JS script to interact with the new Azure Function endpoint.

#### [MODIFY] frontend/resume/index.html
Add a new section for the AI summarizer.
```html
<section class="ai-summary">
    <h2>AI Resume Summarizer</h2>
    <div class="form-group">
        <textarea id="resume-input" rows="5" placeholder="Paste your resume here..." style="width: 100%;"></textarea>
    </div>
    <button id="summarize-btn" type="button">Summarize</button>
    <div id="summary-result" style="margin-top: 15px; font-style: italic;"></div>
</section>
<script>
    document.getElementById('summarize-btn').addEventListener('click', async () => {
        const input = document.getElementById('resume-input').value;
        const resultDiv = document.getElementById('summary-result');
        if (!input) return;
        
        resultDiv.innerText = "Summarizing...";
        try {
            const response = await fetch('https://<your-function-app-url>/api/summarize_resume', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ resume: input })
            });
            const data = await response.json();
            resultDiv.innerText = data.summary || "No summary generated.";
        } catch (err) {
            resultDiv.innerText = "Error generating summary.";
        }
    });
</script>
```

---
### Infrastructure (Terraform)
Updates to the Terraform definitions to create the Azure OpenAI resource, Private Endpoint, VNet, and role assignments.

#### [MODIFY] azure/backend-resources/main.tf
Add the following resources:
1. `azurerm_virtual_network` and `azurerm_subnet` (one for endpoints, one for function app).
2. `azurerm_cognitive_account` (Kind: OpenAI, SKU: S0).
3. `azurerm_cognitive_deployment` (Model: `gpt-4o-mini`).
4. `azurerm_private_endpoint` for the Cognitive Account.
5. `azurerm_private_dns_zone`, `azurerm_private_dns_zone_virtual_network_link`, and `azurerm_private_dns_a_record` for `privatelink.openai.azure.com`.
6. Update `azurerm_function_app_flex_consumption.func` to include `virtual_network_subnet_id` (VNet Integration) and add `AZURE_OPENAI_ENDPOINT` to `app_settings`.
7. `azurerm_role_assignment` for the Function App Identity to have `Cognitive Services OpenAI User` on the Cognitive Services Account.

---
### Backend (Azure Function)
Updates to the Python Azure Function to handle the new route and communicate with OpenAI using Managed Identity.

#### [MODIFY] azure/backend-resources/visitor-counter/function_app.py
Add a new HTTP POST route `/api/summarize_resume`:
```python
import os
import json
import logging
import azure.functions as func
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# ... existing code ...

@app.route(route="summarize_resume", methods=["POST"])
def summarize_resume(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing resume summarization request.')
    try:
        req_body = req.get_json()
        resume_text = req_body.get('resume')
    except ValueError:
        return func.HttpResponse("Invalid JSON", status_code=400)
    
    if not resume_text:
        return func.HttpResponse("Resume text is required.", status_code=400)
        
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )
    
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_ad_token_provider=token_provider,
        api_version="2024-02-01"
    )
    
    try:
        # Use gpt-4o-mini for cost efficiency
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes resumes."},
                {"role": "user", "content": f"Please summarize this resume:\n{resume_text}"}
            ]
        )
        summary = response.choices[0].message.content
        return func.HttpResponse(json.dumps({"summary": summary}), mimetype="application/json")
    except Exception as e:
        logging.error(f"OpenAI error: {e}")
        return func.HttpResponse("Error communicating with AI.", status_code=500)
```

#### [MODIFY] azure/backend-resources/visitor-counter/requirements.txt
Add the `openai` package.
```text
openai>=1.0.0
```

## Verification Plan
### Automated Tests
* Run `terraform plan` to verify that the syntax and state changes are valid.
* Run `pytest` if there are any unit tests in `azure/backend-resources/visitor-counter/tests/`.

### Manual Verification
1. Provision the resources using `terraform apply`.
2. Wait for the OpenAI model deployment to complete.
3. Open the Cloud Resume frontend, paste a sample resume in the form, and click "Summarize".
4. Ensure the UI displays the generated summary and verify there are no CORS or authentication errors in the browser console.
5. Verify in Azure Portal that the Azure Function uses VNet integration and that the OpenAI instance is only accessible via the Private Endpoint.

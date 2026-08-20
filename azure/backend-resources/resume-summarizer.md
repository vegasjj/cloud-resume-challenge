# Resume Summarizer Implementation (Draft)

## Diagrams

**TODO:** Merge both diagrams.

```mermaid
flowchart LR
    A["Browser<br/>(resume page)"] -->|"POST /summarize<br/>{ resume_text }"| B["Azure Function<br/>func-crc-prod-001"]
    B -->|"Private Endpoint<br/>(VNet integrated)"| C["Azure OpenAI<br/>GPT-4.1 Nano"]
    C -->|"Summary response"| B
    B -->|"JSON { summary }"| A
    
    subgraph "VNet: vnet-crc-prod-001"
        direction TB
        D["snet-func-crc-prod<br/>/24 delegated"] --- E["snet-pe-crc-prod<br/>/24 private endpoints"]
    end
    
    B -.->|"VNet Integration"| D
    E -.->|"Private Link"| C
```

```mermaid
flowchart LR
    A["Browser<br/>(resume page)"] -->|"POST /resume-summarizer/summarize<br/>subscription key in header"| B["Azure API Management<br/>(Consumption SKU)"]
    B -->|"Rate limit<br/>Payload validation<br/>CORS<br/>Method restriction<br/>Quota enforcement"| B
    B -->|"POST /api/summarize<br/>+ function key"| C["Azure Function<br/>func-crc-prod-001<br/>(auth_level=FUNCTION)"]
    C -->|"Private Endpoint"| D["Azure OpenAI<br/>GPT-4.1 Nano"]
    D -->|"Summary"| C
    C -->|"JSON response"| B
    B -->|"JSON response"| A
```

## OpenAI Deployment

- GPT-4.1-nano is chosen because of its cost-effectiveness for demo projects, in production environments model selection must carry other considerations like performance or precision to complete the tasks.
- Input length limit: 10,000 characters (~2,500 tokens) — Enforced client side.
- OpenAI API style: Using the Responses API (client.responses.create()) instead of Chat Completions.
- Outbound data loss prevention is a non issue here as only basic inference for summarization is performance which is then return to the web client. No tool calls or external resources are involved, and the model never initiate any communication as the current pipeline is one way..

## Changes to the current project

**TODO:** Finish section.

### Backend Infrastructure

**TODO:** Finish section.

### Python API

**TODO:** Finish section.

### Frontend

**TODO:** Finish section.

## Security and performance considerations

- Metric monitoring idea: TPM and RPM monitoring
- Consider using key vault to store function key to be use by azure apim via managed identity, this way there’s no need for the value to be stored in terraform state outside of azure
- I think for the outbound IP whitelisting of the azure APIM instance to be done in the function app network settings (closing the gap in case of function key exposure), I need to upgrade as consumptions SKU doesn’t support static IPs. Also, it would be necessary to bring visitor_counter into the azure APIM because it uses the same function app. Region-level whitelisting of Azure datacenter could be explored as well if security requirements allow for it.
- Unfortunately, both rate-limiting-by-key and quota-by-key are not possible in the consumption tier so subscription based limiting is the next best thing. Cannot separate malicious traffic from legitimate traffic (shared `rate-limit` and `quota` allowance). This risk is acceptable in demo projects like this one but cannot be recommended in production environments where traffic must be protected for legitimate users while malicious traffic is blocked/throttled.
- The subscription key to call the API will be manually injected post deployment on JavaScript and an automated fix will be implemented after a minimum viable product is functional (the fix could add unforeseen frontend architecture changes outside of the scope os this PR).
- The risk of publishing the subscription key in static JavaScript is fine in this case as it only provides throttling functionality, the function is authenticated and the OpenAI deployment is behind a private endpoint accessible through managed identity only which provide the real security.

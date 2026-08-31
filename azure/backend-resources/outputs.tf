output "apim_resume_endpoint" {
  description = "Full APIM gateway URL for the resume summarizer API operation."
  value       = "${azurerm_api_management.apim.gateway_url}/${azurerm_api_management_api.resume_api.path}${azurerm_api_management_api_operation.summarize.url_template}"
}

output "apim_subscription_key" {
  description = "Primary subscription key for the frontend APIM subscription."
  value       = azurerm_api_management_subscription.frontend_sub.primary_key
  sensitive   = true
}

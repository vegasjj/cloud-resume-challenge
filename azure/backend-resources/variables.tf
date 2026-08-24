variable "resource_group_name" {
  description = "Name of the resource group."
  default     = "rg-crc-backend-prod-001"
  type        = string

  validation {
    condition     = can(regex("^[a-zA-Z0-9._()\\-]+$", var.resource_group_name)) && length(var.resource_group_name) >= 1 && length(var.resource_group_name) <= 90 && !can(regex("\\.$", var.resource_group_name))
    error_message = "Resource group name must be 1-90 characters, alphanumeric with hyphens, underscores, periods, parentheses, and cannot end with a period."
  }
}

variable "location" {
  description = "Location of the resources."
  default     = "eastus"
  type        = string
}

variable "cosmosdb_account_name" {
  description = "Name of the Cosmos DB account."
  default     = "cosmos-crc-prod"
  type        = string
}

variable "cosmosdb_table_name" {
  description = "Name of the Cosmos DB table."
  default     = "counter"
  type        = string
}

variable "storage_account_name" {
  description = "Name of the Storage Account."
  default     = "stcrcapi002"
  type        = string

  validation {
    condition     = length(var.storage_account_name) >= 3 && length(var.storage_account_name) <= 24 && can(regex("^[a-z0-9]+$", var.storage_account_name))
    error_message = "Storage account name must be 3-24 characters, lowercase letters and numbers only."
  }
}

variable "service_plan_name" {
  description = "Name of the App Service Plan."
  default     = "sp-crc-prod"
  type        = string
}

variable "function_app_name" {
  description = "Name of the Function App."
  default     = "func-crc-prod-001"
  type        = string
}

variable "log_analytics_name" {
  description = "Name of the Log Analytics Workspace."
  default     = "law-crc-prod-001"
  type        = string
}

variable "application_insights_name" {
  description = "Name of the Application Insights."
  default     = "insights-crc-prod-001"
  type        = string
}

variable "function_name" {
  description = "Name of the visitor counter function."
  default     = "visitor_counter"
  type        = string
}

variable "slack_channel_name" {
  description = "The name of the Slack channel for alerts"
  default     = "#counter-function-alerts"
  type        = string
}

variable "openai_account_name" {
  description = "Name of the Azure OpenAI account."
  default     = "oai-crc-prod-001"
  type        = string
}

variable "openai_model_name" {
  description = "Name of the Azure OpenAI model deployment."
  default     = "gpt-41-nano"
  type        = string
}

variable "openai_sku" {
  description = "SKU for the Azure OpenAI account."
  default     = "S0"
  type        = string
}

variable "vnet_name" {
  description = "Name of the Virtual Network."
  default     = "vnet-crc-prod-001"
  type        = string
}

variable "subnet_function_name" {
  description = "Name of the subnet delegated to the Function App."
  default     = "snet-func-crc-prod"
  type        = string
}

variable "subnet_pe_name" {
  description = "Name of the subnet for private endpoints."
  default     = "snet-pe-crc-prod"
  type        = string
}

variable "apim_name" {
  description = "Name of the Azure API Management instance."
  default     = "apim-crc-prod-001"
  type        = string
}

variable "apim_publisher_name" {
  description = "Publisher name for APIM."
  default     = "Cloud Resume Challenge"
  type        = string
}

variable "apim_publisher_email" {
  description = "Publisher email for APIM."
  default     = "vegasjj@gmail.com"
  type        = string
}
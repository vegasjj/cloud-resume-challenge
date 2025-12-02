variable "resource_group_name" {
  description = "Name of the Azure Resource Group"
  default     = "rg-crc-prod-001"
  type        = string
}

variable "location" {
  description = "Azure region to deploy resources"
  default     = "eastus"
  type        = string
}

variable "storage_account_name" {
  description = "Name of the Storage Account"
  default     = "stcrc002"
  type        = string
}

variable "cdn_profile_name" {
  description = "Name of the CDN Profile"
  default      = "cdn-crc-prod-001"
  type        = string
}

variable "cdn_endpoint_name" {
  description = "Name of the CDN Endpoint"
  default     = "ep-crc-prod-001"
  type        = string
}

variable "custom_domain_name" {
  description = "Custom domain for CDN endpoint"
  default     = "resume.technicalmind.cloud"
  type        = string
}
terraform {
  required_version = "1.14.1"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "4.55.0"
    }
  }
  
  # This block should only be uncommented for local testing
  cloud {
    # organization = "azure-terraform-labs"
    # workspaces {
    #   name = "azure-cloud-resume-challenge-prod"
    # }
  }
}
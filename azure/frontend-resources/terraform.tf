terraform {
  required_version = "~>1.15.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>5.0.0"
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
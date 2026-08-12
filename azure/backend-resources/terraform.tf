terraform {
  required_version = "~>1.15.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>5.0.0"
    }
  }

  cloud {}

  # For local testing, uncomment this block and comment the cloud block above this one.
  # cloud {
  #   organization = "azure-terraform-labs" 

  #   workspaces { 
  #     name = "azure-cloud-resume-challenge-backend-prod" 
  #   }
  # }
}
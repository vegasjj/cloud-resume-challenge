terraform {
  required_version = "1.14.3"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "4.57.0"
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
terraform {
  required_version = "1.14.1"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "4.55.0"
    }
  }

  cloud {
    # organization = "azure-terraform-labs"
    # workspaces {
    #   name = "azure-cloud-resume-challenge-prod"
    # }
  }
}
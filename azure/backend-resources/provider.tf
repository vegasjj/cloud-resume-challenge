provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
     }

    application_insights {
      disable_generated_rule = true
    }
  }
}
provider "azurerm" {
  resource_providers_to_register = [
    "Microsoft.Web",
    "Microsoft.DocumentDB",
    "Microsoft.Network",
    "Microsoft.Storage",
    "Microsoft.Insights",
    "Microsoft.Logic",
    "Microsoft.CognitiveServices"
  ]

  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }

    application_insights {
      disable_generated_rule = true
    }
  }
}
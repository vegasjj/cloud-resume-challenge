resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_cosmosdb_account" "db" {
  name                            = var.cosmosdb_account_name
  location                        = azurerm_resource_group.rg.location
  resource_group_name             = azurerm_resource_group.rg.name
  offer_type                      = "Standard"
  local_authentication_disabled   = true

  tags = {
    defaultExperience = "Azure Table"
  }

  backup {
      type = "Continuous"
      tier = "Continuous7Days"
    }

  capabilities {
      name = "EnableServerless"
    }

  capabilities {
    name = "EnableTable"
  }

  capacity {
    total_throughput_limit = 4000
  }
  
  consistency_policy {
    consistency_level       = "BoundedStaleness"
    max_interval_in_seconds = 86400
    max_staleness_prefix    = 1000000
  }
  geo_location {
    location          = var.location
    failover_priority = 0
  }
  depends_on = [
    azurerm_resource_group.rg
  ]
}

resource "azurerm_cosmosdb_table" "tb" {
  name                = var.cosmosdb_table_name
  resource_group_name = azurerm_resource_group.rg.name
  account_name        = azurerm_cosmosdb_account.db.name
  depends_on = [
    azurerm_cosmosdb_account.db
  ]
}

resource "azurerm_storage_account" "st" {
  name                            = var.storage_account_name
  resource_group_name             = azurerm_resource_group.rg.name
  location                        = azurerm_resource_group.rg.location
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  allow_nested_items_to_be_public = false
  # shared_access_key_enabled = false
  depends_on = [
    azurerm_resource_group.rg
  ]
}

resource "azurerm_storage_container" "sc" {
  name                  = "deploymentpackage"
  storage_account_id  = azurerm_storage_account.st.id
}

resource "azurerm_log_analytics_workspace" "law" {
  name                          = var.log_analytics_name
  location                      = var.location
  resource_group_name           = azurerm_resource_group.rg.name
  # local_authentication_enabled  = false
  sku                           = "PerGB2018"
  retention_in_days             = 30
  depends_on = [
    azurerm_resource_group.rg
  ]
}

resource "azurerm_application_insights" "ai" {
  name                = var.application_insights_name
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  workspace_id        = azurerm_log_analytics_workspace.law.id
  application_type    = "web"
  # local_authentication_disabled = true
  depends_on = [
    azurerm_resource_group.rg
  ]
}

resource "azurerm_service_plan" "sp" {
  name                = var.service_plan_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"
  sku_name            = "FC1"
  depends_on = [
    azurerm_resource_group.rg
  ]
}
resource "azurerm_function_app_flex_consumption" "func" {
  name                                     = var.function_app_name
  resource_group_name                      = azurerm_resource_group.rg.name
  location                                 = azurerm_resource_group.rg.location
  service_plan_id                          = azurerm_service_plan.sp.id
  
  storage_container_type                   = "blobContainer"
  storage_container_endpoint               = "${azurerm_storage_account.st.primary_blob_endpoint}${azurerm_storage_container.sc.name}"
  storage_authentication_type              = "StorageAccountConnectionString"
  storage_access_key                       = azurerm_storage_account.st.primary_access_key
  runtime_name                             = "python"
  runtime_version                          = "3.12"
  webdeploy_publish_basic_authentication_enabled = false
  # TO-DO Need to dig into this
  client_certificate_mode                  = "Required"
  https_only                               = true
  identity {
    type = "SystemAssigned"
  }
  
  site_config {
    application_insights_connection_string = azurerm_application_insights.ai.connection_string
    http2_enabled                          = true
    cors {
      allowed_origins = ["https://portal.azure.com", "https://resume.technicalmind.cloud"]
    }
  }

  app_settings = {
    COSMOS_DB_ACCOUNT_NAME  = var.cosmosdb_account_name
    COSMOS_DB_PARTITION_KEY = "counter_partitionkey"
    COSMOS_DB_ROW_KEY       = "counter_rowkey"
    COSMOS_DB_TABLE_NAME    = var.cosmosdb_table_name
  }
  # Dig into the need of this tag
  tags = { 
    "hidden-link: /app-insights-resource-id" = azurerm_application_insights.ai.id
   }
}

resource "azurerm_cosmosdb_sql_role_definition" "rd" {
  name                = "Azure Cosmos DB for Table Visitor Counter contributor"
  resource_group_name = azurerm_resource_group.rg.name
  account_name        = azurerm_cosmosdb_account.db.name
  assignable_scopes   = [azurerm_cosmosdb_account.db.id]
  permissions {
    data_actions = [
          "Microsoft.DocumentDB/databaseAccounts/readMetadata",
          "Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/items/read",
          "Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/items/replace"
    ]
  }
}

resource "azurerm_cosmosdb_sql_role_assignment" "ra" {
  resource_group_name = azurerm_resource_group.rg.name
  account_name        = azurerm_cosmosdb_account.db.name
  role_definition_id  = azurerm_cosmosdb_sql_role_definition.rd.id
  principal_id        = azurerm_function_app_flex_consumption.func.identity.0.principal_id
  scope               = azurerm_cosmosdb_account.db.id
}

data "azurerm_managed_api" "api_data" {
  name     = "slack"
  location = azurerm_resource_group.rg.location
}
#API Connection must be manually authenticated with Slack OAuth in Azure Portal
resource "azurerm_api_connection" "api_connection" {
  name                = "SlackConnection"
  resource_group_name = azurerm_resource_group.rg.name
  managed_api_id      = data.azurerm_managed_api.api_data.id
  display_name        = "Slack API Connection"
  depends_on = [
    azurerm_resource_group.rg
  ]
}
# Test possible alternative with bot channel registration for fully
# automated workflow with Slack API authentication
# resource "azurerm_bot_channels_registration" "example" {
#   name                = "example"
#   location            = "global"
#   resource_group_name = azurerm_resource_group.example.name
#   sku                 = "F0"
#   microsoft_app_id    = data.azurerm_client_config.current.client_id
# }

# resource "azurerm_bot_channel_slack" "example" {
#   bot_name            = azurerm_bot_channels_registration.example.name
#   location            = azurerm_bot_channels_registration.example.location
#   resource_group_name = azurerm_resource_group.example.name
#   client_id           = "exampleId"
#   client_secret       = "exampleSecret"
#   verification_token  = "exampleVerificationToken"
# }

resource "azurerm_logic_app_workflow" "alert_workflow" {
  name     = "slack-channel-integration"
  location = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  parameters = {
    "$connections" = "{\"slack\":{\"connectionId\":\"${azurerm_api_connection.api_connection.id}\",\"id\":\"${azurerm_api_connection.api_connection.managed_api_id}\"}}"
  }
  workflow_parameters = {
    "$connections" = "{\"defaultValue\":{},\"type\":\"Object\"}"
  }
  depends_on = [
    azurerm_resource_group.rg
  ]
}

resource "azurerm_logic_app_trigger_http_request" "workflow_trigger" {
  name         = "azure-monitor-trigger"
  logic_app_id = azurerm_logic_app_workflow.alert_workflow.id

  schema = jsonencode({
    "$schema" = "http://json-schema.org/draft-04/schema#"
    properties = {
      data = {
        properties = {
          essentials = {
            properties = {
              alertId = {
                type = "string"
              }
              alertRule = {
                type = "string"
              }
              firedDateTime = {
                type = "string"
              }
              monitorCondition = {
                type = "string"
              }
              severity = {
                type = "string"
              }
            }
            required = ["alertId", "alertRule", "severity", "monitorCondition", "firedDateTime"]
            type     = "object"
          }
        }
        required = ["essentials"]
        type     = "object"
      }
    }
    required = ["data"]
    type     = "object"
  })
}

resource "azurerm_logic_app_action_custom" "slack_message" {
  name         = "slack-channel-post"
  logic_app_id = azurerm_logic_app_workflow.alert_workflow.id

  body = jsonencode({
    inputs = {
      host = {
        connection = {
          name = "@parameters('$connections')['slack']['connectionId']"
        }
      }
      method = "post"
      path   = "/chat.postMessage"
      queries = {
        channel = "#counter-function-alerts"
        text    = "Azure Alert - '@{triggerBody()['data']['essentials']['alertRule']}' is @{triggerBody()['data']['essentials']['monitorCondition']}. Severity: @{triggerBody()['data']['essentials']['severity']}. Fired at: @{triggerBody()['data']['essentials']['firedDateTime']}. Details: @{concat('https://ms.portal.azure.com/#blade/Microsoft_Azure_Monitoring/AlertDetailsTemplateBlade/alertId/', uriComponent(triggerBody()['data']['essentials']['alertId']))}"
      }
    }
    type = "ApiConnection"
  })
}

resource "azurerm_monitor_action_group" "alert_notifications" {
  name                = "alert-notifications"
  resource_group_name = azurerm_resource_group.rg.name
  short_name          = "Alert Sender"
  arm_role_receiver {
    name    = "Owner Notifications"
    role_id = "8e3af657-a8ff-443c-a75c-2fe8c4bcb635"
  }
  # Cannot commit to repository until a safe way to reference the PagerDuty integration URL is implemented
  # webhook_receiver {
  #   name                    = "PagerDuty alert integration"
  #   service_uri             = "<pagerduty service uri>"
  #   use_common_alert_schema = true
  # }
  webhook_receiver {
    name                    = "Slack alert channel"
    service_uri             = "${azurerm_logic_app_trigger_http_request.workflow_trigger.callback_url}"
    use_common_alert_schema = true
  }
  depends_on = [
    azurerm_logic_app_trigger_http_request.workflow_trigger,
    azurerm_resource_group.rg
  ]
}

resource "azurerm_monitor_metric_alert" "metric_1" {
  enabled             = true
  name                = "Average failure count exceeded"
  resource_group_name = azurerm_resource_group.rg.name
  scopes              = [azurerm_application_insights.ai.id]
  severity            = 1
  description         = "Action will be triggered when average failure count is greater than 5 for the visitor counter."
  frequency           = "PT1M"
  window_size         = "PT5M"
  
  criteria {
    aggregation            = "Average"
    metric_name            = "${var.function_name} Failures"
    metric_namespace       = "Azure.ApplicationInsights"
    operator               = "GreaterThan"
    threshold              = 5
    skip_metric_validation = true
  }

  action {
    action_group_id = azurerm_monitor_action_group.alert_notifications.id
  }
}

resource "azurerm_monitor_metric_alert" "metric_2" {
  enabled             = true
  name                = "Unusual invocation number"
  resource_group_name = azurerm_resource_group.rg.name
  scopes              = [azurerm_function_app_flex_consumption.func.id]
  severity            = 2
  description         = "Action will be triggered when Execution count is greater than 50."
  frequency           = "PT1M"
  window_size         = "PT5M"


  criteria {
    aggregation      = "Total"
    metric_name      = "OnDemandFunctionExecutionCount"
    metric_namespace = "Microsoft.Web/sites"
    operator         = "GreaterThan"
    threshold        = 50
  }
  
  action {
    action_group_id = azurerm_monitor_action_group.alert_notifications.id
  }
}

resource "azurerm_monitor_metric_alert" "metric_3" {
  enabled             = true
  name                = "Unusual average duration"
  resource_group_name = azurerm_resource_group.rg.name
  scopes              = [azurerm_application_insights.ai.id]
  severity            = 3
  description         = "Action will be triggered when average duration is greater than 1000ms for the visitor counter."
  frequency           = "PT1M"
  window_size         = "PT5M"

  criteria {
    aggregation            = "Average"
    metric_name            = "${var.function_name} AvgDurationMs"
    metric_namespace       = "Azure.ApplicationInsights"
    operator               = "GreaterThan"
    threshold              = 1000
    skip_metric_validation = true
  }

  action {
    action_group_id = azurerm_monitor_action_group.alert_notifications.id
  }
}

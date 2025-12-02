locals {
  static_web_host = trim(replace(azurerm_storage_account.staticweb.primary_web_endpoint, "https://", ""), "/")
}

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_storage_account" "staticweb" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_account_static_website" "staticwebsite" {
  storage_account_id = azurerm_storage_account.staticweb.id
  error_404_document = "404.html"
  index_document     = "index.html"
}

resource "azurerm_cdn_profile" "cdn_profile" {
  name                = var.cdn_profile_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = "global"
  sku                 = "Standard_Microsoft"
}

resource "azurerm_cdn_endpoint" "cdn_endpoint" {
  name                = var.cdn_endpoint_name
  profile_name        = azurerm_cdn_profile.cdn_profile.name
  resource_group_name = azurerm_resource_group.rg.name
  location            = "global"
  origin {
    name      = "resumeorigin"
    host_name = local.static_web_host
  }
    
  is_http_allowed  = false
  is_https_allowed = true
  is_compression_enabled = true
  origin_host_header = local.static_web_host
  content_types_to_compress = ["application/eot", "application/font", "application/font-sfnt", "application/javascript", "application/json", "application/opentype", "application/otf", "application/pkcs7-mime", "application/truetype", "application/ttf", "application/vnd.ms-fontobject", "application/x-font-opentype", "application/x-font-truetype", "application/x-font-ttf", "application/x-httpd-cgi", "application/x-javascript", "application/x-mpegurl", "application/x-opentype", "application/x-otf", "application/x-perl", "application/x-ttf", "application/xhtml+xml", "application/xml", "application/xml+rss", "font/eot", "font/opentype", "font/otf", "font/ttf", "image/svg+xml", "text/css", "text/csv", "text/html", "text/javascript", "text/js", "text/plain", "text/richtext", "text/tab-separated-values", "text/x-component", "text/x-java-source", "text/x-script", "text/xml"]
}

resource "azurerm_cdn_endpoint_custom_domain" "custom_domain" {
  name               = "resume"
  cdn_endpoint_id    = azurerm_cdn_endpoint.cdn_endpoint.id
  host_name          = var.custom_domain_name

  cdn_managed_https {
    certificate_type = "Dedicated"
    protocol_type = "ServerNameIndication"
  }
}
# Writing and Deploying the Resume's Frontend

The following Azure resources directly serve the static site's files, set up the custom domain and configure the HTTPS infrastructure:

- An Azure Storage Account.
- An Azure CDN Profile.
- An Azure CDN Endpoint.

## Local Development Environment details

The following tools need to be installed to support local development:

- Azure CLI.
- Terraform CLI.
<!-- - Azure Functions Core Tools. -->

### Setting up Azure CLI

To install **Azure CLI** in one step use this script:

```sh
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

To login to Azure CLI run:

```sh
az login --use-device-code
```

As I'm using GitHub Codespaces as my development environment (which doesn't have direct browser access) I need to use the `--use-device-code` option. If you are using your own PC just run `az login` and follow the login workflow to enter your credentials (later when we setup CI/CD with GitHub Actions, we will be using managed identities with OpenID Connect for authentication).

Make sure to select the Azure subscription where you want to deploy the resources so that when you run terraform locally for testing you don't deploy on the wrong subscription by accident (ignore this if you only have one subscription).

If you are not sure what subscription you are pointing at, you can run:

```sh
az account list
```

In the json response make sure the desired subscription includes `"isDefault": true`. If it is `false` you can select it by running:

```sh
az account set -s <subscription-id>
```

### Setting Up Terraform

#### Installing Terraform CLI

First, install the Hashicorp keys:

```sh
wget -O - https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
```

Then, configure the Hashicorp repository:

```sh
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(grep -oP '(?<=UBUNTU_CODENAME=).*' /etc/os-release || lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
```

Finally, update the repository and install **Terraform**:

```sh
sudo apt update && sudo apt install terraform
```

#### Setting Up Terraform CLI with Local State

We need to configure the **Terraform CLI** for it to work with a local state while we test our configuration (later we will move to a remote state using Terraform Cloud and automation with GitHub Actions).

Now, use a text editor (I will use `vim`) to create/open the `terraform.tf` file:

```sh
vim terraform.tf
```

Paste the following code snippet and make sure to pin the terraform and provider version so that you always run jobs under a version you have perviously tested (in my case I'm using terraform 1.14.1 and azurerm 4.55.0 which are the stable versions as of december 2025)::

```sh
terraform {
  required_version = "1.14.1"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "4.55.0"
    }
  }
  
    # cloud {}
}
```

Note the `cloud` block is commented because we are not using a remote state yet.

Then, you can run:

```sh
terraform init
```

You should see an output similar to this:

```sh
Initializing the backend...

Initializing provider plugins...
- Finding hashicorp/azurerm versions matching "= 4.55.0"...
- Installing hashicorp/azurerm v4.55.0...
- Installed hashicorp/azurerm v4.55.0 (signed by HashiCorp)

Terraform has been successfully initialized!

You may now begin working with Terraform. Try running "terraform plan" to see
any changes that are required for your infrastructure. All Terraform commands
should now work.

If you ever set or change modules or backend configuration for Terraform,
rerun this command to reinitialize your working directory. If you forget, other
commands will detect it and remind you to do so if necessary.
```

With the last step completed, the **Terraform CLI** should be able run `terraform plan` and `terraform apply` commands, store states locally and run jobs directly own your development environment. Terraform will [authenticate implicitly with Azure](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/guides/azure_cli) if you already authenticated with the **Azure CLI** as stated [before](#setting-up-azure-cli).

From here you can [proceed to setup terraform files](#setting-up-terraform-files)

#### Setting Up Terraform CLI with Remote State

When we are ready to automate our deployment we will be saving the Azure terraform state to [Terraform Cloud](https://spacelift.io/blog/what-is-terraform-cloud) so that we can use it with the ephemeral jobs of GitHub Actions at deployment. If we would keep our terraform state local we could only use it from that environment which is not the most flexible way and we could't leverage DevOps tooling.

To achieve this, you first need to create an account on [Terraform Cloud](https://app.terraform.io/session) and then set up an [organization](https://developer.hashicorp.com/terraform/cloud-docs/users-teams-organizations/organizations#creating-organizations) and a [workspace](https://developer.hashicorp.com/terraform/cloud-docs/workspaces) where you would be able to manage your state, access settings, jobs, etc.

In order to login to **Terraform Cloud** I recommend you create a [team API token](https://developer.hashicorp.com/terraform/cloud-docs/users-teams-organizations/api-tokens#team-api-tokens) as this will scope access to the a specific organization and not to the entire account (which is the behavior when you use a [user token](https://developer.hashicorp.com/terraform/cloud-docs/users-teams-organizations/api-tokens#team-api-tokens) belonging to the account owner).

When you have all this in place, you could login locally to **Terraform Cloud** running `terraform login` and following that workflow, which will prompt you to create a token, but as you already created it you can set it up directly. Make sure you are in your home directory:

```sh
cd
```

Now, create the following file:

```sh
vim .terraform.d/credentials.tfrc.json
```

Paste this json snippet and replace `<API token>` with your own token before saving the file:

```sh
{
  "credentials": {
    "app.terraform.io": {
      "token": "<API token>"
    }
}
```

Next, you need to configure two environment variables belonging to the terraform organization and workspace you created earlier:

```sh
export TF_CLOUD_ORGANIZATION=<your organization>
export TF_WORKSPACE=<your workspace>
```

Open the `terraform.tf` file:

```sh
vim terraform.tf
```

Paste the following code snippet (note the `cloud` block is uncommented now):

```sh
terraform {
  required_version = "1.14.1"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "4.55.0"
    }
  }

    cloud {}
}
```

As you can see, the `cloud` block is empty as you already have configured the environment variables `TF_CLOUD_ORGANIZATION` and `TF_WORKSPACE`, so you can skip the step to declare them in the `cloud` block (you can still choose to do it, however, consider comment them when you've setup CI/CD with GitHub Actions because they will be declared directly on that workflow and might be redundant). However, don't delete the block as it is necessary for terraform to setup a remote state.

Finally, you can run:

```sh
terraform init
```

You should see an output similar to this:

```sh
Initializing HCP Terraform...
Initializing provider plugins...
- Reusing previous version of hashicorp/azurerm from the dependency lock file
- Using previously-installed hashicorp/azurerm v4.55.0

HCP Terraform has been successfully initialized!

You may now begin working with HCP Terraform. Try running "terraform plan" to
see any changes that are required for your infrastructure.

If you ever set or change modules or Terraform Settings, run "terraform init"
again to reinitialize your working directory.
```

If you see it, it means that the **Terraform CLI** has been authenticated with your workspace on **Terraform Cloud** but you won't be able to run `terraform plan` and `terraform apply` commands for local testing until you set the environment variables to authenticate with Azure in your workspace's settings. You will see the terraform logs from your terminal but the jobs will be executing remotely and your state will be saved on **Terraform Cloud** as well.

Also, a [.terraform.lock.hcl](.terraform.lock.hcl) will be created on your base directory to ensure the required version of the provider is locked. You will need to run `terraform init -upgrade` every time you modify the provider version otherwise you will see a `Failed to query available provider packages` error:

```sh
Waiting for the plan to start...

Terraform v1.14.1
on linux_amd64
Initializing plugins and modules...
Initializing HCP Terraform...
Initializing provider plugins...
- Reusing previous version of hashicorp/azurerm from the dependency lock file
╷
│ Error: Failed to query available provider packages
│ 
│ Could not retrieve the list of available versions for provider
│ hashicorp/azurerm: locked provider registry.terraform.io/hashicorp/azurerm
│ 4.52.0 does not match configured version constraint 4.55.0; must use
│ terraform init -upgrade to allow selection of new versions
│ 
│ To see which modules are currently depending on hashicorp/azurerm and what
│ versions are specified, run the following command:
│     terraform providers
╵
Operation failed: failed running terraform init (exit 1)
```

As you can see above, [terraform.tf](./terraform.tf) was modified to work with `azurerm 4.55.0` but [.terraform.lock.hcl](.terraform.lock.hcl) hasn't been upgraded from `azurerm 4.52.0`.

Make sure to match the required terraform version on [terraform.tf](./terraform.tf) with the one configured on your **Terraform Cloud** workspace's settings:

![](./images/required-terraform-version.png)

If you don't, you may receive an `Unsupported Terraform Core version` error like this one:

```sh
Waiting for the plan to start...

Terraform v1.14.0
on linux_amd64
Initializing plugins and modules...
Initializing HCP Terraform...
╷
│ Error: Unsupported Terraform Core version
│ 
│   on terraform.tf line 2, in terraform:
│    2:   required_version = "1.14.1"
│ 
│ This configuration does not support Terraform version 1.14.0. To proceed,
│ either choose another supported Terraform version or update this version
│ constraint. Version constraints are normally set for good reason, so
│ updating the constraint may lead to other errors or unexpected behavior.
╵
Operation failed: failed running terraform init (exit 1)
```

As you can see above, the workspace is configured to run version `1.14.0` while the [terraform.tf](./terraform.tf) file was expecting version `1.14.1`

#### Setting Up Terraform Files

You need to create the `provider.tf` file:

```sh
touch provider.tf
```

This file is necessary to declare the Azure provider we are using (`azurerm`) and any optional features that might be needed.

Open the file:

```sh
vim provider.tf
```

 Then, copy the content from [`provider.tf`](provider.tf).

The next file is `variables.tf`:

```sh
touch variables.tf
```

You will need this file to declare the variables to be used in your Azure infrastructure, this way you avoid hardcoding values on your code and is much more maintainable.

Open the file:

```sh
vim variables.tf
```

You can use [`variables.tf`](variables.tf) as a template but you might want to use your own naming convention.

Finally, create the `main.tf` file:

```sh
touch main.tf
```

This will be the main document where you will write you resources using [Hashicorp Configuration Language](https://developer.hashicorp.com/terraform/language) or `HCL` for short.

You can copy the content from [`main.tf`](main.tf) (which I will discuss much more [bellow](#azure-infrastructure-key-considerations)) after you have opened the file:

```sh
vim main.tf
```

## Azure Infrastructure Key Considerations

When writing the Azure Infrastructure (where the resume will be served as a static site) on `main.tf`, the following considerations were taken:

- A [resource group](https://dev.to/lotanna_obianefo/understanding-azure-resource-groups-a-comprehensive-guide-34he) was needed to hold all the frontend resources.
- I used the `eastus` [region](https://learn.microsoft.com/en-us/azure/reliability/regions-list) as it was closer to my location.
- For the **storage account** where the resume files will be stored ([using blob storage](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction)), the [standard tier](https://learn.microsoft.com/en-us/azure/storage/common/storage-account-overview?toc=%2Fazure%2Fstorage%2Fblobs%2Ftoc.json&bc=%2Fazure%2Fstorage%2Fblobs%2Fbreadcrumb%2Ftoc.json) and [Locally Redundant Storage replication](https://learn.microsoft.com/en-us/azure/storage/common/storage-redundancy) (LRS) were chosen as the more cost-effective options for our purposes.
- The [built-in feature to serve static sites stored as blob files](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-static-website) was used to publish the resume static files.
- As **Azure Storage** doesn't support HTTP infrastructure with custom domains, it was needed to integrate it with [Azure CDN](https://docs.azure.cn/en-us/cdn/cdn-overview) to enable this functionality. **Note**: is no longer possible use the `Standard_Microsoft` SKU for Azure CDN as it was deprecated in [August 2025](https://www.linkedin.com/pulse/azure-cdn-standard-from-microsoft-classic-retirement-what-salamat-l4n1f/). The only options within Azure is to use [Azure Front Door](https://learn.microsoft.com/en-us/azure/frontdoor/front-door-overview) on its [standard or premium tier](https://learn.microsoft.com/en-us/azure/frontdoor/front-door-cdn-comparison) which could be cost-prohibited if you only plan to host a site on that service.
- [The endpoint configured in the Azure CDN profile](https://learn.microsoft.com/en-us/azure/cdn/scripts/cli/cdn-azure-cli-create-endpoint?toc=%2Fazure%2Ffrontdoor%2Ftoc.json) was configured to be accessible through HTTPS only.
- The local variable `static_web_host` was created to avoid redundant code when configuring the endpoint.
- The endpoint was set up to validate ownership of a domain ([resume.technicalmind.cloud](https://resume.technicalmind.cloud)) in an external registrar (in my case I used Cloudflare) and enable a [managed certificate without additional cost](./images/domain-certificate-validation.png).
- You need to set up a [CNAME record pointing to your endpoint hostname](./images/cloudflare-cname-record.png) before applying the infrastructure otherwise the deployment will fail.

## Locally Testing Your Terraform Configuration

In time, we will use **GitHub Actions** workflows to automate deployment but, right now you are ready to test your terraform configuration to see if the Azure resources are deployed in the way you expect.

If your followed the instructions to setup [Azure CLI](#setting-up-azure-cli) and [Terraform CLI](#installing-terraform-cli) you are good to go. Just double check the Azure subscription your are pointing to because it will be there where terraform will deploy your infrastructure (so make sure the identity you logged in to has sufficient privileges, a [contributor role](https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/privileged#contributor)  will be enough for now, we will tighten up things later).

Next, you will be using [`terraform plan`](https://developer.hashicorp.com/terraform/cli/commands/plan) and [`terraform apply`](https://developer.hashicorp.com/terraform/cli/commands/apply) to both preview and apply your configuration.

If all goes well you should see the three resources on the [Azure Portal](https://portal.azure.com/):

![An Azure resource group containing an Azure Front Door profile, a CDN endpoint and a storage account](./images/frontend-resources-deployed.png)

## Setting Up Authentication for Automation Workflow

Now that you know that your terraform configuration works as intended, we can proceed to make the final adjustments on **Azure** to prepare authentication for the automation workflow with **GitHub Actions** and **Terraform Cloud**.

### Setting Up Azure Identities

In order for **Terraform Cloud** and **GitHub** can access your [subscriptions](https://learn.microsoft.com/en-us/azure/cost-management-billing/manage/cloud-subscription) to run commands and deploy resources we need to create secure identities that represent these workloads.

Specifically, I recommend using [user-assigned managed identities](https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/manage-user-assigned-managed-identities-azure-cli) as they are ideal for this scenario (workloads external to Azure with non-interactive authentication) with the added benefit that we don't need to rotate secrets manually (Azure manage secrets automatically).

Normally, we can only use managed identities to authenticate resources within Azure, in fact, system-assigned managed identities  cannot be used outside Azure, however, [user-assigned managed identities](https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/manage-user-assigned-managed-identities-azure-cli) can "break" this rule by using the [OpenID Connect](https://openid.net/developers/how-connect-works/) (OIDC) protocol to validate ephemeral authentication tokens from external services (like a GitHub Actions workflow requesting to deploy resources).

#### Setting Up Authentication for GitHub Actions

You can [use these instructions](https://learn.microsoft.com/en-us/azure/developer/github/connect-from-azure-openid-connect) following the **option 2** to configure authentication for ephemeral jobs scoped to the specific GitHub repository where you hold your project.

In short you need to:

- Create a **user-assigned managed identity** by running the [`az identity create`](https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/manage-user-assigned-managed-identities-azure-cli) command.
- Configure the managed identity with the appropriate roles on the subscription of your choice. I recommend you only set the `
CDN Endpoint Contributor` role and the `Storage Blob Data Contributor` role for this identity ([see reference image](./images/managed-identity-assigment-1.png)) as this workflow only need access to upload blobs and purge the CDN endpoint (the resources will be deployed from **Terraform Cloud** which will have its own identity).
- Configure the identity to trust and external identity provider (in this case GitHub) using the [`az identity federated-credential create`](https://learn.microsoft.com/en-us/cli/azure/identity/federated-credential#az-identity-federated-credential-create) command and providing values for [`--subject`](https://docs.github.com/en/actions/reference/security/oidc#filtering-for-a-specific-branch), [`--audiences`](https://docs.github.com/en/actions/reference/security/oidc#customizing-the-audience-value) and [`--issuer`](https://docs.github.com/en/actions/reference/security/oidc#standard-audience-issuer-and-subject-claims). You can check the federated credential configuration using the [`az identity federated-credential list`](https://learn.microsoft.com/en-us/cli/azure/identity/federated-credential?view=azure-cli-latest#az-identity-federated-credential-listx) command or alternatively in the identity's settings using the [Azure Portal](https://portal.azure.com/) ([see reference image](./images/federated-managed-identity-1.png)).
- Configure [GitHub Secrets](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets) on your project's repository with the names `AZURE_CLIENT_ID`, `AZURE_TENANT_ID` and `AZURE_SUBSCRIPTION_ID`. As values you must use your identity's **Client ID**, **Tenant ID** and **Subscription ID** respectively ([see reference image](./images/github-actions-secrets.png))

With this steps completed, the **GitGub Actions** workflows (executed from your project's repository) will be able to request ephemeral tokens to Azure. This tokens will be valid only for the duration of the job and scoped for the selected subscription and Azure RBAC Roles.

#### Setting Up Authentication for Terraform Cloud

For **Terraform Cloud** (TFC) we will be using its native integration with OIDC to allow it to request per job ephemeral tokens to authenticate and deploy resources to Azure just like we did with GitHub in the [last section](#setting-up-authentication-for-github-actions).

However, every platform is different and we need to follow the [specific instructions](https://developer.hashicorp.com/terraform/cloud-docs/dynamic-provider-credentials/azure-configuration#use-dynamic-credentials-with-the-azure-provider) for TFC in this case.

Just like before, we need to:

- Create a **user-assigned managed identity** by running the [`az identity create`](https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/manage-user-assigned-managed-identities-azure-cli) command. I recommend not to reuse the same identity you used for **GitHub Actions** as is best to create a specific one to identify this workload.
- Configure the managed identity with the appropriate roles on the subscription of your choice. This time, you must set this identity with the `contributor` role ([see the reference image](./images/managed-identity-assigment-2.png)) as is the minimum permission required to create all the resources for this workflow (the storage account, the Azure CDN profile and the CDN endpoint).
- Configure the identity to trust and external identity provider (in this case TFC) using the [`az identity federated-credential create`](https://learn.microsoft.com/en-us/cli/azure/identity/federated-credential#az-identity-federated-credential-create) command and providing values for [subject, audiences and issuer](https://developer.hashicorp.com/terraform/cloud-docs/dynamic-provider-credentials/azure-configuration#configure-microsoft-entra-id-application-to-trust-a-generic-issuer) (this time you will need to set two federated credentials, one for apply jobs and one of plan jobs). You can check the federated credential configuration using the [`az identity federated-credential list`](https://learn.microsoft.com/en-us/cli/azure/identity/federated-credential?view=azure-cli-latest#az-identity-federated-credential-listx) command or alternatively in the identity's settings using the [Azure Portal](https://portal.azure.com/) ([see reference image](./images/federated-managed-identity-2.png)).
- Configure your TFC workspace with this environment variables: `TFC_AZURE_RUN_CLIENT_ID`, `ARM_TENANT_ID`, `ARM_SUBSCRIPTION_ID`, `ARM_USE_CLI` and `TFC_AZURE_PROVIDER_AUTH`. As values you must use your identity's **Client ID**, **Tenant ID** and **Subscription ID** respectively. The last two must be set to `false` and `true` as this will ensure TFC attempts to authenticate using OIDC ([see reference image](./images/hcp-environment-variables.png)).

With that last step, we have finished our configuration to authenticate TFC with Azure using OIDC.

## Setting up the GitHub Actions Workflow

<!-- To install **Azure Functions Core Tools run**:

```sh
sudo apt-get install azure-functions-core-tools-4
```

In GitHub Codespaces you don't need to configure Microsoft repository to install [Azure Functions Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=linux%2Cisolated-process%2Cnode-v4%2Cpython-v2%2Chttp-trigger%2Ccontainer-apps&pivots=programming-language-python), but you might need to do it in your own PC. -->

<!-- Example for link to specific line
[Upload static site files to Azure Storage](../.github/workflows/deploy.yml#L61) -->
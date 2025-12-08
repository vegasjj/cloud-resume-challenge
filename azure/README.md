# Backend Technical Specifications

The following Azure resources directly serve the static site's files, set up the custom domain and configure the HTTPS infrastructure:

- Azure Storage Account.
- Azure CDN Profile.
- Azure CDN Endpoint.

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

As I'm using GitHub Codespaces as my development environment (which doesn't have direct browser access) I need to use the `--use-device-code` option. If you are using your own PC just run `az login` and follow the login workflow to enter your credentials.

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

For **Terraform**, install the Hashicorp keys:

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

We will be saving the Azure terraform state to [Terraform Cloud](https://spacelift.io/blog/what-is-terraform-cloud) so that we can use it with the ephemeral jobs of GitHub Actions at deployment. If we would keep our terraform state local we could only use it from that environment which is not the most flexible way and we could't leverage DevOps tooling.

To achieve this, you first need to create an account on [Terraform Cloud](https://app.terraform.io/session) and then set up an [organization](https://developer.hashicorp.com/terraform/cloud-docs/users-teams-organizations/organizations#creating-organizations) and a [workspace](https://developer.hashicorp.com/terraform/cloud-docs/workspaces) where you would be able to manage your state, access settings, jobs, etc.

In order to login to **Terraform Cloud** I recommend you create a [team API token](https://developer.hashicorp.com/terraform/cloud-docs/users-teams-organizations/api-tokens#team-api-tokens) as this will scope access to the a specific organization and not to the entire account (which is the behavior when you use a [user token](https://developer.hashicorp.com/terraform/cloud-docs/users-teams-organizations/api-tokens#team-api-tokens) belonging to the account owner).

When you have all this in place, you could login locally to **Terraform Cloud** running `terraform login` and following that workflow, which will prompt you to create a token, but as you already created it you can set it up directly. Make sure you are in your home directory:

```sh
cd
```

Now use a text editor (I will use `vim`) to create the following file:

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

Next, you need to configure two environment variables belonging to your terraform organization and workspace you created earlier:

```sh
export TF_CLOUD_ORGANIZATION=<your organization>
export TF_WORKSPACE=<your workspace>
```

Create a `terraform.tf` file:

```sh
vim terraform.tf
```

Paste the following code snippet and make sure to pin the terraform and provider version so that you always run jobs under a version you have perviously tested (in my case I'm using `terraform 1.14.1` and `azurerm 4.55.0` which are the stable versions as of december 2025):

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

Note the `cloud` block is empty as you already have configured the environment variables `TF_CLOUD_ORGANIZATION` and `TF_WORKSPACE`, so you can skip the step to declare them here (you can still choose to do it, however, consider comment them when you've setup CI/CD with GitHub Actions because they will be declared there and might be redundant). However, don't delete the block as it is necessary for terraform to setup a remote state.

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

If you see it, it means that the **Terraform CLI** has been authenticated with your workspace on **Terraform Cloud** and you should be good and ready to run `terraform plan` and `terraform apply` commands locally when you start coding and testing your infrastructure. You will see the terraform logs from your terminal but the jobs will be executing remotely and your state will be saved on **Terraform Cloud** as well.

Also, a [.terraform.lock.hcl](.terraform.lock.hcl) will be created on your base directory to ensure the required version of the provider is locked. You will need to run `terraform init -upgrade` every time you modify the provider version otherwise you will see an error:

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

<!-- To install **Azure Functions Core Tools run**:

```sh
sudo apt-get install azure-functions-core-tools-4
```

In GitHub Codespaces you don't need to configure Microsoft repository to install [Azure Functions Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=linux%2Cisolated-process%2Cnode-v4%2Cpython-v2%2Chttp-trigger%2Ccontainer-apps&pivots=programming-language-python), but you might need to do it in your own PC. -->

<!-- Example for link to specific line
[Upload static site files to Azure Storage](../.github/workflows/deploy.yml#L61) -->
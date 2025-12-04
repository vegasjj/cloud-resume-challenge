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

Now open `vim` (or the text editor you prefer) to create the following file:

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

Now you need to configure two environment variables belonging to your terraform organization and workspace you created earlier:

```sh
export TF_CLOUD_ORGANIZATION=<your organization>
export TF_WORKSPACE=<your workspace>
```

Now you should be good and ready to run `terraform plan` and `terraform apply` commands locally when you start coding and testing your infrastructure.

<!-- To install **Azure Functions Core Tools run**:

```sh
sudo apt-get install azure-functions-core-tools-4
```

In GitHub Codespaces you don't need to configure Microsoft repository to install [Azure Functions Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=linux%2Cisolated-process%2Cnode-v4%2Cpython-v2%2Chttp-trigger%2Ccontainer-apps&pivots=programming-language-python), but you might need to do it in your own PC. -->

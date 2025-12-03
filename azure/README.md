# Backend Technical Specifications

The following Azure resources directly serve the static site's files, set up the custom domain and configure the HTTPS infrastructure:

- Azure Storage Account.
- Azure CDN Profile.
- Azure CDN Endpoint.

## Local Development Environment details

The following tools need to be installed to support local development:

- Azure CLI.
- Terraform.
<!-- - Azure Functions Core Tools. -->

To install **Azure CLI** in one step use this script:

```sh
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

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

<!-- To install **Azure Functions Core Tools run**:

```sh
sudo apt-get install azure-functions-core-tools-4
```

In GitHub Codespaces you don't need to configure Microsoft repository to install [Azure Functions Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=linux%2Cisolated-process%2Cnode-v4%2Cpython-v2%2Chttp-trigger%2Ccontainer-apps&pivots=programming-language-python), but you might need to do it in your own PC. -->

To login to Azure CLI run:

```sh
az login --use-device-code
```

As I'm using GitHub Codespaces as my development environment (which doesn't have direct browser access) I need to use the `--use-device-code` option. If you are using your own PC just run `az login` and follow the login workflow to enter your credentials.

In the case of terraform you first need to setup a workspace in Terraform Cloud where you'll save the state of your infrastructure.

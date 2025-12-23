# Backend Deployment

<!-- To install **Azure Functions Core Tools run**:

```sh
sudo apt-get install azure-functions-core-tools-4
```

In GitHub Codespaces you don't need to configure Microsoft repository to install [Azure Functions Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=linux%2Cisolated-process%2Cnode-v4%2Cpython-v2%2Chttp-trigger%2Ccontainer-apps&pivots=programming-language-python), but you might need to do it in your own PC. -->

<!-- Example for link to specific line
[Upload static site files to Azure Storage](../.github/workflows/deploy.yml#L61) -->

It is not necessary to setup another API token to authenticate with Terraform Cloud locally if you are working on the same development environment. Just make sure to be running the same version of terraform in both workspaces to avoid conflicts when running jobs.

![image depicting an authentication error in a logics app workflow with the slack api](./images/slack-channel-authentication.png)
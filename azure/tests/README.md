# Writing and executing smoke tests for the API

The test must run at the end of provisioning all services but there is an issue.

There are not staging slots so production is affected before knowing if all validations checks are green.

One possible solution is deploying and immediately do a rollback if the test fails.

Another solutions could be a staging environment or a ephemeral sandbox.

Ultimately, I could just remark the fact the this is a demonstrative project and go on with the simple deployment without accounting for the production risk (but it must be stated so it is clear I know the potential issues).

## Shadow infra solution

- Run test using "ghost infra" or ephemeral sandbox where it can build and test the current version of the deployment.
- If successful deploy to production's single slot.
- Delete the temporary environment (in any event).

This is the most clean solution but it is necessary to account for name collisions of resources.

## Redeploy last successful Git commit

- Retrieve last successful Git commit using the GitHub API for more reliability.
- Deploy to production.
- If test fails, redeploy last successful committed environment (downtime is incurred).

## Test strategy

Ensure test authenticates and run before implementing safeguards to production.

Test on pushes before implementing pull request variant.

Testing workflow must be configured to run on pull requests (recreating the "ghost" environment) every time
to avoid merging errors and failed deployments to the main branch.

# Writing and executing smoke tests for the API

The test must run at the end of provisioning all services but there is an issue.

There are no staging slots so production is affected before knowing if all validation checks are green.

One possible solution is deploying and immediately do a rollback if the test fails.

Another solution could be a staging environment or an ephemeral sandbox.

Ultimately, I could just remark the fact that this is a demonstrative project and go on with the simple deployment without accounting for the production risk (but it must be stated so it is clear I know the potential issues).

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

- Ensure test authenticates and run before implementing safeguards to production (Success).
- Test on pushes before implementing pull request variant. (Success)
- Test response formatting and authentication separately from testing and comparing response and db values (Success)
- Consider removal of poorly integrated tests (Pending)
- Consider replacing custom function to validate environment variables with using playwright natively (Success).
- Find a way to check if the entity is created in the database like with `create_entity.py`, maybe the order of the validation can help (Pending).
- Testing workflow must be configured to run on pull requests (recreating the "ghost" environment) every time (backend only) to avoid merging errors and failed deployments to the main branch (Pending).

Running the tests in a container is an option if I would be worried about polluting the host but this is a single test so it shouldn't be a problem to run the test on the host.

It shouldn't be necessary to keep a Terraform remote state for the test as it will be created and torn down immediately.

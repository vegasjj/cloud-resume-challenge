# Writing and executing smoke tests for the API

The smoke test validates that the Azure Function API and Database infrastructure are in place to process web application requests successfully. The monitoring system is not validated.

Playwright is used because it provides a Python library, maintaining consistency with the API's implementation language.

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

- Ensure test authenticates and run before implementing safeguards to production (Completed).
- Test on pushes before implementing pull request variant. (Completed)
- Test response formatting and authentication separately from testing and comparing response and db values (Completed).
- Consider removal of poorly integrated tests (Completed).
- Consider replacing custom function to validate environment variables using playwright natively (Completed).
- The database assertion needs to be revisited as this should be validated and handled at the API level (Completed).
- Errors triggered when calling the API must be sent in JSON format so it can be correctly handled in the test for clarity and troubleshooting (Completed).
- Standardize the error responses in the API with a function helper, also use logging.exception instead of logging.error to capture stack traces automatically (check Gemini) (Pending).
- Add environment variable checks on the API that can be validated on the test workflow (Pending).
- Test for the database entity to exist (Pending).
- Test for the database table to exist (Pending).
- Test for the database account to exist and authenticate (Pending).
- Decide if the final comparison between the database value and the API response value makes sense (Completed).
- Testing workflow must be configured to run on pull requests (recreating the "ghost" environment) every time (backend only) to avoid merging errors and failed deployments to the main branch (Pending).
- A safe way to recreate the ephemeral environment on pull requests must be implemented to avoid Azure credentials abuse from untrusted PRs (Pending).

Running the tests in a container is an option if I would be worried about polluting the host but this is a single test so it shouldn't be a problem to run the test on the host.

It shouldn't be necessary to keep a Terraform remote state for the test as it will be created and torn down immediately.

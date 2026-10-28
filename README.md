# project_2_cicd_gcp

## Private provider schemas and Renovate

The `Provider schema refresh` GitHub Actions workflow reads
`contracts/bigquery/*.json` from `musain11/master_project_complete` on its
`dev` branch. It validates the JSON and publishes the files as a
`provider-bigquery-contracts-*` workflow artifact, available for seven days.
The pinned provider commit is recorded in [`provider-schemas.json`](./provider-schemas.json).
Renovate uses the Git refs datasource to update that commit and open a PR.
The workflow explicitly targets this repository and its `dev` base branch.

The workflow requests a short-lived provider token through the `octo-sts`
service using the provider's `.github/chainguard/project_2_cicd_gcp.sts.yaml`
trust policy. The action uses the documented `octo-sts.dev` endpoint by
default; no endpoint variable is required. The Octo STS GitHub App must be
installed with access to the provider repository. No PAT, service-account key,
or GCP authentication is used by this workflow. Enable **Allow GitHub Actions
to create and approve pull requests** in the repository's Actions settings so
Renovate can open update PRs using the workflow token.

The workflow runs on relevant pushes to `dev` or `main`, manual dispatch, and a
six-hour schedule. Scheduled workflows run from the default branch (`main`),
so the workflow is also present there and checks out consumer `dev` before
reading the pin/configuration or running Renovate. The provider trust policy
allows only this repository's `main` and `dev` OIDC subjects, and the minted
provider token remains read-only. Renovate targets consumer `dev`.
See [`poc_sts_renovate.md`](./poc_sts_renovate.md) for the end-to-end proof,
test commits, run results, and update procedure.

The Terraform deployment workflow (`terraform.yml` on `main`) is separate.
The provider-schema workflow does not run Terraform or deploy to GCP.
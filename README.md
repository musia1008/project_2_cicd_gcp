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

The workflow runs on pushes to `dev`. Manual dispatch is available after the
workflow file is present on the default branch; select `dev` as the run
ref. It is intentionally not scheduled: GitHub schedules run against the
default branch (`main` here), but the trust policy accepts only the `dev`
OIDC subject. To enable scheduled Renovate runs without broadening trust,
make `dev` the repository default branch.

The existing Terraform deployment workflow, if present on another branch, is
not part of this provider-schema workflow.
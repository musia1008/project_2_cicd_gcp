# POC: Private BigQuery schemas with STS and Renovate

## Result

The end-to-end update path was exercised successfully:

1. The consumer workflow exchanged GitHub's OIDC identity for a short-lived,
   read-only token from Octo STS.
2. It checked out the private provider repository and validated all 18
   BigQuery schema JSON files.
3. Renovate detected a newer provider commit, created its update branch, and
   opened [consumer PR #2](https://github.com/musia1008/project_2_cicd_gcp/pull/2)
   targeting `dev`.
4. The workflow also ran successfully from consumer `main`, verifying the
   default-branch identity needed for scheduled polling.

The Renovate update PR is intentionally left open for review. It changes only
the pinned provider commit; it does not change any BigQuery schema JSON.

## What changed for the test

Three documentation-only commits were pushed to provider `dev`:

| Commit | Change |
|---|---|
| `5846f0c` | Documented ownership and review of BigQuery contract schemas. |
| `859b5ad` | Added schema compatibility guidance. |
| `473d609` | Documented immutable commit pins and consumer validation. |

These updates added `contracts/bigquery/README.md`. The schema JSON files were
not edited. Renovate detected the resulting branch-head change:

- Consumer pin before the test: `da9120bbb05492f0c6c717931cff8fed8dbc72f9`
- Provider `dev` after the test: `473d609132f56e535070971e044294e398cb737f`
- Renovate PR: `da9120b` → `473d609`, based on consumer `dev`

The three provider commits intentionally produce one Renovate PR: Renovate
tracks the latest commit of the configured provider branch, not each
intermediate commit separately.

## How the workflow works

1. **Trigger:** the consumer workflow runs on relevant pushes to `dev` or
   `main`, manual dispatch, and every six hours. The workflow file is present
   on both `dev` and default branch `main`, because GitHub runs scheduled
   workflows from the default branch.
2. **Use consumer `dev` configuration:** regardless of whether the event is a
   push, dispatch, or schedule, the job checks out consumer `dev`. That is where
   `provider-schemas.json`, `renovate.json`, and the validator are maintained.
3. **Authenticate to the provider:** GitHub OIDC identifies the exact consumer
   repository and branch. The provider trust policy accepts only the
   `main` and `dev` branch subjects. Octo STS issues a short-lived token with
   `contents: read` and `metadata: read`; no PAT, service-account key, or GCP
   authentication is used.
4. **Read a reproducible provider revision:** `provider-schemas.json` stores
   the provider repository, tracked branch (`dev`), and full commit SHA. The
   workflow checks out that exact SHA rather than a moving branch name.
5. **Validate and publish:** the validator checks the provider BigQuery JSON
   files. The run uploads the schemas as an artifact retained for seven days.
6. **Find provider updates:** Renovate uses its `git-refs` datasource and the
   temporary STS token to check the latest `dev` commit. It uses the consumer
   workflow token to create or update a PR against consumer `dev`.
7. **Adopt an update:** review and merge the Renovate PR. The merge updates the
   pin on consumer `dev`; the push trigger then checks out and validates the
   newly pinned provider commit.

## Verification evidence

| Check | Result |
|---|---|
| [Provider STS policy PR #4](https://github.com/musain11/master_project_complete/pull/4) | Merged after trust-policy validation, Python, Dataform, and Terraform checks passed. |
| Provider CI for test revision `473d609` | [Python, Dataform, and Terraform checks](https://github.com/musain11/master_project_complete/actions/runs/40710900154) and [workload-identity verification](https://github.com/musain11/master_project_complete/actions/runs/40710900041) passed. |
| Consumer run [#40711170154](https://github.com/musia1008/project_2_cicd_gcp/actions/runs/40711170154) | Successful from `dev`: OIDC/STS, provider checkout, 18-schema validation, artifact upload, Renovate extraction, and PR creation. |
| Consumer run [#40711716142](https://github.com/musia1008/project_2_cicd_gcp/actions/runs/40711716142) | Successful from `main`: the main-branch OIDC subject was accepted and Renovate still targeted consumer `dev`. |
| Published artifact | `provider-bigquery-contracts-7f9b4dea02497b60ea6798550d8ae48a51aaa9ec`, present and unexpired after run #40711170154. |
| Local validation of exact provider revision `473d609` | `py -3 scripts/validate_provider_schemas.py D:\office_learnings\master_project_complete\contracts\bigquery` passed: 18 files validated. |
| Renovate extraction | 8 dependencies found: 7 GitHub Actions references and 1 provider commit reference. |
| Consumer PR #2 | Open, mergeable, and targets `dev`; it updates the provider digest to `473d609`. |
| Provider schema content | No schema JSON changes were made in the three test commits. |

The successful PR creation confirms the repository setting **Allow GitHub
Actions to create and approve pull requests** is enabled. The scheduled
workflow is configured for every six hours; the POC verified its default-branch
workflow and STS path with a push-triggered run, but did not wait for the next
cron tick.

## What to do next

Review [consumer PR #2](https://github.com/musia1008/project_2_cicd_gcp/pull/2)
and merge it when satisfied. After merge, confirm the `dev` push-triggered
workflow checks out provider commit `473d609` and uploads its schema artifact.
Future provider updates on `dev` will be discovered during the next scheduled
run (within six hours), or sooner when a relevant consumer `dev` change
triggers the workflow.

This workflow only reads and validates provider schemas. It does not run
Terraform or deploy to GCP.

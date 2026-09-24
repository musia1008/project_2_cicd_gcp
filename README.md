# project_2_cicd_gcp

This project creates branch-specific BigQuery datasets and tables using Terraform, then deploys the Terraform configuration through GitHub Actions with Google Cloud Workload Identity Federation (WIF).

## Resources Created

- `dev` branch: dataset `temp_dev`, table `student_dev`
- `test` branch: dataset `temp_test`, table `student_test`
- `prod` branch: dataset `temp_prod`, table `student_prod`
- Columns: `roll_number` (`INT64`), `name` (`STRING`), and `class` (`STRING`), all required.

## One-Time Google Cloud Setup

Enable BigQuery:

```powershell
gcloud services enable bigquery.googleapis.com --project=my-goal-learning
```

Grant the WIF service account permission to create the dataset and table:

```powershell
gcloud projects add-iam-policy-binding my-goal-learning --member="serviceAccount:github-deployer@my-goal-learning.iam.gserviceaccount.com" --role="roles/bigquery.admin"
```

The account running these commands must be a project administrator. Do not add a JSON key to GitHub.

## GitHub Variables

In `Settings -> Secrets and variables -> Actions -> Variables`, create these repository variables:

```text
GCP_PROJECT_ID=my-goal-learning
GCP_WIF_PROVIDER=projects/820724304018/locations/global/workloadIdentityPools/github-pool/providers/github-provider
GCP_SERVICE_ACCOUNT=github-deployer@my-goal-learning.iam.gserviceaccount.com
TF_STATE_BUCKET=REPLACE_WITH_YOUR_UNIQUE_TERRAFORM_STATE_BUCKET
```

These are Variables, not Secrets. WIF uses GitHub's short-lived OIDC token and does not require a service-account key.

Create the Terraform state bucket once, using a globally unique bucket name:

```powershell
gcloud storage buckets create gs://REPLACE_WITH_YOUR_UNIQUE_TERRAFORM_STATE_BUCKET --project=my-goal-learning --location=us-central1 --uniform-bucket-level-access
```

Enable object versioning:

```powershell
gcloud storage buckets update gs://REPLACE_WITH_YOUR_UNIQUE_TERRAFORM_STATE_BUCKET --versioning
```

Allow the GitHub deployment service account to use the Terraform state bucket:

```powershell
gcloud storage buckets add-iam-policy-binding gs://REPLACE_WITH_YOUR_UNIQUE_TERRAFORM_STATE_BUCKET --member="serviceAccount:github-deployer@my-goal-learning.iam.gserviceaccount.com" --role="roles/storage.objectAdmin"
```

The existing provider was restricted to `main`. Update it to allow the three deployment branches:

```powershell
gcloud iam workload-identity-pools providers update-oidc github-provider --project=my-goal-learning --location=global --workload-identity-pool=github-pool --issuer-uri="https://token.actions.githubusercontent.com/" --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner" --attribute-condition="assertion.repository == 'musia1008/project_2_cicd_gcp' && (assertion.ref == 'refs/heads/dev' || assertion.ref == 'refs/heads/test' || assertion.ref == 'refs/heads/prod' || assertion.ref.startsWith('refs/pull/'))"
```

## Deploy

The workflow is `.github/workflows/terraform.yml`.

Create a pull request targeting `dev`, `test`, or `prod` to run Terraform format, validation, and plan. Push or merge to `dev` to create `temp_dev.student_dev`, to `test` to create `temp_test.student_test`, or to `prod` to create `temp_prod.student_prod`.

## Local Terraform Checks

```powershell
terraform -chdir=terraform init
```

```powershell
terraform -chdir=terraform fmt -check -recursive
```

```powershell
terraform -chdir=terraform validate
```

For a local plan, authenticate Application Default Credentials first:

```powershell
gcloud auth application-default login
```

```powershell
terraform -chdir=terraform plan -var="project_id=my-goal-learning"
```

## Verify the Table

```powershell
gcloud bigquery tables describe my-goal-learning:temp_dev.student_dev
```

Insert a test row:

```powershell
gcloud bigquery query --use_legacy_sql=false "INSERT INTO my-goal-learning.temp_dev.student_dev (roll_number, name, class) VALUES (1, 'Alice', '10A')"
```

Query the row:

```powershell
gcloud bigquery query --use_legacy_sql=false "SELECT roll_number, name, class FROM my-goal-learning.temp_dev.student_dev"
```

## Important Notes

- Terraform state is stored in the configured GCS bucket under separate `dev`, `test`, and `prod` prefixes.
- The GitHub provider condition must allow `dev`, `test`, and `prod`, as shown above.
- `roles/bigquery.admin` is convenient for learning. Use narrower roles for production.
- The WIF service-account IAM binding must include the repository principal for `musia1008/project_2_cicd_gcp`.
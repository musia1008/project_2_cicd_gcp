output "bigquery_dataset" {
  description = "Created BigQuery dataset ID."
  value       = google_bigquery_dataset.school.dataset_id
}

output "bigquery_table" {
  description = "Created BigQuery table ID."
  value       = google_bigquery_table.student.table_id
}

output "bigquery_table_reference" {
  description = "Fully qualified BigQuery table reference."
  value       = "${var.project_id}.${google_bigquery_dataset.school.dataset_id}.${google_bigquery_table.student.table_id}"
}

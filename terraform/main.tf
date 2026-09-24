resource "google_bigquery_dataset" "school" {
  dataset_id = var.dataset_id
  location   = var.location

  delete_contents_on_destroy = false
}

resource "google_bigquery_table" "student" {
  dataset_id = google_bigquery_dataset.school.dataset_id
  table_id   = var.table_id

  schema = jsonencode([
    {
      name        = "roll_number"
      type        = "INT64"
      mode        = "REQUIRED"
      description = "Student roll number."
    },
    {
      name        = "name"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Student name."
    },
    {
      name        = "class"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Student class or grade."
    }
  ])
}

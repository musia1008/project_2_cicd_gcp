variable "project_id" {
  description = "Google Cloud project ID."
  type        = string
}

variable "region" {
  description = "Google Cloud region used by the provider."
  type        = string
  default     = "us-central1"
}

variable "dataset_id" {
  description = "BigQuery dataset ID."
  type        = string
  default     = "school_data"
}

variable "table_id" {
  description = "BigQuery table ID."
  type        = string
  default     = "student"
}

variable "location" {
  description = "BigQuery dataset location."
  type        = string
  default     = "US"
}

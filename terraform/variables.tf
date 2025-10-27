variable "project_id" {
  description = "The ID of the Google Cloud project."
  type        = string
}

variable "location" {
  description = "The Google Cloud region to deploy the resources in."
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "The name of the Cloud Run service."
  type        = string
}

variable "repository_id" {
  description = "The ID of the Artifact Registry repository."
  type        = string
}

variable "image_name" {
  description = "The name of the Docker image."
  type        = string
}

variable "repo_name" {
  description = "The name of the source repository."
  type        = string
}

variable "branch_name" {
  description = "The name of the branch to trigger builds from."
  type        = string
}

variable "image_tag" {
  description = "The tag for the Docker image."
  type        = string
  default     = "latest"
}

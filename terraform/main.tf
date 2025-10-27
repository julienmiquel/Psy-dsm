terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.38.0"
    }
  }
  backend "gcs" {}
}

provider "google" {
  project = var.project_id
  region  = var.location
}

resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "iam.googleapis.com",
    "storage.googleapis.com",
  ])
  project            = var.project_id
  service            = each.key
  disable_on_destroy = false
}


resource "google_artifact_registry_repository" "default" {
  project       = var.project_id
  location      = var.location
  repository_id = var.repository_id
  description   = "Docker repository"
  format        = "DOCKER"
}

resource "google_cloud_run_v2_service" "default" {
  project    = var.project_id
  name       = var.service_name
  location   = var.location
  ingress    = "INGRESS_TRAFFIC_ALL"
  depends_on = [google_project_service.apis]

  template {
    containers {
      image = "us-central1-docker.pkg.dev/${var.project_id}/${var.repository_id}/${var.image_name}:${var.image_tag}"
      ports {
        container_port = 8080
      }
      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
      volume_mounts {
        name = "gemini-api-key"
        mount_path = "/secrets/api_key"
      }
    }
    volumes {
      name = "gemini-api-key"
      secret {
        secret = "GEMINI_API_KEY"
        items {
          path = "latest"
        }
      }
    }
  }
}

resource "google_cloudbuild_trigger" "default" {
  project     = var.project_id
  name        = "${var.service_name}-trigger"
  description = "Trigger for ${var.service_name}"
  location    = var.location
  depends_on  = [google_project_service.apis]

  trigger_template {
    repo_name   = var.repo_name
    branch_name = var.branch_name
  }

  filename = "cloudbuild.yaml"
}

resource "google_cloud_run_service_iam_member" "noauth" {
  project  = google_cloud_run_v2_service.default.project
  location = google_cloud_run_v2_service.default.location
  service  = google_cloud_run_v2_service.default.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

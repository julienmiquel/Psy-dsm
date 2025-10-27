output "service_url" {
  description = "The URL of the deployed Cloud Run service."
  value       = google_cloud_run_v2_service.default.uri
}

output "trigger_id" {
  description = "The ID of the Cloud Build trigger."
  value       = google_cloudbuild_trigger.default.id
}

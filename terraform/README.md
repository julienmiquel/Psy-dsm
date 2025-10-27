# Terraform Configuration for Cloud Run Deployment

This directory contains the Terraform configuration for deploying the application to Google Cloud Run.

## Prerequisites

- [Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli) installed
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed and authenticated
- A Google Cloud project with the necessary APIs enabled (handled by the Terraform configuration)
- A Git repository connected to Google Cloud Build
- A GCS bucket to store the Terraform state.

## Usage

1. **Create the GCS bucket for Terraform state:**
   ```bash
   gsutil mb gs://your-terraform-state-bucket
   ```

2. **Initialize Terraform:**
   ```bash
   terraform init -backend-config="bucket=your-terraform-state-bucket"
   ```

3. **Create a `terraform.tfvars` file or use environment variables to provide the required variable values.** See `variables.tf` for the full list of variables.

4. **Apply the Terraform configuration:**
   ```bash
   terraform apply -var-file="path/to/your/environment.tfvars"
   ```
   For example, to deploy to the staging environment, use:
   ```bash
   terraform apply -var-file="staging.tfvars"
   ```

5. **Connect the Cloud Build Trigger:**
   - After the Terraform configuration is applied, a Cloud Build trigger will be created. You will need to manually connect this trigger to your Git repository in the Google Cloud Console. This is a one-time setup step.

6. **Destroy the infrastructure:**
   ```bash
   terraform destroy -var-file="path/to/your/environment.tfvars"
   ```

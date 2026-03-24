# Add steps/actions here:
```bash
Step 1: Backup Current State and Configuration

Before making any changes, create a backup of your current state and configuration. This ensures you can recover easily if anything goes wrong.

Step 2: Define Stable Identifiers in variables.tf

Create a map of resources with stable, unique keys. These identifiers should remain constant, even when resources are added or removed.

Step 3: Update main.tf to Use for_each

Replace the count meta-argument with for_each. This allows Terraform to reference resources using stable keys instead of numeric indices.

Step 4: Migrate Existing Resources Using terraform state mv

Use terraform state mv to map existing resources to their new for_each addresses. Without this step, Terraform will interpret the change as a need to destroy and recreate resources.

Step 5: Verify the Migration

Confirm the migration was successful by listing the resources in the state and ensuring they reflect the new for_each structure.

Step 6: Remove the Target Resource from Configuration

Update variables.tf by removing the entry for "file1". This signals that the resource is no longer managed by Terraform.

Step 7: Remove the Target Resource from State

Use Terraform to remove the resource from the state file. This prevents Terraform from attempting to delete it automatically.

Step 8: Delete the Physical Resource

Manually remove the file from the filesystem.

Step 9: Apply the Changes

Run terraform plan (and terraform apply if needed) to confirm and apply the final changes.
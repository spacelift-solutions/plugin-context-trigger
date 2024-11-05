module "ec2_worker_pool_stack" {
  source = "spacelift.io/spacelift-solutions/plugin-context-trigger/spacelift"

  # Required Variables
  spacelift_domain = "https://spacelift-solutions.app.spacelift.io"

  # Optional Variables
  name     = "plugin-context-trigger"
  space_id = "root"
}
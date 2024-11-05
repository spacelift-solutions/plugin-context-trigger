terraform {
  required_providers {
    spacelift = {
      source  = "spacelift-io/spacelift"
      version = ">= 0.0.1"
    }
  }
}

resource "spacelift_context" "this" {
  name = var.name

  labels   = ["autoattach:trigger_attached_contexts_stacks"]
  space_id = var.space_id

  after_apply = [
    "python3 /mnt/workspace/trigger_stacks.py"
  ]
}

resource "spacelift_mounted_file" "this" {
  context_id    = spacelift_context.this.id
  relative_path = "trigger_stacks.py"
  content       = filebase64("${path.module}/trigger_stacks.py")
  write_only    = false
}

resource "spacelift_environment_variable" "domain" {
  context_id = spacelift_context.this.id
  name       = "SPACELIFT_DOMAIN"
  value      = var.spacelift_domain
  write_only = false
}
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
    "python /mnt/workspace/space.py start trigger_attached_contexts_stacks"
  ]
}

resource "spacelift_mounted_file" "this" {
  context_id    = spacelift_context.this.id
  relative_path = "trigger_attached_contexts_stacks.py"
  content       = filebase64("${path.module}/trigger_attached_contexts_stacks.py")
  write_only    = false
}

resource "spacelift_mounted_file" "spacepy" {
  context_id    = spacelift_context.this.id
  relative_path = "space.py"
  content       = filebase64("${path.module}/space.py")
  write_only    = false
}

resource "spacelift_environment_variable" "domain" {
  context_id = spacelift_context.this.id
  name       = "SPACELIFT_DOMAIN"
  value      = var.spacelift_domain
  write_only = false
}
    
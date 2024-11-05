variable "name" {
  type        = string
  description = "Name of the context"
  default     = "plugin-context-trigger"
}

variable "space_id" {
  type        = string
  description = "ID of the space"
  default     = "root"
}

variable "spacelift_domain" {
  type        = string
  description = "fqdn of the spacelift instance (https://spacelift-solutions.app.spacelift.io)"
}

# Plugin Stack Trigger

This module adds the "stack trigger" plugin to your Spacelift account.
It works by analyzing the after state of an administrative stack, if there are changes to a `spacelift_context`,
`spacelift_environment_variable` or `spacelift_mounted_file` (IE. you change anything about a context) and that context is explicitly 
attached with a `spacelift_context_attachment` resource, it will find that resource and trigger the stack it is attached to.

## Usage

1. Spin up the module (see examples below)
2. Add the `trigger_attached_contexts_stacks` label to any administrative stacks that manage contexts and their attachments.
3. When a context changes that is managed by the stack with that label, any stacks using that context will be triggered.

## Gotchyas

Theres a few things to keep in mind when using this plugin.
1. The plugin only works in `administrative` stacks.
2. The plugin does **not** work with autoattached contexts, the context **must** be attached with a `spacelift_context_attachment` resource.
3. If the stack id, or context id is unknown until after apply, the plugin will not work. This is because the plugin needs to know the stack id and context id to trigger the stack.
  - This limitation may change in the future.

<!-- BEGIN_TF_DOCS -->
## Example

<!-- END_TF_DOCS -->

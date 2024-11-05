import os
import urllib.request
import json

this_run_id = os.environ["TF_VAR_spacelift_run_id"]
start_color = "\033[36m"
end_color = "\033[0m"

def determine_actions_match(actions: list[str], match: list[str]):
    return all(action in actions for action in match)

def determine_after_state(resource: dict, key: str):
    if "change" in resource and "after" in resource["change"] and key in resource["change"]["after"]:
        return resource["change"]["after"][key]
    else:
        return None


def find_effected_stacks():
    with open("spacelift.plan.json") as f:
        plan = json.load(f)

    resources_to_watch = [
        "spacelift_mounted_file",
        "spacelift_environment_variable",
        "spacelift_context"
    ]

    # find context id's for contexts that have changes or env vars or mounted files that have changes.
    effected_contexts = []
    for resource in plan["resource_changes"]:
        if resource["type"] in resources_to_watch:
            if determine_actions_match(resource["change"]["actions"], ["delete", "create"])\
                    or determine_actions_match(resource["change"]["actions"], ["create"])\
                    or determine_actions_match(resource["change"]["actions"], ["update"]) \
                    or determine_actions_match(resource["change"]["actions"], ["delete"]):

                if resource["type"] == "spacelift_context":
                    effected_contexts.append(determine_after_state(resource, "id"))
                else:
                    effected_contexts.append(determine_after_state(resource, "context_id"))

    # Remove None values and duplicates
    # we do this because we may not know the context id when something is first created
    effected_contexts = list(set(filter(None, effected_contexts)))

    # find stack id's for stacks that have context attachments that have changes.
    effected_stacks = []
    for resource in plan["resource_changes"]:
        if resource["type"] == "spacelift_context_attachment":
            if determine_after_state(resource, "context_id") in effected_contexts:
                effected_stacks.append(determine_after_state(resource, "stack_id"))

    # Remove None values and duplicates
    # we do this because we may not know the stack id when something is first created
    effected_stacks = list(set(filter(None, effected_stacks)))


    return effected_stacks

def trigger_stack(stack_id):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['SPACELIFT_API_TOKEN']}"
    }

    mutation_query = f"""
mutation {{
  runResourceCreate(stack: \"{stack_id}\", proposed: false) {{}}
}}
"""

    data = {
        "query": mutation_query,
    }

    print(f"{start_color}[{this_run_id}] {end_color}Triggering stack {stack_id}...", end=" ")

    req = urllib.request.Request(f"{os.environ['SPACELIFT_DOMAIN']}/graphql", json.dumps(data).encode('utf-8'), headers)
    with urllib.request.urlopen(req) as response:
        resp = json.loads(response.read().decode('utf-8'))

    if "data" not in resp:
        print(f"Error: {resp}")
    else:
        if "runResourceCreate" not in resp["data"]:
            print(f"Error: {resp}")
        else:
            run_id = resp['data']['runResourceCreate']
            print(f"DONE: {os.environ['SPACELIFT_DOMAIN']}/stack/{stack_id}/run/{run_id}")


stacks = find_effected_stacks()
for stack in stacks:
    trigger_stack(stack)


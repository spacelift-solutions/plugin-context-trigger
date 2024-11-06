import os
from space import SpacePy

def determine_actions_match(actions: list[str], match: list[str]):
    return all(action in actions for action in match)

def determine_after_state(resource: dict, key: str):
    if "change" in resource and "after" in resource["change"] and key in resource["change"]["after"]:
        return resource["change"]["after"][key]
    else:
        return None


def find_effected_stacks(plan):
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

def trigger_stack(stack_id, logger, query_api):

    mutation_query = """
    mutation Run($stackID: ID!) {
        runResourceCreate(stack: $stackID, proposed: false) {}
    }
    """

    variables = {
        "stackID": stack_id
    }

    logger.log(f"Triggering stack {stack_id}...")

    resp = query_api(mutation_query, variables)

    if "data" in resp and "runResourceCreate" in resp["data"]:
        run_id = resp['data']['runResourceCreate']
        logger.log(f"DONE: {os.environ['SPACELIFT_DOMAIN']}/stack/{stack_id}/run/{run_id}")

@SpacePy
def main(logger, query_api, plan_json):
    stacks = find_effected_stacks(plan_json)
    for stack in stacks:
        trigger_stack(stack, logger, query_api)


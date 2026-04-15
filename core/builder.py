import json
import os

TOOLS_DIR = "tools"


def load_tool_data(tool, domain):
    path = os.path.join(TOOLS_DIR, domain, f"{tool}.json")

    if not os.path.exists(path):
        raise Exception(f"Tool config not found: {tool}")

    with open(path, "r") as f:
        return json.load(f)


def apply_mappings(params, mappings):
    if not mappings:
        return params

    new_params = params.copy()

    for key, mapping_dict in mappings.items():
        if key in new_params:
            value = new_params[key]

            if value in mapping_dict:
                new_params[key] = mapping_dict[value]

    return new_params


def flatten_params(params):
    flat = {}

    for k, v in params.items():
        if isinstance(v, dict):
            flat.update(v)  # e.g. time → start/end
        else:
            flat[k] = v

    return flat



def build_command(intent_data, ir, tool):
    intent_name = intent_data["name"]
    domain = intent_data["file_type"]

    tool_data = load_tool_data(tool, domain)
    intents = tool_data.get("intents", {})

    if intent_name not in intents:
        raise Exception(f"{tool} does not support {intent_name}")

    intent_config = intents[intent_name]

    template = intent_config["template"]
    mappings = intent_config.get("mappings", {})

    params = ir["params"]

    # flatten nested structures
    flat_params = flatten_params(params)

    # apply mappings from JSON
    flat_params = apply_mappings(flat_params, mappings)

    try:
        command = template.format(**flat_params)
    except KeyError as e:
        raise Exception(f"Missing parameter for command: {e}")

    return command
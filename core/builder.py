import json
import os

TOOLS_DIR ="tools"

def load_tool_data(tool, domain):
    path = os.path.join(TOOLS_DIR, domain, f"{tool}.json")

    if not os.path.exists(path):
        raise Exception(f"Tool config not found : {tool}")

    with open(path, "r") as f:
        return json.load(f)


def build_command(intent_data, params, tool):
    intent_name = intent_data["name"]
    domain = intent_data["file_type"]
    tool_data = load_tool_data(tool, domain)
    intents = tool.data.get("intents", {})

    if intent_name not in intents:
        raise Exception(f"{tool} does not support {intent_name}")

    template = intents[intent_name]["template"]

    try:
        command = template.format(**parms)
    except keyError as e:
        raise Exception(f"Missing parameter for command : {e}")
    
    return command
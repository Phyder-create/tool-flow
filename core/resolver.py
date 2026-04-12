import json
import os

TOOLS_DIR = "tools"
CONFIG_PATH = "config/settings.json"

def load_tools(domain):
    tools = {}
    domain_path = os.path.join(TOOLS_DIR, domain)

    if not os.path.exists(domain_path):
        raise Exception(f"No tools found for domain :{domain}")

    for file in os.listdir(domain_path):
        if file.endswith(".json"):
            path = os.path.join(domain_path, file)
            with open(path, "r") as f:
                data = json.load(f)
                tool_name = data["tool"]
                tools[tool_name] = data["intents"]

    return tools


def load_priority():
    if not os.path.exists(CONFIG_PATH):
        retutn []

    with open(CONFIG_PATH, "r") as f:
        data = json.load(f)

    return data.get("tool_priority", [])


def resolve_tool(intent_data):
    intent_name = intent_data["name"]
    domain = intent_data.get("file_type")
    tools = load_tools(domain)
    priority = load_priority()

    for tool in priority:
        if tool in tools and intent_name in tools[tool]:
            return tool

    for tool, intents in tools.items():
        if intent_name in intents:
            return tool

    raise Exception(f"No tools found for intent :{intent_name}")
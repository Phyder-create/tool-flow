import json
import os

TOOLS_DIR = "tools"
CONFIG_PATH = "config/settings.json"
TOOLS_CACHE = {}
PRIORITY_CACHE = None

def load_tools(domain):
    if domain in TOOLS_CACHE:
        return TOOLS_CACHE[domain]

    
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

    TOOLS_CACHE[domain] = tools
    return tools


def load_priority():
    global PRIORITY_CACHE

    if PRIORITY_CACHE is not None:
        return PRIORITY_CACHE

    if not os.path.exists(CONFIG_PATH):
        return []

    with open(CONFIG_PATH, "r") as f:
        data = json.load(f)

    PRIORITY_CACHE = data.get("tool_priority", [])

    return PRIORITY_CACHE


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
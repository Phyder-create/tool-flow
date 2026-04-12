import re 

def extract_file(text):
    return re.findall(r'\b[\w\-.]+\.\w+\b', text)


def extract_range(text):
    match = re.search(r'(\d+)\s*(?:to|-)\s*(\d+)', text)
    if match:
        return f"{match.group(1)}-{match.group(2)}"

    single = re.search(r'\b\d+\b', text)
    if single:
        return f"{single.group()}-end"

    return None


def extract_number(text):
    match = re.search(r'\b\d+\b', text)
    return int(match.group()) if match else None




def parse(text, intent_data):
    text = text.lower()
    params = {}

    param_defs = intent_data.get("parameters", {})

    files = extract_file(text)
    file_index = 0

    for name, config in param_defs.items():
        ptype = config.get("type")
        if ptype == "file":
            if file_index < len(files):
                params[name] = files[file_index]
                file_index += 1

        elif ptype == "range":
            val = extract_range(text)
            if val:
                params[name] = val

        elif ptype == "number":
            val = extract_number(text)
            if val is not None:
                params[name] = val

        if name not in params and "default" in config:
            params[name] = config["default"]

        if name not in params and not config.get("optional", False):
            raise Exception(f"Missing parameter: {name}")

    return params
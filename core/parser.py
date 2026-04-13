import re

#extractors

def extract_files(text):
    return re.findall(r'\b[\w\-.]+\.\w+\b', text)


def extract_number(text):
    match = re.search(r'\b\d+(\.\d+)?\b', text)
    return float(match.group()) if match else None


def extract_numbers(text):
    return [int(x) for x in re.findall(r'\b\d+\b', text)]


def extract_range(text):
    match = re.search(r'(\d+)\s*(?:to|-)\s*(\d+)', text)
    if match:
        return f"{match.group(1)}-{match.group(2)}"

    single = re.search(r'\b\d+\b', text)
    if single:
        return f"{single.group()}-end"

    return None


def extract_output_file(text):
    match = re.search(r'(?:to|into|as|output)\s+([\w\-.]+\.\w+)', text)
    return match.group(1) if match else None


def extract_choice(text, choices):
    for choice in choices:
        if choice.lower() in text:
            return choice
    return None


def extract_resolution(text):
    match = re.search(r'(\d+)[xX](\d+)', text)
    if match:
        return int(match.group(1)), int(match.group(2))

    nums = extract_numbers(text)
    if len(nums) >= 2:
        return nums[0], nums[1]

    return None, None


#time helpers for ffmpeg and other tools

def format_time(seconds):
    seconds = int(seconds)
    return f"{seconds//3600:02}:{(seconds%3600)//60:02}:{seconds%60:02}"


def extract_time_range(text):
    nums = extract_numbers(text)
    if len(nums) >= 2:
        return format_time(nums[0]), format_time(nums[1])
    return None, None


#handle files for builder command

def handle_file(name, config, text, context):
    files = context["files"]

    # output file (prefer "to file.ext")
    if name == "output_file":
        out = extract_output_file(text)
        if out:
            return out

    # fallback: sequential assignment
    if context["file_index"] < len(files):
        file = files[context["file_index"]]
        context["file_index"] += 1

        if name == "input_file":
            context["used_input"] = file

        return file

    return None


def handle_files(name, config, text, context):
    files = context["files"][:]
    input_file = context.get("used_input")

    if input_file in files:
        files.remove(input_file)

    return " ".join(files) if files else None


def handle_range(name, config, text, context):
    return extract_range(text)


def handle_number(name, config, text, context):
    if "time_range" in context:
        return None
    return extract_number(text)


def handle_float(name, config, text, context):
    return extract_number(text)


def handle_numbers(name, config, text, context):
    nums = extract_numbers(text)

    if name == "width" and len(nums) >= 1:
        return nums[0]

    if name == "height" and len(nums) >= 2:
        return nums[1]

    return None


def handle_resolution(name, config, text, context):
    w, h = extract_resolution(text)

    if name == "width":
        return w
    elif name == "height":
        return h

    return None


def handle_time(name, config, text, context):
    # avoid interpreting ranges like 2-5 as time
    if "-" in text:
        return None

    if "time_range" not in context:
        context["time_range"] = extract_time_range(text)

    start, end = context["time_range"]

    if name == "start":
        return start
    elif name == "end":
        return end

    return None


def handle_string(name, config, text, context):
    return None 


def handle_choice(name, config, text, context):
    choices = config.get("choices", [])
    return extract_choice(text, choices)




TYPE_HANDLERS = {
    "file": handle_file,
    "files": handle_files,
    "range": handle_range,
    "number": handle_number,
    "float": handle_float,
    "numbers": handle_numbers,
    "resolution": handle_resolution,
    "time": handle_time,
    "string": handle_string,
    "choice": handle_choice,
}




def parse(text, intent_data):
    text = text.lower()
    params = {}

    param_defs = intent_data.get("parameters", {})

    context = {
        "files": extract_files(text),
        "file_index": 0,
        "used_input": None,
    }

    for name, config in param_defs.items():
        ptype = config.get("type")

        handler = TYPE_HANDLERS.get(ptype)
        if not handler:
            raise Exception(f"Unsupported parameter type: {ptype}")

        value = handler(name, config, text, context)

        if value is not None:
            params[name] = value

        if name not in params and "default" in config:
            params[name] = config["default"]

        
        if name not in params and not config.get("optional", False):
            raise Exception(f"Missing parameter: {name}")

    return params
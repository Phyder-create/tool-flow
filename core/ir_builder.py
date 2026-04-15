
def format_file(value):
    return f'"{value}"' if " " in str(value) else str(value)

def format_number(value):
    clean_val = str(value).replace('%', '')
    f_val = float(clean_val)
    return int(f_val) if f_val.is_integer() else f_val

def format_string(value):
    return str(value)

FORMATTERS = {
    "file": format_file,
    "files": format_string,
    "number": format_number,
    "resolution": format_number,
    "dimension": format_string,
    "percentage": format_string,
    "string": format_string,
    "quoted_string": format_string,
    "time": format_string,
    "range": format_string
}

#-------------------------------------------------------------------------------------------------

def assemble_blur(params):
    if "shorthand" in params:
        params["blur_params"] = params["shorthand"]
    elif "radius" in params and "sigma" in params:
        params["blur_params"] = f"{params['radius']}x{params['sigma']}"
    elif "radius" in params or "strength" in params:
        val = params.get("radius", params.get("strength", 0))
        params["blur_params"] = f"0x{val}"
    else:
        params["blur_params"] = "0x5"

def assemble_brightness_contrast(params):
    if "shorthand" in params:
        params["bc_params"] = params["shorthand"]
    else:
        b = params.get("brightness", 0)
        c = params.get("contrast", 0)
        params["bc_params"] = f"{b}x{c}"

ASSEMBLERS = {
    "blur_image": assemble_blur,
    "gaussian_blur": assemble_blur,
    "sharpen_image": assemble_blur,
    "brightness_contrast": assemble_brightness_contrast
}

def validate_resize(params, problems):
    if "height" not in params:
        problems.append("Width provided without Height.")

def validate_quality(params, problems):
    try:
        val = int(float(str(params["quality"]).replace('%', '')))
        
        if val < 1 or val > 100:
            problems.append(f"Image quality ({val}) should be between 1 and 100.")
            
        params["quality"] = val 
        
    except ValueError:
        problems.append(f"Quality must be a number, got: {params.get('quality')}")


VALIDATORS = {
    "width": validate_resize,
    "quality": validate_quality
}

# ===============================================================================================================================

def build_ir(intent_data: dict, params: dict) -> dict:
    ir = {
        "intent": intent_data["name"],
        "target": intent_data.get("file_type"),
        "params": {},
        "problems": [],
    }

    for key, value in params.items():
        try:
            param_type = intent_data.get("parameters", {}).get(key, {}).get("type", "string")
            
            formatter = FORMATTERS.get(param_type, lambda x: x)
            
            ir["params"][key] = formatter(value)
        except ValueError:
            ir["problems"].append(f"Invalid format for {key}: '{value}'")
            ir["params"][key] = value


    assembler_func = ASSEMBLERS.get(ir["intent"])
    if assembler_func:
        assembler_func(ir["params"])


    for key in ir["params"]:
        validator_func = VALIDATORS.get(key)
        if validator_func:
            validator_func(ir["params"], ir["problems"])

    return ir
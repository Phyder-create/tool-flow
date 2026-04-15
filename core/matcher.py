import json
import os 
import re 

INTENT_DIR = "intents"
INTENT_CACHE = None


import re

DOMAIN_MAP = {
    # Images
    "jpg": "image", "jpeg": "image", "png": "image", "webp": "image", 
    "gif": "image", "tiff": "image", "bmp": "image", "ico": "image",
    # Video
    "mp4": "video", "mkv": "video", "avi": "video", "mov": "video",
    # Audio
    "mp3": "audio", "wav": "audio", "aac": "audio",
    # PDF
    "pdf": "pdf"
}

def detect_domain(text: str) -> str:
    # Look for anything ending in a dot followed by 2-4 letters
    extensions = re.findall(r'\.([a-zA-Z0-9]{2,4})\b', text.lower())
    
    for ext in extensions:
        if ext in DOMAIN_MAP:
            return DOMAIN_MAP[ext]
            
    return "unknown"



def load_intents():
    global INTENT_CACHE
    if INTENT_CACHE is not None:
        return INTENT_CACHE

    intents = []
    for root, _, files in os.walk(INTENT_DIR):
        for file in files:
            if file.endswith(".json"):
                path = os.path.join(root, file)
                with open(path, "r") as f:
                    intents.append(json.load(f))

    INTENT_CACHE = intents
    return intents



def normalize_text(text):
    return text.lower().strip()



def score_intent(text: str, intent: dict, detected_domain: str) -> int:
    score = 0
    keywords = intent.get("keywords", [])
    file_type = intent.get("file_type")

    
    for word in keywords:
        if word in text:
            score += 1


    if file_type and file_type in text:
        score += 2


    intent_name = intent.get("name", "")
    main_action = intent_name.split("_")[0]
    if main_action in text:
        score += 3


    if detected_domain != "unknown" and file_type:
        if file_type == detected_domain:
            score += 10
        else:
            score -= 10  

    return score




def match_intent(user_input):
    text = normalize_text(user_input)
    intents = load_intents()
    detected_domain = detect_domain(text)

    best_intent = None
    best_score = 0
    candidates = []

    for intent in intents:
        score = score_intent(text, intent, detected_domain)

        if score > best_score:
            best_score = score
            best_intent = intent
            candidates = [(intent, score)]
        elif score == best_score and score > 0 :
            candidates.append((intent, score))

    if best_score <= 0 or best_intent is None:
        raise Exception("No intent found")

    if len(candidates) > 1:
        candidates.sort(key = lambda x: len(x[0].get("keywords", [])), reverse = True)
        best_intent = candidates[0][0]
        
    return best_intent
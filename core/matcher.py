import json
import os

INTENT_DIR = "intents"

def load_intents():
    intents = []

    for root, _, files in os.walk(INTENT_DIR):
        for file in files:
            if(file.endswith(".json")) :
                path = os.path.join(root, file)
                with open(path, "r") as f:
                    data = json.load(f)
                    intents.append(data)

    return intents


def normalize(text) :
    return text.lower().strip()

def score_intent(text, keywords) :
    score = 0
    for word in keywords:
        if word in text:
            score += 1
    return score


def match_intent(user_input):
    text = normalize(user_input)
    intents = load_intents()
    best_intent = None
    best_score = 0

    for intent in intents :
        keywords = intent.get("keywords", [])
        score = score_intent(text, keywords)

        if score > best_score :
            best_score = score
            best_intent = intent

    if best_intent is None:
        raise Exception("No intent matched")

    return best_intent


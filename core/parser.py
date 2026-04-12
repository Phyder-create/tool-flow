import re 

def parse(text, intent_data):
    params = {}
    text = text.lower()
    
    file_type = intent_data.get("file_type")
    # will have to think about it, parsing would be difficult
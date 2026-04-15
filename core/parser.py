import re
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from config.supported_extension import EXT_REGEX


@dataclass
class ExtractedItem:
    value: Any
    used: bool = False

class ExtractionContext:
    def __init__(self, text: str):
        self.text = text.lower()
        self.files: List[ExtractedItem] = []
        self.times: List[ExtractedItem] = []
        self.numbers: List[ExtractedItem] = []
        self.output_hint: Optional[str] = None
        
        self._scan_text()

    def _scan_text(self):
        
        output_hint_pattern = r'(?:to|into|as|output|save as)\s+([a-zA-Z0-9_\-.]+\.[a-zA-Z0-9]{2,5})'        
        file_pattern = rf'\b[a-zA-Z0-9_\-.]+\.(?:{EXT_REGEX})\b'

        # output Hint
        out_matches = re.findall(output_hint_pattern, self.text, re.IGNORECASE)
        if out_matches:
            self.output_hint = out_matches[-1]

        # files
        file_matches = re.findall(file_pattern, self.text)
        for f in file_matches:
            # avoid grabbing timestamps that the regex might mistake for files
            if ":" not in f:
                self.files.append(ExtractedItem(value=f))

        # times
        self._extract_times()
        self._extract_numbers()

    def _extract_times(self):
        # colon Style Pattern (HH:MM:SS or MM:SS)
        colon_pattern = r'\b\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?\b'
        
        # verbose Chunk Pattern (Finds blocks like "1h 20m 30s")
        verbose_chunk_pattern = r'((?:\d+\s*[hms][a-z]*\s*)+)'
        
        h_pat = r'(\d+)\s*h'
        m_pat = r'(\d+)\s*m'
        s_pat = r'(\d+)\s*s'

        colons = re.findall(colon_pattern, self.text)
        for t in colons:
            parts = t.split(':')
            if len(parts) == 2: 
                self.times.append(ExtractedItem(f"00:{int(parts[0]):02}:{int(parts[1]):02}"))
            elif len(parts) == 3: 
                self.times.append(ExtractedItem(f"{int(parts[0]):02}:{int(parts[1]):02}:{int(parts[2]):02}"))


        time_chunks = re.findall(verbose_chunk_pattern, self.text, re.IGNORECASE)
        for chunk in time_chunks:
            h = re.search(h_pat, chunk, re.IGNORECASE)
            m = re.search(m_pat, chunk, re.IGNORECASE)
            s = re.search(s_pat, chunk, re.IGNORECASE)
            
            h_val = int(h.group(1)) if h else 0
            m_val = int(m.group(1)) if m else 0
            s_val = int(s.group(1)) if s else 0
            
            verbose_time = f"{h_val:02}:{m_val:02}:{s_val:02}"
            
            if verbose_time != "00:00:00" and not any(t.value == verbose_time for t in self.times):
                self.times.append(ExtractedItem(verbose_time))

    def get_unused_file(self) -> Optional[str]:
        for item in self.files:
            if not item.used:
                item.used = True
                return item.value
        return None

    def get_unused_time(self) -> Optional[str]:
        for item in self.times:
            if not item.used:
                item.used = True
                return item.value
        return None

    def _extract_numbers(self):
        res_pattern = r'\d+\s*(?:x|by)\s*\d+'
        time_pattern = r'\d{1,2}:\d{2}(?::\d{2})?'
        text_clean = re.sub(res_pattern, '', self.text, flags=re.IGNORECASE)
        text_clean = re.sub(time_pattern, '', text_clean)
        
        nums = re.findall(r'\b\d+(?:\.\d+)?\b', text_clean)
        for n in nums:
            self.numbers.append(ExtractedItem(value=float(n)))

    def get_unused_number(self) -> Optional[float]:
        for item in self.numbers:
            if not item.used:
                item.used = True
                return item.value
        return None

# --- Handlers ----------------------------------------------------------------------------------------------------------


def handle_file(name: str, config: dict, ctx: ExtractionContext) -> Optional[str]:
    if name == "output_file":

        if len(ctx.files) == 1:
            return None
        # try to use the hint (e.g., "to out.mp4")
        if ctx.output_hint:
            for item in ctx.files:
                if item.value == ctx.output_hint:
                    item.used = True
            return ctx.output_hint
            
        #grab the last file IF there are multiple unused files
        unused_files = [item for item in ctx.files if not item.used]
        if len(unused_files) > 1:  # <--- THIS IS THE FIX
            last_file = unused_files[-1]
            last_file.used = True
            return last_file.value
            
        return None 

    
    return ctx.get_unused_file()


def handle_files(name: str, config: dict, ctx: ExtractionContext) -> Optional[str]:
    collected = []
    
    for item in ctx.files:
        #gab it if it hasn't been used and it isn't the output hint
        if not item.used:
            item.used = True
            collected.append(item.value)
            
    #return them joined by a space for the CLI command (e.g., "a.pdf b.pdf")
    return " ".join(collected) if collected else None

def handle_percentage(name: str, config: dict, ctx: ExtractionContext) -> Optional[str]:
    pattern = r'(\d+)\s*(?:%|percent(?:age)?)\b'
    
    match = re.search(pattern, ctx.text, re.IGNORECASE)
    if match:
        return f"{match.group(1)}%"  
    return None

def handle_string(name: str, config: dict, ctx: ExtractionContext) -> Optional[str]:
    choices = config.get("choices", [])
    for choice in choices:
        pattern = rf'\b{re.escape(choice)}\b'
        if re.search(pattern, ctx.text, re.IGNORECASE):
            return choice
    return None

def handle_quoted_string(name: str, config: dict, ctx: ExtractionContext) -> Optional[str]:

    pattern = r'(["\'])(.*?)\1'
    
    match = re.search(pattern, ctx.text)
    if match:
        # We return 2 because we want the text, not the quotes around it.
        return match.group(2)
        
    return None

def handle_time(name: str, config: dict, ctx: ExtractionContext) -> Optional[str]:
    return ctx.get_unused_time()

def handle_range(name: str, config: dict, ctx: ExtractionContext) -> Optional[str]:
    range_pattern = r'(\d+)\s*(?:to|-)\s*(\d+)'
    single_pattern = r'\bpage\s+(\d+)\b'

    range_match = re.search(range_pattern, ctx.text)
    if range_match: 
        return f"{range_match.group(1)}-{range_match.group(2)}"
    
    single_match = re.search(single_pattern, ctx.text)
    if single_match: 
        return single_match.group(1)
    
    return None

def handle_resolution(name: str, config: dict, ctx: ExtractionContext) -> Optional[int]:
    pattern = r'(\d+)\s*(?:x|by)\s*(\d+)'
    
    match = re.search(pattern, ctx.text, re.IGNORECASE)
    
    if match:
        if name == "width": 
            return int(match.group(1))
        if name == "height": 
            return int(match.group(2))
            
    return None


def handle_number(name: str, config: dict, ctx: ExtractionContext) -> Optional[float]:
    return ctx.get_unused_number()

def handle_dimension(name: str, config: dict, ctx: ExtractionContext) -> Optional[str]:
    pattern = r'\b(\d+(?:\.\d+)?\s*(?:x|by)\s*\d+(?:\.\d+)?)\b'
    match = re.search(pattern, ctx.text, re.IGNORECASE)
    
    if match:
        return match.group(1).lower().replace(' by ', 'x').replace(' ', '')
    return None

TYPE_HANDLERS = {
    "file": handle_file,
    "files": handle_files,
    "time": handle_time,
    "range": handle_range,
    "resolution": handle_resolution,
    "number": handle_number,
    "percentage": handle_percentage,
    "string": handle_string,
    "quoted_string": handle_quoted_string,
    "dimension": handle_dimension 
}

def parse(text: str, intent_data: dict) -> dict:
    ctx = ExtractionContext(text)
    params = {}
    param_defs = intent_data.get("parameters", {})

    sorted_params = sorted(param_defs.items(), key=lambda x: x[0] != "output_file")

    for name, config in sorted_params:
        ptype = config.get("type")
        handler = TYPE_HANDLERS.get(ptype)
        
        if not handler: continue

        value = handler(name, config, ctx)

        if value is not None:
            params[name] = value
        elif "default" in config:
            params[name] = config["default"]
        elif not config.get("optional", False):
            raise Exception(f"Error: Command requires '{name}' but I couldn't find it in your request.")

    return params
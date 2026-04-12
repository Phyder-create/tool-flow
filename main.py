from core.matcher import match_intent
from core.parser import parse
from core.resolver import resolve_tool
from core.builder import build_command


def main() :
    text = input(">> ")
    intent = match_intent(text)
    params = parse(text)
    tool = resolve_tool(intent)
    command = build_command(intent, params, tool)
    print(command)

if __name__ == "__main__":
    main()
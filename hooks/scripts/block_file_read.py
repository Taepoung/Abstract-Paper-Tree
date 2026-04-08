"""
PreToolUse hook (Bash): cat/head/tail/more/less 등으로 .py 파일을 읽는 것을 차단합니다.
"""
import json
import re
import sys

FILE_READ_COMMANDS = {"cat", "head", "tail", "more", "less"}


def main():
    try:
        hook_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    cmd = hook_data.get("tool_input", {}).get("command", "").strip()
    tokens = re.split(r"\s+", cmd) if cmd else []
    first_token = tokens[0] if tokens else ""

    if first_token in FILE_READ_COMMANDS and any(t.endswith(".py") for t in tokens[1:]):
        print(
            "BLOCKED: .py 파일은 읽을 수 없습니다.",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()

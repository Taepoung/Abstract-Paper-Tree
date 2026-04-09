"""
PreToolUse hook (Bash):
- cat/head/tail 등으로 .py/.html 파일을 읽는 것을 차단
- python -c 인라인 코드로 .py/.html 파일을 조작하는 것을 차단
- python script.py 형태의 정상 스크립트 실행은 허용
"""
import json
import re
import sys

FILE_READ_COMMANDS = {"cat", "head", "tail", "more", "less"}
PROTECTED_EXTENSIONS = (".py", ".html")


def main():
    try:
        hook_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    cmd = hook_data.get("tool_input", {}).get("command", "").strip()
    tokens = re.split(r"\s+", cmd) if cmd else []
    first_token = tokens[0] if tokens else ""

    # Block: cat/head/tail .py/.html
    if first_token in FILE_READ_COMMANDS:
        for t in tokens[1:]:
            for ext in PROTECTED_EXTENSIONS:
                if t.endswith(ext):
                    print(
                        f"BLOCKED: {ext} 파일은 읽을 수 없습니다.",
                        file=sys.stderr,
                    )
                    sys.exit(2)

    # Block: python -c "..." containing .py/.html file path patterns
    # (open('file.html'), 'w') 등의 파일 조작)
    if re.search(r"python[23]?\s+-c\s", cmd):
        inline_code = cmd[cmd.index("-c") + 2:].strip()
        for ext in PROTECTED_EXTENSIONS:
            # Match file extensions in quotes: 'file.html', "file.py"
            if re.search(rf"""['\"][^'\"]*\{ext}['\"]""", inline_code):
                print(
                    f"BLOCKED: python -c 로 {ext} 파일을 조작할 수 없습니다.",
                    file=sys.stderr,
                )
                sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()

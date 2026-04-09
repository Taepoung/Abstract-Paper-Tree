"""
PreToolUse hook (Write/Edit): .py 파일 쓰기/수정을 차단합니다.
스크립트는 완성된 상태이므로 Claude가 수정할 수 없습니다.
"""
import json
import sys


def main():
    try:
        hook_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    file_path = hook_data.get("tool_input", {}).get("file_path", "")

    if file_path.endswith(".py"):
        print(
            "BLOCKED: .py 파일은 직접 수정할 수 없습니다.",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()

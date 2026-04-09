"""
PreToolUse hook (Read): .html 파일 읽기를 차단합니다.
템플릿은 완성된 상태이므로 Claude가 읽을 필요가 없습니다.
"""
import json
import sys


def main():
    try:
        hook_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    file_path = hook_data.get("tool_input", {}).get("file_path", "")

    if file_path.endswith(".html"):
        print("BLOCKED: .html 파일은 읽을 수 없습니다.", file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()

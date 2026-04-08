"""
PreToolUse hook (Write): .html 파일 직접 작성을 차단합니다.
HTML은 빌드 스크립트(build_all.py)로만 생성해야 합니다.
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
        print(
            "BLOCKED: .html 파일은 직접 작성할 수 없습니다. build_all.py로 생성하세요.",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()

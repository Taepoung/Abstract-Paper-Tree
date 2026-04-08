"""
PostToolUse hook (Write): HTML 파일의 onclick 핸들러에서 호출하는
함수가 <script> 블록에 정의되어 있는지 검증합니다.
"""
import json
import os
import re
import sys


def validate_html(filepath):
    errors = []
    fname = os.path.basename(filepath)

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            html = f.read()
    except OSError as e:
        errors.append(f"[ERROR] {fname}: 파일 읽기 실패 — {e}")
        return errors

    # onclick="funcName(...)" 에서 함수 이름 추출
    onclick_funcs = set(re.findall(r'onclick\s*=\s*["\'](\w+)\s*\(', html))

    # <script> 블록에서 function 정의 추출
    scripts = "".join(re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL))
    defined_funcs = set(re.findall(r'function\s+(\w+)\s*\(', scripts))
    # const/let/var name = function(...) 또는 arrow
    defined_funcs |= set(re.findall(r'(?:const|let|var)\s+(\w+)\s*=\s*(?:function|\()', scripts))

    missing = onclick_funcs - defined_funcs
    if missing:
        errors.append(
            f"[ERROR] {fname}: onclick에서 호출하는 함수가 정의되지 않음 — {', '.join(sorted(missing))}\n"
            f"  해당 함수를 <script> 블록에 추가하거나 onclick을 수정하세요."
        )

    return errors


def main():
    try:
        hook_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    file_path = hook_data.get("tool_input", {}).get("file_path", "")
    norm = file_path.replace("\\", "/")

    if not norm.endswith(".html"):
        sys.exit(0)

    errors = validate_html(file_path)

    if errors:
        print("[validate_html] 검증 실패:\n", file=sys.stderr)
        for err in errors:
            print(err, file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()

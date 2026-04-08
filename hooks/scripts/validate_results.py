"""
PostToolUse hook (Write): results/*.json 파일의 구조와
filename 필드가 실제 JSON 파일명과 일치하는지 검증합니다.
"""
import json
import os
import sys

REQUIRED_KEYS = {"filename", "title", "research_type", "problem", "methodology", "keywords"}
VALID_RESEARCH_TYPES = {"Method", "Empirical", "Qualitative", "Benchmark", "Survey"}


def validate_file(filepath):
    """단일 JSON 파일을 검증하고 오류 목록을 반환합니다."""
    errors = []
    json_file = os.path.basename(filepath)
    expected_pdf = os.path.splitext(json_file)[0] + ".pdf"

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            obj = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"[ERROR] {json_file}: JSON 파싱 실패 — {e}")
        return errors
    except OSError as e:
        errors.append(f"[ERROR] {json_file}: 파일 읽기 실패 — {e}")
        return errors

    if not isinstance(obj, dict):
        errors.append(f"[ERROR] {json_file}: 최상위가 객체가 아닙니다 — {type(obj).__name__}")
        return errors

    missing = REQUIRED_KEYS - obj.keys()
    if missing:
        errors.append(f"[ERROR] {json_file}: 필수 키 누락 — {', '.join(sorted(missing))}")
        return errors

    actual = obj.get("filename", "")
    if not actual:
        errors.append(f"[ERROR] {json_file}: 'filename' 필드가 비어 있습니다.")
    elif not actual.endswith(".pdf"):
        errors.append(f"[ERROR] {json_file}: filename이 .pdf로 끝나야 합니다 — '{actual}'")
    elif actual != expected_pdf:
        errors.append(
            f"[ERROR] {json_file}: filename 불일치\n"
            f"  예상: '{expected_pdf}'\n"
            f"  실제: '{actual}'"
        )

    rt = obj.get("research_type", "")
    if rt not in VALID_RESEARCH_TYPES:
        errors.append(f"[ERROR] {json_file}: 'research_type' 값이 유효하지 않습니다 — '{rt}' (허용값: {', '.join(sorted(VALID_RESEARCH_TYPES))})")

    for key in REQUIRED_KEYS - {"keywords", "research_type"}:
        val = obj.get(key, "")
        if not isinstance(val, str) or not val.strip():
            errors.append(f"[ERROR] {json_file}: '{key}' 필드가 비어 있거나 문자열이 아닙니다")

    kw = obj.get("keywords", None)
    if not isinstance(kw, list) or len(kw) == 0:
        errors.append(f"[ERROR] {json_file}: 'keywords' 필드가 비어 있거나 배열이 아닙니다")

    return errors


def main():
    try:
        hook_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_input = hook_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    # results/*.json 에 해당하는 경우만 검증
    norm = file_path.replace("\\", "/")
    if "/results/" not in norm or not norm.endswith(".json"):
        sys.exit(0)

    errors = validate_file(file_path)

    if errors:
        print("[validate_results] 검증 실패 — 아래 오류를 즉시 수정하세요:\n", file=sys.stderr)
        for err in errors:
            print(err, file=sys.stderr)
        print(
            "\n수정 방법: 필수 키(filename, title, research_type, problem, methodology, keywords)를 확인하고 수정한 뒤 다시 저장하세요.",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()

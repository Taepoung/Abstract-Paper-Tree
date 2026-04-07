"""
PostToolUse hook: Bash 명령 실행 후 results/*.json 파일의
filename 필드가 실제 JSON 파일명과 일치하는지 검증합니다.
"""
import json
import os
import sys


def main():
    try:
        hook_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    # save_result.py 실행 시에만 검증
    tool_input = hook_data.get('tool_input', {})
    command = tool_input.get('command', '')

    if 'save_result.py' not in command:
        sys.exit(0)

    cwd = hook_data.get('cwd', os.getcwd())
    results_dir = os.path.join(cwd, 'results')

    if not os.path.isdir(results_dir):
        sys.exit(0)

    errors = []
    for json_file in sorted(os.listdir(results_dir)):
        if not json_file.endswith('.json'):
            continue

        expected_pdf = os.path.splitext(json_file)[0] + '.pdf'
        filepath = os.path.join(results_dir, json_file)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                obj = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"[ERROR] results/{json_file}: JSON 파싱 실패 — {e}")
            continue
        except OSError as e:
            errors.append(f"[ERROR] results/{json_file}: 파일 읽기 실패 — {e}")
            continue

        actual = obj.get('filename', '')
        if not actual:
            errors.append(f"[ERROR] results/{json_file}: 'filename' 필드가 없습니다.")
        elif actual != expected_pdf:
            errors.append(
                f"[ERROR] results/{json_file}: filename 불일치\n"
                f"  예상: '{expected_pdf}'\n"
                f"  실제: '{actual}'"
            )

    if errors:
        print("[validate_results] filename 검증 실패 — 아래 파일들을 즉시 수정하세요:\n", file=sys.stderr)
        for err in errors:
            print(err, file=sys.stderr)
        print(
            "\n수정 방법: 각 JSON 파일을 열어 'filename' 필드를 해당 PDF 파일명으로 정확히 수정한 뒤 다시 저장하세요.",
            file=sys.stderr
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == '__main__':
    main()

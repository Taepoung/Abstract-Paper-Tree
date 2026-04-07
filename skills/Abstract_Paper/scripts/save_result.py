"""
stdin으로 받은 JSON 객체를 results/{filename}.json 으로 저장합니다.

사용법:
    python skills/Abstract_Paper/scripts/save_result.py << 'EOF'
    { "filename": "paper.pdf", "title": "...", ... }
    EOF
"""
import json
import os
import sys


def main():
    raw = sys.stdin.read().strip()
    if not raw:
        print("ERROR: stdin이 비어 있습니다.", file=sys.stderr)
        sys.exit(1)

    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: JSON 파싱 실패 — {e}", file=sys.stderr)
        sys.exit(1)

    filename = obj.get("filename", "")
    if not filename:
        print("ERROR: 'filename' 필드가 없습니다.", file=sys.stderr)
        sys.exit(1)

    if not filename.endswith(".pdf"):
        print(f"ERROR: filename이 .pdf로 끝나야 합니다 — '{filename}'", file=sys.stderr)
        sys.exit(1)

    os.makedirs("results", exist_ok=True)
    out = os.path.join("results", os.path.splitext(filename)[0] + ".json")

    with open(out, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

    print(f"Saved: {out}")


if __name__ == "__main__":
    main()

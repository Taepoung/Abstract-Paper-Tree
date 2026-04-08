"""
PostToolUse hook (Write): problem.json / method.json 저장 시
results.jsonl의 모든 논문이 클러스터에 포함되었는지 검증합니다.
"""
import json
import os
import sys


def main():
    try:
        hook_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    file_path = hook_data.get("tool_input", {}).get("file_path", "")
    norm = file_path.replace("\\", "/")

    if not (norm.endswith("/problem.json") or norm.endswith("/method.json")):
        sys.exit(0)

    # results.jsonl은 같은 디렉토리에 있다고 가정
    base_dir = os.path.dirname(file_path)
    jsonl_path = os.path.join(base_dir, "results.jsonl")

    if not os.path.exists(jsonl_path):
        sys.exit(0)

    # results.jsonl에서 전체 파일명 수집
    all_filenames = set()
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                fn = obj.get("filename", "")
                if fn:
                    all_filenames.add(fn)
            except json.JSONDecodeError:
                continue

    if len(all_filenames) < 2:
        sys.exit(0)

    # cluster json에서 포함된 파일명 수집
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            cluster_data = json.load(f)
    except (json.JSONDecodeError, OSError):
        sys.exit(0)

    clustered = set()
    for cluster in cluster_data.values():
        for fn in cluster.get("filenames", []):
            clustered.add(fn)

    missing = all_filenames - clustered
    if missing:
        label = os.path.basename(file_path)
        print(
            f"[validate_cluster] {label}: 누락된 논문 {len(missing)}편 — 즉시 해당 논문을 적절한 클러스터에 추가하세요:\n",
            file=sys.stderr,
        )
        for fn in sorted(missing):
            print(f"  - {fn}", file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()

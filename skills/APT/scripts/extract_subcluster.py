"""
output_dir의 problem.json/method.json을 자동 탐지하여,
모든 클러스터의 논문 데이터를 서브 디렉토리로 일괄 추출합니다.
논문이 1편뿐인 클러스터는 건너뜁니다.

사용법:
    python skills/APT/scripts/extract_subcluster.py [output_dir]

기본값: output_dir = "." (현재 디렉토리)
"""
import json
import os
import re
import sys


def sanitize_dirname(name):
    safe = re.sub(r'[^\w\s\-]', '', name, flags=re.UNICODE)
    safe = re.sub(r'\s+', '_', safe).strip('_')
    return safe[:60] if safe else 'cluster'


def main():
    output_dir = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')

    # results.jsonl 로드
    results_file = os.path.join(output_dir, 'results.jsonl')
    if not os.path.exists(results_file):
        print(f"Error: '{results_file}' not found.", file=sys.stderr)
        sys.exit(1)

    results = {}
    with open(results_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    data = json.loads(line)
                    fn = data.get('filename', '')
                    if fn:
                        results[fn] = data
                except json.JSONDecodeError:
                    pass

    # problem.json / method.json 중 있는 것을 모두 처리
    total = 0
    for fname in ('problem.json', 'method.json'):
        json_file = os.path.join(output_dir, fname)
        if not os.path.exists(json_file):
            continue

        with open(json_file, 'r', encoding='utf-8') as f:
            clusters = json.load(f)

        for cluster_name, info in clusters.items():
            filenames = info.get('filenames', [])
            if len(filenames) <= 1:
                continue

            sub_results = []
            missing = []
            for fn in filenames:
                if fn in results:
                    sub_results.append(results[fn])
                else:
                    missing.append(fn)

            if missing:
                print(f"Warning: {cluster_name}: {len(missing)} papers not in results.jsonl", file=sys.stderr)

            safe_name = sanitize_dirname(cluster_name)
            sub_dir = os.path.join(output_dir, 'clusters', safe_name)
            os.makedirs(sub_dir, exist_ok=True)
            with open(os.path.join(sub_dir, 'results.jsonl'), 'w', encoding='utf-8') as f:
                for obj in sub_results:
                    f.write(json.dumps(obj, ensure_ascii=False) + '\n')

            print(f"{sub_dir} ({len(sub_results)} papers)")
            total += 1

    print(f"Done: {total} sub-clusters extracted.")


if __name__ == '__main__':
    main()

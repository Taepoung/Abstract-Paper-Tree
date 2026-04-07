"""
클러스터의 논문 데이터를 서브 디렉토리로 추출합니다.

사용법:
    python skills/APT/scripts/extract_subcluster.py <output_dir> <cluster_name> <filename1> [filename2 ...]
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
    if len(sys.argv) < 4:
        print("Usage: extract_subcluster.py <output_dir> <cluster_name> <filename1> [filename2 ...]")
        sys.exit(1)

    output_dir = sys.argv[1]
    cluster_name = sys.argv[2]
    cluster_filenames = sys.argv[3:]

    safe_name = sanitize_dirname(cluster_name)

    # results.jsonl에서 해당 논문만 추출
    results_file = os.path.join(output_dir, 'results.jsonl')
    if not os.path.exists(results_file):
        print(f"Error: '{results_file}' not found.")
        sys.exit(1)

    sub_results = []
    with open(results_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    data = json.loads(line)
                    if data.get('filename') in cluster_filenames:
                        sub_results.append(data)
                except json.JSONDecodeError:
                    pass

    # 서브 디렉토리에 저장
    sub_dir = os.path.join(output_dir, 'clusters', safe_name)
    os.makedirs(sub_dir, exist_ok=True)
    with open(os.path.join(sub_dir, 'results.jsonl'), 'w', encoding='utf-8') as f:
        for obj in sub_results:
            f.write(json.dumps(obj, ensure_ascii=False) + '\n')

    print(f"Prepared sub-dir: {sub_dir} ({len(sub_results)} papers)")


if __name__ == '__main__':
    main()

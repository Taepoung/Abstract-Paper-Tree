"""
results/*.json 파일들을 하나의 results.jsonl로 병합합니다.

사용법:
    python skills/Abstract_Area/scripts/merge_results.py [output_dir]
"""
import glob
import json
import os
import sys


def main():
    output_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    results_dir = os.path.join(output_dir, 'results')

    if not os.path.isdir(results_dir):
        print(f"Error: '{results_dir}' not found.")
        sys.exit(1)

    files = sorted(glob.glob(os.path.join(results_dir, '*.json')))
    if not files:
        print(f"Error: No JSON files in '{results_dir}'.")
        sys.exit(1)

    output_file = os.path.join(output_dir, 'results.jsonl')
    with open(output_file, 'w', encoding='utf-8') as out:
        for fp in files:
            try:
                with open(fp, 'r', encoding='utf-8') as f:
                    obj = json.load(f)
                    out.write(json.dumps(obj, ensure_ascii=False) + '\n')
            except (json.JSONDecodeError, OSError) as e:
                print(f"Warning: Skipping '{fp}' — {e}", file=sys.stderr)

    print(f"Merged {len(files)} papers into {output_file}")


if __name__ == '__main__':
    main()

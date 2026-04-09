"""
results.jsonl을 파싱하여 keywords.html을 생성합니다.
"""
import json


def safe_json(obj):
    import json
    return json.dumps(obj, ensure_ascii=False).replace('</', '<\/')


def _write_chunked(filepath, content, chunk_size=32*1024):
    with open(filepath, 'w', encoding='utf-8') as f:
        for i in range(0, len(content), chunk_size):
            f.write(content[i:i + chunk_size])
            f.flush()
            os.fsync(f.fileno())
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
def generate_keywords(output_dir):
    jsonl_path = os.path.join(output_dir, 'results.jsonl')
    if not os.path.exists(jsonl_path):
        print(f"Error: '{jsonl_path}' not found.", file=__import__('sys').stderr)
        return

    results = []
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    results.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    template_path = os.path.join(SCRIPT_DIR, '..', 'assets', 'keywords_template.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()

    html = html.replace(
        'const researchResults = [];',
        f'const researchResults = {safe_json(results)};'
    )

    output_file = os.path.join(output_dir, 'keywords.html')
    _write_chunked(output_file, html)
    print(f"Built: {output_file} ({len(html)} bytes)")
if __name__ == '__main__':
    import sys
    generate_keywords(os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.'))

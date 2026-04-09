"""
problem.json / method.json 계층 구조를 읽어 방사형 트리 시각화 페이지(tree.html)를 생성합니다.
클러스터 노드 + 논문 리프 노드를 모두 표시합니다.

사용법:
    python skills/APT/scripts/generate_tree.py [output_dir]
"""
import argparse
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
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
def sanitize_dirname(name):
    safe = re.sub(r'[^\w\s\-]', '', name, flags=re.UNICODE)
    safe = re.sub(r'\s+', '_', safe).strip('_')
    return safe[:60] if safe else 'cluster'
def count_papers(directory):
    results_file = os.path.join(directory, 'results.jsonl')
    if not os.path.exists(results_file):
        return 0
    with open(results_file, 'r', encoding='utf-8') as f:
        return sum(1 for line in f if line.strip())
def load_results(directory):
    results_map = {}
    results_file = os.path.join(directory, 'results.jsonl')
    if os.path.exists(results_file):
        with open(results_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line)
                        if data.get('filename'):
                            results_map[data['filename']] = data
                    except json.JSONDecodeError:
                        pass
    return results_map
def paper_leaf(filename, results_map):
    """논문 파일명을 리프 노드로 변환."""
    paper = results_map.get(filename, {})
    return {
        'name': paper.get('title', filename),
        'filename': filename,
        'research_type': paper.get('research_type', ''),
        'count': 0,
        'summary': paper.get('problem', ''),
        'keywords': paper.get('keywords', []),
        'children': [],
        'is_paper': True,
    }
def _collect_filenames(children):
    """children 리스트에서 모든 논문 filename을 재귀적으로 수집."""
    fns = set()
    for child in children:
        if child.get('is_paper'):
            fns.add(child.get('filename', ''))
        fns.update(_collect_filenames(child.get('children', [])))
    return fns

def build_problem_tree(output_dir, root_label='Research Map', results_map=None):
    """problem.json 기반 트리 — 클러스터 계층 + 리프 클러스터에 논문 노드."""
    problem_file = os.path.join(output_dir, 'problem.json')
    if not os.path.exists(problem_file):
        return None

    if results_map is None:
        results_map = load_results(output_dir)

    with open(problem_file, 'r', encoding='utf-8') as f:
        clusters = json.load(f)

    children = []
    for name, info in clusters.items():
        safe_name = sanitize_dirname(name)
        sub_dir = os.path.join(output_dir, 'clusters', safe_name)
        sub_index = os.path.join(sub_dir, 'index.html')
        sub_url = f'clusters/{safe_name}/index.html'
        cluster_url = sub_url if os.path.exists(sub_index) else None

        node = {
            'name': name,
            'url': cluster_url,
            'count': len(info.get('filenames', [])),
            'summary': info.get('summary', ''),
            'children': [],
        }

        # 서브 클러스터 재귀
        if os.path.exists(sub_dir):
            sub_results = load_results(sub_dir) or results_map
            sub_tree = build_problem_tree(sub_dir, root_label=name, results_map=sub_results)
            if sub_tree and sub_tree['children']:
                node['children'] = sub_tree['children']

        # 리프 클러스터(서브 없음)이거나 서브에서 누락된 논문을 리프로 추가
        covered = _collect_filenames(node['children'])
        for fn in info.get('filenames', []):
            if fn not in covered:
                node['children'].append(paper_leaf(fn, results_map))

        children.append(node)

    return {
        'name': root_label,
        'url': 'index.html',
        'count': count_papers(output_dir),
        'summary': '',
        'children': children,
    }
def build_method_tree(output_dir, root_label='Research Map', results_map=None):
    """method.json 기반 트리 — 클러스터 계층 + 리프 클러스터에 논문 노드."""
    method_file = os.path.join(output_dir, 'method.json')
    if not os.path.exists(method_file):
        return None

    if results_map is None:
        results_map = load_results(output_dir)

    with open(method_file, 'r', encoding='utf-8') as f:
        clusters = json.load(f)

    children = []
    for name, info in clusters.items():
        safe_name = sanitize_dirname(name)
        sub_dir = os.path.join(output_dir, 'clusters', safe_name)
        sub_index = os.path.join(sub_dir, 'index.html')
        sub_url = f'clusters/{safe_name}/index.html'
        cluster_url = sub_url if os.path.exists(sub_index) else None

        node = {
            'name': name,
            'url': cluster_url,
            'count': len(info.get('filenames', [])),
            'summary': info.get('summary', ''),
            'children': [],
        }

        # 서브 클러스터 재귀
        if os.path.exists(sub_dir):
            sub_results = load_results(sub_dir) or results_map
            sub_tree = build_method_tree(sub_dir, root_label=name, results_map=sub_results)
            if sub_tree and sub_tree['children']:
                node['children'] = sub_tree['children']

        # 리프 클러스터(서브 없음)이거나 서브에서 누락된 논문을 리프로 추가
        covered = _collect_filenames(node['children'])
        for fn in info.get('filenames', []):
            if fn not in covered:
                node['children'].append(paper_leaf(fn, results_map))

        children.append(node)

    return {
        'name': root_label,
        'url': 'index.html',
        'count': count_papers(output_dir),
        'summary': '',
        'children': children,
    }
def generate_tree(output_dir):
    problem_tree = build_problem_tree(output_dir)
    method_tree = build_method_tree(output_dir)

    if not problem_tree and not method_tree:
        print("Error: problem.json / method.json not found.")
        sys.exit(1)

    template_path = os.path.join(SCRIPT_DIR, '..', 'assets', 'tree_template.html')
    if not os.path.exists(template_path):
        print(f"Error: '{template_path}' not found.")
        sys.exit(1)

    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()

    html = html.replace(
        'const problemTreeData = {};',
        f'const problemTreeData = {safe_json(problem_tree or {})};'
    ).replace(
        'const methodTreeData = {};',
        f'const methodTreeData = {safe_json(method_tree or {})};'
    )

    output_file = os.path.join(output_dir, 'tree.html')
    _write_chunked(output_file, html)
    print(f"Generated {output_file} ({len(html)} bytes)")
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('output_dir', nargs='?', default='.')
    args = parser.parse_args()

    output_dir = os.path.abspath(args.output_dir)
    if not os.path.isdir(output_dir):
        print(f"Error: '{output_dir}' is not a valid directory.")
        sys.exit(1)
    generate_tree(output_dir)

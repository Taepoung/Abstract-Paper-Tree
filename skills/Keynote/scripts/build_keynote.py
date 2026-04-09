"""
keynote.json + results.jsonl을 읽어 keynote.html(대시보드)과
keynote_tree.html(트리 뷰)을 생성합니다.

사용법:
    python skills/Keynote/scripts/build_keynote.py

동작:
    현재 디렉토리의 keynote.json과 results.jsonl을 읽고,
    템플릿에 데이터를 주입하여 두 개의 HTML 파일을 생성합니다.
"""
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def safe_json(obj):
    return json.dumps(obj, ensure_ascii=False).replace('</', '<\\/')


def load_papers(output_dir):
    """results.jsonl → {filename: paper_data} dict"""
    jsonl_path = os.path.join(output_dir, 'results.jsonl')
    paper_lookup = {}
    if os.path.exists(jsonl_path):
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        data = json.loads(line)
                        fn = data.get('filename', '')
                        if fn:
                            paper_lookup[fn] = data
                    except json.JSONDecodeError:
                        continue
    return paper_lookup


def build_tree_data(axis_data, paper_lookup):
    """
    keynote.json의 한 축(tool 또는 technique) 데이터를 트리 구조로 변환.

    트리 구조:
      Root
      ├── Method (research_type)
      │   ├── Group Name
      │   │   ├── paper1 (leaf)
      │   │   └── paper2 (leaf)
      │   └── ...
      └── Empirical
          └── ...
    """
    total_papers = set()
    type_children = []

    for rtype, groups in axis_data.items():
        if not groups:
            continue
        group_children = []
        type_paper_count = 0

        for group in groups:
            paper_children = []
            for fn in group.get('filenames', []):
                paper = paper_lookup.get(fn, {})
                paper_children.append({
                    'name': paper.get('title', fn),
                    'filename': fn,
                    'is_paper': True,
                    'research_type': paper.get('research_type', rtype),
                    'keywords': paper.get('keywords', []),
                })
                total_papers.add(fn)

            group_children.append({
                'name': group['name'],
                'summary': group.get('summary', ''),
                'keywords': group.get('keywords', []),
                'count': len(paper_children),
                'children': paper_children,
            })
            type_paper_count += len(paper_children)

        type_children.append({
            'name': rtype,
            'is_type': True,
            'count': type_paper_count,
            'children': group_children,
        })

    return {
        'name': 'Keynote',
        'count': len(total_papers),
        'children': type_children,
    }


def build_dashboard(keynote_data, paper_lookup, output_dir):
    """대시보드 HTML 빌드"""
    template_path = os.path.join(SCRIPT_DIR, '..', 'assets', 'keynote_template.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()

    html = html.replace(
        'const keynoteData = {};',
        f'const keynoteData = {safe_json(keynote_data)};'
    )
    html = html.replace(
        'const paperLookup = {};',
        f'const paperLookup = {safe_json(paper_lookup)};'
    )

    output_file = os.path.join(output_dir, 'keynote.html')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Built: {output_file}")


def build_tree(keynote_data, paper_lookup, output_dir):
    """트리 뷰 HTML 빌드"""
    tool_tree = build_tree_data(keynote_data.get('tool', {}), paper_lookup)
    technique_tree = build_tree_data(keynote_data.get('technique', {}), paper_lookup)

    template_path = os.path.join(SCRIPT_DIR, '..', 'assets', 'keynote_tree_template.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()

    html = html.replace(
        'const toolTreeData = {};',
        f'const toolTreeData = {safe_json(tool_tree)};'
    )
    html = html.replace(
        'const techniqueTreeData = {};',
        f'const techniqueTreeData = {safe_json(technique_tree)};'
    )

    output_file = os.path.join(output_dir, 'keynote_tree.html')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Built: {output_file}")


def main():
    output_dir = os.path.abspath('.')

    # keynote.json 로드
    keynote_path = os.path.join(output_dir, 'keynote.json')
    if not os.path.exists(keynote_path):
        print(f"Error: '{keynote_path}' not found.", file=sys.stderr)
        sys.exit(1)

    with open(keynote_path, 'r', encoding='utf-8') as f:
        keynote_data = json.load(f)

    paper_lookup = load_papers(output_dir)

    build_dashboard(keynote_data, paper_lookup, output_dir)
    build_tree(keynote_data, paper_lookup, output_dir)


if __name__ == '__main__':
    main()

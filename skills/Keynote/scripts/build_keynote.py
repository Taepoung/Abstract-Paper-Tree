"""
keynote.json을 읽어 keynote.html(대시보드)과
keynote_tree.html(트리 뷰)을 생성합니다.

사용법:
    python skills/Keynote/scripts/build_keynote.py

동작:
    현재 디렉토리의 keynote.json을 읽고,
    템플릿에 데이터를 주입하여 두 개의 HTML 파일을 생성합니다.
"""
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def safe_json(obj):
    return json.dumps(obj, ensure_ascii=False).replace('</', '<\\/')


def build_tree_data(axis_data):
    """
    keynote.json의 한 축(tool 또는 technique) 데이터를 트리 구조로 변환.
    같은 이름의 그룹은 research_type과 무관하게 하나로 병합.
    그룹이 리프 노드 (키워드는 하단 목록에서 pill로 표시).

    트리 구조:
      Root
      ├── Group Name (leaf)
      └── ...
    """
    merged = {}  # name → { summary, keywords list, research_types set }
    order = []

    for rtype, groups in axis_data.items():
        if not groups:
            continue
        for group in groups:
            name = group['name']
            if name not in merged:
                merged[name] = {
                    'summary': group.get('summary', ''),
                    'keywords': set(group.get('keywords', [])),
                    'research_types': set(),
                }
                order.append(name)
            else:
                merged[name]['keywords'].update(group.get('keywords', []))
            merged[name]['research_types'].add(rtype)

    all_keywords = set()
    group_children = []
    for name in order:
        m = merged[name]
        all_keywords.update(m['keywords'])
        group_children.append({
            'name': name,
            'summary': m['summary'],
            'keywords': sorted(m['keywords']),
            'research_types': sorted(m['research_types']),
        })

    return {
        'name': 'Keynote',
        'count': len(all_keywords),
        'children': group_children,
    }


def build_dashboard(keynote_data, output_dir):
    """대시보드 HTML 빌드"""
    template_path = os.path.join(SCRIPT_DIR, '..', 'assets', 'keynote_template.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()

    html = html.replace(
        'const keynoteData = {};',
        f'const keynoteData = {safe_json(keynote_data)};'
    )

    output_file = os.path.join(output_dir, 'keynote.html')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Built: {output_file}")


def build_kw_type_map(axis_data):
    """keyword → [research_types] 정확한 매핑 (병합 전 원본 기준)"""
    kw_map = {}
    for rtype, groups in axis_data.items():
        if not groups:
            continue
        for group in groups:
            for kw in group.get('keywords', []):
                if kw not in kw_map:
                    kw_map[kw] = set()
                kw_map[kw].add(rtype)
    return {kw: sorted(types) for kw, types in kw_map.items()}


def build_tree(keynote_data, output_dir):
    """트리 뷰 HTML 빌드"""
    tool_tree = build_tree_data(keynote_data.get('tool', {}))
    technique_tree = build_tree_data(keynote_data.get('technique', {}))
    tool_kw_map = build_kw_type_map(keynote_data.get('tool', {}))
    technique_kw_map = build_kw_type_map(keynote_data.get('technique', {}))

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
    html = html.replace(
        'const toolKwTypeMap = {};',
        f'const toolKwTypeMap = {safe_json(tool_kw_map)};'
    )
    html = html.replace(
        'const techniqueKwTypeMap = {};',
        f'const techniqueKwTypeMap = {safe_json(technique_kw_map)};'
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

    build_dashboard(keynote_data, output_dir)
    build_tree(keynote_data, output_dir)


if __name__ == '__main__':
    main()

import argparse
import glob
import json


def safe_json(obj):
    import json
    return json.dumps(obj, ensure_ascii=False).replace('</', '<\/')
import os
import re
import sys
def sanitize_dirname(name):
    safe = re.sub(r'[^\w\s\-]', '', name, flags=re.UNICODE)
    safe = re.sub(r'\s+', '_', safe).strip('_')
    return safe[:60] if safe else 'cluster'
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
def generate_dashboard(output_dir, parent_url=None, page_title=None, tree_url=None):
    results_file = os.path.join(output_dir, 'results.jsonl')
    problem_file = os.path.join(output_dir, 'problem.json')
    method_file = os.path.join(output_dir, 'method.json')
    template_path = os.path.join(SCRIPT_DIR, '..', 'assets', 'template.html')
    output_file = os.path.join(output_dir, 'index.html')

    if not os.path.exists(template_path):
        print(f"Error: '{template_path}' not found.")
        sys.exit(1)
    if not os.path.exists(problem_file) and not os.path.exists(method_file):
        print(f"Error: Neither problem.json nor method.json found in '{output_dir}'.")
        sys.exit(1)

    # results.jsonl 우선, 없으면 results/*.json fallback
    results_map = {}
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

    if not results_map:
        for fp in glob.glob(os.path.join(output_dir, 'results/*.json')):
            try:
                with open(fp, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('filename'):
                        results_map[data['filename']] = data
            except (json.JSONDecodeError, OSError):
                pass

    if not results_map:
        print("Error: No paper results found.")
        sys.exit(1)

    problem_clusters = {}
    if os.path.exists(problem_file):
        with open(problem_file, 'r', encoding='utf-8') as f:
            problem_clusters = json.load(f)
    method_clusters = {}
    if os.path.exists(method_file):
        with open(method_file, 'r', encoding='utf-8') as f:
            method_clusters = json.load(f)

    def join_paper_details(clusters):
        joined = {}
        for name, info in clusters.items():
            papers = [results_map[fn] for fn in info.get('filenames', []) if fn in results_map]
            safe_name = sanitize_dirname(name)
            sub_page_path = os.path.join(output_dir, 'clusters', safe_name, 'index.html')
            sub_page_url = f'clusters/{safe_name}/index.html' if os.path.exists(sub_page_path) else None
            joined[name] = {
                "summary": info.get('summary', ''),
                "papers": papers,
                "sub_page_url": sub_page_url,
            }
        return joined

    all_results = list(results_map.values())
    joined_problems = join_paper_details(problem_clusters)
    joined_methods = join_paper_details(method_clusters)

    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()

    html = html.replace(
        'const researchResults = [];',
        f'const researchResults = {safe_json(all_results)};'
    ).replace(
        'const problemGroups = {};',
        f'const problemGroups = {safe_json(joined_problems)};'
    ).replace(
        'const methodologyGroups = {};',
        f'const methodologyGroups = {safe_json(joined_methods)};'
    ).replace(
        'const parentUrl = null;',
        f'const parentUrl = {json.dumps(parent_url)};'
    ).replace(
        'const pageTitle = "";',
        f'const pageTitle = {json.dumps(page_title or "Research Map")};'
    ).replace(
        'const treeUrl = "tree.html";',
        f'const treeUrl = {json.dumps(tree_url or "tree.html")};'
    )

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Generated {output_file} ({len(all_results)} papers)")
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('output_dir', nargs='?', default='.')
    parser.add_argument('--parent-url', default=None, dest='parent_url')
    parser.add_argument('--page-title', default=None, dest='page_title')
    parser.add_argument('--tree-url', default=None, dest='tree_url')
    args = parser.parse_args()

    output_dir = os.path.abspath(args.output_dir)
    if not os.path.isdir(output_dir):
        print(f"Error: '{output_dir}' is not a valid directory.")
        sys.exit(1)
    generate_dashboard(output_dir, parent_url=args.parent_url, page_title=args.page_title, tree_url=args.tree_url)

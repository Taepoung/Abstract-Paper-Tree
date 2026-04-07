import argparse
import glob
import json
import os
import re
import sys


def sanitize_dirname(name):
    safe = re.sub(r'[^\w\s\-]', '', name, flags=re.UNICODE)
    safe = re.sub(r'\s+', '_', safe).strip('_')
    return safe[:60] if safe else 'cluster'


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def generate_dashboard(output_dir, parent_url=None, page_title=None):
    results_file = os.path.join(output_dir, 'results.jsonl')
    problem_file = os.path.join(output_dir, 'problem.json')
    method_file = os.path.join(output_dir, 'method.json')
    template_path = os.path.join(SCRIPT_DIR, '..', 'assets', 'template.html')
    output_file = os.path.join(output_dir, 'index.html')

    for f in [problem_file, method_file, template_path]:
        if not os.path.exists(f):
            print(f"Error: '{f}' not found.")
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

    with open(problem_file, 'r', encoding='utf-8') as f:
        problem_clusters = json.load(f)
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
        f'const researchResults = {json.dumps(all_results, ensure_ascii=False)};'
    ).replace(
        'const problemGroups = {};',
        f'const problemGroups = {json.dumps(joined_problems, ensure_ascii=False)};'
    ).replace(
        'const methodologyGroups = {};',
        f'const methodologyGroups = {json.dumps(joined_methods, ensure_ascii=False)};'
    ).replace(
        'const parentUrl = null;',
        f'const parentUrl = {json.dumps(parent_url)};'
    ).replace(
        'const pageTitle = "";',
        f'const pageTitle = {json.dumps(page_title or "Research Map")};'
    )

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Generated {output_file} ({len(all_results)} papers)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('output_dir', nargs='?', default='.')
    parser.add_argument('--parent-url', default=None, dest='parent_url')
    parser.add_argument('--page-title', default=None, dest='page_title')
    args = parser.parse_args()

    if not os.path.isdir(args.output_dir):
        print(f"Error: '{args.output_dir}' is not a valid directory.")
        sys.exit(1)
    generate_dashboard(args.output_dir, parent_url=args.parent_url, page_title=args.page_title)

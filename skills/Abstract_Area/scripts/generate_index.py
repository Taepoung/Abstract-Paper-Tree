import glob
import json
import os
import sys


def generate_dashboard(output_dir):
    results_file = os.path.join(output_dir, 'results.jsonl')
    problem_file = os.path.join(output_dir, 'problem.json')
    method_file = os.path.join(output_dir, 'method.json')
    template_path = os.path.join('skills', 'Abstract_Area', 'assets', 'template.html')
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
            joined[name] = {"summary": info.get('summary', ''), "papers": papers}
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
    )

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Generated {output_file} ({len(all_results)} papers)")


if __name__ == "__main__":
    output_directory = sys.argv[1] if len(sys.argv) > 1 else '.'
    if not os.path.isdir(output_directory):
        print(f"Error: '{output_directory}' is not a valid directory.")
        sys.exit(1)
    generate_dashboard(output_directory)

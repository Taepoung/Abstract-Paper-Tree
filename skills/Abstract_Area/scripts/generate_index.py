import json
import os
import sys

def generate_dashboard(output_dir):
    # 1. 파일 경로 설정
    results_file = 'results.jsonl'
    problem_file = 'problem.json'
    method_file = 'method.json'
    template_path = os.path.join('skills', 'Abstract_Area', 'assets', 'template.html')
    output_file = os.path.join(output_dir, 'index.html')

    # 2. 필수 파일 존재 확인
    # results, problem, method 파일은 현재 실행 디렉토리에 있다고 가정
    for f in [results_file, problem_file, method_file]:
        if not os.path.exists(f):
            print(f"Error: Required file '{f}' not found in current directory.")
            sys.exit(1)
    
    if not os.path.exists(template_path):
        print(f"Error: Template file '{template_path}' not found.")
        sys.exit(1)

    # 3. 데이터 로드: results.jsonl (파일명 기반 맵 생성)
    results_map = {}
    with open(results_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    data = json.loads(line)
                    filename = data.get('filename')
                    if filename:
                        results_map[filename] = data
                except json.JSONDecodeError:
                    print(f"Warning: Failed to parse line in {results_file}: {line}")

    # 4. 데이터 로드: problem.json & method.json
    try:
        with open(problem_file, 'r', encoding='utf-8') as f:
            problem_clusters = json.load(f)
        with open(method_file, 'r', encoding='utf-8') as f:
            method_clusters = json.load(f)
    except Exception as e:
        print(f"Error: Failed to load JSON configuration: {e}")
        sys.exit(1)

    # 5. 데이터 결합: filenames을 실제 연동 데이터로 치환
    def join_paper_details(clusters):
        joined = {}
        for cluster_name, info in clusters.items():
            filenames = info.get('filenames', [])
            summary = info.get('summary', '')
            papers = []
            for fname in filenames:
                if fname in results_map:
                    papers.append(results_map[fname])
                else:
                    print(f"Warning: Filename '{fname}' not found in {results_file}")
            joined[cluster_name] = {
                "summary": summary,
                "papers": papers
            }
        return joined

    joined_problem_groups = join_paper_details(problem_clusters)
    joined_methodology_groups = join_paper_details(method_clusters)
    all_results = list(results_map.values())

    # 6. 템플릿에 데이터 주입
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        # 데이터 직렬화 (JSON 문자열로 변환)
        results_json = json.dumps(all_results, ensure_ascii=False, indent=2)
        problems_json = json.dumps(joined_problem_groups, ensure_ascii=False, indent=2)
        methods_json = json.dumps(joined_methodology_groups, ensure_ascii=False, indent=2)

        # 마커 치환
        # template.html의 스크립트 영역을 정확히 타겟팅합니다.
        injected_content = template_content.replace(
            'const researchResults = [];', f'const researchResults = {results_json};'
        ).replace(
            'const problemGroups = {};', f'const problemGroups = {problems_json};'
        ).replace(
            'const methodologyGroups = {};', f'const methodologyGroups = {methods_json};'
        )

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(injected_content)

        print(f"Successfully generated {output_file} from {len(all_results)} papers.")

    except Exception as e:
        print(f"Error during assembly: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # 인자로 출력 디렉토리를 받음 (기본값: 현재 디렉토리)
    output_directory = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    if not os.path.isdir(output_directory):
        print(f"Error: '{output_directory}' is not a valid directory.")
        sys.exit(1)

    generate_dashboard(output_directory)

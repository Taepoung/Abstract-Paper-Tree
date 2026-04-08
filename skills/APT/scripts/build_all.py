"""
전체 디렉토리를 재귀 순회하며 대시보드(index.html)와 트리(tree.html)를 일괄 생성합니다.

동작:
  1. output_dir부터 시작하여 clusters/ 하위를 재귀 탐색
  2. results.jsonl + (problem.json 또는 method.json)이 있는 디렉토리마다 index.html 생성
  3. 루트에서 tree.html 생성

사용법:
    python skills/APT/scripts/build_all.py [output_dir]

기본값: output_dir = "." (현재 디렉토리)
"""
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 같은 디렉토리의 스크립트를 import
sys.path.insert(0, SCRIPT_DIR)
import subprocess
from generate_index import generate_dashboard
from generate_tree import generate_tree
from generate_keywords import generate_keywords


def sanitize_dirname(name):
    safe = re.sub(r'[^\w\s\-]', '', name, flags=re.UNICODE)
    safe = re.sub(r'\s+', '_', safe).strip('_')
    return safe[:60] if safe else 'cluster'


def has_data(directory):
    """대시보드를 생성할 수 있는 디렉토리인지 확인."""
    has_jsonl = os.path.exists(os.path.join(directory, 'results.jsonl'))
    has_cluster = (os.path.exists(os.path.join(directory, 'problem.json')) or
                   os.path.exists(os.path.join(directory, 'method.json')))
    return has_jsonl and has_cluster


def relative_path(from_dir, to_dir):
    """from_dir에서 to_dir까지의 상대 경로를 계산."""
    return os.path.relpath(to_dir, from_dir).replace('\\', '/')


def build_recursive(directory, root_dir, parent_dir=None, page_title=None):
    """디렉토리를 재귀 순회하며 대시보드를 생성."""
    if not has_data(directory):
        return

    # 상대 경로 계산
    parent_url = None
    tree_url = None

    if parent_dir:
        rel_to_parent = relative_path(directory, parent_dir)
        parent_url = f"{rel_to_parent}/index.html"

    if directory != root_dir:
        rel_to_root = relative_path(directory, root_dir)
        tree_url = f"{rel_to_root}/tree.html"

    # 대시보드 생성
    generate_dashboard(directory, parent_url=parent_url,
                       page_title=page_title, tree_url=tree_url)
    print(f"Built: {os.path.join(directory, 'index.html')}")

    # 서브 클러스터 탐색
    clusters_dir = os.path.join(directory, 'clusters')
    if os.path.isdir(clusters_dir):
        for sub_name in sorted(os.listdir(clusters_dir)):
            sub_dir = os.path.join(clusters_dir, sub_name)
            if os.path.isdir(sub_dir) and has_data(sub_dir):
                # sub_name에서 원래 클러스터 이름 복원 (표시용)
                display_name = sub_name.replace('_', ' ')
                build_recursive(sub_dir, root_dir,
                                parent_dir=directory,
                                page_title=display_name)


def main():
    output_dir = os.path.abspath('.')

    if not os.path.isdir(output_dir):
        print(f"Error: '{output_dir}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    # 0. 서브 클러스터 데이터 재추출 (results.jsonl 변경 반영)
    extract_script = os.path.join(SCRIPT_DIR, 'extract_subcluster.py')
    subprocess.run([sys.executable, extract_script, output_dir], check=True)

    # 1. 모든 대시보드 재귀 생성
    build_recursive(output_dir, root_dir=output_dir)

    # 2. 루트 대시보드 재생성 (서브 페이지 링크 반영)
    if has_data(output_dir):
        generate_dashboard(output_dir)
        print(f"Rebuilt root: {os.path.join(output_dir, 'index.html')}")

    # 3. 트리 시각화 생성
    generate_tree(output_dir)
    generate_keywords(output_dir)
    print(f"Built: {os.path.join(output_dir, 'tree.html')}")

    print("Done.")


if __name__ == '__main__':
    main()

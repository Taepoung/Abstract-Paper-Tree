"""
현재 디렉토리의 PDF 파일을 스캔하고, results/ 디렉토리와 비교하여
아직 분석되지 않은 논문 목록을 출력합니다.

사용법:
    python skills/APT/scripts/scan_papers.py [output_dir]

출력 (stdout):
    미분석 PDF 파일명 (한 줄에 하나씩)
    마지막 줄: "총 X개 미분석 / Y개 전체"
"""
import os
import sys


def main():
    output_dir = sys.argv[1] if len(sys.argv) > 1 else '.'

    # PDF 목록
    pdfs = sorted(f for f in os.listdir(output_dir)
                  if f.lower().endswith('.pdf'))

    # results/ 의 기분석 목록
    results_dir = os.path.join(output_dir, 'results')
    os.makedirs(results_dir, exist_ok=True)

    analyzed = set()
    for f in os.listdir(results_dir):
        if f.endswith('.json'):
            analyzed.add(os.path.splitext(f)[0] + '.pdf')

    # 미분석 목록
    pending = [p for p in pdfs if p not in analyzed]

    for p in pending:
        print(p)

    print(f"총 {len(pending)}개 미분석 / {len(pdfs)}개 전체")


if __name__ == '__main__':
    main()

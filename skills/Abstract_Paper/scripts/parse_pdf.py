"""
PDF 파일을 파싱하고 본문 / Appendix로 분리합니다.

사용법:
    python skills/Abstract_Paper/scripts/parse_pdf.py [filename]

인자:
    filename  파일명을 지정하면 현재 디렉토리에서 찾습니다.
              생략하면 앱 업로드 경로(/mnt/user-data/uploads/)에서 찾습니다.

출력:
    /tmp/paper_main.txt       — 본문 (References/Bibliography 이전)
    /tmp/paper_appendix.txt   — Appendix (없으면 빈 파일)
    stdout: PDF 경로, 분리 결과 요약
"""

import glob
import os
import re
import subprocess
import sys

REF_PATTERN = re.compile(
    r"^\s*("
    r"References|REFERENCES"
    r"|Bibliography|BIBLIOGRAPHY|Bibliographie|BIBLIOGRAPHIE"
    r"|Works\s+Cited|WORKS\s+CITED"
    r"|Literature|LITERATURE"
    r")\s*$",
    re.MULTILINE,
)

APP_PATTERN = re.compile(
    r"^\s*("
    r"Appendix|APPENDIX|Appendices|APPENDICES"
    r"|Supplementary|SUPPLEMENTARY"
    r"|Supplement|SUPPLEMENT"
    r"|[A-Z]\.\s+[A-Z][a-z]"
    r")\b",
    re.MULTILINE,
)


def find_pdf(filename: str) -> str:
    if filename:
        return filename
    matches = glob.glob("/mnt/user-data/uploads/*.pdf")
    return matches[0] if matches else ""


def split_text(text: str) -> tuple[str, str]:
    app_match = APP_PATTERN.search(text)
    search_end = app_match.start() if app_match else len(text)
    appendix = text[app_match.start():].strip() if app_match else ""

    ref_matches = list(REF_PATTERN.finditer(text, 0, search_end))
    ref_match = ref_matches[-1] if ref_matches else None
    main = text[:ref_match.start()].rstrip() if ref_match else text[:search_end].rstrip()

    return main, appendix


def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else ""
    pdf = find_pdf(filename)

    if not pdf:
        print("ERROR: PDF 파일을 찾을 수 없습니다.", file=sys.stderr)
        sys.exit(1)

    print(pdf)

    import tempfile
    tmp_dir = tempfile.gettempdir()
    raw_path = os.path.join(tmp_dir, "paper_raw.txt")
    main_path = os.path.join(tmp_dir, "paper_main.txt")
    app_path = os.path.join(tmp_dir, "paper_appendix.txt")

    subprocess.run(["pdftotext", "-layout", pdf, raw_path], check=True)

    with open(raw_path, encoding="utf-8", errors="replace") as f:
        raw = f.read()
    main_text, appendix_text = split_text(raw)

    with open(main_path, "w", encoding="utf-8") as f:
        f.write(main_text)
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(appendix_text)

    has_appendix = "있음" if appendix_text else "없음"
    print(f"분리 완료 — 본문: {len(main_text)}자 / Appendix: {has_appendix}")


if __name__ == "__main__":
    main()

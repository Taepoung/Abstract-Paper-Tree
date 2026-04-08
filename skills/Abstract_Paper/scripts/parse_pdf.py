"""
PDF 파일에서 본문(References 이전)을 추출합니다.

사용법:
    python skills/Abstract_Paper/scripts/parse_pdf.py [filename]

인자:
    filename  파일명을 지정하면 현재 디렉토리에서 찾습니다.
              생략하면 앱 업로드 경로(/mnt/user-data/uploads/)에서 찾습니다.

출력:
    .parsed/{stem}_main.txt — 본문 (References/Bibliography 이전)
    stdout: PDF 경로, 본문 파일 경로, 결과 요약
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


def extract_main(text: str) -> str:
    app_match = APP_PATTERN.search(text)
    search_end = app_match.start() if app_match else len(text)

    ref_matches = list(REF_PATTERN.finditer(text, 0, search_end))
    ref_match = ref_matches[-1] if ref_matches else None
    main = text[:ref_match.start()].rstrip() if ref_match else text[:search_end].rstrip()

    return main


def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else ""
    pdf = find_pdf(filename)

    if not pdf:
        print("ERROR: PDF 파일을 찾을 수 없습니다.", file=sys.stderr)
        sys.exit(1)

    print(pdf)

    out_dir = os.path.join(os.getcwd(), '.parsed')
    os.makedirs(out_dir, exist_ok=True)

    stem = os.path.splitext(os.path.basename(pdf))[0]
    raw_path = os.path.join(out_dir, f"{stem}_raw.txt")
    main_path = os.path.join(out_dir, f"{stem}_main.txt")

    subprocess.run(["pdftotext", "-layout", pdf, raw_path], check=True)

    with open(raw_path, encoding="utf-8", errors="replace") as f:
        raw = f.read()
    main_text = extract_main(raw)

    with open(main_path, "w", encoding="utf-8") as f:
        f.write(main_text)

    print(f"본문: {main_path}")
    print(f"추출 완료 — 본문: {len(main_text)}자")


if __name__ == "__main__":
    main()

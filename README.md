# What in My Researches

> Claude plugin for turning a folder of research PDFs into structured insights and navigable HTML research maps.

[한국어](#한국어) | [English](#english)

---

## 한국어

### 개요

**What in My Researches**는 여러 개의 PDF 논문을 분석해 연구 문제, 방법론, 한계점을 구조화된 JSON으로 정리하고, 이를 다시 클러스터링해 HTML 대시보드와 트리 맵으로 시각화하는 Claude 플러그인입니다.

이 저장소는 다음 3가지 구성요소로 이루어져 있습니다.

- `Abstract_Paper`: 논문 1편을 정밀 분석해 JSON 결과 생성
- `APT`: 여러 논문을 병렬 분석하고 연구 지형을 시각화
- `PostToolUse Hook`: 저장된 결과의 `filename` 정합성 자동 검증

### 주요 기능

- PDF 논문별 핵심 정보 추출
- `problem`, `methodology`, `limitation` 중심의 구조화된 결과 저장
- 다수 논문 병렬 처리
- 문제 기준 / 방법론 기준 이중 클러스터링
- 재귀형 하위 클러스터 대시보드 생성
- `index.html`, `tree.html` 기반 시각화 결과 생성
- 결과 저장 직후 JSON 파일 무결성 검증

### 출력 예시

논문별 분석 결과는 `results/*.json`으로 저장됩니다.

```json
{
  "filename": "paper.pdf",
  "title": "Paper Title",
  "problem": "이 논문이 해결하려는 핵심 문제",
  "methodology": "방법론 설명",
  "limitation": "한계점 설명"
}
```

여러 결과를 묶으면 다음과 같은 산출물이 만들어집니다.

- `results/`: 논문별 개별 JSON
- `results.jsonl`: 전체 논문 병합 파일
- `problem.json`: 문제 기준 클러스터
- `method.json`: 방법 기준 클러스터
- `index.html`: 메인 리서치 대시보드
- `tree.html`: 전체 계층 트리 시각화

### 동작 흐름

1. `Abstract_Paper`가 PDF를 파싱하고 핵심 정보를 추출합니다.
2. 결과는 `results/{paper}.json` 형태로 저장됩니다.
3. Hook이 JSON의 `filename`과 실제 파일명이 일치하는지 검사합니다.
4. `APT`가 개별 결과를 병합하고 클러스터링합니다.
5. HTML 대시보드와 트리 뷰를 생성합니다.

### 저장소 구조

```text
.
├─ .claude-plugin/
│  └─ plugin.json
├─ hooks/
│  ├─ hook.json
│  └─ scripts/
│     └─ validate_results.py
└─ skills/
   ├─ Abstract_Paper/
   │  ├─ SKILL.md
   │  └─ scripts/
   │     ├─ parse_pdf.py
   │     └─ save_result.py
   └─ APT/
      ├─ SKILL.md
      ├─ assets/
      │  ├─ template.html
      │  └─ tree_template.html
      └─ scripts/
         ├─ merge_results.py
         ├─ generate_index.py
         ├─ generate_tree.py
         └─ extract_subcluster.py
```

### 요구 사항

- Python 3.x
- `pdftotext` 명령 사용 가능 환경
- Claude 플러그인/스킬/훅 구조를 실행할 수 있는 환경

`parse_pdf.py`는 내부적으로 아래 명령을 사용합니다.

```bash
pdftotext -layout <paper.pdf> <output.txt>
```

### 빠른 시작

1. 분석할 PDF 논문들을 작업 디렉토리에 둡니다.
2. 단일 논문 분석이 필요하면 `Abstract_Paper`를 사용합니다.
3. 전체 연구 지형 분석이 필요하면 `APT`를 사용합니다.
4. 생성된 `index.html`과 `tree.html`을 열어 결과를 확인합니다.

예시 스킬 인자:

```text
Abstract_Paper: my_paper.pdf korean
APT: korean 2
```

### 사용 포인트

- 개별 논문을 정밀하게 JSON으로 축적하고 싶을 때
- 여러 논문의 연구 흐름을 한 번에 보고 싶을 때
- 연구 분야 지도를 HTML 형태로 공유하고 싶을 때
- 후속 분석용 구조화 데이터셋을 만들고 싶을 때

### 플러그인 정보

```json
{
  "name": "what-in-my-researches",
  "version": "1.0.0",
  "author": "Tim_Yoon"
}
```

### 비고

- 이 플러그인은 논문 내용을 임의로 보강하지 않도록 설계되어 있습니다.
- 논문에 없는 정보는 추측 대신 명시적으로 비워 두거나 "논문에 명시되지 않음" 규칙을 따릅니다.
- 결과 검증 훅은 `save_result.py` 실행 이후 자동으로 동작하도록 구성되어 있습니다.

---

## English

### Overview

**What in My Researches** is a Claude plugin that analyzes research PDFs, extracts structured insights such as the core problem, methodology, and limitations, then clusters the results into interactive HTML dashboards and tree views.

The repository is built around three parts:

- `Abstract_Paper`: analyzes a single paper and saves a structured JSON record
- `APT`: processes multiple papers in parallel and builds a research map
- `PostToolUse Hook`: validates filename consistency in saved results

### Features

- Structured extraction from PDF papers
- JSON outputs centered on `problem`, `methodology`, and `limitation`
- Parallel multi-paper processing
- Dual clustering by research problem and methodology
- Recursive sub-cluster dashboard generation
- HTML outputs through `index.html` and `tree.html`
- Automatic post-save validation for result files

### Output Example

Each paper is stored as `results/*.json`.

```json
{
  "filename": "paper.pdf",
  "title": "Paper Title",
  "problem": "The core problem addressed by the paper",
  "methodology": "Description of the method",
  "limitation": "Description of the limitation"
}
```

Aggregated runs produce:

- `results/`: per-paper JSON files
- `results.jsonl`: merged result set
- `problem.json`: clusters grouped by problem
- `method.json`: clusters grouped by methodology
- `index.html`: main research dashboard
- `tree.html`: radial tree visualization

### Workflow

1. `Abstract_Paper` parses a PDF and extracts key fields.
2. The result is saved as `results/{paper}.json`.
3. The hook validates whether the JSON `filename` matches the actual file.
4. `APT` merges results and creates clusters.
5. HTML dashboards and tree views are generated.

### Repository Layout

```text
.
├─ .claude-plugin/
│  └─ plugin.json
├─ hooks/
│  ├─ hook.json
│  └─ scripts/
│     └─ validate_results.py
└─ skills/
   ├─ Abstract_Paper/
   │  ├─ SKILL.md
   │  └─ scripts/
   │     ├─ parse_pdf.py
   │     └─ save_result.py
   └─ APT/
      ├─ SKILL.md
      ├─ assets/
      │  ├─ template.html
      │  └─ tree_template.html
      └─ scripts/
         ├─ merge_results.py
         ├─ generate_index.py
         ├─ generate_tree.py
         └─ extract_subcluster.py
```

### Requirements

- Python 3.x
- An environment where `pdftotext` is available
- A Claude setup that supports plugin, skill, and hook execution

`parse_pdf.py` relies on:

```bash
pdftotext -layout <paper.pdf> <output.txt>
```

### Quick Start

1. Put the target PDF papers in your working directory.
2. Use `Abstract_Paper` when you want to analyze a single paper.
3. Use `APT` when you want a full research-map build across multiple papers.
4. Open `index.html` and `tree.html` to review the generated outputs.

Example skill arguments:

```text
Abstract_Paper: my_paper.pdf korean
APT: korean 2
```

### Good Fit For

- Building a structured dataset from individual papers
- Reviewing the landscape of a research area at a glance
- Publishing a shareable HTML research map
- Preparing downstream inputs for broader literature analysis

### Plugin Metadata

```json
{
  "name": "what-in-my-researches",
  "version": "1.0.0",
  "author": "Tim_Yoon"
}
```

### Notes

- The plugin is designed to avoid inventing information not present in the paper.
- Missing details should remain explicit rather than inferred.
- The validation hook is configured to run after `save_result.py`.

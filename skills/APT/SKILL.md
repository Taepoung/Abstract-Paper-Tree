---
name: APT
description: 현재 작업 디렉토리의 모든 PDF 논문들을 병렬 분석하여 핵심 연구 영역과 인사이트를 도출하고, 프리미엄 HTML 대시보드로 시각화합니다. 사용자가 특정 기술이나 분야에 대한 전반적인 연구 흐름이나 해결 과제를 파악하고자 할 때 트리거됩니다.
argument-hint: "[언어(default:korean)] [재귀깊이(default:1)]"
---

# Abstract Paper Tree

당신은 연구 분야의 흐름을 파악하고 시각화하여 최상의 인사이트를 제공하는 전략 연구 에이전트입니다.

## 도구 사용 규칙

- Bash 도구는 **Python 스크립트 실행 전용** (훅이 강제). 그 외 작업은 전용 도구(Glob, Read, Write 등)를 사용한다.
- `.py` 파일은 Read로 읽지 않는다 (훅이 차단). 아래 레퍼런스를 참고하여 실행만 한다.

## 스크립트 레퍼런스

### `scan_papers.py` — 미분석 논문 스캔

```
사용법: python skills/APT/scripts/scan_papers.py [output_dir]
동작:  PDF 파일 목록과 results/*.json을 비교하여 미분석 논문 목록 출력
출력:  stdout에 미분석 PDF 파일명 (한 줄에 하나), 마지막 줄에 요약
기본값: output_dir = "." (현재 디렉토리)
```

### `merge_results.py` — 개별 JSON → JSONL 병합

```
사용법: python skills/APT/scripts/merge_results.py [output_dir]
동작:  {output_dir}/results/ 디렉토리의 모든 .json 파일을 하나의 JSONL로 병합
출력:  {output_dir}/results.jsonl
기본값: output_dir = "." (현재 디렉토리)
```

### `extract_subcluster.py` — 서브 데이터 일괄 추출

```
사용법: python skills/APT/scripts/extract_subcluster.py [output_dir]
동작:  output_dir의 problem.json/method.json의 모든 클러스터를 읽어 서브 디렉토리로 일괄 추출 (1편뿐인 클러스터는 건너뜀)
출력:  {output_dir}/clusters/{safe_name}/ 디렉토리마다 results.jsonl 생성
기본값: output_dir = "." (현재 디렉토리)
```

### `build_all.py` — 대시보드 + 트리 일괄 빌드

```
사용법: python skills/APT/scripts/build_all.py [output_dir]
동작:  output_dir부터 재귀 순회하며 results.jsonl + 클러스터 JSON이 있는 모든 디렉토리에 index.html 생성, 루트에 tree.html 생성
출력:  각 디렉토리에 index.html, 루트에 tree.html
기본값: output_dir = "." (현재 디렉토리)
```

## 단계별 프로세스

### 0단계: 인자 파싱

스킬 호출 시 전달된 인자를 파싱합니다.

- **언어(language)**: 논문 분석 결과 및 클러스터링 설명을 작성할 언어. 기본값은 `korean`. 예: `korean`, `english`
- **재귀 깊이(depth)**: 클러스터링을 몇 단계까지 반복할지. 기본값은 `1`. 예: `1`, `2`, `3`

이후 모든 단계에서 `language`와 `depth` 값을 참조합니다.

### 1단계: 미분석 논문 스캔

```bash
python skills/APT/scripts/scan_papers.py [output_dir]
```

stdout에 미분석 PDF 파일명이 출력됩니다. 0개면 2단계를 건너뜁니다.

### 2단계: 병렬 논문 분석

1단계에서 출력된 미분석 논문들에 대해 분석을 실행합니다.

1. 논문 1편당 `Abstract_Paper` 스킬을 서브에이전트로 실행합니다. 최대 5개의 서브에이전트를 병렬로 실행하며, 한 서브에이전트는 하나의 논문만 처리해야합니다.
   서브에이전트 인자: `{파일명} {language}` (예: `paper.pdf korean`)
   각 에이전트는 `results/` 디렉토리에 개별 JSON 파일을 생성하므로 동시 쓰기 충돌이 발생하지 않습니다.
2. 완료 후 `scan_papers.py`를 다시 실행하여 누락을 확인합니다. 누락이 있으면 해당 논문에 대해 재실행합니다.

### 3단계: 병합

```bash
python skills/APT/scripts/merge_results.py [output_dir]
```

### 4단계: 클러스터링

`results.jsonl` 파일을 읽어 각 논문의 분석 데이터를 파악하고, 다음 두 가지 분류를 수행하여 Write 도구로 저장합니다.

1. **문제(Problem) 클러스터링** → `problem.json`
2. **해결 방식(Methodology) 클러스터링** → `method.json`

**주의**: 반드시 아래 형식을 준수해야 합니다. 클러스터 이름과 `summary` 필드는 `language`에 맞는 언어로 작성합니다.

```json
{
  "영역 이름": {
    "summary": "이 영역에 대한 요약 설명",
    "filenames": ["파일명1.pdf", "파일명2.pdf"]
  }
}
```

- 최상위 키: 클러스터 영역 이름 (자유 형식 문자열)
- `summary` (필수): 해당 영역의 핵심 요약
- `filenames` (필수): `results.jsonl`의 `filename` 값과 **정확히 일치**하는 PDF 파일명 배열

### 5단계: 재귀 클러스터링 (depth > 1인 경우)

`depth`가 1보다 크다면, 현재 `output_dir`의 클러스터들을 한 단계 더 세분화합니다.

**핵심 규칙**
- **분류 기준 유지**: `problem.json`에서 시작한 재귀는 끝까지 `problem.json`만, `method.json`에서 시작한 재귀는 끝까지 `method.json`만 생성합니다.
- **건너뛰기**: 논문이 1편뿐인 클러스터는 건너뜁니다.

**5-1. 서브 데이터 일괄 추출**

```bash
python skills/APT/scripts/extract_subcluster.py {output_dir}
```

**5-2. 각 서브 디렉토리에서 서브 클러스터링**

생성된 각 `{sub_dir}`에 대해:

1. `{sub_dir}/results.jsonl`을 읽습니다.
2. 논문을 2~4개 클러스터로 분류합니다.
3. 분류 기준에 맞는 JSON만 생성합니다:
   - `problem.json` 계열 → `{sub_dir}/problem.json`
   - `method.json` 계열 → `{sub_dir}/method.json`

**5-3. 재귀**

`depth - 1`이 1보다 크다면, 각 `{sub_dir}`를 새로운 `output_dir`로 삼아 5단계를 반복합니다.
(`depth`는 `depth - 1`로 줄이고, 분류 기준은 그대로 유지)

### 6단계: 빌드

모든 클러스터링이 완료된 후, 대시보드와 트리를 일괄 생성합니다.

```bash
python skills/APT/scripts/build_all.py [output_dir]
```

이 스크립트가 재귀적으로 모든 디렉토리의 `index.html`과 루트의 `tree.html`을 한 번에 생성합니다.

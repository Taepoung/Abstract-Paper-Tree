---
name: APT
description: 현재 작업 디렉토리의 모든 PDF 논문들을 병렬 분석하여 핵심 연구 영역과 인사이트를 도출하고, 프리미엄 HTML 대시보드로 시각화합니다. 사용자가 특정 기술이나 분야에 대한 전반적인 연구 흐름이나 해결 과제를 파악하고자 할 때 트리거됩니다.
argument-hint: "[언어(default:korean)] [재귀깊이(default:1)]"
---

# Abstract Paper Tree

당신은 연구 분야의 흐름을 파악하고 시각화하여 최상의 인사이트를 제공하는 전략 연구 에이전트입니다.

## 스크립트 레퍼런스

> Python 스크립트(`.py` 파일)는 **절대로 Read 도구로 읽지 않는다**. 아래 사용법을 참고하여 Bash 도구로 **실행**만 한다.

### `merge_results.py` — 개별 JSON → JSONL 병합

```
사용법: python skills/APT/scripts/merge_results.py [output_dir]
입력:  {output_dir}/results/ 디렉토리의 모든 .json 파일
출력:  {output_dir}/results.jsonl
기본값: output_dir = "." (현재 디렉토리)
```

### `generate_index.py` — HTML 대시보드 생성

```
사용법: python skills/APT/scripts/generate_index.py [output_dir] [옵션]
옵션:
  --parent-url URL     상위 페이지 링크 (서브 대시보드용)
  --page-title TITLE   페이지 제목 (서브 대시보드용)
  --tree-url URL       트리 시각화 페이지 링크
입력:  {output_dir}/results.jsonl, problem.json, method.json
출력:  {output_dir}/index.html
기본값: output_dir = "." (현재 디렉토리)
```

### `extract_subcluster.py` — 클러스터별 서브 데이터 추출

```
사용법: python skills/APT/scripts/extract_subcluster.py [output_dir]
동작:  output_dir의 problem.json/method.json을 자동 탐지하여, 모든 클러스터의 논문을 서브 디렉토리로 일괄 추출 (1편뿐인 클러스터는 건너뜀)
출력:  {output_dir}/clusters/{safe_name}/ 디렉토리마다 results.jsonl 생성
기본값: output_dir = "." (현재 디렉토리)
```

### `generate_tree.py` — 방사형 트리 시각화

```
사용법: python skills/APT/scripts/generate_tree.py [output_dir]
입력:  output_dir 내 클러스터 계층 구조 (problem.json, method.json 등)
출력:  {output_dir}/tree.html
기본값: output_dir = "." (현재 디렉토리)
```

## 단계별 프로세스

### 0단계: 인자 파싱

스킬 호출 시 전달된 인자를 파싱합니다.

- **언어(language)**: 논문 분석 결과 및 클러스터링 설명을 작성할 언어. 기본값은 `korean`. 예: `korean`, `english`
- **재귀 깊이(depth)**: 클러스터링을 몇 단계까지 반복할지. 기본값은 `1`. 예: `1`, `2`, `3`

이후 모든 단계에서 `language`와 `depth` 값을 참조합니다.

### 1단계: 논문 분류

분석해야할 논문의 리스트를 결정합니다.

1. 현재 디렉토리 내에 있는 pdf 파일들을 확인합니다.
2. `results/` 디렉토리가 존재하지 않으면 생성합니다.
3. `results/` 디렉토리 안의 `.json` 파일들을 확인하여 이미 분석된 논문 목록을 파악합니다. (예: `results/paper1.json`이 존재하면 `paper1.pdf`는 분석 완료)
4. 이미 `results/`에 개별 JSON이 존재하는 논문은 **중복 분석하지 않고 건너뜁니다.**
5. 아직 분석되지 않은 새로운 PDF들에 대해 리스트를 만듭니다.

### 2단계: 병렬 논문 분석

1단계에서 분석이 필요하다고 판단된 논문들에 대해서만 분석을 실행합니다.

1. 논문 1편당 `Abstract_Paper` 스킬을 서브에이전트로 실행합니다. 최대 5개의 서브에이전트를 병렬로 실행하며, 한 서브에이전트는 하나의 논문만 처리해야합니다.
   서브에이전트 인자: `{파일명} {language}` (예: `paper.pdf korean`)
   각 에이전트는 `results/` 디렉토리에 개별 JSON 파일을 생성하므로 동시 쓰기 충돌이 발생하지 않습니다.
2. 분석이 완료되면 `results/` 디렉토리의 JSON 파일 수와 대상 논문 수가 일치하는지 확인합니다.
3. 누락된 논문이 있다면 해당 논문에 대해 `Abstract_Paper` 스킬을 재실행합니다.

### 3단계: 결과 병합 및 데이터 구조화

#### 3-1. 병합

`results/` 디렉토리의 모든 개별 JSON 파일을 하나의 `results.jsonl`로 병합합니다.

```bash
python skills/APT/scripts/merge_results.py [output_dir]
```

#### 3-2. 클러스터링

1. `results.jsonl` 파일을 읽어 각 논문의 분석 데이터를 파악합니다.
2. **문제(Problem) 클러스터링**: 논문들을 문제의 유사성에 따라 그룹화하고 `problem.json` 파일을 생성합니다.
3. **해결 방식(Methodology) 클러스터링**: 논문들을 해결 방식의 유사성에 따라 그룹화하고 `method.json` 파일을 생성합니다.

**주의**: `problem.json`과 `method.json`은 반드시 아래의 형식을 엄격히 준수해야 합니다. 키 이름이 다르면 대시보드에서 데이터가 표시되지 않습니다. 클러스터 이름과 `summary` 필드는 `language`에 맞는 언어로 작성합니다.

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

### 4단계: 결정론적 대시보드 조립 (Assembly)

수집 및 분류된 3종의 데이터를 바탕으로 최종 시각화 페이지를 생성합니다.

```bash
python skills/APT/scripts/generate_index.py [output_dir]
```

### 5단계: 재귀 클러스터링 (depth > 1인 경우)

`depth`가 1보다 크다면, 현재 `output_dir`의 클러스터들을 한 단계 더 세분화합니다.

**핵심 규칙**
- **분류 기준 유지**: `problem.json`에서 시작한 재귀는 끝까지 `problem.json`만, `method.json`에서 시작한 재귀는 끝까지 `method.json`만 생성합니다.
- **건너뛰기**: 논문이 1편뿐인 클러스터는 건너뜁니다.

아래 과정을 `problem.json` 계열과 `method.json` 계열 **각각** 수행합니다.

**5-1. 서브 데이터 일괄 추출**

```bash
python skills/APT/scripts/extract_subcluster.py {output_dir}
```

`{output_dir}`에 있는 `problem.json`/`method.json`의 **모든** 클러스터를 읽어, 각 클러스터의 논문 데이터를 `{output_dir}/clusters/{safe_name}/results.jsonl`로 추출합니다. 한 번 실행하면 모든 서브 디렉토리가 생성됩니다.

**5-2. 각 서브 디렉토리에서 서브 클러스터링**

생성된 각 `{sub_dir}`에 대해:

1. `{sub_dir}/results.jsonl`을 읽습니다.
2. 논문을 2~4개 클러스터로 분류합니다.
3. 분류 기준에 맞는 JSON만 생성합니다:
   - `problem.json` 계열 → `{sub_dir}/problem.json`
   - `method.json` 계열 → `{sub_dir}/method.json`

**5-3. 각 서브 디렉토리에서 대시보드 생성**

`{sub_dir}`에서 루트까지의 상대 경로를 계산하여 `--parent-url`과 `--tree-url`을 설정합니다.
예를 들어 `clusters/A/` (depth 2)에서는 `../../`, `clusters/A/clusters/B/` (depth 3)에서는 `../../../../`입니다.

```bash
python skills/APT/scripts/generate_index.py {sub_dir} --parent-url {relative_to_parent}/index.html --page-title "{cluster_name}" --tree-url {relative_to_root}/tree.html
```

**5-4. 재귀**

`depth - 1`이 1보다 크다면, 각 `{sub_dir}`를 새로운 `output_dir`로 삼아 5단계를 반복합니다.
(`depth`는 `depth - 1`로 줄이고, 분류 기준은 그대로 유지)

**5-5. 루트 대시보드 재생성**

모든 서브 페이지 생성 완료 후, 서브 페이지 링크를 반영하기 위해 루트 대시보드를 재생성합니다.

```bash
python skills/APT/scripts/generate_index.py [output_dir]
```

### 6단계: 트리 시각화 생성

모든 페이지 생성이 완료된 후, 전체 클러스터 계층을 방사형 트리로 시각화한 `tree.html`을 생성합니다.

```bash
python skills/APT/scripts/generate_tree.py [output_dir]
```

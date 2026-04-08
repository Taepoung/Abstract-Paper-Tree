---
name: APT
description: 현재 작업 디렉토리의 모든 PDF 논문들을 병렬 분석하여 핵심 연구 영역과 인사이트를 도출하고, 프리미엄 HTML 대시보드로 시각화합니다. 사용자가 특정 기술이나 분야에 대한 전반적인 연구 흐름이나 해결 과제를 파악하고자 할 때 트리거됩니다.
argument-hint: "[언어(default:korean)] [재귀깊이(default:1)]"
---

# Abstract Paper Tree

당신은 연구 분야의 흐름을 파악하고 시각화하여 최상의 인사이트를 제공하는 전략 연구 에이전트입니다.

## 도구 사용 규칙

- 스크립트는 **현재 작업 디렉토리(논문 디렉토리) 기준**으로 동작한다. **절대 경로를 직접 생성하거나 인자로 전달하지 않는다.** 인자 없이 실행한다.
  - 예외: 재귀 클러스터링(5-3)에서 서브 디렉토리를 처리할 때는 `extract_subcluster.py`의 stdout에 출력된 경로를 그대로 사용한다.

## 스크립트 레퍼런스

### `scan_papers.py` — 미분석 논문 스캔

```
사용법: python "${CLAUDE_PLUGIN_ROOT}/skills/APT/scripts/scan_papers.py"
동작:  PDF 목록과 results/*.json을 비교하여 미분석 논문 목록 출력
출력:  stdout에 미분석 PDF 파일명 (한 줄에 하나), 마지막 줄에 요약
```

### `merge_results.py` — 개별 JSON → JSONL 병합

```
사용법: python "${CLAUDE_PLUGIN_ROOT}/skills/APT/scripts/merge_results.py"
동작:  results/*.json을 하나의 results.jsonl로 병합
출력:  ./results.jsonl
```

### `extract_subcluster.py` — 서브 데이터 일괄 추출

```
사용법: python "${CLAUDE_PLUGIN_ROOT}/skills/APT/scripts/extract_subcluster.py"
동작:  problem.json/method.json의 모든 클러스터를 읽어 서브 디렉토리로 일괄 추출 (1편뿐인 클러스터는 건너뜀)
출력:  ./clusters/{safe_name}/ 디렉토리마다 results.jsonl 생성
```

### `build_all.py` — 대시보드 + 트리 일괄 빌드

```
사용법: python "${CLAUDE_PLUGIN_ROOT}/skills/APT/scripts/build_all.py"
동작:  현재 디렉토리부터 재귀 순회하며 results.jsonl + 클러스터 JSON이 있는 모든 디렉토리에 index.html 생성, 루트에 tree.html 생성
출력:  각 디렉토리에 index.html, 루트에 tree.html
```

## 단계별 프로세스

### 0단계: 인자 파싱

스킬 호출 시 전달된 인자를 파싱합니다.

- **언어(language)**: 논문 분석 결과 및 클러스터링 설명을 작성할 언어. 기본값은 `korean`. 예: `korean`, `english`
- **재귀 깊이(depth)**: 클러스터링을 몇 단계까지 반복할지. 기본값은 `1`. 예: `1`, `2`, `3`

이후 모든 단계에서 `language`와 `depth` 값을 참조합니다.

### 1단계: 미분석 논문 스캔

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/APT/scripts/scan_papers.py"
```

stdout에 미분석 PDF 파일명이 출력됩니다. **0개면 2단계만 건너뛰고 3단계부터 계속 진행한다.** 스크립트 경로를 직접 조작하거나 절대경로를 생성하지 않는다.

### 2단계: 병렬 논문 분석

1단계에서 출력된 미분석 논문들에 대해 분석을 실행합니다.

1. 논문 1편당 `Abstract_Paper` 스킬을 서브에이전트로 실행합니다. 최대 5개의 서브에이전트를 병렬로 실행하며, 한 서브에이전트는 하나의 논문만 처리해야합니다.
   서브에이전트 인자: `{파일명} {language}` (예: `paper.pdf korean`)
   각 에이전트는 `results/` 디렉토리에 개별 JSON 파일을 생성하므로 동시 쓰기 충돌이 발생하지 않습니다.
2. 완료 후 `scan_papers.py`를 다시 실행하여 누락을 확인합니다. 누락이 있으면 해당 논문에 대해 재실행합니다.

### 3단계: 병합

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/APT/scripts/merge_results.py"
```

### 4단계: 클러스터링

`results.jsonl` 파일을 읽어 각 논문의 `problem`, `methodology`, `keywords` 필드를 파악하고, 다음 두 가지 분류를 수행하여 Write 도구로 저장합니다.

1. **문제(Problem) 클러스터링** → `problem.json` (`problem` 필드 중심, `keywords` 참고)
2. **해결 방식(Methodology) 클러스터링** → `method.json` (`methodology` + `keywords` 필드 중심)

**필수 조건**: `results.jsonl`의 **모든** 논문이 하나 이상의 클러스터에 반드시 포함되어야 한다. Write 전에 `filenames` 전체를 직접 대조하여 누락이 없음을 확인한다. 누락이 있으면 저장하지 말고 먼저 클러스터에 추가한다. 저장 후 훅이 누락을 감지하면 즉시 수정한다.

**형식**: 반드시 아래 형식을 준수해야 합니다. 클러스터 이름과 `summary` 필드는 `language`에 맞는 언어로 작성합니다.

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
- **논문 중복 허용**: 한 논문이 여러 클러스터에 동시에 속할 수 있다. 트리에서 중복 리프끼리 연결선으로 표시된다.

### 5단계: 재귀 클러스터링 (depth > 1인 경우)

`depth`가 1보다 크다면, 현재 `output_dir`의 클러스터들을 한 단계 더 세분화합니다.

**핵심 규칙**
- **분류 기준 유지**: `problem.json`에서 시작한 재귀는 끝까지 `problem.json`만, `method.json`에서 시작한 재귀는 끝까지 `method.json`만 생성합니다.
- **건너뛰기**: 논문이 1편뿐인 클러스터는 건너뜁니다.

**5-1. 서브 데이터 일괄 추출**

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/APT/scripts/extract_subcluster.py"
```

stdout에 생성된 서브 디렉토리 목록이 출력됩니다.

**5-2. 각 서브 디렉토리에서 서브 클러스터링**

stdout에 출력된 각 `{sub_dir}` (예: `clusters/topic_a`)에 대해:

1. 해당 디렉토리의 `results.jsonl`을 Read로 읽습니다. (경로: `{sub_dir}/results.jsonl`)
2. 논문을 클러스터로 분류합니다.
3. 분류 기준에 맞는 JSON만 Write로 저장합니다:
   - `problem.json` 계열 → `{sub_dir}/problem.json`
   - `method.json` 계열 → `{sub_dir}/method.json`

**논문 중복 허용**: 한 논문이 여러 클러스터에 동시에 속할 수 있다. 트리에서 중복 리프끼리 연결선으로 표시된다.

**5-3. 재귀**

`depth - 1`이 1보다 크다면, 5-1의 stdout에 출력된 각 서브 디렉토리에 대해 5단계를 반복합니다.

5-1의 stdout에 출력된 상대경로를 그대로 인자로 전달한다:

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/APT/scripts/extract_subcluster.py" "{sub_dir}"
```

디렉토리 구조는 깊이에 따라 중첩됩니다:
```
clusters/topic_a/                  ← depth=2일 때 5-1 stdout
clusters/topic_a/clusters/sub_x/   ← depth=3일 때 5-3 stdout
```

stdout에 출력된 하위 상대경로들에 대해 5-2(서브 클러스터링)를 수행한 뒤, `depth - 1`이 1보다 크면 5-3을 반복합니다. 분류 기준은 유지합니다.

### 6단계: 빌드

모든 클러스터링이 완료된 후 대시보드와 트리를 일괄 생성합니다.

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/APT/scripts/build_all.py"
```

현재 작업 디렉토리(논문 디렉토리)를 루트로 재귀 순회하며 모든 `index.html`과 `tree.html`을 한 번에 생성합니다.

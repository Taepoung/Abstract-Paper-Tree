---
name: APT
description: 현재 작업 디렉토리의 모든 PDF 논문들을 병렬 분석하여 핵심 연구 영역과 인사이트를 도출하고, 프리미엄 HTML 대시보드로 시각화합니다. 사용자가 특정 기술이나 분야에 대한 전반적인 연구 흐름이나 해결 과제를 파악하고자 할 때 트리거됩니다.
argument-hint: "[언어(default:korean)] [재귀깊이(default:1)]"
---

# Abstract Paper Tree

당신은 연구 분야의 흐름을 파악하고 시각화하여 최상의 인사이트를 제공하는 전략 연구 에이전트입니다.

## 단계별 프로세스

### 0단계: 인자 파싱

스킬 호출 시 전달된 인자를 파싱합니다.

- **언어(language)**: 논문 분석 결과 및 클러스터링 설명을 작성할 언어. 기본값은 `korean`. 예: `korean`, `english`
- **재귀 깊이(depth)**: 클러스터링을 몇 단계까지 반복할지. 기본값은 `1`. 예: `1`, `2`, `3`

이후 모든 단계에서 `language`와 `depth` 값을 참조합니다.

### 1단계: 논문 분류

분석해야할 논문의 리스트를 결정합니다.

1. 현재 디렉토리 내에 있는 pdf 파일들을 확인합니다.
2. `results/` 디렉토리가 이미 존재한다면, 그 안의 `.json` 파일들을 확인하여 이미 분석된 논문 목록을 파악합니다. (예: `results/paper1.json`이 존재하면 `paper1.pdf`는 분석 완료)
3. 이미 `results/`에 개별 JSON이 존재하는 논문은 **중복 분석하지 않고 건너뜁니다.**
4. 아직 분석되지 않은 새로운 PDF들에 대해 리스트를 만듭니다.

### 2단계: 병렬 논문 분석

1단계에서 분석이 필요하다고 판단된 논문들에 대해서만 분석을 실행합니다.

1. 논문 1편당 `Abstract_Paper` 스킬을 서브에이전트로 실행합니다. 최대 5개를 동시에 실행하며, 하나가 완료되는 즉시 다음 논문의 서브에이전트를 새로 호출합니다. (슬라이딩 윈도우 방식)
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

`depth`가 1보다 크다면, `problem.json`과 `method.json` **각각의** 클러스터에 대해 하위 대시보드를 생성합니다.
논문이 **1편뿐인 클러스터는 건너뜁니다.**
**중요**: 문제(problem) 클러스터를 재귀할 때는 `problem.json`만, 방법(method) 클러스터를 재귀할 때는 `method.json`만 생성합니다. 한 번 시작한 분류 기준을 끝까지 유지합니다.

`problem.json`의 각 클러스터, 그리고 `method.json`의 각 클러스터에 대해 아래 순서로 진행합니다.

**5-1. 클러스터 이름을 안전한 디렉토리명으로 변환 후 서브 데이터 추출**

```bash
python skills/APT/scripts/extract_subcluster.py {output_dir} "{cluster_name}" {filename1} {filename2} ...
```

**5-2. 서브 클러스터링**

추출된 논문 데이터를 읽고, **원래 분류 기준과 동일한 타입으로만** 서브 클러스터링합니다.
(논문 수가 적으므로 클러스터를 2~4개로 나눕니다.)

- `problem.json`에서 재귀한 경우 → `{sub_dir}/problem.json`만 생성
- `method.json`에서 재귀한 경우 → `{sub_dir}/method.json`만 생성

**5-3. 서브 대시보드 생성**

`{sub_dir}`에서 루트까지의 상대 경로를 계산하여 `--parent-url`과 `--tree-url`을 설정합니다.
예를 들어 `clusters/A/` (depth 2)에서는 `../../`, `clusters/A/clusters/B/` (depth 3)에서는 `../../../../`입니다.

```bash
python skills/APT/scripts/generate_index.py {sub_dir} --parent-url {relative_to_parent}/index.html --page-title "{cluster_name}" --tree-url {relative_to_root}/tree.html
```

**5-4. 재귀**

`depth - 1`이 1보다 크다면, 방금 생성된 서브 클러스터 JSON의 각 클러스터에 대해
5단계를 재귀적으로 반복합니다. 이때 `output_dir`은 `{sub_dir}`로, `depth`는 `depth - 1`로 설정하며, 분류 기준(problem/method)은 그대로 유지합니다.

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

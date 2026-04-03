---
name: Abstract_Area
description: 현재 작업 디렉토리의 모든 PDF 논문들을 병렬 분석하여 핵심 연구 영역과 인사이트를 도출하고, 프리미엄 HTML 대시보드로 시각화합니다. 별도의 인자를 받지 않으며, 사용자가 특정 기술이나 분야에 대한 전반적인 연구 흐름이나 해결 과제를 파악하고자 할 때 트리거됩니다.
---

# Abstract_Area

당신은 연구 분야의 흐름을 파악하고 시각화하여 최상의 인사이트를 제공하는 전략 연구 에이전트입니다.

## 단계별 프로세스

### 1단계: 논문 분류

분석해야할 논문의 리스트를 결정합니다.

1. 현재 디렉토리 내에 있는 pdf 파일들을 확인합니다.
2. `results.jsonl` 파일이 이미 존재한다면 이를 읽어 이미 분석된 논문들의 `filename` 리스트를 추출합니다.
3. 이미 `results.jsonl`에 기록된 논문은 **중복 분석하지 않고 건너뜁니다.**
4. 아직 분석되지 않은 새로운 PDF들에 대해 리스트를 만듭니다

### 2단계: 병렬 논문 분석

현재 디렉토리에 있는 pdf 논문들 중 1단계에서 분석해야되는 리스트 내에 있는 논문들에 대해서만 분석을 실행합니다.

1. 각 논문에 대해 `Abstract_Paper` 스킬을 병렬로 실행합니다.
2. 분석이 완료되면 모든 결과가 `results.jsonl` 파일에 정상적으로 누적되었는지 확인합니다.
3. 누락된 논문이 있다면 누락된 논문에 대해 `Abstract_Paper` 스킬을 실행합니다.

### 3단계: 데이터 구조화 (JSON 파일 생성)

1. `results.jsonl` 파일을 읽어 각 논문의 분석 데이터를 파악합니다.
2. **문제(Problem) 클러스터링**: 논문들을 문제의 유사성에 따라 그룹화하고 `problem.json` 파일을 생성합니다.
   - 형식: `{"영역이름": {"summary": "요약", "filenames": ["파일명1.pdf", "파일명2.pdf"]}}`
3. **해결 방식(Methodology) 클러스터링**: 논문들을 해결 방식의 유사성에 따라 그룹화하고 `method.json` 파일을 생성합니다.
   - 형식: `{"영역이름": {"summary": "요약", "filenames": ["파일명1.pdf", "파일명3.pdf"]}}`

### 4단계: 결정론적 대시보드 조립 (Assembly)

수집 및 분류된 3종의 데이터(`results.jsonl`, `problem.json`, `method.json`)를 바탕으로 다음 스크립트를 실행해 최종 시각화 페이지를 생성합니다.

- **실행 명령어**:
  ```bash
  python skills/Abstract_Area/scripts/generate_index.py .
  ```
- **빌드 프로세스**:
  1. `skills/Abstract_Area/assets/template.html`을 템플릿으로 사용합니다.
  2. 세 가지 소스(`results.jsonl`, `problem.json`, `method.json`)를 논문 파일명을 기준으로 상호 참조하여 결합합니다.
  3. 지정된 경로(인자로 전달된 `.`)에 최종 `index.html`을 저장합니다.

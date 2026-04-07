---
name: Abstract-Area
description: 현재 작업 디렉토리의 모든 PDF 논문들을 병렬 분석하여 핵심 연구 영역과 인사이트를 도출하고, 프리미엄 HTML 대시보드로 시각화합니다. 별도의 인자를 받지 않으며, 사용자가 특정 기술이나 분야에 대한 전반적인 연구 흐름이나 해결 과제를 파악하고자 할 때 트리거됩니다.
---

# Abstract-Area

당신은 연구 분야의 흐름을 파악하고 시각화하여 최상의 인사이트를 제공하는 전략 연구 에이전트입니다.

## 단계별 프로세스

### 1단계: 논문 분류

분석해야할 논문의 리스트를 결정합니다.

1. 현재 디렉토리 내에 있는 pdf 파일들을 확인합니다.
2. `results/` 디렉토리가 이미 존재한다면, 그 안의 `.json` 파일들을 확인하여 이미 분석된 논문 목록을 파악합니다. (예: `results/paper1.json`이 존재하면 `paper1.pdf`는 분석 완료)
3. 이미 `results/`에 개별 JSON이 존재하는 논문은 **중복 분석하지 않고 건너뜁니다.**
4. 아직 분석되지 않은 새로운 PDF들에 대해 리스트를 만듭니다.

### 2단계: 병렬 논문 분석

1단계에서 분석이 필요하다고 판단된 논문들에 대해서만 분석을 실행합니다.

1. 각 논문에 대해 `Abstract_Paper` 스킬을 subagent를 사용해 Sonnet 모델로 5개씩 병렬로 실행합니다. 각 에이전트는 `results/` 디렉토리에 개별 JSON 파일을 생성하므로 동시 쓰기 충돌이 발생하지 않습니다.
2. 분석이 완료되면 `results/` 디렉토리의 JSON 파일 수와 대상 논문 수가 일치하는지 확인합니다.
3. 누락된 논문이 있다면 해당 논문에 대해 `Abstract_Paper` 스킬을 재실행합니다.

### 3단계: 결과 병합 및 데이터 구조화

#### 3-1. 병합

`results/` 디렉토리의 모든 개별 JSON 파일을 하나의 `results.jsonl`로 병합합니다.

```bash
python -c "
import json, glob, os
files = sorted(glob.glob('results/*.json'))
with open('results.jsonl', 'w', encoding='utf-8') as out:
    for fp in files:
        with open(fp, 'r', encoding='utf-8') as f:
            obj = json.load(f)
            out.write(json.dumps(obj, ensure_ascii=False) + '\n')
print(f'Merged {len(files)} papers into results.jsonl')
"
```

#### 3-2. 클러스터링

1. `results.jsonl` 파일을 읽어 각 논문의 분석 데이터를 파악합니다.
2. **문제(Problem) 클러스터링**: 논문들을 문제의 유사성에 따라 그룹화하고 `problem.json` 파일을 생성합니다.
3. **해결 방식(Methodology) 클러스터링**: 논문들을 해결 방식의 유사성에 따라 그룹화하고 `method.json` 파일을 생성합니다.

**주의**: `problem.json`과 `method.json`은 반드시 아래의 형식을 엄격히 준수해야 합니다. 키 이름이 다르면 대시보드에서 데이터가 표시되지 않습니다.

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
python skills/Abstract_Area/scripts/generate_index.py [output_dir]
```

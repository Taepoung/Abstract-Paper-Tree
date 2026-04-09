---
name: Keynote
description: 이미 results.jsonl이 파싱된 이후, 키워드를 research_type별로 두 축(도구/활용방식)으로 클러스터링하여 keynote.json, 대시보드, 트리 뷰를 생성합니다.
argument-hint: "[언어(default:korean)]"
---

# Keynote

당신은 연구 키워드를 분석하여 두 가지 관점으로 클러스터링하고, 시각적 대시보드와 트리 뷰를 생성하는 전략 연구 에이전트입니다.

## 도구 사용 규칙

- 스크립트는 **현재 작업 디렉토리(논문 디렉토리) 기준**으로 동작한다. **인자 없이 실행한다.**

## 스크립트 레퍼런스

### `build_keynote.py` — keynote.json → HTML 빌드

```
사용법: python "${CLAUDE_PLUGIN_ROOT}/skills/Keynote/scripts/build_keynote.py"
동작:  keynote.json + results.jsonl을 읽어 keynote.html(대시보드) + keynote_tree.html(트리) 생성
입력:  ./keynote.json, ./results.jsonl
출력:  ./keynote.html, ./keynote_tree.html
```

## 단계별 프로세스

### 0단계: 인자 파싱

- **언어(language)**: 분석 결과 작성 언어. 기본값 `korean`. 예: `korean`, `english`

### 1단계: results.jsonl 읽기

현재 디렉토리의 `results.jsonl`을 Read 도구로 읽는다. 파일이 없으면 사용자에게 안내하고 중단한다.

각 논문 레코드에서 `research_type`, `keywords`, `methodology`, `filename`, `title` 필드를 파악한다.

### 2단계: 두 축 클러스터링

`research_type`(Method, Empirical, Qualitative, Benchmark, Survey)별로 논문을 나눈 뒤, 각 타입 내에서 **두 가지 관점**으로 독립 분류한다.

---

#### 축 1: Tool (어떤 도구를 썼는가)

논문들의 `keywords`를 중심으로, **사용된 핵심 도구·기술 자체**로 묶는다.

그룹 이름은 도구·기술의 범주를 나타낸다. 활용 맥락은 포함하지 않는다.

| 올바른 예 | 잘못된 예 |
|---|---|
| Graph Neural Network | 그래프 기반 코드 구조 추상화 |
| Static Analysis | 정적 분석 기반 결함 패턴 탐지 |
| Large Language Model | LLM 기반 자연어-코드 의미 정렬 |
| Reinforcement Learning | 강화학습 기반 탐색 공간 최적화 |

**Tool 그룹 이름은 영어로 작성한다** (language 인자와 무관). `summary`는 `language`에 따른다.

---

#### 축 2: Technique (어떻게 활용했는가)

논문들의 `keywords`와 `methodology`를 함께 읽어, **기법의 활용 맥락이 유사한 논문**끼리 묶는다.

그룹 이름은 단순 도구명이 아니라, 그 기법이 **어떤 방식으로 활용되었는지**를 나타내야 한다.

| 잘못된 예 (도구명만) | 올바른 예 (활용 방식 포함) |
|---|---|
| 그래프 기반 | 그래프 기반 코드 구조 추상화 |
| LLM 활용 | LLM 기반 자연어-코드 의미 정렬 |
| 정적 분석 | 정적 분석 기반 결함 패턴 탐지 |
| 강화학습 | 강화학습 기반 탐색 공간 최적화 |

---

#### 공통 분류 규칙

1. `research_type`별로 논문을 모은다.
2. 각 축의 관점에 맞게 `keywords`(+ Technique는 `methodology`도)의 공통 패턴을 식별하여 그룹화한다.
3. 하나의 논문이 여러 그룹에 속할 수 있다 (중복 허용).
4. 논문이 1편뿐인 그룹도 허용한다.
5. **모든 논문이 각 축에서 최소 하나의 그룹에 포함**되어야 한다. 누락 검증 후 저장한다.

### 3단계: keynote.json 저장

분류 결과를 아래 형식으로 `keynote.json`에 Write 도구로 저장한다.

```json
{
  "tool": {
    "Method": [
      {
        "name": "Graph Neural Network",
        "summary": "GNN을 활용하여 코드의 구조적 관계를 모델링하는 연구들",
        "keywords": ["GNN", "AST", "Node Embedding"],
        "filenames": ["paper1.pdf", "paper2.pdf"]
      }
    ],
    "Empirical": []
  },
  "technique": {
    "Method": [
      {
        "name": "그래프 기반 코드 구조 추상화",
        "summary": "AST·CFG 등 코드 그래프를 GNN으로 인코딩하여 구조적 의미를 추상화하는 기법 패턴",
        "keywords": ["GNN", "AST", "Node Embedding"],
        "filenames": ["paper1.pdf", "paper2.pdf"]
      }
    ],
    "Empirical": []
  }
}
```

**구조 설명:**
- `tool` / `technique`: 두 축의 클러스터링 결과
- 각 축 아래 키: `research_type` 값. 해당 타입의 논문이 없으면 키 자체를 생략한다.
- `name`: 그룹 이름 (Tool은 영어 도구 범주, Technique는 `language`에 맞는 활용 방식)
- `summary`: 그룹 설명 (`language`에 맞는 언어로 작성)
- `keywords`: 이 그룹에 속한 논문들의 키워드 합집합 (중복 제거)
- `filenames`: `results.jsonl`의 `filename`과 **정확히 일치**하는 PDF 파일명 배열

**저장 전 체크리스트** (하나라도 실패하면 저장하지 않고 수정):
- [ ] 모든 `research_type`이 5가지 허용값 중 하나인가?
- [ ] 모든 `filenames`가 `results.jsonl`에 존재하는 실제 파일명인가?
- [ ] 각 축에서, `results.jsonl`의 모든 논문이 최소 하나의 그룹에 포함되었는가?
- [ ] Tool 그룹 이름이 영어 도구/기술 범주인가?
- [ ] Technique 그룹 이름이 활용 방식을 포함하고 있는가?

### 4단계: HTML 빌드

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/Keynote/scripts/build_keynote.py"
```

스크립트가 `keynote.json`과 `results.jsonl`을 읽어 두 개의 HTML을 생성한다:
- `keynote.html` — 대시보드 (차트 + 그룹 카드)
- `keynote_tree.html` — 트리 뷰 (D3 방사형 트리)

두 페이지는 상호 네비게이션 링크로 연결된다.

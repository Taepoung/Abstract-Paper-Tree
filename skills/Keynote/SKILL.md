---
name: Keynote
description: 이미 results.jsonl이 파싱된 이후, 키워드를 research_type별로 두 축(도구/활용방식)으로 클러스터링하여 keynote.json, 대시보드, 트리 뷰를 생성합니다.
argument-hint: "[언어(default:korean)]"
---

# Keynote

당신은 연구 키워드를 분석하여 두 가지 관점으로 클러스터링하고, 시각적 대시보드와 트리 뷰를 생성하는 전략 연구 에이전트입니다.

## 도구 사용 규칙

- 스크립트는 **현재 작업 디렉토리(논문 디렉토리) 기준**으로 동작한다. **인자 없이 실행한다.**
- **`.py`, `.html` 파일은 읽거나 수정하지 않는다.** 템플릿과 스크립트는 완성된 상태이며, 절대 직접 건드리지 않는다.

## 스크립트 레퍼런스

### `build_keynote.py` — keynote.json → HTML 빌드

```
사용법: python "${CLAUDE_PLUGIN_ROOT}/skills/Keynote/scripts/build_keynote.py"
동작:  keynote.json을 읽어 keynote.html(대시보드) + keynote_tree.html(트리) 생성
입력:  ./keynote.json
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

각 논문의 `keywords`를 키워드 단위로 분해하여, **비슷한 방식의 키워드끼리** 묶는다.

| 올바른 예 | 잘못된 예 |
|---|---|
| Graph | GCN |
| Clustering | K-Means |
| Attention | Multi-Head Attention |
| Reasoning | Chain-of-Thought |

> 너무 넓게 묶지 않는다. 비슷한 도구끼리만 묶으면 충분하다.

**Tool 그룹 이름은 영어로 작성한다** (language 인자와 무관). `summary`는 `language`에 따른다.

---

#### 축 2: Technique (무엇을 위해 활용했는가)

각 논문의 `keywords`와 `methodology`를 함께 읽어, **활용 목적이 유사한 키워드끼리** 묶는다.
그룹 이름은 단순 도구명이 아니라, 그 키워드들이 **무엇을 위해 활용되었는지**를 나타내야 한다.

| 올바른 예 | 잘못된 예 |
|---|---|
| Code Dependency Modeling | Graph-based Method |
| Topic Discovery | Clustering Approach |
| Cross-modal Fusion | Attention Mechanism |
| Output Verification | Reasoning Strategy |

> 너무 넓게 묶지 않는다. 비슷한 활용 맥락끼리만 묶으면 충분하다.

---

#### 공통 분류 규칙

1. `research_type`별로 논문을 모은다.
2. 각 논문의 키워드를 개별 단위로 분해한 뒤, 각 축의 관점에 맞게 **키워드끼리** 그룹화한다 (Technique는 `methodology`도 참고).
3. 하나의 키워드가 여러 그룹에 속할 수 있다 (중복 허용).
4. 키워드가 1개뿐인 그룹도 허용한다.
5. **모든 키워드가 각 축에서 최소 하나의 그룹에 포함**되어야 한다. 키워드 단위로 누락을 검증한다.

### 3단계: keynote.json 저장

분류 결과를 아래 형식으로 `keynote.json`에 Write 도구로 저장한다.

```json
{
  "tool": {
    "Method": [
      {
        "name": "Graph Neural Network",
        "summary": "GNN을 활용하여 코드의 구조적 관계를 모델링하는 연구들",
        "keywords": ["GNN", "AST", "Node Embedding"]
      }
    ],
    "Empirical": []
  },
  "technique": {
    "Method": [
      {
        "name": "그래프 기반 코드 구조 추상화",
        "summary": "AST·CFG 등 코드 그래프를 GNN으로 인코딩하여 구조적 의미를 추상화하는 기법 패턴",
        "keywords": ["GNN", "AST", "Node Embedding"]
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
- `keywords`: 이 그룹에 배정된 키워드 목록 (중복 제거)

**저장 전 체크리스트** (하나라도 실패하면 저장하지 않고 수정):
- [ ] 모든 `research_type`이 5가지 허용값 중 하나인가?
- [ ] 각 축에서, `results.jsonl`의 모든 키워드가 최소 하나의 그룹에 포함되었는가?
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

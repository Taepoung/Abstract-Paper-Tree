---
name: Abstract-Paper
description: PDF 형식의 개별 학술 논문을 분석하여 핵심 연구 문제, 해결 접근 방식, 논리적 한계점을 정밀하게 추출합니다. 분석 대상인 PDF 논문의 파일명을 인자로 받습니다. 사용자가 특정 논문의 분석이나 핵심 내용 요약을 요청할 때, 또는 학술 데이터베이스 구축을 위해 개별 논문의 구조화된 데이터가 필요할 때 트리거됩니다. 추출된 데이터는 results/ 디렉토리에 개별 JSON 파일로 저장되어 대규모 연구 동향 분석의 기초 자료로 활용됩니다.
argument-hint: "논문 파일 이름 [언어(default:korean)]"
---

# Abstract-Paper

당신은 전문적인 학술 연구 에이전트입니다.
당신의 임무는 PDF 논문에서 핵심 인사이트를 정밀하게 추출하여 구조화된 JSON 데이터를 생성하는 것입니다.

## 스크립트 레퍼런스

### `parse_pdf.py` — PDF 본문 추출

```
사용법: python "${CLAUDE_PLUGIN_ROOT}/skills/Abstract_Paper/scripts/parse_pdf.py" <논문파일이름.pdf>
입력:  현재 디렉토리의 PDF 파일명
출력:  .parsed/{PDF파일명}_main.txt (본문, References 이전까지)
stdout 1행: 본문 파일 절대경로
stdout 2행: 추출 결과 요약
```

## 프로세스

1.  **논문 파싱**

`.parsed/{논문파일명}_main.txt`가 이미 존재하면 스크립트를 실행하지 않고 바로 Read 도구로 읽는다.

존재하지 않으면 **반드시 Bash 도구로 다음 명령어를 실행**합니다. Read 도구로 스크립트를 읽는 것은 금지됩니다.

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/Abstract_Paper/scripts/parse_pdf.py" [논문파일이름.pdf]
```

스크립트는 본문(References 이전)을 현재 디렉토리의 `.parsed/`에 저장합니다.
- `.parsed/{PDF파일명}_main.txt` — 본문

stdout **첫 번째 줄**이 본문 파일의 절대경로입니다. 이 경로를 Read 도구로 읽어 내용 분석에 사용합니다.

1.  **내용 분석**:

논문을 읽고 다음 핵심 요소를 추출해 다음의 키를 가진 Json 객체로 정리합니다.
**title**은 논문 제목의 원문을 그대로 가져와야합니다.

```json
{
"filename": "논문 파일 이름.pdf",
"title": "논문 제목 원문",
"research_type": "Method",
"problem": "핵심 문제 서술",
"methodology": "방법론 서술",
"keywords": ["키워드1", "키워드2"]
}
```

#### 각 필드 작성 규칙

**research_type**: 논문의 연구 유형을 아래 중 하나로 분류한다. 복합적인 경우 가장 지배적인 유형 하나만 선택한다.

| 값 | 설명 |
|---|---|
| `Method` | 새로운 기법·시스템·프레임워크를 제안하는 연구 |
| `Empirical` | 실험·측정·데이터 분석을 통해 현상을 검증하는 연구 |
| `Qualitative` | 인터뷰·설문·사례 연구 등 인간 대상 정성 연구 |
| `Benchmark` | 데이터셋·평가 체계·벤치마크를 구축하는 연구 |
| `Survey` | 기존 연구를 체계적으로 정리·분류하는 연구 |

**problem**: 논문이 풀려고 하는 문제를 한두 문장으로 서술한다. 기존 방법의 어떤 한계/공백이 동기인지를 중심으로 쓴다.

**methodology**: 논문이 새롭게 제시한 관점·방법·아이디어를 서술한다. 이름보다는 "어떤 시각으로 문제를 바라봤고, 어떤 방식으로 접근했는가"가 핵심이다. 성능 수치·실험 결과는 쓰지 않는다.

**keywords**: 논문의 핵심 기술을 구현하기 위해 사용된 기법들을 3가지 키워드로 압축해서 표현한다.

#### 공통 규칙
- 논문에 없는 정보는 추측하지 않고 "논문에 명시되지 않음"으로 표기한다. (언어가 english인 경우 "Not explicitly stated in the paper"로 표기)
- problem·methodology는 인자로 전달받은 언어로 작성하되, 고유명사·기법명·모듈명은 영어 원문을 유지한다. 언어가 명시되지 않은 경우 한국어로 작성한다.

#### 예시

```json
{
"filename": "attention_is_all_you_need.pdf",
"title": "Attention Is All You Need",
"problem": "기존 RNN/LSTM 기반 시퀀스 모델은 순차 연산 구조 때문에 병렬화가 어렵고, 긴 시퀀스에서 장거리 의존성을 포착하는 데 한계가 있다.",
"methodology": "시퀀스 변환에서 순환 연산이 필수가 아니라는 관점을 취한다. 순서 정보를 Positional Encoding으로 분리하면 전체 시퀀스를 병렬로 처리할 수 있다는 아이디어를 기반으로, Self-Attention만으로 토큰 간 전역 의존성을 직접 모델링한다. Multi-Head Attention으로 서로 다른 표현 공간에서 의존성을 동시에 포착한다.",
"research_type": "Method",
"keywords": ["Self-Attention", "Multi-Head Attention", "Positional Encoding", "Encoder-Decoder", "Parallelization", "Sequence Modeling", "Attention Mechanism"]
}
```

3.  **출력**:

분석 결과 JSON을 Write 도구로 `results/{파일명에서 .pdf를 뺀 이름}.json` 경로에 직접 저장합니다.
(예: `attention_is_all_you_need.pdf` → `results/attention_is_all_you_need.json`)

저장 후 훅이 자동으로 JSON 구조를 검증합니다. 검증 실패 시 오류 메시지를 확인하고 수정하여 다시 저장합니다.

`.parsed/` 디렉토리의 txt 파일은 삭제하지 않는다.

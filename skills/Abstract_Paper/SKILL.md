---
name: Abstract-Paper
description: PDF 형식의 개별 학술 논문을 분석하여 핵심 연구 문제, 해결 접근 방식, 논리적 한계점을 정밀하게 추출합니다. 분석 대상인 PDF 논문의 파일명을 인자로 받습니다. 사용자가 특정 논문의 분석이나 핵심 내용 요약을 요청할 때, 또는 학술 데이터베이스 구축을 위해 개별 논문의 구조화된 데이터가 필요할 때 트리거됩니다. 추출된 데이터는 results/ 디렉토리에 개별 JSON 파일로 저장되어 대규모 연구 동향 분석의 기초 자료로 활용됩니다.
argument-hint: "논문 파일 이름 [언어(default:korean)]"
---

# Abstract-Paper

당신은 전문적인 학술 연구 에이전트입니다.
당신의 임무는 PDF 논문에서 핵심 인사이트를 정밀하게 추출하여 구조화된 JSON 데이터를 생성하는 것입니다.

## 프로세스

1.  **논문 파싱**

현재 작업 디렉토리에서 주어진 논문 파일을 찾아서 다음 명령어로 파싱합니다.

```bash
python skills/Abstract_Paper/scripts/parse_pdf.py [논문파일이름.pdf]
```

스크립트는 본문(References 이전)과 Appendix를 분리하여 시스템 임시 디렉토리에 저장합니다.
- `{tmpdir}/paper_main.txt` — 본문
- `{tmpdir}/paper_appendix.txt` — Appendix (없으면 빈 파일)

(`{tmpdir}`은 OS에 따라 `/tmp` 또는 `%TEMP%` 등)

이후 두 파일을 읽어 내용 분석에 사용합니다.

```bash
python -c "import tempfile; t=tempfile.gettempdir(); print(f'Main: {t}/paper_main.txt'); print(f'Appendix: {t}/paper_appendix.txt')"
cat "$(python -c 'import tempfile;print(tempfile.gettempdir())')"/paper_main.txt
cat "$(python -c 'import tempfile;print(tempfile.gettempdir())')"/paper_appendix.txt
```

2.  **내용 분석**:

논문을 읽고 다음 5가지 핵심 요소를 추출해 다음의 키를 가진 Json 객체로 정리합니다.
**title**은 논문 제목의 원문을 그대로 가져와야합니다.

```json
{
"filename": "논문 파일 이름.pdf",
"title": "논문 제목 원문",
"problem": "핵심 문제 (core problem)",
"methodology": "방법론 서술",
"limitation": "한계점 서술"
}
```

#### 각 필드 작성 규칙

**problem**: 이 논문이 해결하려는 핵심 문제(core problem)를 한두 문장으로 직접적으로 서술한다.

**methodology**: 아래 4가지를 모두 포함하는 하나의 문자열로 작성한다.
1. **방법 이름 및 유래** — 제안하는 방법/프레임워크의 이름과 약자의 의미. 논문이 밝히지 않으면 "이름 유래는 논문에 명시되지 않음"으로 적는다. 논문이 통합 방법에 고유 이름을 붙이지 않았다면 임의로 만들지 않는다.
2. **핵심 키워드** — 방법을 이해하는 데 필요한 개념 키워드 5~12개를 괄호 안에 나열한다.
3. **개념적 계보** — 어떤 기존 개념/기법에서 파생·확장·대체되었는지 서술한다. 논문이 직접 밝힌 것과 추론한 것을 구분하여 표기한다.
4. **파이프라인** — 입력이 어떤 단계를 거쳐 최종 출력이 되는지 단계별로 서술한다. 각 단계는 "입력 → 처리(구체적 동사) → 출력"이 드러나야 하며 단계 간 산출물이 끊기지 않아야 한다.

성능 수치, 벤치마크 비교, 실험 결과는 methodology에 쓰지 않는다.

**limitation**: 단순 약점 나열이 아니라, 방법의 어떤 부분이 원인인지를 연결하여 서술한다. (예: "~단계가 ~에 의존하기 때문에 ~한 한계가 있다")

#### 공통 규칙
- 논문에 없는 정보는 추측하지 않고 "논문에 명시되지 않음"으로 표기한다. (언어가 english인 경우 "Not explicitly stated in the paper"로 표기)
- 인자로 전달받은 언어로 작성하되, 고유명사·기법명·모듈명은 영어 원문을 유지한다. 언어가 명시되지 않은 경우 한국어로 작성한다.

#### 예시

```json
{
"filename": "attention_is_all_you_need.pdf",
"title": "Attention Is All You Need",
"problem": "기존 시퀀스 변환 모델(RNN, LSTM)은 순차적 연산 구조로 인해 병렬화가 어렵고, 긴 시퀀스에서 장거리 의존성 포착에 한계가 있다.",
"methodology": "Transformer라는 아키텍처를 제안한다. (키워드: Self-Attention, Multi-Head Attention, Positional Encoding, Encoder-Decoder, Scaled Dot-Product, Feed-Forward Network, Layer Normalization, Residual Connection) 기존 Seq2Seq Encoder-Decoder 구조에서 순환/합성곱 연산을 제거하고 Attention 메커니즘만으로 대체한 것이 핵심이다(논문 명시). 파이프라인: (1) 입력 토큰 시퀀스 → 임베딩 + Positional Encoding → 위치 정보가 포함된 벡터 시퀀스 (2) 벡터 시퀀스 → Encoder의 Multi-Head Self-Attention으로 전역 의존성 포착 → 문맥화된 표현 (3) 문맥화된 표현 → Decoder의 Masked Self-Attention + Encoder-Decoder Attention → 출력 토큰 확률 분포 (4) 확률 분포 → Auto-regressive 디코딩 → 최종 출력 시퀀스.",
"limitation": "Self-Attention이 모든 토큰 쌍을 비교하는 구조이므로 계산 복잡도가 시퀀스 길이의 제곱(O(n²))에 비례하여 긴 시퀀스 처리 비용이 크다. 고정된 Positional Encoding 방식으로 인해 학습 시 접하지 못한 길이의 시퀀스에 대한 일반화가 제한될 수 있다(추론)."
}
```

3.  **출력**:

분석 결과 JSON을 stdout에 작성한 뒤 저장 스크립트에 파이프로 전달합니다.

```bash
python skills/Abstract_Paper/scripts/save_result.py << 'EOF'
{
  "filename": "논문파일이름.pdf",
  "title": "...",
  "problem": "...",
  "methodology": "...",
  "limitation": "..."
}
EOF
```

이후 다음의 메세지를 출력합니다

|key|element|
|---|---|
|status|`success`, `error`|
|reason|reason of error|

```json
{
"status": "success",
"reason": ""
}
```

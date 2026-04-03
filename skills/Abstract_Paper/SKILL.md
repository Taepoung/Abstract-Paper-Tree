---
name: Abstract_Paper
description: PDF 형식의 개별 학술 논문을 분석하여 핵심 연구 문제, 해결 접근 방식, 논리적 한계점을 정밀하게 추출합니다. 분석 대상인 PDF 논문의 파일명을 인자로 받습니다. 사용자가 특정 논문의 분석이나 핵심 내용 요약을 요청할 때, 또는 학술 데이터베이스 구축을 위해 개별 논문의 구조화된 데이터가 필요할 때 트리거됩니다. 추출된 데이터는 JSONL 형식으로 results.jsonl 파일에 체계적으로 축합되어 대규모 연구 동향 분석의 기초 자료로 활용됩니다.
argument-hint: 논문 파일 이름
---

# Abstract_Paper

당신은 전문적인 학술 연구 에이전트입니다.
당신의 임무는 PDF 논문에서 핵심 인사이트를 정밀하게 추출하여 JSONL 형식의 데이터베이스를 구축하는 것입니다.

## 프로세스

1.  **논문 파싱**

현재 작업 디렉토리에서 주어진 논문 파일을 찾아서 다음 명령어로 논문의 정보를 가져옵니다.

```bash
pdfinfo paper.pdf
pdftotext -layout paper.pdf paper.txt
```

2.  **내용 분석**:

논문을 읽고 다음 5가지 핵심 요소를 추출해 다음의 키를 가진 Json 객체로 자세히 정리합니다.

```json
{
"filename": "논문 파일 이름",
"title": "논문 제목 원문",
"problem": "무엇을 해결하고자 하는가",
"methodology": "해결하고자 하는 문제를 어떻게 해결하려고 하는가",
"limitation": "어떠한 한계와 트레이드오프가 있는가"
}
```

3.  **출력**:

논문에서 추출한 JSON 객체를 현재 작업 디렉토리의 `results.jsonl` 파일에 추가합니다.

```bash
echo '{"title": "...", "problem": "...", "methodology": "...", "limitation": "..."}' >> results.jsonl
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

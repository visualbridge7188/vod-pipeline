---
name: vod-pipeline
description: YouTube Membership와 프드프 강의를 720p로 아카이빙하고, 단일 흐름 학습 노트·Google Drive 자료·Notion 페이지로 동기화한다. "VOD 파이프라인", "YouTube 멤버십 강의", "강의 노션 동기화", "강의 전사/요약", "프드프 강의 수집"에 사용한다.
---

# vod-pipeline v5.0 (노션 자체 파일 호스팅 & 토글형 리치 교안)

온라인 강의(YouTube, YouTube Membership, 웹 VOD)의 720p 무손실 아카이빙, 스마트 프레임 추출, 전사록 심층 분석, 노션 토글형 리치 교안 생성, Google Drive 일원화 관리를 하나의 완전한 학습 흐름으로 통합한다.

## 핵심 원칙 (Core Principles)

0. **최상단 Google Drive 듀얼 플레이어 의무화**:
   - 모든 노션 강의 노트의 최상단은 예외 없이 아래 순서를 지킨다:
     1. 📁 **Google Drive 720p 원본 영상 & 고해상도 프레임 아카이브 폴더 바로보기 callout** (영구 링크)
     2. embed **Google Drive 720p 인라인 비디오 스트리밍 플레이어** (노션 내부에서 즉시 시청)
     3. divider
     4. table_of_contents (목차 블록)
     5. divider

1. **대제목(H1) 블록 전체 배경 하이라이트 표준화**:
   - 각 챕터 대제목(`# [N]. [이모지] [챕터 제목] [HH:MM:SS]`)은 텍스트 부분 형광펜이 아닌, **Notion 블록 속성(`color: "yellow_background"`)을 적용하여 블록 전체가 가로 직사각형 배경 배너**로 채워지도록 생성한다. (시각적 대단원 구별 극대화)

2. **모든 세부 소주제(H2)의 토글 제목(`is_toggleable: true`) 및 내부 수납 의무화**:
   - `## [N].[M] [소제목]` 형태의 모든 하위 세션은 Notion 공식 **토글 제목(`heading_2` + `is_toggleable: true`)**으로 생성한다.
   - 각 소주제에 해당하는 **타임스탬프 시연 프레임 이미지 2~4장, 다단계 중첩 불릿 리스트, 인용구, 콜아웃 등 세부 콘텐츠 전체를 토글의 `children`으로 수납**한다.
   - 평소에는 닫혀 있어 최상위 스크롤 피로도를 80% 이상 압축하고, 필요한 세션만 `▶`로 펼쳐 학습할 수 있도록 한다.
   - 최상단 목차(TOC) 블록에서는 모든 H2 토글 제목이 100% 정상 연동되어 클릭 시 해당 위치로 즉시 점프한다.

3. **순수 마크다운 기반 렌더링 & HTML 태그(`<mark>`, `<code>`) 절대 금지**:
   - 마크다운 원문에 `<mark>`, `<code>`, `<span>` 등 raw HTML 태그의 주입을 엄격히 금지한다.
   - **노란 형광펜**: `==핵심 키워드==` ➔ 노션 RichText `annotations: {"bold": true, "color": "yellow_background"}`로 1:1 매핑.
   - **인라인 코드**: 백틱(` `코드` `) ➔ 노션 RichText `annotations: {"code": true}`로 매핑.
   - **볼드**: `**볼드**` ➔ 노션 RichText `annotations: {"bold": true}`로 매핑.
   - 변환기(`md_notion_converter.py`)는 모든 HTML 잔여물을 안전 스트립하여 태그 누출을 원천 방어한다.

3-1. **볼드 기호 중첩 및 잔존 방지 검증 의무화**:
   - 체크리스트(`to_do`), 리스트 항목 생성 시 이미 볼드가 적용된 텍스트를 다시 `**`로 감싸는 중첩 실수를 엄격히 금지한다.
   - 변환 및 검수 파이프라인에서 블록 내부의 `plain_text`에 `**` 기호가 리터럴로 잔존하는지 전수 검사(`literal_asterisks == 0`)를 통과해야만 최종 배포를 허용한다.

3-2. **노션 자체 프라이빗 파일 호스팅 (외부 CDN 절대 배제)**:
   - GitHub 공개 레포지토리나 외부 CDN에 강의 캡처 이미지를 올리는 방식을 전면 폐기한다.
   - Notion 공식 파일 업로드 API(`POST /v1/file_uploads`)를 통해 이미지를 **Notion 내부 AWS S3 보안 스토리지**로 직접 업로드한다.
   - 블록 페이로드: `image: {"type": "file_upload", "file_upload": {"id": file_id}, "caption": [...]}`
   - 노션 워크스페이스 내부 보안 스토리지에 영구 저장되므로 외부 이미지 유출 위험이 0%이며, 링크 만료 및 엑박이 발생하지 않는다.

4. **단락 분할 및 일체형 콜아웃 표준화**:
   - 총괄 요약과 챕터 인트로의 긴 설명글은 반드시 1~2문장 단위(`

`)로 나누어 시각적 여백을 확보한다.
   - 콜아웃은 `!> 💡 **[헤더명]**
!> [설명 본문]` 형태로 첫 줄 볼드 헤더 후 줄바꿈을 의무화하고, 주의/리스크는 `yellow_background`, 목표/원칙은 `green_background`로 위계를 분리한다.

5. **실무 실행 체크포인트의 커리큘럼 적합성 의무화**:
   - 무의미하거나 진도에 맞지 않는 과제를 배제하고, **해당 회차의 실제 진도와 수강생 수준에 정확히 부합하는 [필수 공식 과제] 및 [1주차 실무 실행 체크포인트]**를 체크박스(`to_do`)로 구성한다.
   - 모든 자료실 연계 링크는 `notion_resources.index.json` 기반의 영구 노션 페이지 URL로 연결한다.

6. **GitHub CDN 기반 영구 미디어 아카이브**:
   - Google Drive 임시 링크의 CORS 차단을 배제하고, GitHub 공개 레포지토리(`visualbridge7188/vod-pipeline/main/assets/frames/...`) 영구 CDN을 통해 노션 공식 `image` 블록으로 무인증 로딩을 100% 보장한다.

7. **원자적 스왑 (Atomic Swap)**:
   - 새 페이지 생성이 완료되고 API 검증을 통과한 시점에만 이전 구버전 페이지를 아카이브한다.

## Notion 페이지 블록 계층 표준

1. 📁 **Google Drive 720p 원본 영상 폴더 callout**
2. 🎬 **Google Drive 720p 인라인 비디오 스트리밍 embed 플레이어**
3. `divider`
4. `table_of_contents` (전체 H1, H2 목차)
5. `divider`
6. `# 🎯 총괄 요약 (Executive Summary)` (단락 분할 + 형광펜 강조)
7. `divider`
8. `# 🗺️ 타임라인 기반 심층 분석 (Timeline-based Deep Dive)`
9. 시간순 챕터 전개 (반복):
   - `# [N]. [이모지] [챕터 제목] [HH:MM:SS]` (**color: yellow_background 블록 하이라이트**)
   - `image` (대표 슬라이드 배너)
   - 인트로 요약 문단 (1~2문장 분할 단락)
   - `!> 💡 **수강생 핵심 목표**
!> 본문` (일체형 콜아웃)
   - `table` (챕터 요약 또는 비교 매트릭스)
   - **하위 세부 세션 (토글 제목 수납)**:
     - `## [N].[M] [소제목]` (**is_toggleable: true**)
       - ↳ `image` (핵심 시연 프레임 2~4장)
       - ↳ `bulleted_list_item` (2~3단계 계층형 들여쓰기 불릿)
       - ↳ `quote` (현장 어록 인용구)
10. `divider`
11. `# 💡 실행 가능한 인사이트 (Actionable Insights)`
    - `## 🚀 Pro-Tips`
    - `## 🤔 추가 연계 질문 (For Deeper Thinking)`
12. `divider`
13. `# ✅ 강의 실전 실행 과제 (Action Checklist)`
    - `## 1. 📌 필수 공식 과제 (네이버 카페 인증)` (`to_do`)
    - `## 2. 🧰 1주차 실무 실행 체크포인트 (자료실 연계)` (`to_do` + 자료실 영구 링크)
14. `divider`
15. 🔗 **자료실 메인 페이지 및 질의응답 안내 callout**
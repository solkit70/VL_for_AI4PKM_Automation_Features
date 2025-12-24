# 워크플로우 체인 구성 가이드

여러 에이전트를 연결하여 자동화 파이프라인을 구축하는 방법을 다룹니다.

---

## 목차

1. [워크플로우 체인이란?](#워크플로우-체인이란)
2. [체인 설계 원칙](#체인-설계-원칙)
3. [기본 체인 패턴](#기본-체인-패턴)
4. [고급 체인 패턴](#고급-체인-패턴)
5. [실전 예제](#실전-예제)
6. [문제 해결](#문제-해결)

---

## 워크플로우 체인이란?

### 개념

**워크플로우 체인**은 여러 에이전트를 순차적 또는 병렬로 연결하여 복잡한 자동화 작업을 수행하는 패턴입니다.

```
입력 → 에이전트 A → 에이전트 B → 에이전트 C → 최종 출력
```

### 왜 필요한가?

**단일 에이전트의 한계**:
- 복잡한 작업을 하나의 프롬프트로 처리하기 어려움
- 재사용성 낮음
- 유지보수 어려움

**워크플로우 체인의 장점**:
- 각 에이전트는 단일 책임
- 재사용 가능한 모듈화
- 유연한 구성
- 쉬운 디버깅

### 예시: 블로그 발행 파이프라인

```
1. 웹 클리핑 저장
   ↓
2. [EIC] 콘텐츠 정리 및 구조화
   ↓
3. [SNS] 핵심 개념 요약
   ↓
4. [BPG] 블로그 포스트 형식으로 변환
   ↓
5. [IMG] 이미지 제안 및 삽입
   ↓
6. [SEO] SEO 최적화
   ↓
7. 발행 준비 완료
```

---

## 체인 설계 원칙

### 1. 입출력 일관성

각 에이전트의 출력이 다음 에이전트의 입력 형식과 일치해야 합니다.

```yaml
# 좋은 예
nodes:
  - name: Agent A
    output_path: step1/  # 마크다운 파일 생성

  - name: Agent B
    input_path: step1/   # 마크다운 파일 읽기
    output_path: step2/
```

### 2. 폴더 구조

체인의 각 단계를 명확한 폴더로 분리:

```
VL_AI4PKM_Automation/
├── 00-Inbox/           # 원본 입력
├── 01-Processed/       # 1단계 처리
├── 02-Enriched/        # 2단계 강화
├── 03-Formatted/       # 3단계 포맷팅
└── 04-Published/       # 최종 출력
```

### 3. 파일 명명 규칙

체인 단계를 파일명에 반영:

```
# Agent A 출력
article_01_processed.md

# Agent B 출력
article_02_enriched.md

# Agent C 출력
article_03_formatted.md
```

또는:

```yaml
# Agent A
output_suffix: "_processed"

# Agent B
output_suffix: "_enriched"
```

### 4. 실패 처리

한 에이전트가 실패해도 전체 체인이 멈추지 않도록:

```yaml
nodes:
  - name: Critical Agent
    task_priority: high

  - name: Optional Agent
    task_priority: low  # 실패해도 다음 단계 진행
```

---

## 기본 체인 패턴

### 패턴 1: 순차 체인 (Sequential Chain)

가장 기본적인 패턴. A → B → C 순서로 실행.

```yaml
nodes:
  # 1단계: 원본 정리
  - type: agent
    name: Cleaner
    input_path: 00-Inbox
    output_path: 01-Cleaned
    output_type: new_file

  # 2단계: 내용 강화
  - type: agent
    name: Enricher
    input_path: 01-Cleaned
    output_path: 02-Enriched
    output_type: new_file

  # 3단계: 발행 준비
  - type: agent
    name: Publisher
    input_path: 02-Enriched
    output_path: 03-Published
    output_type: new_file
```

**동작**:
1. 사용자가 `00-Inbox/article.md` 저장
2. Cleaner 실행 → `01-Cleaned/article_cleaned.md` 생성
3. Enricher 감지 → `02-Enriched/article_enriched.md` 생성
4. Publisher 감지 → `03-Published/article_published.md` 생성

### 패턴 2: 분기 체인 (Branching Chain)

하나의 입력에서 여러 출력으로 분기.

```yaml
nodes:
  # 공통 1단계
  - type: agent
    name: Processor
    input_path: Inbox
    output_path: Processed

  # 분기 A: 요약
  - type: agent
    name: Summarizer
    input_path: Processed
    output_path: Summaries

  # 분기 B: 번역
  - type: agent
    name: Translator
    input_path: Processed
    output_path: Translated

  # 분기 C: 코드 추출
  - type: agent
    name: Code Extractor
    input_path: Processed
    output_path: CodeSnippets
```

**동작**:
```
Inbox/article.md
     ↓
Processed/article_processed.md
     ├→ Summaries/article_summary.md
     ├→ Translated/article_ko.md
     └→ CodeSnippets/article_snippets.md
```

### 패턴 3: 병합 체인 (Merging Chain)

여러 입력을 하나의 출력으로 병합.

```yaml
nodes:
  # 여러 소스에서 입력
  - type: agent
    name: Weekly Report
    input_path:
      - DailyNotes/
      - Projects/
      - Research/
    output_path: Reports/Weekly
    cron: "0 18 * * 0"  # 매주 일요일
```

**동작**:
```
DailyNotes/*.md   ─┐
Projects/*.md     ─┼→ Weekly Report → Reports/weekly_YYYYMMDD.md
Research/*.md     ─┘
```

### 패턴 4: 조건부 체인 (Conditional Chain)

특정 조건에 따라 다른 에이전트 실행.

```yaml
nodes:
  # 긴 문서 처리
  - type: agent
    name: Long Document Processor
    input_path: Documents
    trigger_min_size_kb: 100  # 100KB 이상만
    output_path: LongDocs/Processed

  # 짧은 문서 처리
  - type: agent
    name: Short Document Processor
    input_path: Documents
    trigger_max_size_kb: 100  # 100KB 미만만
    output_path: ShortDocs/Processed
```

**동작**:
```
Documents/
├── short.md (50KB)  → Short Document Processor
└── long.md (500KB)  → Long Document Processor
```

### 패턴 5: 루프 체인 (Feedback Loop)

출력을 다시 입력으로 사용 (주의: 무한 루프 방지 필요).

```yaml
nodes:
  - type: agent
    name: Iterative Improver
    input_path: Drafts
    trigger_content_pattern: "%% #improve %%"  # 마커 있을 때만
    post_process_action: remove_trigger_content  # 처리 후 마커 제거
    output_path: Drafts  # 같은 폴더에 업데이트
    output_type: update_file
```

**동작**:
1. `Drafts/article.md`에 `%% #improve %%` 추가
2. Agent 실행 → 개선된 내용으로 업데이트
3. 마커 제거 → 다시 트리거되지 않음

---

## 고급 체인 패턴

### 패턴 6: 우선순위 체인 (Priority Chain)

중요한 작업을 먼저 처리.

```yaml
nodes:
  # 우선 처리: 긴급 문서
  - type: agent
    name: Urgent Processor
    input_path: Inbox
    input_pattern: "*_urgent.md"
    task_priority: high
    output_path: Processed/Urgent

  # 일반 처리
  - type: agent
    name: Normal Processor
    input_path: Inbox
    exclude_pattern: "*_urgent.md"
    task_priority: medium
    output_path: Processed/Normal
```

### 패턴 7: 시간 기반 체인 (Time-based Chain)

시간대별로 다른 처리.

```yaml
nodes:
  # 아침: 일일 요약
  - type: agent
    name: Morning Briefing
    cron: "0 9 * * *"  # 매일 오전 9시
    input_path: DailyNotes
    output_path: Briefings/Morning

  # 저녁: 주간 리뷰
  - type: agent
    name: Weekly Review
    cron: "0 18 * * 0"  # 일요일 저녁 6시
    input_path: DailyNotes
    trigger_max_age_hours: 168  # 지난 7일
    output_path: Reviews/Weekly
```

### 패턴 8: 병렬 처리 후 병합 (Map-Reduce)

여러 에이전트가 병렬로 처리한 후 결과를 병합.

```yaml
nodes:
  # Map: 병렬 처리
  - type: agent
    name: Chapter Summarizer
    input_path: Chapters
    output_path: ChapterSummaries
    max_parallel: 5  # 5개까지 동시 실행

  # Reduce: 병합
  - type: agent
    name: Book Compiler
    input_path: ChapterSummaries
    output_path: Books
    trigger_min_files: 10  # 10개 챕터 모이면 실행
    cron: "0 0 * * 0"  # 또는 매주 일요일
```

### 패턴 9: 다단계 검증 체인 (Validation Chain)

각 단계에서 검증 수행.

```yaml
nodes:
  # 1단계: 초안 작성
  - type: agent
    name: Draft Writer
    input_path: Ideas
    output_path: Drafts

  # 2단계: 문법 검사
  - type: agent
    name: Grammar Checker
    input_path: Drafts
    output_path: GrammarChecked

  # 3단계: 사실 확인
  - type: agent
    name: Fact Checker
    input_path: GrammarChecked
    output_path: FactChecked

  # 4단계: 최종 승인
  - type: agent
    name: Final Approver
    input_path: FactChecked
    output_path: Approved
```

---

## 실전 예제

### 예제 1: AI 학습 자료 파이프라인

**목표**: 웹 클리핑 → 정리 → 요약 → 블로그 포스트

#### 폴더 구조

```
VL_AI4PKM_Automation/
├── vl_ai4pkm_clippings/      # 0. 웹 클리핑 원본
├── vl_ai4pkm_materials/      # 1. 정리된 자료
├── AI/Study/                 # 2. 학습 요약
└── Publish/Blog/             # 3. 블로그 포스트
```

#### orchestrator.yaml

```yaml
nodes:
  # 1단계: 웹 클리핑 정리
  - type: agent
    name: Enrich Ingested Content (EIC)
    abbreviation: eic
    executor: claude_code
    input_path: vl_ai4pkm_clippings
    output_path: vl_ai4pkm_materials
    output_type: new_file
    timeout_minutes: 15
    max_parallel: 3
    enabled: true

  # 2단계: 학습 노트 요약
  - type: agent
    name: Summarize Note for Study (SNS)
    abbreviation: sns
    executor: claude_code
    input_path: vl_ai4pkm_materials
    input_pattern: "*_enriched.md"  # EIC 출력만 처리
    output_path: AI/Study
    output_type: new_file
    timeout_minutes: 10
    max_parallel: 2
    enabled: true

  # 3단계: 블로그 포스트 생성
  - type: agent
    name: Blog Post Generator (BPG)
    abbreviation: bpg
    executor: claude_code
    input_path: AI/Study
    input_pattern: "*_summary.md"  # SNS 출력만 처리
    trigger_content_pattern: "%% #publish %%"  # 발행 마커 있을 때만
    post_process_action: remove_trigger_content
    output_path: Publish/Blog
    output_type: new_file
    timeout_minutes: 20
    enabled: true
```

#### 실행 흐름

```
1. 사용자: vl_ai4pkm_clippings/ai_article.md 저장
   ↓ (FileSystem Monitor 감지)

2. EIC 실행
   입력: vl_ai4pkm_clippings/ai_article.md
   출력: vl_ai4pkm_materials/ai_article_enriched.md
   ↓ (FileSystem Monitor 감지)

3. SNS 실행 (input_pattern 일치)
   입력: vl_ai4pkm_materials/ai_article_enriched.md
   출력: AI/Study/ai_article_summary.md
   ↓ (FileSystem Monitor 감지)

4. 사용자: AI/Study/ai_article_summary.md에 "%% #publish %%" 추가
   ↓ (trigger_content_pattern 일치)

5. BPG 실행
   입력: AI/Study/ai_article_summary.md
   출력: Publish/Blog/ai_article.md
   마커 제거 완료
```

### 예제 2: 프로젝트 문서화 파이프라인

**목표**: 코드 → 문서 추출 → API 문서 → README 업데이트

#### 폴더 구조

```
Project/
├── src/                       # 0. 소스 코드
├── docs/extracted/            # 1. 추출된 문서
├── docs/api/                  # 2. API 문서
└── docs/README.md             # 3. 최종 README
```

#### orchestrator.yaml

```yaml
nodes:
  # 1단계: 코드에서 문서 추출
  - type: agent
    name: Code Doc Extractor (CDE)
    abbreviation: cde
    executor: claude_code
    input_path: src
    input_pattern: "*.{py,js,ts}"
    output_path: docs/extracted
    output_type: new_file

  # 2단계: API 문서 생성
  - type: agent
    name: API Doc Generator (ADG)
    abbreviation: adg
    executor: claude_code
    input_path: docs/extracted
    output_path: docs/api
    output_type: new_file

  # 3단계: README 업데이트
  - type: agent
    name: README Updater (RU)
    abbreviation: ru
    executor: claude_code
    input_path: docs/api
    output_path: docs
    output_type: update_file  # README.md 업데이트
    cron: "0 0 * * 0"  # 매주 일요일 자정
```

### 예제 3: 멀티미디어 학습 자료 파이프라인

**목표**: 영상 스크립트 → 텍스트 요약 → 플래시카드 → 퀴즈

#### 폴더 구조

```
Learning/
├── 00-VideoScripts/           # 0. 영상 스크립트
├── 01-Summaries/              # 1. 텍스트 요약
├── 02-Flashcards/             # 2. 플래시카드
└── 03-Quizzes/                # 3. 퀴즈
```

#### orchestrator.yaml

```yaml
nodes:
  # 1단계: 스크립트 요약
  - type: agent
    name: Script Summarizer
    input_path: 00-VideoScripts
    output_path: 01-Summaries
    output_type: new_file

  # 2A단계: 플래시카드 생성 (병렬)
  - type: agent
    name: Flashcard Generator
    input_path: 01-Summaries
    output_path: 02-Flashcards
    output_type: new_file
    max_parallel: 3

  # 2B단계: 퀴즈 생성 (병렬)
  - type: agent
    name: Quiz Generator
    input_path: 01-Summaries
    output_path: 03-Quizzes
    output_type: new_file
    max_parallel: 3
```

**동작 (병렬 분기)**:
```
00-VideoScripts/lesson1.md
         ↓
01-Summaries/lesson1_summary.md
         ├→ 02-Flashcards/lesson1_flashcards.md (동시)
         └→ 03-Quizzes/lesson1_quiz.md (동시)
```

---

## 문제 해결

### 문제 1: 체인이 멈춤

**증상**:
- 1단계는 실행되지만 2단계가 시작되지 않음

**원인**:
- 파일명 패턴 불일치
- 폴더 경로 오류
- FileSystem Monitor 비활성화

**해결**:

1. 출력 파일명 확인:
```bash
ls -la 01-Processed/
# article_processed.md 확인
```

2. 2단계 input_pattern 확인:
```yaml
nodes:
  - name: Step 2
    input_path: 01-Processed
    input_pattern: "*_processed.md"  # 파일명과 일치하는지 확인
```

3. 로그 확인:
```bash
tail -f _Settings_/Logs/orchestrator.log
```

### 문제 2: 무한 루프

**증상**:
- 같은 에이전트가 계속 반복 실행됨

**원인**:
- 출력이 다시 입력으로 들어감
- 파일명이 변경되지 않음

**해결**:

1. 입출력 경로 분리:
```yaml
# 나쁜 예
input_path: Documents
output_path: Documents  # 무한 루프 위험!

# 좋은 예
input_path: Documents
output_path: Documents/Processed
```

2. exclude_pattern 사용:
```yaml
input_path: Documents
output_path: Documents
exclude_pattern: "*_processed.md"  # 출력 파일 제외
```

3. 트리거 마커 사용:
```yaml
trigger_content_pattern: "%% #process %%"
post_process_action: remove_trigger_content  # 한 번만 실행
```

### 문제 3: 파일명 중복

**증상**:
- 같은 파일명으로 여러 에이전트 출력이 충돌

**해결**:

1. 파일명 접미사 사용:
```yaml
nodes:
  - name: Step 1
    output_suffix: "_step1"  # article_step1.md

  - name: Step 2
    output_suffix: "_step2"  # article_step2.md
```

2. 폴더로 분리:
```yaml
nodes:
  - name: Step 1
    output_path: Step1/  # Step1/article.md

  - name: Step 2
    output_path: Step2/  # Step2/article.md
```

### 문제 4: 체인 중간에 실패

**증상**:
- 2단계 에이전트가 실패하면 전체 체인 중단

**해결**:

1. 에러 핸들링 설정:
```yaml
nodes:
  - name: Critical Step
    task_priority: high
    # 실패 시 재시도

  - name: Optional Step
    task_priority: low
    # 실패해도 무시
```

2. 수동 재개 기능:
```bash
# 실패한 Task 찾기
grep -l "FAILED" _Settings_/Tasks/*.md

# 수동으로 재실행
ai4pkm -t step2
```

### 문제 5: 성능 저하

**증상**:
- 체인이 너무 느림
- 시스템 리소스 과다 사용

**해결**:

1. max_parallel 조정:
```yaml
# CPU 집약적 작업
max_parallel: 1

# 가벼운 작업
max_parallel: 5
```

2. timeout 최적화:
```yaml
# 긴 작업
timeout_minutes: 30

# 짧은 작업
timeout_minutes: 5
```

3. 배치 처리:
```yaml
# 파일이 많이 모일 때까지 대기
trigger_min_files: 10
cron: "0 */6 * * *"  # 6시간마다
```

---

## 체크리스트

- [ ] 워크플로우 체인의 개념을 이해한다
- [ ] 입출력 일관성을 유지할 수 있다
- [ ] 순차 체인을 구현할 수 있다
- [ ] 분기 체인을 구현할 수 있다
- [ ] 조건부 체인을 구현할 수 있다
- [ ] 무한 루프를 방지할 수 있다
- [ ] 파일명 충돌을 해결할 수 있다
- [ ] 체인 실패를 디버깅할 수 있다
- [ ] 성능을 최적화할 수 있다
- [ ] 실전 파이프라인을 설계할 수 있다

## 다음 단계

1. ✅ 기본 체인 패턴 학습
2. ✅ 고급 체인 패턴 학습
3. ✅ 실전 예제 분석
4. ⬜ 자신만의 워크플로우 설계
5. ⬜ 프로덕션 배포 및 모니터링

## 관련 문서

- [[01_custom_agent_guide.md]] - 커스텀 에이전트 생성
- [[../03-Orchestrator_Deep_Dive/01_orchestrator_architecture.md]] - Orchestrator 아키텍처
- [[../03-Orchestrator_Deep_Dive/03_orchestrator_hands_on.md]] - 실습 가이드
